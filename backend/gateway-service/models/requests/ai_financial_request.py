import uuid
from pydantic import BaseModel
from typing import List, Optional

class UserRequest(BaseModel):
    nome_completo: str
    cpf: str
    data_nascimento: str  # formato YYYY-MM-DD
    email: str
    senha: str


class MessageRequest(BaseModel):
    sender: str  # "user" ou "bot"
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    sender: str = "user"
    content: str
    user_id: uuid.UUID
    conversation_id: Optional[uuid.UUID] = None

class ConversationRequest(BaseModel):
    conversation_id: uuid.UUID
    user_id: uuid.UUID
    title: str
    messages: List[MessageRequest]
    