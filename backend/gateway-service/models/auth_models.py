from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime
from uuid import UUID


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
    id: UUID
    nome_completo: str
    email: EmailStr
    data_nascimento: Optional[date] = None
    cpf: Optional[str] = None
    is_google_user: Optional[bool] = False
    profile_picture: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CookieInfo(BaseModel):
    cookie_name: str
    cookie_max_age: Optional[int] = None
    cookie_expires_in: Optional[str] = None
    cookie_secure: Optional[bool] = None
    cookie_httponly: Optional[bool] = None
    cookie_samesite: Optional[str] = None
    cookie_path: Optional[str] = None
    auth_method: Optional[str] = None

class SessionInfo(BaseModel):
    expires_in_minutes: int

class LoginSuccessResponse(BaseModel):
    message: str
    user: UserResponse
    cookie: CookieInfo
    session: SessionInfo
