# app.py

import os
import streamlit as st
import boto3
from dotenv import load_dotenv
from typing_extensions import TypedDict, List

from langchain_aws import ChatBedrockConverse, BedrockEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import START, StateGraph

#  configuracao inicial
load_dotenv()


bedrock_client = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_DEFAULT_REGION"))

llm = ChatBedrockConverse(
    client=bedrock_client,
    model='mistral.mistral-7b-instruct-v0:2'  
)

embeddings = BedrockEmbeddings(
    client=bedrock_client,
    model_id="amazon.titan-embed-text-v2:0"
)

# carregamento e vetorizacao dos documentos
vector_store = InMemoryVectorStore(embeddings)

loader = PyPDFLoader("indi_fundamentalistas.pdf")  
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = splitter.split_documents(docs)

vector_store.add_documents(splits)

# pipeline básico
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

def retrieve(state: State):
    docs = vector_store.similarity_search(state["question"])
    return {"context": docs}

prompt = ChatPromptTemplate.from_template(
    "Você é um assistente de investimentos especializado em análise fundamentalista, e toda a sua atuação deve se basear exclusivamente no conteúdo do guia abaixo. Todas as respostas devem ser dadas apenas em português brasileiro, com linguagem clara, natural, direta, sem jargão excessivo e sempre profissional, focando na explicação acessível e rigorosa dos conceitos.\n\n"
    "Regras de atuação:\n"
    "- Utilize apenas o conteúdo do guia de referência. Não crie, suponha ou extrapole informações não presentes no texto.\n"
    "- Sempre responda no formato de educador: explique conceitos, indicadores, fórmulas, significados, usos práticos, limitações e boas práticas conforme apresentados no guia.\n"
    "- Quando perguntado sobre qualquer indicador (ex: EBITDA, ROE, ROIC, P/L, Dividend Yield, Margem Líquida, Ativo Total, Dívida Líquida, EV/EBITDA, etc.), explique com base nas definições, cálculos, relevância, limitações e contexto de uso exatamente como apresentado no material.\n"
    "- Sempre que possível, destaque que decisões de análise e investimento exigem avaliação conjunta de múltiplos indicadores e aspectos qualitativos, como gestão, setor, contexto econômico e vantagens competitivas, de acordo com o guia.\n"
    "- Ao explicar indicadores, use as fórmulas e exemplos práticos contidos no texto. Nunca utilize exemplos inventados ou informações externas.\n"
    "- Caso seja questionado sobre a diferença entre indicadores (por exemplo, ROE x ROIC), traga os pontos de distinção conforme apresentados no documento, inclusive quando abordar análise DuPont ou outras decomposições mencionadas.\n"
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
    "Guia de referência:\n{context}\n\nPergunta: {question}"
)

def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({
        "question": state["question"],
        "context": docs_content
    })
    response = llm.invoke(messages)
    return {"answer": response.content}

graph_builder = StateGraph(State)
graph_builder.add_node("retrieve", retrieve)
graph_builder.add_node("generate", generate)
graph_builder.add_edge(START, "retrieve")
graph_builder.add_edge("retrieve", "generate")
graph = graph_builder.compile()

def responder_pergunta(pergunta: str) -> str:
    result = graph.invoke({"question": pergunta})
    return result["answer"]

# streamlit 
st.set_page_config(page_title="Bull Capital", layout="centered")

st.title("RAG - Pergunte sobre Fundamentos de Mercado")
st.caption("Base teórica baseda na literatura'")

pergunta = st.text_input("Digite sua pergunta:")
if st.button("Enviar") and pergunta:
    with st.spinner("Buscando resposta..."):
        try:
            resposta = responder_pergunta(pergunta)
            st.markdown("## 📣 Resposta:")
            st.success(resposta)
        except Exception as e:
            st.error(f"Erro ao gerar resposta: {e}")