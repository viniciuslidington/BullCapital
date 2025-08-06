import os
from pathlib import Path
from dotenv import load_dotenv 


load_dotenv()
# Ajustes de robustez
os.environ.update(
    {
        "OPENAI_MAX_RETRIES": "10",       
        "OPENAI_API_TIMEOUT": "60",      
        "AGNO_TRUNCATE_CONTEXT": "head",  
    }
)


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

load_dotenv()
# Ajustes de robustez
os.environ.update(
    {
        "OPENAI_MAX_RETRIES": "10",       
        "OPENAI_API_TIMEOUT": "60",      
        "AGNO_TRUNCATE_CONTEXT": "head",  
    }
)

# helpers
def normalize_ticker(tk: str) -> str:
    return f"{tk}.SA" if "." not in tk and tk[-1].isdigit() else tk


# RAG sobre o PDF
@tool(
    name="consultar_pdf_fundamentalista",
    description="Responde perguntas usando o PDF de análise fundamentalista e cita página.",
)
def consultar_pdf_fundamentalista(question: str) -> str:
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
    return llm.predict(prompt)


# Valuation (6 métodos)
@tool(
    name="calcular_valuation",
    description="Calcula DCF, Gordon, EV/EBIT, P/L, PEG e CAPM; devolve tabela markdown.",
)
def calcular_valuation(ticker: str) -> str:
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


# Múltiplos
@tool(
    name="calcular_multiplos",
    description="Retorna tabela markdown com P/L, P/VP, EV/EBITDA, EV/Receita.",
)
def calcular_multiplos(ticker: str) -> str:
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


# Agentes
ag_rag = Agent(
    name="RAG Fundamentalista",
    role="Consulta PDF",
    model=OpenAIChat(id="gpt-3.5-turbo"),
    tools=[consultar_pdf_fundamentalista],
)

ag_val = Agent(
    name="Valuation",
    role="6 métodos de valuation",
    model=OpenAIChat(id="gpt-3.5-turbo"),
    tools=[calcular_valuation],
)

ag_mult = Agent(
    name="Múltiplos",
    role="Calcula múltiplos",
    model=OpenAIChat(id="gpt-3.5-turbo"),
    tools=[calcular_multiplos],
)



# Equipe

equipe = Team(
    name="Equipe Financeira Completa",
    mode="coordinate",
    model=OpenAIChat(id="gpt-4o"),             
    members=[ag_rag, ag_val, ag_mult],
    tools=[ReasoningTools(add_instructions=True)],
    enable_agentic_context=False,              
    instructions=[
        "Crie relatório final em seções: Introdução, Fundamentação, Valuation, Múltiplos, Conclusão.",
        "Use tabelas markdown sempre que houver números.",
    ],
    markdown=True,
    show_members_responses=False,
)

# Execução CLI
if __name__ == "__main__":
    prompt = (
        "Analise a ação PETR4:\n"
        "1. Resuma o conceito de margem de segurança do PDF.\n"
        "2. Faça valuation (6 métodos, inclua CAPM).\n"
        "3. Calcule os principais múltiplos.\n"
        "4. Conclua recomendando comprar, manter ou vender."
    )
    equipe.print_response(prompt)