from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


class UserCreate(BaseModel):
    nome_completo: str
    data_nascimento: date
    email: str
    senha: str

class UserLogin(BaseModel):
    email: str
    senha: str

class UserUpdate(BaseModel):
    nome_completo: Optional[str] = None
    email: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    nome_completo: str
    email: str
    data_nascimento: date
    is_active: bool

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
