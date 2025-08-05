"""
API HTTP Server para o Agente Financeiro.
Servidor FastAPI que expõe o agente como endpoints REST.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from ia.Agent.financial_agent import agent


# Modelos Pydantic para a API
class QuestionRequest(BaseModel):
    question: str
    ticker: Optional[str] = None

class AgentResponse(BaseModel):
    response: str
    status: str = "success"


# Criar aplicação FastAPI
app = FastAPI(
    title="Agente de Análise Financeira",
    description="API para análise fundamentalista de ações usando Agno Framework",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Endpoint raiz da API."""
    return {
        "message": "Agente de Análise Financeira API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat",
            "analyze": "/analyze",
            "docs": "/docs"
        }
    }


@app.post("/chat", response_model=AgentResponse)
async def chat_with_agent(request: QuestionRequest):
    """
    Endpoint principal para conversar com o agente.
    Similar ao ChatGPT - recebe uma pergunta e retorna uma resposta.
    """
    try:
        response = agent.chat(request.question)
        
        return AgentResponse(
            response=response,
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no agente: {str(e)}")


@app.post("/analyze", response_model=AgentResponse)
async def analyze_stock(request: QuestionRequest):
    """
    Endpoint específico para análise de ações.
    Requer ticker na requisição.
    """
    if not request.ticker:
        raise HTTPException(status_code=400, detail="Ticker é obrigatório para análise")
    
    try:
        response = agent.analyze_stock(request.question, request.ticker)
        
        return AgentResponse(
            response=response,
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}")


@app.get("/health")
async def health_check():
    """Endpoint de health check."""
    return {"status": "healthy", "service": "Agente Financeiro"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) 