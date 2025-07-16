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

class MarketData (BaseModel):
    id: int | None = None  # Torna opcional
    nome: str
    ticker: str
    data_inicio: date
    data_fim: date
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    symbol: str
    shortName: str
    longName: str
    sector: str
    industry: str
    exchange: str

    class Config:
        from_attributes = True