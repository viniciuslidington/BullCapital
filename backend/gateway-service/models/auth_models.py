from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import date


class UserCreate(BaseModel):
    nome_completo: str = Field(..., example="João da Silva")
    data_nascimento: date = Field(..., example="1990-01-01")
    cpf: str = Field(..., example="52998224725")  # CPF válido para exemplo
    email: EmailStr = Field(..., example="usuario@email.com")
    senha: str = Field(..., example="senhaSegura123")

class UserLogin(BaseModel):
    email: EmailStr
    senha: str

class UserUpdate(BaseModel):
    nome_completo: Optional[str] = None
    email: Optional[EmailStr] = None

class UserResponse(BaseModel):
    id: int
    nome_completo: str
    email: EmailStr
    data_nascimento: date
    is_active: bool

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
