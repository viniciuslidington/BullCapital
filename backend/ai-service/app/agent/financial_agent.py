"""
Módulo do Agente Financeiro COM CONTEXTO - Análise Fundamentalista com Agno Framework.
Versão que considera histórico de mensagens para respostas mais contextuais.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import json
import unicodedata
import requests
from datetime import datetime, timedelta

# Carregar variáveis de ambiente
load_dotenv()

# Configurações de robustez
os.environ.update({
    "OPENAI_MAX_RETRIES": "10",
    "OPENAI_API_TIMEOUT": "60",
    "AGNO_TRUNCATE_CONTEXT": "head",
})

import pdfplumber
import yfinance as yf
import numpy as np
import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.faiss import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team.team import Team
from agno.tools import tool
from agno.tools.reasoning import ReasoningTools

# topo do arquivo (perto dos imports)
from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"

def read_prompt(filename: str) -> str:
    path = PROMPTS_DIR / filename
    return path.read_text(encoding="utf-8")


class FinancialAgent:
    """
    Classe principal do Agente Financeiro COM CONTEXTO.
    Encapsula toda a lógica de análise fundamentalista considerando histórico.
    """
    
    def __init__(self):
        """Inicializa o agente financeiro com todas as ferramentas e equipe."""
        self._setup_tools()
        self._setup_agents()
        self._setup_team()
    
    def _setup_tools(self):
        """Configura todas as ferramentas (tools) do agente."""
        self.normalize_ticker = normalize_ticker
        self.consultar_pdf_fundamentalista = consultar_pdf_fundamentalista
        self.calcular_valuation = calcular_valuation
        self.calcular_multiplos = calcular_multiplos
    
    def _setup_agents(self):
        """Configura os agentes especializados."""
        self.ag_rag = Agent(
            name="RAG Fundamentalista",
            role="Consulta PDF",
            model=OpenAIChat(id="gpt-4o"),
            tools=[consultar_pdf_fundamentalista],
        )

        self.ag_val = Agent(
            name="Valuation",
            role="6 métodos de valuation",
            model=OpenAIChat(id="gpt-4o", temperature=0.3),
            tools=[calcular_valuation],
            instructions=[read_prompt("valuation_prompt.txt")],
        )

        self.ag_mult = Agent(
            name="Múltiplos",
            role="Calcula múltiplos",
            model=OpenAIChat(id="gpt-4o"),
            tools=[calcular_multiplos],
            instructions=[read_prompt("multiplos_prompt.txt")],
        )

        self.ag_api_json = Agent(
            name="API JSON Financeira",
            role="Retornar somente dados em JSON",
            model=OpenAIChat(id="gpt-4o-mini"),
            tools=[calcular_valuation, calcular_multiplos, obter_json_financeiro],
            instructions=[
              "Quando o usuário pedir JSON para um ticker, chame `obter_json_financeiro` com o ticker.",
               "Responda SOMENTE com JSON válido; sem comentários, sem markdown."],
        )
    
    def _setup_team(self):
        """Configura a equipe coordenada de agentes."""
        self.equipe = Team(
            name="Equipe Financeira Completa",
            mode="coordinate",
            model=OpenAIChat(id="gpt-4o"),
            members=[self.ag_rag, self.ag_val, self.ag_mult, self.ag_api_json],
            tools=[ReasoningTools(add_instructions=True)],
            enable_agentic_context=False,
            instructions=[
                "Crie relatório final em seções: Introdução, Fundamentação, Valuation, Múltiplos, Conclusão.",
                "Use tabelas markdown sempre que houver números.",
            ],
            markdown=True,
            show_members_responses=False,
        )
    
    def _build_context_prompt(self, messages: list, current_question: str) -> str:
        """
        Constrói um prompt com contexto baseado no histórico de mensagens.
        
        Args:
            messages (list): Lista de mensagens anteriores
            current_question (str): Pergunta atual
            
        Returns:
            str: Prompt com contexto
        """
        if not messages:
            return current_question
        
        # Construir contexto das últimas 10 mensagens (para não exceder limite de tokens)
        recent_messages = messages[-10:] 
        
        context_parts = []
        for msg in recent_messages:
            role = "Usuário" if msg.sender == "user" else "Assistente"
            context_parts.append(f"{role}: {msg.content}")
        
        # Adicionar pergunta atual
        context_parts.append(f"Usuário: {current_question}")
        
        # Construir prompt final
        context = "\n".join(context_parts)
        
        prompt = f"""
        Histórico da conversa:
        {context}
        
        Instruções:
        1. Considere o contexto da conversa anterior
        2. Se a pergunta atual se refere a algo mencionado antes, use esse contexto
        3. Se for uma pergunta de follow-up, responda de forma contextual
        4. Mantenha a continuidade da conversa
        5. Se for uma nova pergunta, responda normalmente
        
        Responda à pergunta atual considerando o contexto:
        """
        
        return prompt
    
    def chat(self, question: str, conversation_history: list = None) -> str:
        """
        Processa uma pergunta com contexto do histórico.
        
        Args:
            question (str): Pergunta do usuário
            conversation_history (list): Histórico de mensagens da conversa
            
        Returns:
            str: Resposta do agente
        """
        try:
            # Construir prompt com contexto
            if conversation_history:
                prompt = self._build_context_prompt(conversation_history, question)
            else:
                prompt = question
            
            response = self.equipe.run(prompt)
            return self._extract_response_content(response)
        except Exception as e:
            raise Exception(f"Erro no chat: {str(e)}")
    
    def analyze_stock(self, question: str, ticker: str, conversation_history: list = None) -> str:
        """
        Analisa uma ação específica com contexto.
        
        Args:
            question (str): Pergunta do usuário
            ticker (str): Ticker da ação
            conversation_history (list): Histórico de mensagens da conversa
            
        Returns:
            str: Análise completa da ação
        """
        try:
            # Construir prompt base
            base_prompt = f"""
            Analise a ação {ticker}:
            
            Pergunta do usuário: {question}
            
            Por favor:
            1. Resuma o conceito de margem de segurança do PDF.
            2. Faça valuation (6 métodos, inclua CAPM).
            3. Calcule os principais múltiplos.
            4. Conclua recomendando comprar, manter ou vender.
            """
            
            # Adicionar contexto se houver histórico
            if conversation_history:
                context_prompt = self._build_context_prompt(conversation_history, base_prompt)
                final_prompt = f"{context_prompt}\n\nAnálise específica: {base_prompt}"
            else:
                final_prompt = base_prompt
            
            response = self.equipe.run(final_prompt)
            return self._extract_response_content(response)
        except Exception as e:
            raise Exception(f"Erro na análise: {str(e)}")
    
    def _extract_response_content(self, response) -> str:
        """
        Extrai o conteúdo da resposta como string.
        
        Args:
            response: Resposta do agente
            
        Returns:
            str: Conteúdo da resposta
        """
        if hasattr(response, 'content'):
            return response.content
        else:
            return str(response)


# Helpers
def normalize_ticker(tk: str) -> str:
    """Normaliza o ticker para formato brasileiro."""
    return f"{tk}.SA" if "." not in tk and tk[-1].isdigit() else tk


# Ferramentas (Tools) - Mesmas do arquivo original
@tool(
    name="consultar_pdf_fundamentalista",
    description="Responde perguntas usando o PDF de análise fundamentalista e cita página.",
)
def consultar_pdf_fundamentalista(question: str) -> str:
    """Consulta o PDF de análise fundamentalista."""
    pdf_path = Path("indicadores_fundamentalistas (1).pdf")
    with pdfplumber.open(pdf_path) as pdf:
        texto = "\n".join(page.extract_text() or "" for page in pdf.pages)

    chunks = RecursiveCharacterTextSplitter(
        chunk_size=600, chunk_overlap=150
    ).split_text(texto)
    vect = FAISS.from_texts(chunks, OpenAIEmbeddings())
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0.5)

    ctx = "\n\n".join(d.page_content for d in vect.similarity_search(question, k=2))[:6000]
    prompt = (
        "Você é um assistente de investimentos especializado em análise fundamentalista, e toda a sua atuação deve se basear exclusivamente no conteúdo do guia abaixo. Todas as respostas devem ser dadas apenas em português brasileiro, com linguagem clara, natural, direta, sem jargão excessivo e sempre profissional, focando na explicação acessível e rigorosa dos conceitos.\n\n"
        "Regras de atuação:\n"
        "- Utilize apenas o conteúdo do guia de referência. Não crie, suponha ou extrapole informações não presentes no texto.\n"
        "- Sempre responda no formato de educador: explique conceitos, indicadores, fórmulas, significados, usos práticos, limitações e boas práticas conforme apresentados no guia.\n"
        "- Quando perguntado sobre qualquer indicador (ex: EBITDA, ROE, ROIC, P/L, Dividend Yield, Margem Líquida, Ativo Total, Dívida Líquida, EV/EBITDA, etc.), explique com base nas definições, cálculos, relevância, limitações e contexto de uso exatamente como apresentado no material.\n"
        "- Sempre que possível, destaque que decisões de análise e investimento exigem avaliação conjunta de múltiplos indicadores e aspectos qualitativos, como gestão, setor, contexto econômico e vantagens competitivas, de acordo com o guia.\n"
        "- Ao explicar indicadores, use as fórmulas e exemplos práticos contidos no texto. Nunca utilize exemplos inventados ou informações externas.\n"
        "- Caso seja questionado sobre a diferença entre indicadores (ex: ROE x ROIC), traga os pontos de distinção conforme apresentados no documento, inclusive quando abordar análise DuPont ou outras decomposições mencionadas.\n"
        "- Sempre destaque as limitações dos indicadores e os riscos de análise isolada, reforçando que cada métrica deve ser considerada no contexto da empresa e do setor, conforme os princípios do guia.\n"
        "- Se for perguntado sobre recomendação de compra, venda ou decisão de investimento, nunca responda diretamente e oriente, de acordo com o material, que a função do assistente é esclarecer e ensinar os fundamentos, não recomendar operações no mercado financeiro.\n"
        "- Utilize exemplos e referências aos grandes investidores (Benjamin Graham, Warren Buffett, Peter Lynch, etc.) apenas se estiverem descritos no guia, nunca extrapolando além do que está no texto.\n"
        "- Caso a resposta não esteja clara ou detalhada no guia de referência, diga explicitamente que não sabe responder com base nesse material.\n"
        "- Nunca utilize dados de mercado atual, não busque informações externas, não faça previsões e não utilize análises técnicas. Limite-se sempre ao escopo do guia abaixo.\n"
        "- Adote sempre um tom educacional, gentil, sem ser professoral, e evite respostas excessivamente longas ou repetitivas, a não ser que o usuário peça detalhamento.\n"
        "- Se a pergunta envolver a escolha de ações, estratégias de investimento, análise de empresas, ou questões sobre valuation, destaque a importância de análise integrada (quantitativa e qualitativa) conforme orientado pelo guia, e oriente o usuário a considerar múltiplos indicadores e contexto, nunca um único fator isolado.\n"
        "- Se questionado sobre política de dividendos, crescimento, endividamento, múltiplos de mercado ou temas similares, explique com base no conteúdo do guia, incluindo a relevância de cada indicador e o que está por trás das melhores práticas segundo o material.\n"
        "- Se a pergunta for genérica (ex: 'como analisar uma empresa?'), responda com as orientações amplas e os passos sugeridos no guia, reforçando sempre a análise multifatorial e integrada.\n"
        "- Se o usuário tentar levar a resposta para temas não abordados no guia, seja transparente e informe que a resposta está limitada ao escopo do documento.\n"
        "- Mantenha sempre o compromisso de não sair do conteúdo do guia, mesmo que solicitado.\n\n"
        "Guia de referência:\n{ctx}\n\nPergunta: {question}\nResposta:"
    )
    response = llm.invoke(prompt)
    return response.content

def _get_selic_anualizada() -> float | None:
    """SELIC anual %, via BCB (série 11). Retorna None em erro."""
    try:
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados/ultimos/1?formato=json"
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()
        if not data:
            return None
        taxa_diaria = float(data[0]["valor"]) / 100.0
        taxa_anual = (1 + taxa_diaria) ** 252 - 1
        return round(taxa_anual * 100, 2)  # em %
    except Exception:
        return None

def _get_ibov_retorno_12m() -> float | None:
    """Retorno % 12m do Ibovespa (^BVSP). Retorna None em erro."""
    try:
        hoje = datetime.now()
        ini = hoje - timedelta(days=365)
        ibov = yf.Ticker("^BVSP")
        hist = ibov.history(start=ini.strftime("%Y-%m-%d"), end=hoje.strftime("%Y-%m-%d"))
        if hist.empty:
            return None
        p0 = float(hist["Close"].iloc[0])
        p1 = float(hist["Close"].iloc[-1])
        ret = (p1 / p0 - 1) * 100.0
        return round(ret, 4)
    except Exception:
        return None

def _get_beta(tk: str) -> float:
    """Beta do yfinance com fallback 1.0."""
    try:
        return float(yf.Ticker(tk).info.get("beta") or 1.0)
    except Exception:
        return 1.0

def _ke_capm(tk: str) -> float:
    """
    Ke em DECIMAL (ex: 0.12 = 12%).
    rf: SELIC anual (%) -> decimal
    rm: Ibov 12m (%) -> decimal
    erp = rm - rf
    Fallback: rf=4%, erp=6% se dados ausentes.
    """
    rf_pct = _get_selic_anualizada()
    rm_pct = _get_ibov_retorno_12m()
    beta = _get_beta(tk)

    if rf_pct is not None and rm_pct is not None:
        rf = rf_pct / 100.0
        rm = rm_pct / 100.0
        erp = max(rm - rf, 0.0)  # evita erp negativo em período ruim
    else:
        rf, erp = 0.04, 0.06

    return rf + beta * erp

# --- Novo helper: dividendo TTM robusto
def _get_dividend_ttm(tk: str) -> float:
    """
    Retorna o dividendo TTM (12m). Tenta na ordem:
    1) info['dividendRate']
    2) dividendYield * regularMarketPrice
    3) soma dos dividendos (historical .dividends) dos últimos 12m (ou últimos 4 lançamentos)
    """
    try:
        t = yf.Ticker(tk)
        info = t.info

        div = info.get("dividendRate")
        if div:
            try:
                v = float(div)
                if v > 0:
                    return v
            except Exception:
                pass

        dy = info.get("dividendYield")
        px = info.get("regularMarketPrice")
        if dy is not None and px is not None:
            try:
                v = float(dy) * float(px)
                if v > 0:
                    return v
            except Exception:
                pass

        dser = t.dividends
        if dser is not None and len(dser) > 0:
            cutoff = pd.Timestamp.today() - pd.DateOffset(years=1)
            last_12m = dser[dser.index >= cutoff]
            if last_12m.empty:
                last_12m = dser.tail(4)
            v = float(last_12m.sum())
            if v > 0:
                return v
    except Exception:
        pass
    return 0.0

@tool(
    name="calcular_valuation",
    description="Calcula DCF, Gordon, EV/EBIT, P/L, PEG e CAPM; devolve tabela markdown.",
)
def calcular_valuation(ticker: str) -> str:
    """Calcula valuation usando 6 métodos diferentes."""
    tk = normalize_ticker(ticker)
    info = yf.Ticker(tk).info
    shares = info.get("sharesOutstanding") or 1

    g = info.get("earningsQuarterlyGrowth", 0.05) or 0.05
    dr = 0.10

    # 1) DCF
    fcf = info.get("freeCashflow") or 0
    if fcf:
        proj = sum(fcf * (1 + g) ** i / (1 + dr) ** i for i in range(1, 6))
        term = (fcf * (1 + g) ** 5) * (1 + g) / (dr - g)
        dcf_price = (proj + term / (1 + dr) ** 5) / shares
    else:
        dcf_price = None

    # 2) Gordon
    div = info.get("dividendRate") or 0
    g_d = g * 0.6
    gordon = div * (1 + g_d) / (dr - g_d) if div else None

    # 3) EV/EBIT comparável
    peers = ["VALE3.SA", "ITUB4.SA", "BBDC4.SA"]
    ev_ebit = [
        yf.Ticker(p).info["enterpriseValue"] / yf.Ticker(p).info["ebit"]
        for p in peers
        if yf.Ticker(p).info.get("enterpriseValue") and yf.Ticker(p).info.get("ebit")
    ]
    ev_mult = np.mean(ev_ebit) if ev_ebit else None
    ebit = info.get("ebit")
    ev_based = (
        (ev_mult * ebit - info.get("totalDebt", 0) + info.get("cash", 0)) / shares
        if ev_mult and ebit
        else None
    )

    # 4) P/L comparável
    pl_mults = [
        yf.Ticker(p).info.get("trailingPE") for p in peers if yf.Ticker(p).info.get("trailingPE")
    ]
    pl_mult = np.mean(pl_mults) if pl_mults else None
    eps = info.get("trailingEps")
    pl_price = pl_mult * eps if pl_mult and eps else None

    # 5) PEG
    peg = info.get("pegRatio")
    peg_price = peg * eps if peg and eps else None

    # 6) CAPM (Ke dinâmico + dividendo TTM robusto)
    ke = _ke_capm(tk)  # decimal (ex: 0.12)
    # g para CAPM: limitar e garantir < ke
    g_raw = info.get("earningsQuarterlyGrowth", 0.05) or 0.05
    g_d_capm = max(0.0, min(float(g_raw) * 0.6, 0.06))
    if ke and ke > 0.02:
        g_d_capm = min(g_d_capm, ke - 0.01)
    div_ttm = _get_dividend_ttm(tk)
    capm_price = (
        div_ttm * (1 + g_d_capm) / (ke - g_d_capm)
        if (div_ttm > 0 and ke and ke > g_d_capm)
        else None
    )

    df = pd.DataFrame(
        {
            "Método": [
                "DCF (5 anos)",
                "Gordon Dividend",
                "EV/EBIT Comparável",
                "P/L Comparável",
                "PEG",
                "CAPM (Dividendo)",
            ],
            "Comentário": [
                "Projeta FCF + terminal",
                "Dividendos perpétuos",
                "Múltiplo médio pares",
                "Aplica P/L médio",
                "P/L ajustado a g",
                "Preço via CAPM",
            ],
            "Preço Justo": [
                round(dcf_price, 2) if dcf_price else "N/A",
                round(gordon, 2) if gordon else "N/A",
                round(ev_based, 2) if ev_based else "N/A",
                round(pl_price, 2) if pl_price else "N/A",
                round(peg_price, 2) if peg_price else "N/A",
                round(capm_price, 2) if capm_price else "N/A",
            ],
        }
    )
    media = df[df["Preço Justo"] != "N/A"]["Preço Justo"].astype(float).mean()
    df.loc[len(df)] = ["Média", "Média simples", round(media, 2) if not np.isnan(media) else "N/A"]
    return df.to_markdown(index=False)


@tool(
    name="calcular_multiplos",
    description="Retorna tabela markdown com P/L, P/VP, EV/EBITDA, EV/Receita.",
)
def calcular_multiplos(ticker: str) -> str:
    """Calcula múltiplos financeiros da ação."""
    info = yf.Ticker(normalize_ticker(ticker)).info
    pe = info.get("trailingPE")
    pb = info.get("priceToBook")
    ev = info.get("enterpriseValue")
    ebitda = info.get("ebitda")
    revenue = info.get("totalRevenue")
    ev_ebitda = ev / ebitda if ev and ebitda else None
    ev_sales = ev / revenue if ev and revenue else None

    df = pd.DataFrame(
        {
            "Múltiplo": ["P/L", "P/VP", "EV/EBITDA", "EV/Receita"],
            "Valor": [
                round(pe, 2) if pe else "N/A",
                round(pb, 2) if pb else "N/A",
                round(ev_ebitda, 2) if ev_ebitda else "N/A",
                round(ev_sales, 2) if ev_sales else "N/A",
            ],
        }
    )
    return df.to_markdown(index=False)

#  Helpers p/ parse de tabelas markdown em JSON 
def _to_float(x):
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    x = str(x).strip().replace("%", "")
    if x in ("N/A", "NA", "-", ""):
        return None
    try:
        return float(x.replace(",", "."))  
    except Exception:
        return None

def _slug_metodo(nome: str) -> str:
    nome = (nome or "").strip().lower()
    if nome.startswith("dcf"):
        return "dcf_5y"
    if nome.startswith("gordon"):
        return "gordon"
    if "ev/ebit" in nome:
        return "ev_ebit_comparavel"
    if nome.startswith("p/") or "p/l" in nome:
        return "pl_comparavel"
    if nome == "peg":
        return "peg"
    if "capm" in nome:
        return "capm_dividendo"
    if "média" in nome:
        return "media"
    return nome.replace(" ", "_")

def _parse_valuation_markdown(md: str):
    """
    Espera 3 colunas: Método | Comentário | Preço Justo
    e uma linha extra 'Média' no fim.
    """
    metodos = {}
    media_precos = None
    for raw in md.splitlines():
        line = raw.strip()
        if not line or set(line) <= set("|-: ") or line.lower().startswith("| método"):
            continue
        # quebra por '|'
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) < 3:
            continue
        metodo, comentario, preco = parts[0], parts[1], parts[2]
        key = _slug_metodo(metodo)
        if "média" in metodo.lower():
            media_precos = _to_float(preco)
        else:
            metodos[key] = {
                "preco_justo": _to_float(preco),
                "comentario": comentario,
            }
    return {"metodos": metodos, "media_precos": media_precos}

def _parse_multiplos_markdown(md: str):
    """
    Espera 2 colunas: Múltiplo | Valor
    """
    out = {}
    for raw in md.splitlines():
        line = raw.strip()
        if not line or set(line) <= set("|-: ") or line.lower().startswith("| múltiplo"):
            continue
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) < 2:
            continue
        nome, valor = parts[0], parts[1]
        key = (
            "pl" if "p/l" in nome.lower() else
            "pvp" if "p/vp" in nome.lower() else
            "ev_ebitda" if "ev/ebitda" in nome.lower() else
            "ev_receita" if "ev/receita" in nome.lower() else
            nome.lower().replace(" ", "_")
        )
        out[key] = _to_float(valor)
    return out

@tool(
    name="capm_calcular",
    description="Calcula Ke via CAPM (SELIC + Ibov 12m) e preço pelo modelo de Gordon com dividendo TTM; retorna JSON."
)
def capm_calcular(ticker: str) -> str:
    try:
        tk = normalize_ticker(ticker)
        info = yf.Ticker(tk).info
        ke = _ke_capm(tk)  # decimal
        g_raw = info.get("earningsQuarterlyGrowth", 0.05) or 0.05
        g_d = max(0.0, min(float(g_raw) * 0.6, 0.06))
        if ke and ke > 0.02:
            g_d = min(g_d, ke - 0.01)
        div_ttm = _get_dividend_ttm(tk)
        price = (
            div_ttm * (1 + g_d) / (ke - g_d)
            if (div_ttm > 0 and ke and ke > g_d)
            else None
        )
        return json.dumps(
            {
                "ticker": ticker.upper(),
                "ke_pct": round(ke * 100, 2) if ke else None,
                "dividend_ttm": round(div_ttm, 4) if div_ttm is not None else None,
                "g_dividendo": round(g_d, 4),
                "capm_price": round(price, 2) if price else None,
            },
            ensure_ascii=False,
        )
    except Exception as e:
        return json.dumps({"ticker": ticker.upper(), "error": str(e)}, ensure_ascii=False)

# Tool que consolida Valuation + Múltiplos em JSON puro 
@tool(
    name="obter_json_financeiro",
    description=(
        "Retorna SOMENTE JSON com os resultados do valuation (6 métodos + média) "
        "e dos múltiplos para um ticker."
    ),
)
def obter_json_financeiro(ticker: str) -> str:
    """
    Chama as tools já existentes (calcular_valuation, calcular_multiplos),
    parseia as tabelas markdown e devolve um JSON (string) consolidado.
    """
    try:
        tk = normalize_ticker(ticker)
        # Usa as tools existentes (retornam markdown)
        md_val = calcular_valuation.entrypoint(ticker=tk)
        md_mult = calcular_multiplos.entrypoint(ticker=tk)

        valuation = _parse_valuation_markdown(md_val)
        multiplos = _parse_multiplos_markdown(md_mult)

        payload = {
            "ticker": ticker.upper(),
            "valuation": valuation,
            "multiplos": multiplos,
        }
        return json.dumps(payload, ensure_ascii=False)
    except Exception as e:
        # Sempre retorne JSON válido 
        return json.dumps({"ticker": ticker.upper(), "error": str(e)}, ensure_ascii=False)


agent = FinancialAgent() 

# CASO QUEIRAM TESTAR, descomentem o bloco abaixo

# ---- CLI multi-modo: python -m app.agent.financial_agent PETR4 [--tables|--capm]
# if __name__ == "__main__":
#     import sys, json
#     # uso: python -m app.agent.financial_agent PETR4 [--tables|--capm]
#     args = [a for a in sys.argv[1:] if not a.startswith("--")]
#     flags = {a for a in sys.argv[1:] if a.startswith("--")}
#     tk = args[0] if args else "PETR4"

#     if "--tables" in flags:
#         print(calcular_multiplos.entrypoint(ticker=tk))
#         print(calcular_valuation.entrypoint(ticker=tk))
#         raw = obter_json_financeiro.entrypoint(ticker=tk)
#         print(json.dumps(json.loads(raw), ensure_ascii=False, indent=2))
#     elif "--capm" in flags:
#         print(capm_calcular.entrypoint(ticker=tk))
#     else:
#         print(obter_json_financeiro.entrypoint(ticker=tk))