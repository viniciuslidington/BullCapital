"""
Módulo do Agente Financeiro COM CONTEXTO - Análise Fundamentalista com Agno Framework.
Versão que considera histórico de mensagens para respostas mais contextuais.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

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
            model=OpenAIChat(id="gpt-3.5-turbo"),
            tools=[consultar_pdf_fundamentalista],
        )

        self.ag_val = Agent(
            name="Valuation",
            role="6 métodos de valuation",
            model=OpenAIChat(id="gpt-3.5-turbo"),
            tools=[calcular_valuation],
        )

        self.ag_mult = Agent(
            name="Múltiplos",
            role="Calcula múltiplos",
            model=OpenAIChat(id="gpt-3.5-turbo"),
            tools=[calcular_multiplos],
        )
    
    def _setup_team(self):
        """Configura a equipe coordenada de agentes."""
        self.equipe = Team(
            name="Equipe Financeira Completa",
            mode="coordinate",
            model=OpenAIChat(id="gpt-4o"),
            members=[self.ag_rag, self.ag_val, self.ag_mult],
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
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

    ctx = "\n\n".join(d.page_content for d in vect.similarity_search(question, k=2))[:6000]
    prompt = (
        "Você é um analista fundamentalista. Use o contexto e cite página quando possível.\n\n"
        f"{ctx}\n\nPergunta: {question}\nResposta:"
    )
    response = llm.invoke(prompt)
    return response.content


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

    # 6) CAPM
    rf = 0.04
    erp = 0.06
    beta = info.get("beta") or 1
    ke = rf + beta * erp
    capm_price = div * (1 + g_d) / (ke - g_d) if div and ke > g_d else None

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


# Instância global do agente com contexto
agent = FinancialAgent() 