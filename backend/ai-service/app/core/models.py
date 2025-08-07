from typing import Optional, List
from pydantic import BaseModel

from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

# Modelos SQLAlchemy para o banco de dados
class User(Base):
    """
    Modelo de dados para representar um usuário no sistema.
    
    Esta classe define a estrutura da tabela 'users' no banco de dados,
    contendo todas as informações necessárias para autenticação e perfil do usuário.
    
    Attributes:
        id (int): Identificador único do usuário (chave primária)
        nome_completo (str): Nome completo do usuário
        cpf (str): CPF único do usuário (apenas números)
        data_nascimento (date): Data de nascimento do usuário
        email (str): Email único do usuário (usado para login)
        senha (str): Senha hasheada do usuário
        created_at (datetime): Data e hora de criação do registro
        updated_at (datetime): Data e hora da última atualização do registro
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nome_completo = Column(String, nullable=False)
    cpf = Column(String(11), unique=True, index=True, nullable=False)
    data_nascimento = Column(Date, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")

class Conversation(Base):
    """
    Modelo de dados para representar uma conversa no sistema.
    
    Esta classe define a estrutura da tabela 'conversations' no banco de dados,
    contendo todas as informações necessárias para gerenciar conversas do AI.
    
    Attributes:
        id (int): Identificador único da conversa (chave primária)
        conversation_id (str): ID único da conversa
        user_id (int): ID do usuário (Foreign Key)
        title (str): Título da conversa
        created_at (datetime): Data e hora de criação do registro
        updated_at (datetime): Data e hora da última atualização do registro
    """
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
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
        id (int): Identificador único da mensagem (chave primária)
        conversation_id (int): ID da conversa (Foreign Key)
        sender (str): Remetente da mensagem ("user" ou "bot")
        content (str): Conteúdo da mensagem
        timestamp (datetime): Data e hora da mensagem
    """
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    sender = Column(String, nullable=False)  # "user" ou "bot"
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    conversation = relationship("Conversation", back_populates="messages")

# Modelos Pydantic para a API
class UserRequest(BaseModel):
    nome_completo: str
    cpf: str
    data_nascimento: str  # formato YYYY-MM-DD
    email: str
    senha: str

class UserResponse(BaseModel):
    id: int
    nome_completo: str
    cpf: str
    data_nascimento: str
    email: str
    created_at: str
    updated_at: str

class MessageRequest(BaseModel):
    sender: str  # "user" ou "bot"
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    sender: str = "user"
    content: str
    user_id: str 
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    messages: List[MessageRequest]

class ConversationRequest(BaseModel):
    conversation_id: str
    user_id: str
    title: str
    messages: List[MessageRequest]

class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: str
