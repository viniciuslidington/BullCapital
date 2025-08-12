from typing import Optional, List
from pydantic import BaseModel
import uuid
from sqlalchemy import Column, String, Date, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

# Modelos SQLAlchemy para o banco de dados
class User(Base):
    """
    Modelo de dados para representar um usuário no sistema.
    
    Esta classe define a estrutura da tabela 'users' no banco de dados,
    contendo apenas o identificador único do usuário.
    
    Attributes:
        id (UUID): Identificador único do usuário (chave primária)
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Relacionamentos
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")

class Conversation(Base):
    """
    Modelo de dados para representar uma conversa no sistema.
    
    Esta classe define a estrutura da tabela 'conversations' no banco de dados,
    contendo todas as informações necessárias para gerenciar conversas do AI.
    
    Attributes:
        id (UUID): Identificador único da conversa (chave primária)
        user_id (UUID): ID do usuário (Foreign Key, opcional para conversas temporárias)
        title (str): Título da conversa
        temporario (bool): Indica se a conversa é temporária (sem usuário)
        created_at (datetime): Data e hora de criação do registro
        updated_at (datetime): Data e hora da última atualização do registro
    """
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    title = Column(String, nullable=False)
    temporario = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    """
    Modelo de dados para representar uma mensagem no sistema.
    
    Esta classe define a estrutura da tabela 'messages' no banco de dados,
    contendo todas as informações necessárias para gerenciar mensagens do AI.
    
    Attributes:
        id (UUID): Identificador único da mensagem (chave primária)
        conversation_id (UUID): ID da conversa (Foreign Key)
        sender (str): Remetente da mensagem ("user" ou "bot")
        content (str): Conteúdo da mensagem
        timestamp (datetime): Data e hora da mensagem
    """
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    sender = Column(String, nullable=False)  # "user" ou "bot"
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    conversation = relationship("Conversation", back_populates="messages")

# Modelos Pydantic para a API
class UserRequest(BaseModel):
    id: uuid.UUID

class UserResponse(BaseModel):
    id: uuid.UUID

class MessageRequest(BaseModel):
    sender: str  # "user" ou "bot"
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    sender: str = "user"
    content: str
    user_id: Optional[uuid.UUID] = None  # Agora é opcional
    conversation_id: Optional[uuid.UUID] = None

class ChatResponse(BaseModel):
    conversation_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    temporario: bool  # Adicionado campo temporario
    messages: List[MessageRequest]

class ConversationRequest(BaseModel):
    conversation_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None  # Agora é opcional
    title: str
    temporario: bool  # Adicionado campo temporario
    messages: List[MessageRequest]

class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: str

    class Config:
        from_attributes = True  # Para compatibilidade com SQLAlchemy
