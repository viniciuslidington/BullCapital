from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional

class UserBase(BaseModel):
    """
    Schema base para dados do usuário.
    
    Contém os campos comuns compartilhados entre diferentes
    operações relacionadas ao usuário (criar, atualizar, resposta).
    
    Attributes:
        nome_completo (str): Nome completo do usuário
        data_nascimento (date): Data de nascimento no formato YYYY-MM-DD
        email (EmailStr): Email válido do usuário
    """
    nome_completo: str
    data_nascimento: date
    email: EmailStr

class UserCreate(UserBase):
    """
    Schema para criação de novo usuário.
    
    Herda todos os campos de UserBase e adiciona o campo senha
    necessário para o registro de um novo usuário.
    
    Attributes:
        senha (str): Senha em texto plano (será hasheada antes de salvar)
    """
    senha: str

class UserLogin(BaseModel):
    """
    Schema para dados de login do usuário.
    
    Contém apenas os campos necessários para autenticação:
    email e senha.
    
    Attributes:
        email (EmailStr): Email do usuário para login
        senha (str): Senha em texto plano para verificação
    """
    email: EmailStr
    senha: str

class UserResponse(UserBase):
    """
    Schema para resposta com dados do usuário.
    
    Herda campos de UserBase e adiciona metadados do sistema
    como ID e timestamps. Usado para retornar dados do usuário
    em APIs sem expor informações sensíveis como senha.
    
    Attributes:
        id (int): Identificador único do usuário
        created_at (datetime, optional): Data/hora de criação do registro
        updated_at (datetime, optional): Data/hora da última atualização
    """
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    """
    Schema para atualização de dados do usuário.
    
    Todos os campos são opcionais, permitindo atualização
    parcial dos dados do usuário.
    
    Attributes:
        nome_completo (str, optional): Novo nome completo
        data_nascimento (date, optional): Nova data de nascimento
        email (EmailStr, optional): Novo email
    """
    nome_completo: Optional[str] = None
    data_nascimento: Optional[date] = None
    email: Optional[EmailStr] = None

class TokenResponse(BaseModel):
    """
    Schema para resposta de autenticação com token JWT.
    
    Retornado após login bem-sucedido, contém o token de acesso
    e informações sobre sua validade, além dos dados do usuário.
    
    Attributes:
        access_token (str): Token JWT para autenticação
        token_type (str): Tipo do token (sempre "bearer")
        expires_in (int): Tempo de expiração em segundos
        user (UserResponse): Dados do usuário autenticado
    """
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse
