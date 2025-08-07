"""
API HTTP Server para o Agente Financeiro COM CONTEXTO.
Servidor FastAPI que expõe o agente como endpoints REST com sistema de chat contextual.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn
from core.models import Message, ChatRequest, ChatResponse, Conversation, HealthResponse
from agent.financial_agent import agent
from typing import Optional
from core.database import engine
from core.models import Base
from contextlib import asynccontextmanager
import logging


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação FastAPI.
    
    Função assíncrona que controla eventos de inicialização e finalização
    da aplicação. Durante a inicialização, cria as tabelas do banco de dados
    automaticamente usando SQLAlchemy.
    
    Args:
        app: Instância da aplicação FastAPI
        
    Yields:
        None: Controle retorna ao FastAPI durante a execução da aplicação
        
    Note:
        Em caso de falha na criação das tabelas, a aplicação continua
        executando mas registra o erro no log.
    """
    # Startup
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        logger.warning("Application will continue without database connection")
    
    yield
    
    # Shutdown
    logger.info("Application shutting down...")


# Criar aplicação FastAPI
app = FastAPI(
    title="Agente de Análise Financeira",
    description="API para análise fundamentalista de ações usando Agno Framework",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Armazenamento temporário de conversas usando o modelo Conversation
conversations: dict[str, Conversation] = {}

def generate_conversation_id() -> str:
    """Gera um ID único para uma nova conversa."""
    import uuid
    return f"conv_{uuid.uuid4().hex[:8]}"

def generate_conversation_title(first_message: str) -> str:
    """Gera um título para a conversa baseado na primeira mensagem."""
    try:
        # Se a mensagem for muito longa, pegar apenas o início
        if len(first_message) > 100:
            first_message = first_message[:100] + "..."
        
        # Gerar título usando o agente
        title_prompt = f"""
        Gere um título curto e descritivo (máximo 50 caracteres) para uma conversa que começou com:
        "{first_message}"
        
        O título deve ser:
        - Conciso e claro
        - Descrever o assunto principal
        - Máximo 50 caracteres
        - Sem aspas ou pontuação desnecessária
        
        Exemplos de bons títulos:
        - "Análise de margem de segurança"
        - "Dúvidas sobre valuation"
        - "Comparação de múltiplos"
        - "Conceitos fundamentais"
        - "Explicação de múltiplos"
        - "Fundamentos de investimento"
        
        Título:"""
        
        title_response = agent.chat(title_prompt)
        
        # Limpar e validar o título
        title = title_response.strip()
        if len(title) > 50:
            title = title[:47] + "..."
        
        return title if title else "Nova conversa"
        
    except Exception as e:
        print(f"Erro ao gerar título: {e}")
        return "Nova conversa"

def create_conversation_object(conversation_id: str, user_id: str, title: str) -> Conversation:
    """Cria uma nova conversa."""
    return Conversation(
        conversation_id=conversation_id,
        user_id=user_id,
        title=title,
        messages=[]
    )

def get_or_create_conversation(conversation_id: str, user_id: str, first_message: str = None) -> Conversation:
    """Obtém uma conversa existente ou cria uma nova com título gerado pelo agente."""
    if conversation_id not in conversations:
        # Gerar título baseado na primeira mensagem
        if first_message:
            title = generate_conversation_title(first_message)
        else:
            title = "Nova conversa"
        
        conversations[conversation_id] = create_conversation_object(conversation_id, user_id, title)
    return conversations[conversation_id]


def create_message(sender: str, content: str) -> Message:
    """Cria uma mensagem com timestamp."""
    return Message(
        sender=sender,
        content=content,
        timestamp=datetime.now().isoformat()
    )


@app.get("/")
async def root():
    """Endpoint raiz da API."""
    return {
        "message": "Agente de Análise Financeira API",
        "version": "1.0.0",
        "features": [
            "Chat com histórico de conversas",
            "Sistema de conversas persistentes"
        ],
        "endpoints": {
            "chat": "POST /chat",
            "get_conversation": "GET /conversations/{id}",
            "delete_conversation": "DELETE /conversations/{id}",
            "list_conversations": "GET /conversations?user_id={user_id}",
            "health": "GET /health",
            "docs": "/docs"
        }
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """
    Endpoint principal para conversar com o agente.
    Se conversation_id não for fornecido, usa a conversa "default".
    """
    try:
        # Criar mensagem do usuário
        user_message = create_message(request.sender, request.content)
        
        # Usar conversation_id fornecido ou "default"
        conversation_id = request.conversation_id or generate_conversation_id()
        
        # Obter ou criar conversa usando o modelo Conversation com título gerado pelo agente
        conversation = get_or_create_conversation(conversation_id, request.user_id, request.content)
        
        # Processar com o agente COM CONTEXTO
        agent_response = agent.chat(
            question=request.content,
            conversation_history=conversation.messages
        )
        
        # Criar mensagem do bot
        bot_message = create_message("bot", agent_response)
        
        # Adicionar mensagens à conversa
        conversation.messages.extend([user_message, bot_message])
        
        return ChatResponse(messages=conversation.messages)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no agente: {str(e)}")



@app.get("/conversations/{conversation_id}", response_model=ChatResponse)
async def get_conversation(conversation_id: str):
    """
    Recupera o histórico de uma conversa específica.
    """
    if conversation_id not in conversations:
        return ChatResponse(messages=[])
    
    conversation = conversations[conversation_id]
    return ChatResponse(messages=conversation.messages)


@app.delete("/conversations/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """
    Limpa o histórico de uma conversa específica.
    """
    if conversation_id in conversations:
        del conversations[conversation_id]
    
    return {"message": f"Conversa {conversation_id} limpa com sucesso"}


@app.get("/conversations")
async def list_conversations(user_id: Optional[str] = None):
    """
    Lista todas as conversas disponíveis.
    
    Args:
        user_id (Optional[str]): Filtrar conversas por ID do usuário. Se não fornecido, retorna todas as conversas.
    """
    conversation_list = []
    
    for conv_id, conversation in conversations.items():
        # Filtrar por user_id se fornecido
        if user_id is not None and conversation.user_id != user_id:
            continue
            
        conversation_list.append({
            "conversation_id": conversation.conversation_id,
            "user_id": conversation.user_id,
            "title": conversation.title,
            "message_count": len(conversation.messages),
            "last_message": conversation.messages[-1].timestamp if conversation.messages else None
        })
    
    return {
        "conversations": conversation_list,
        "count": len(conversation_list),
        "filtered_by_user_id": user_id
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Endpoint de health check."""
    return HealthResponse(
        status="healthy",
        service="Agente Financeiro",
        timestamp=datetime.now().isoformat()
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) 