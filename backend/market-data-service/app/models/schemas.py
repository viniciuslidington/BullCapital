from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

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
    id: Optional[int] = None
    data: date
    ticker: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    symbol: str
    shortName: str
    longName: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    exchange: Optional[str] = None

    class Config:
        from_attributes = True
        orm_mode = True