from typing import Optional, List
from pydantic import BaseModel

from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.sql import func
from core.database import Base



# Modelos Pydantic para a API
class Message(BaseModel):
    sender: str  # "user" ou "bot"
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    sender: str = "user"
    content: str
    user_id: str 
    conversation_id: Optional[str] = None

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
