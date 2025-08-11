# app/public_api.py
import json
import os
import time
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import uuid

from dotenv import load_dotenv
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY não definida")

# Importa SOMENTE o que precisamos do teu agente
try:
    from app.agent.financial_agent import (
        agent,                  # teu orquestrador
        obter_json_financeiro,  # tool que consolida valuation + múltiplos (retorna str JSON)
        calcular_valuation,     # tool -> markdown
        calcular_multiplos,     # tool -> markdown
    )
except Exception as e:
    raise RuntimeError(f"Falha ao importar financial_agent: {e}")

# CAPM é opcional: se não existir, tratamos
try:
    from app.agent.financial_agent import capm_calcular  # tool -> str JSON
except Exception:
    capm_calcular = None

# Config CORS via env
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*")
origins = [o.strip() for o in allowed_origins.split(",") if o.strip()] or ["*"]

app = FastAPI(title="BullCapital Public API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =======================
# Rate limiting simples (janela deslizante por IP)
# =======================
RATE_LIMIT_MAX = int(os.getenv("RATE_LIMIT_MAX", "60"))  # req por janela
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seg
_ip_windows: Dict[str, Tuple[int, float]] = {}

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    try:
        ip = request.client.host if request.client else "unknown"
        count, window_start = _ip_windows.get(ip, (0, time.time()))
        now = time.time()
        if now - window_start > RATE_LIMIT_WINDOW:
            count = 0
            window_start = now
        count += 1
        _ip_windows[ip] = (count, window_start)
        if count > RATE_LIMIT_MAX:
            return HTTPException(status_code=429, detail="too many requests")
    except Exception:
        pass
    response = await call_next(request)
    return response

# =======================
# Histórico (in-memory com persistência opcional via SQLAlchemy)
# =======================
CONVERSATIONS: Dict[str, List["ConversationMessage"]] = {}
PERSIST_HISTORY = os.getenv("PERSIST_HISTORY", "false").lower() == "true"

# tenta habilitar persistência
SessionLocal = None
Models = None
try:
    if PERSIST_HISTORY:
        from app.core.database import SessionLocal as _SessionLocal, Base, engine
        from app.core import models as _models
        # cria tabelas se não existirem
        Base.metadata.create_all(bind=engine)
        SessionLocal = _SessionLocal
        Models = _models
except Exception as e:
    # fallback: desabilita persistência se falhar
    PERSIST_HISTORY = False

class ConversationMessage(BaseModel):
    role: str  # 'user' | 'ai'
    content: str
    timestamp: str  # ISO 8601

# util: salvar mensagem se persistência ativa
def _persist_message(conversation_id: str, role: str, content: str) -> None:
    if not PERSIST_HISTORY or SessionLocal is None or Models is None:
        return
    try:
        db = SessionLocal()
        # garante conversa
        from sqlalchemy import select
        conv = db.execute(
            select(Models.Conversation).where(Models.Conversation.id == conversation_id)
        ).scalar_one_or_none()
        if conv is None:
            # cria conversa sem user amarrado
            conv = Models.Conversation(id=uuid.UUID(conversation_id), user_id=uuid.uuid4(), title="Conversa")
            db.add(conv)
            db.flush()
        msg = Models.Message(
            conversation_id=conv.id,
            sender="user" if role == "user" else "bot",
            content=content,
        )
        db.add(msg)
        db.commit()
    except Exception:
        if 'db' in locals():
            db.rollback()
    finally:
        if 'db' in locals():
            db.close()

# paginação do histórico
def _get_history(conversation_id: str, limit: int, offset: int) -> List[ConversationMessage]:
    if PERSIST_HISTORY and SessionLocal is not None and Models is not None:
        try:
            db = SessionLocal()
            from sqlalchemy import select
            q = (
                select(Models.Message)
                .where(Models.Message.conversation_id == uuid.UUID(conversation_id))
                .order_by(Models.Message.timestamp.asc())
                .offset(offset)
                .limit(limit)
            )
            rows = db.execute(q).scalars().all()
            return [
                ConversationMessage(
                    role="user" if r.sender == "user" else "ai",
                    content=r.content,
                    timestamp=(r.timestamp.isoformat() + "Z") if r.timestamp else datetime.utcnow().isoformat() + "Z",
                )
                for r in rows
            ]
        finally:
            db.close()
    # fallback in-memory
    hist = CONVERSATIONS.get(conversation_id, [])
    return hist[offset: offset + limit]

# =======================
# Execução com timeout
# =======================
EXECUTOR = ThreadPoolExecutor(max_workers=4)
DEFAULT_TIMEOUT = float(os.getenv("AI_TOOL_TIMEOUT", "20"))

def run_with_timeout(fn, timeout: float = DEFAULT_TIMEOUT):
    future = EXECUTOR.submit(fn)
    try:
        return future.result(timeout=timeout)
    except FuturesTimeout:
        future.cancel()
        raise HTTPException(status_code=504, detail="timeout ao processar solicitação")

# =======================
# Cache TTL para endpoints financeiros
# =======================
TTL_SECONDS = int(os.getenv("AI_CACHE_TTL", "120"))
FinanceCache: Dict[str, Tuple[float, dict]] = {}
ValuationCache: Dict[str, Tuple[float, dict]] = {}
MultiplesCache: Dict[str, Tuple[float, dict]] = {}
CapmCache: Dict[str, Tuple[float, dict]] = {}

def _get_or_set(cache: Dict[str, Tuple[float, dict]], key: str, compute):
    now = time.time()
    entry = cache.get(key)
    if entry:
        exp, value = entry
        if now < exp:
            return value
    value = compute()
    cache[key] = (now + TTL_SECONDS, value)
    return value

# =======================
# Endpoints
# =======================
@app.get("/health")
def health():
    return {"ok": True, "service": "BullCapital Public API"}

# JSON consolidado (valuation + múltiplos)
@app.get("/finance/{ticker}")
def finance_json(ticker: str):
    try:
        def _compute():
            raw = run_with_timeout(lambda: obter_json_financeiro.entrypoint(ticker=ticker))
            return json.loads(raw)
        return _get_or_set(FinanceCache, ticker.upper(), _compute)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro obter_json_financeiro: {e}")

# Tabelas (markdown) se quiser renderizar no front
@app.get("/valuation/{ticker}")
def valuation_markdown(ticker: str):
    try:
        def _compute():
            md = run_with_timeout(lambda: calcular_valuation.entrypoint(ticker=ticker))
            return {"markdown": md}
        return _get_or_set(ValuationCache, ticker.upper(), _compute)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro calcular_valuation: {e}")

@app.get("/multiples/{ticker}")
def multiples_markdown(ticker: str):
    try:
        def _compute():
            md = run_with_timeout(lambda: calcular_multiplos.entrypoint(ticker=ticker))
            return {"markdown": md}
        return _get_or_set(MultiplesCache, ticker.upper(), _compute)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro calcular_multiplos: {e}")

# CAPM detalhado (JSON) — só se a tool existir
@app.get("/capm/{ticker}")
def capm_json(ticker: str):
    if capm_calcular is None:
        raise HTTPException(status_code=501, detail="CAPM não configurado neste servidor.")
    try:
        def _compute():
            raw = run_with_timeout(lambda: capm_calcular.entrypoint(ticker=ticker))
            return json.loads(raw)
        return _get_or_set(CapmCache, ticker.upper(), _compute)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro capm_calcular: {e}")

# Notícias via agente web (se foi adicionado no FinancialAgent)
@app.get("/news")
def news(q: str = Query(..., description="ex: 'notícias PETR4 últimos 90 dias'")):
    try:
        ag_web = getattr(agent, "ag_web", None)
        if ag_web is None:
            raise HTTPException(status_code=501, detail="Agente web não configurado.")
        res = run_with_timeout(lambda: agent._extract_response_content(ag_web.run(q)))
        return {"markdown": res}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro news: {e}")

# ---------- CHAT (stateless com histórico) ----------
class ChatIn(BaseModel):
    question: str
    conversation_id: Optional[str] = None

class ChatOut(BaseModel):
    content: str
    conversation_id: str

@app.post("/chat", response_model=ChatOut)
def chat(payload: ChatIn):
    try:
        # identifica conversa
        conversation_id = payload.conversation_id or str(uuid.uuid4())
        if conversation_id not in CONVERSATIONS:
            CONVERSATIONS[conversation_id] = []

        # registra pergunta do usuário (mem e opcionalmente DB)
        msg_user = ConversationMessage(
            role="user",
            content=payload.question,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )
        CONVERSATIONS[conversation_id].append(msg_user)
        _persist_message(conversation_id, "user", payload.question)

        # resposta do agente com timeout
        content = run_with_timeout(lambda: agent.chat(payload.question))

        # registra resposta da IA
        msg_ai = ConversationMessage(
            role="ai",
            content=content,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )
        CONVERSATIONS[conversation_id].append(msg_ai)
        _persist_message(conversation_id, "ai", content)

        return ChatOut(content=content, conversation_id=conversation_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro chat: {e}")

# ---------- HISTÓRICO DE CONVERSA ----------
@app.get("/conversations/{conversation_id}", response_model=List[ConversationMessage])
def get_conversation_history(
    conversation_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    # retorna lista paginada
    try:
        return _get_history(conversation_id, limit, offset)
    except Exception:
        # fallback em memória se algo falhar
        hist = CONVERSATIONS.get(conversation_id)
        if hist is None:
            raise HTTPException(status_code=404, detail="conversa não encontrada")
        return hist[offset: offset + limit]

class AnalyzeIn(BaseModel):
    ticker: str
    question: str

@app.post("/analyze")
def analyze(payload: AnalyzeIn):
    try:
        content = run_with_timeout(lambda: agent.analyze_stock(payload.question, payload.ticker))
        return {"content": content}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro analyze: {e}")