from sqlalchemy import Column, Integer, String, Date, DateTime
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
        data_nascimento (date): Data de nascimento do usuário
        email (str): Email único do usuário (usado para login)
        senha (str): Senha hasheada do usuário
        created_at (datetime): Data e hora de criação do registro
        updated_at (datetime): Data e hora da última atualização do registro
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nome_completo = Column(String, nullable=False)
    data_nascimento = Column(Date, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
