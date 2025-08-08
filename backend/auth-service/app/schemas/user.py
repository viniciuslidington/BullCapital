from pydantic import BaseModel, EmailStr, field_validator
from datetime import date, datetime
from typing import Optional
import uuid
from utils.validators import validate_cpf, clean_cpf


class LoginResponse(BaseModel):
    message: str
    email: str

class UserBase(BaseModel):
    """
    Schema base para dados do usuário.
    
    Contém os campos comuns compartilhados entre diferentes
    operações relacionadas ao usuário (criar, atualizar, resposta).
    
    Attributes:
        nome_completo (str): Nome completo do usuário
        cpf (str, optional): CPF do usuário (será validado) - opcional para Google OAuth
        data_nascimento (date, optional): Data de nascimento no formato YYYY-MM-DD - opcional para Google OAuth
        email (EmailStr): Email válido do usuário
    """
    nome_completo: str
    cpf: Optional[str] = None
    data_nascimento: Optional[date] = None
    email: EmailStr
    
    @field_validator('cpf')
    @classmethod
    def validate_cpf_field(cls, v: Optional[str]) -> Optional[str]:
        """
        Valida o campo CPF usando o algoritmo oficial brasileiro.
        
        Args:
            v (Optional[str]): CPF a ser validado ou None
            
        Returns:
            Optional[str]: CPF limpo (apenas números) se válido ou None
            
        Raises:
            ValueError: Se o CPF for fornecido mas inválido
        """
        if v is None:
            return v
        if not validate_cpf(v):
            raise ValueError('CPF inválido')
        return clean_cpf(v)

class UserCreate(UserBase):
    """
    Schema para criação de novo usuário.
    
    Herda todos os campos de UserBase e adiciona o campo senha
    necessário para o registro de um novo usuário.
    
    Attributes:
        senha (str): Senha em texto plano (será hasheada antes de salvar)
    """
    senha: str
    
    # Sobrescreve os validadores para tornar CPF e data_nascimento obrigatórios no registro tradicional
    cpf: str
    data_nascimento: date
    
    @field_validator('cpf')
    @classmethod
    def validate_cpf_field(cls, v: str) -> str:
        """
        Valida o campo CPF usando o algoritmo oficial brasileiro.
        
        Args:
            v (str): CPF a ser validado
            
        Returns:
            str: CPF limpo (apenas números) se válido
            
        Raises:
            ValueError: Se o CPF for inválido
        """
        if not validate_cpf(v):
            raise ValueError('CPF inválido')
        return clean_cpf(v)

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
        id (uuid.UUID): Identificador único do usuário
        is_google_user (bool): Indica se o usuário foi criado via Google OAuth
        profile_picture (str, optional): URL da foto do perfil
        created_at (datetime, optional): Data/hora de criação do registro
        updated_at (datetime, optional): Data/hora da última atualização
    """
    id: uuid.UUID
    is_google_user: Optional[bool] = False
    profile_picture: Optional[str] = None
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
        cpf (str, optional): Novo CPF
        data_nascimento (date, optional): Nova data de nascimento
        email (EmailStr, optional): Novo email
    """
    nome_completo: Optional[str] = None
    cpf: Optional[str] = None
    data_nascimento: Optional[date] = None
    email: Optional[EmailStr] = None
    
    @field_validator('cpf')
    @classmethod
    def validate_cpf_field(cls, v: Optional[str]) -> Optional[str]:
        """
        Valida o campo CPF quando fornecido.
        
        Args:
            v (Optional[str]): CPF a ser validado ou None
            
        Returns:
            Optional[str]: CPF limpo se válido ou None
            
        Raises:
            ValueError: Se o CPF for fornecido mas inválido
        """
        if v is None:
            return v
        if not validate_cpf(v):
            raise ValueError('CPF inválido')
        return clean_cpf(v)

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

class GoogleAuthRequest(BaseModel):
    """
    Schema para requisição de autenticação com Google.
    
    Attributes:
        code (str): Código de autorização retornado pelo Google
        redirect_uri (str): URI de redirecionamento usado na autenticação
    """
    code: str
    redirect_uri: str

class GoogleUserInfo(BaseModel):
    """
    Schema para informações do usuário retornadas pelo Google.
    
    Attributes:
        id (str): ID único do usuário no Google
        email (str): Email do usuário
        name (str): Nome completo do usuário
        picture (str, optional): URL da foto do perfil
        verified_email (bool): Se o email foi verificado pelo Google
    """
    id: str
    email: str
    name: str
    picture: Optional[str] = None
    verified_email: bool = False
