"""
Módulo de configurações da aplicação.

Este módulo centraliza todas as configurações necessárias para o funcionamento
do serviço de autenticação, incluindo configurações de banco de dados,
segurança JWT, CORS e debug.

As configurações são carregadas através de variáveis de ambiente e arquivo .env,
usando Pydantic Settings para validação automática de tipos e valores.
"""

from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import List

load_dotenv()

class Settings(BaseSettings):
    """
    Configurações da aplicação usando Pydantic Settings.
    
    Esta classe centraliza todas as configurações da aplicação,
    incluindo conexão com banco de dados, JWT, CORS e debug.
    As configurações são carregadas a partir de variáveis de ambiente
    e arquivo .env.
    
    Attributes:
        user (str): Usuário do banco de dados
        password (str): Senha do banco de dados
        host (str): Host do banco de dados
        port (str): Porta do banco de dados
        dbname (str): Nome do banco de dados
        SECRET_KEY (str): Chave secreta para assinatura JWT
        ALGORITHM (str): Algoritmo usado para JWT (padrão: HS256)
        ACCESS_TOKEN_EXPIRE_MINUTES (int): Tempo de expiração do token em minutos
        ALLOWED_ORIGINS (List[str]): Lista de origens permitidas para CORS
        DEBUG_SQL (bool): Flag para ativar debug de queries SQL
    """
    # Database
    user: str
    password: str
    host: str
    port: str
    dbname: str
    
    @property
    def DATABASE_URL(self) -> str:
        """
        Constrói e retorna a URL de conexão com o banco de dados PostgreSQL.
        
        Para conexões locais (localhost), SSL não é obrigatório.
        Para conexões remotas (produção), SSL será obrigatório.
        
        Returns:
            str: URL de conexão no formato PostgreSQL
        """
        if self.host == "localhost" or self.host == "127.0.0.1":
            # Conexão local - SSL não obrigatório
            return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"
        else:
            # Conexão remota - SSL obrigatório
            return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}?sslmode=require"
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8003/api/v1/auth/google/callback"
    
    # Cookie settings
    ENVIRONMENT: str = "development"
    FRONTEND_URL: str = "http://localhost:3000"
    COOKIE_DOMAIN: str = "localhost"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000", 
        "http://localhost:8003",
        "http://localhost:8000",
        "http://localhost:8080",  # Servidor HTML local
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8003",
        "http://127.0.0.1:8080",  # Servidor HTML local
        "null",  # Para arquivos HTML locais (file://)
        "*"  # Para desenvolvimento - remover em produção
    ]
    
    # Debug
    DEBUG_SQL: bool = False
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False
    }

settings = Settings()
