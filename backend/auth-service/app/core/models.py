from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean
from sqlalchemy.sql import func
from core.database import Base

class User(Base):
    """
    Modelo de dados para representar um usuário no sistema.
    
    Esta classe define a estrutura da tabela 'users' no banco de dados,
    contendo todas as informações necessárias para autenticação e perfil do usuário.
    
    Attributes:
        id (int): Identificador único do usuário (chave primária)
        nome_completo (str): Nome completo do usuário
        cpf (str): CPF único do usuário (apenas números) - opcional para Google OAuth
        data_nascimento (date): Data de nascimento do usuário - opcional para Google OAuth
        email (str): Email único do usuário (usado para login)
        senha (str): Senha hasheada do usuário - opcional para Google OAuth
        google_id (str): ID único do usuário no Google - para OAuth
        is_google_user (bool): Indica se o usuário foi criado via Google OAuth
        profile_picture (str): URL da foto do perfil do Google
        created_at (datetime): Data e hora de criação do registro
        updated_at (datetime): Data e hora da última atualização do registro
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nome_completo = Column(String, nullable=False)
    cpf = Column(String(11), unique=True, index=True, nullable=True)  # Opcional para Google OAuth
    data_nascimento = Column(Date, nullable=True)  # Opcional para Google OAuth
    email = Column(String, unique=True, index=True, nullable=False)
    senha = Column(String, nullable=True)  # Opcional para Google OAuth
    google_id = Column(String, unique=True, index=True, nullable=True)  # Para OAuth
    is_google_user = Column(Boolean, default=False, nullable=False)
    profile_picture = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
