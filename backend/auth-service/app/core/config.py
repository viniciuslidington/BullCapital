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
from typing import List, Union

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
        use_ssl (bool): Flag para indicar se SSL é obrigatório na conexão. Defaults to True.
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
    use_ssl: bool = False  # Default to True for security (e.g., production)

    @property
    def DATABASE_URL(self) -> str:
        """
        Constrói e retorna a URL de conexão com o banco de dados PostgreSQL.

        Adiciona ?sslmode=require se use_ssl=True, caso contrário, conecta sem SSL.
        Ideal para alternar entre desenvolvimento local (sem SSL) e produção (com SSL).

        Returns:
            str: URL de conexão no formato PostgreSQL.
        """
        base_url = f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"
        if self.use_ssl:
            return f"{base_url}?sslmode=require"
        else:
            # Conexão sem SSL (útil para desenvolvimento local com Docker)
            return base_url

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000","http://localhost:5173", "http://localhost:8000"] # Default values

    # Debug
    DEBUG_SQL: bool = False # Default to False

    # Configuração para carregar variáveis de ambiente
    model_config = {
        "env_file": ".env", # Carrega variáveis de um arquivo .env
        "env_file_encoding": "utf-8",
        "case_sensitive": False # Torna os nomes das variáveis de ambiente insensíveis a maiúsculas/minúsculas
    }

    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8003/api/v1/auth/google/callback"
    

    # Cookie settings
    ENVIRONMENT: str = "development"
    FRONTEND_URL: str = "http://localhost:5173"
    COOKIE_DOMAIN: Union[str, None] = "localhost"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000", 
        "http://localhost:5173",
        "http://localhost:8003",
        "http://localhost:8000",
        "http://localhost:8080",  # Servidor HTML local
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
