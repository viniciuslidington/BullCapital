from pydantic import BaseModel, EmailStr
from datetime import date

class UserCreateRequest(BaseModel):
    nome_completo: str
    data_nascimento: date
    email: EmailStr
    senha: str

class UserLoginRequest(BaseModel):
    email: EmailStr
    senha: str

class UserResponse(BaseModel):
    id: int
    nome_completo: str
    data_nascimento: date
    email: str
    
    class Config:
        from_attributes = True
