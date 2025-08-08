from pydantic import BaseModel
from typing import List, Optional
import uuid



class UserResponse(BaseModel):
    id: uuid.UUID
    nome_completo: str
    cpf: str
    data_nascimento: str
    email: str
    created_at: str
    updated_at: Optional[str]

class MessageRequest(BaseModel):
    sender: str  # "user" ou "bot"
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    sender: str = "user"
    content: str
    user_id: uuid.UUID
    conversation_id: Optional[uuid.UUID] = None

class ChatResponse(BaseModel):
    conversation_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    messages: List[MessageRequest]

class ConversationRequest(BaseModel):
    conversation_id: uuid.UUID
    user_id: uuid.UUID
    title: str
    messages: List[MessageRequest]

class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: Optional[str] = None

    class Config:
        from_attributes = True  # Para compatibilidade com SQLAlchemy