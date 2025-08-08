"""
API HTTP Server para o Agente Financeiro COM CONTEXTO.
Servidor FastAPI que expõe o agente como endpoints REST com sistema de chat contextual.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn
from app.core.models import (
    MessageRequest, 
    ChatRequest, 
    ChatResponse, 
    ConversationRequest, 
    HealthResponse, 
    Conversation, 
    Message,
    User
)
from app.agent.financial_agent import agent
from typing import Optional, List
from app.core.database import engine, get_db
from app.core.models import Base
from contextlib import asynccontextmanager
import logging
from sqlalchemy.orm import Session
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação FastAPI.
    """
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        logger.warning("Application will continue without database connection")
    
    yield
    
    logger.info("Application shutting down...")

app = FastAPI(
    title="Agente de Análise Financeira",
    description="API para análise fundamentalista de ações usando Agno Framework",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_conversation_id() -> str:
    """Gera um ID único para uma nova conversa."""
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
        logger.error(f"Erro ao gerar título: {e}")
        return "Nova conversa"


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
async def chat_with_agent(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Endpoint principal para conversar com o agente.
    """
    try:
        # Verificar se o usuário existe
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        # Buscar ou criar conversa
        conversation = None
        if request.conversation_id:
            conversation = db.query(Conversation).filter(
                Conversation.id == request.conversation_id
            ).first()
        
        if not conversation:
            # Criar nova conversa
            title = generate_conversation_title(request.content)
            conversation = Conversation(
                user_id=user.id,
                title=title
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        
        # Criar mensagem do usuário
        user_message = Message(
            conversation_id=conversation.id,
            sender=request.sender,
            content=request.content
        )
        db.add(user_message)
        
        # Buscar histórico de mensagens
        messages_history = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.timestamp).all()
        
        # Processar com o agente
        agent_response = agent.chat(
            question=request.content,
            conversation_history=messages_history  # Passar objetos Message completos
        )
        
        # Criar mensagem do bot
        bot_message = Message(
            conversation_id=conversation.id,
            sender="bot",
            content=agent_response
        )
        db.add(bot_message)
        db.commit()
        
        # Retornar todas as mensagens
        all_messages = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.timestamp).all()
        
        return ChatResponse(messages=[
            MessageRequest(
                sender=msg.sender,
                content=msg.content,
                timestamp=msg.timestamp.isoformat()
            ) for msg in all_messages
        ])
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        logger.error(f"Erro no agente: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro no agente: {str(e)}")

@app.get("/conversations/{conversation_id}", response_model=ChatResponse)
async def get_conversation(conversation_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Recupera o histórico de uma conversa específica.
    """
    try:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if not conversation:
            return ChatResponse(messages=[])
        
        messages = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.timestamp).all()
        
        return ChatResponse(messages=[
            MessageRequest(
                sender=msg.sender,
                content=msg.content,
                timestamp=msg.timestamp.isoformat()
            ) for msg in messages
        ])
    except Exception as e:
        logger.error(f"Erro ao obter conversa: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter conversa: {str(e)}")

@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Remove uma conversa específica e todas suas mensagens.
    """
    try:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail=f"Conversa {conversation_id} não encontrada")
        
        db.delete(conversation)
        db.commit()
        
        return {"message": f"Conversa {conversation_id} removida com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao remover conversa: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao remover conversa: {str(e)}")

@app.get("/conversations")
async def list_conversations(
    user_id: Optional[uuid.UUID] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Lista todas as conversas disponíveis.
    """
    try:
        query = db.query(Conversation)
        
        if user_id is not None:
            query = query.filter(Conversation.user_id == user_id)
        
        query = query.offset(skip).limit(limit)
        conversations = query.all()
        
        conversation_list = []
        for conv in conversations:
            message_count = db.query(Message).filter(
                Message.conversation_id == conv.id
            ).count()
            
            last_message = db.query(Message).filter(
                Message.conversation_id == conv.id
            ).order_by(Message.timestamp.desc()).first()
            
            conversation_list.append({
                "id": conv.id,
                "user_id": conv.user_id,
                "title": conv.title,
                "message_count": message_count,
                "last_message": last_message.timestamp.isoformat() if last_message else None,
                "created_at": conv.created_at.isoformat()
            })
        
        return {
            "conversations": conversation_list,
            "count": len(conversation_list),
            "skip": skip,
            "limit": limit,
            "filtered_by_user_id": user_id
        }
    except Exception as e:
        logger.error(f"Erro ao listar conversas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao listar conversas: {str(e)}")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Endpoint de health check."""
    return HealthResponse(
        status="healthy",
        service="Agente Financeiro",
        timestamp=datetime.now().isoformat()
    )

# Apenas em ambiente de desenvolvimento
@app.delete("/users/delete-all", include_in_schema=False)
async def delete_all_users(db: Session = Depends(get_db)):
    """
    ⚠️ PERIGO: Deleta todos os usuários e suas conversas.
    Endpoint disponível apenas em desenvolvimento.
    """
    try:
        # Contar usuários antes
        total_users = db.query(User).count()
        
        if total_users == 0:
            return {"message": "Não há usuários para deletar."}
        
        # Deletar todos os usuários (cascade delete irá remover conversas e mensagens)
        db.query(User).delete()
        db.commit()
        
        return {
            "message": f"{total_users} usuários foram deletados com sucesso!",
            "deleted_count": total_users
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao deletar usuários: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao deletar usuários: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) 