from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv  
from langchain_core.messages import (
    BaseMessage,    # The foundational class for all message types in LangGraph
    ToolMessage,    # Passes data back to LLM after it calls a tool such as the content and the tool_call_id
    SystemMessage, 
    HumanMessage
)
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import openai 
import yfinance as yf 
import requests
from datetime import datetime, timedelta

load_dotenv()


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


empresa_para_ticker = {
    "petrobras": "PETR4.SA",
    "vale": "VALE3.SA",
    "magalu": "MGLU3.SA",
    "magazine luiza": "MGLU3.SA",
    "itaú": "ITUB4.SA",
    "banco do brasil": "BBAS3.SA",
    "ambev": "ABEV3.SA"
}

# Gera a lista de nomes conhecidos para o prompt
nomes_validos = list(empresa_para_ticker.keys())

llm = ChatOpenAI(model="gpt-4o", temperature=0)


def get_ticker(nome_empresa: str) -> str:
    """Função que recebe nome de uma empresa e retorna o seu ticker"""

    prompt = f"""
    Você é um assistente que ajuda a identificar o nome correto de uma empresa com base em variações ou erros de digitação.

    Abaixo está a lista de nomes válidos de empresas:
    {', '.join(nomes_validos)}

    O usuário escreveu: "{nome_empresa}"

    Com base nisso, retorne APENAS o nome correto correspondente da lista acima, exatamente como está na lista.

    Se não houver correspondência razoável, retorne apenas: "DESCONHECIDO"
    """

    messages = [
        SystemMessage(content="Você é um assistente que normaliza nomes de empresas brasileiras para análise de ações."),
        HumanMessage(content=prompt)
    ]

    response = model.invoke(messages)
    nome_normalizado = response.content.strip().lower()

    return empresa_para_ticker.get(nome_normalizado, "DESCONHECIDO")


def get_beta(ticker: str) -> float | None:
    """
    Retorna o beta da ação dada pelo ticker usando yfinance.
    
    Args:
        ticker (str): ticker da ação, ex: "PETR4.SA"
    
    Returns:
        float | None: beta da ação, ou None se não encontrado
    """
    try:
        acao = yf.Ticker(ticker)
        beta = acao.info.get("beta", None)
        return beta
    except Exception as e:
        print(f"Erro ao buscar beta para {ticker}: {e}")
        return None
    


@tool
def get_selic_taxa_atual() -> float | None:
    """
    Busca a taxa SELIC diária atual pela API do Banco Central do Brasil,
    converte para taxa anual em percentual e retorna.
    
    Retorna:
        float: taxa SELIC anual em percentual (ex: 15.0)
        None: em caso de erro ou indisponibilidade
    """
    try:
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados/ultimos/1?formato=json"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data and len(data) > 0:
            taxa_diaria = float(data[0]["valor"]) / 100  # converte para decimal
            taxa_anual = (1 + taxa_diaria) ** 252 - 1
            return round(taxa_anual * 100, 2)  # converte para percentual e arredonda
    except Exception as e:
        print(f"Erro ao buscar SELIC: {e}")
    return None

@tool
def get_ibovespa_return() -> float:
    """
    Retorna o retorno percentual anual (últimos 12 meses) do índice Ibovespa (ticker ^BVSP).
    """
    try:
        hoje = datetime.now()
        um_ano_atras = hoje - timedelta(days=365)

        ibov = yf.Ticker("^BVSP")
        hist = ibov.history(start=um_ano_atras.strftime('%Y-%m-%d'), end=hoje.strftime('%Y-%m-%d'))

        preco_inicio = hist["Close"].iloc[0]
        preco_fim = hist["Close"].iloc[-1]

        retorno_percentual = ((preco_fim - preco_inicio) / preco_inicio) * 100
        return round(retorno_percentual, 4)
    except Exception as e:
        return f"Erro ao calcular retorno anual do Ibovespa: {str(e)}"


@tool
def calcular_ret_capm(ticker: str) -> float | str:
    """
    Calcula o retorno esperado de uma ação com base no modelo CAPM.
    
    Parâmetros:
        ticker (str): ticker da ação (ex: PETR4.SA)
    
    Retorno:
        float: retorno esperado anual da ação (%) com 4 casas decimais
        str: mensagem de erro caso falte algum dado
    """
    try:
        # Pegar beta
        beta = get_beta(ticker)
        if beta is None:
            return f"Não foi possível obter o beta para o ticker {ticker}."

        # Pegar taxa livre de risco (SELIC anual)
        rf = get_selic_taxa_atual()
        if rf is None:
            return "Erro ao buscar a taxa SELIC."

        # Pegar retorno do mercado (Ibovespa anual)
        rm = get_ibovespa_return()
        if isinstance(rm, str):
            return f"Erro ao obter retorno do mercado: {rm}"

        # Calcular retorno esperado pelo CAPM
        retorno_esperado = rf + beta * (rm - rf)
        return round(retorno_esperado, 4)

    except Exception as e:
        return f"Erro ao calcular CAPM: {str(e)}"



def model_call(state: AgentState) -> AgentState:
    print(f'Chamando our_agent. Estado atual: {state["messages"]}')
    system_prompt = SystemMessage(
        content="You are my AI assistant, please answer my query to the best of your ability."
    )
    response = model.invoke([system_prompt] + state["messages"])
    return {"messages": [response]}


def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    if not getattr(last_message, "tool_calls", None):
        return "end"
    else:
        return "continue"
    

tools = [get_ticker, get_beta, get_selic_taxa_atual, get_ibovespa_return, calcular_ret_capm]

model = ChatOpenAI(model="gpt-4o", temperature=1).bind_tools(tools)


graph = StateGraph(AgentState)
graph.add_node("our_agent", model_call)

tool_node = ToolNode(tools=tools)
graph.add_node("tools", tool_node)

graph.set_entry_point("our_agent")

graph.add_conditional_edges(
    "our_agent",
    should_continue,
    {
        "continue": "tools",
        "end": END,
    },
)

graph.add_edge("tools", "our_agent")

app = graph.compile()


def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()


inputs = {"messages": [("user", "Qual é o retorno anual esperado da petrobras?")]}
print_stream(app.stream(inputs, stream_mode="values"))
