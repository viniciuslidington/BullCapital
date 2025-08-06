"""
API HTTP Server para o Agente Financeiro COM CONTEXTO.
Servidor FastAPI que expõe o agente como endpoints REST com sistema de chat contextual.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uvicorn

from financial_agent import agent


# Modelos Pydantic para a API
class Message(BaseModel):
    sender: str  # "user" ou "bot"
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    sender: str = "user"
    content: str

class ChatResponse(BaseModel):
    messages: List[Message]

class Conversation(BaseModel):
    conversation_id: str
    user_id: str
    title: str
    messages: List[Message]

class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: str


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

# Armazenamento temporário de conversas (em produção, usar banco de dados)
conversations = {}


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
            "chat": "/chat",
            "docs": "/docs"
        }
    }


@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """
    Endpoint principal para conversar com o agente.
    """
    try:
        # Criar mensagem do usuário
        user_message = create_message(request.sender, request.content)
        
        # Obter histórico da conversa
        conversation_id = "default"
        conversation_history = conversations.get(conversation_id, [])
        
        # Processar com o agente COM CONTEXTO
        agent_response = agent.chat(
            question=request.content,
            conversation_history=conversation_history
        )
        
        # Criar mensagem do bot
        bot_message = create_message("bot", agent_response)
        
        # Criar ou atualizar conversa
        if conversation_id not in conversations:
            conversations[conversation_id] = []
        
        # Adicionar mensagens à conversa
        conversations[conversation_id].extend([user_message, bot_message])
        
        return ChatResponse(messages=conversations[conversation_id])
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no agente: {str(e)}")



@app.get("/conversations/{conversation_id}", response_model=ChatResponse)
async def get_conversation(conversation_id: str):
    """
    Recupera o histórico de uma conversa específica.
    """
    if conversation_id not in conversations:
        return ChatResponse(messages=[])
    
    return ChatResponse(messages=conversations[conversation_id])


@app.delete("/conversations/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """
    Limpa o histórico de uma conversa específica.
    """
    if conversation_id in conversations:
        del conversations[conversation_id]
    
    return {"message": f"Conversa {conversation_id} limpa com sucesso"}


@app.get("/conversations")
async def list_conversations():
    """
    Lista todas as conversas disponíveis.
    """
    return {
        "conversations": list(conversations.keys()),
        "count": len(conversations)
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