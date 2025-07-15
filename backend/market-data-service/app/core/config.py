"""
Configurações centrais do Market Data Service.

Este módulo centraliza todas as configurações necessárias para o funcionamento
do microserviço, incluindo configurações de API, cache, rate limiting e integrações
externas. Utiliza Pydantic Settings para validação automática de tipos e valores.

Example:
    from core.config import settings
    
    # Acessar configurações
    print(settings.API_TITLE)
    print(settings.ALLOWED_ORIGINS)
"""

from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables with override=True to ensure .env changes are reflected
load_dotenv(override=True)


class Settings(BaseSettings):
    """
    Configurações da aplicação usando Pydantic Settings.
    
    Esta classe centraliza todas as configurações do microserviço,
    incluindo configurações de API, CORS, cache, rate limiting e
    integrações externas. As configurações são carregadas a partir
    de variáveis de ambiente e arquivo .env.
    
    Attributes:
        DEBUG (bool): Flag para modo debug
        LOG_LEVEL (str): Nível de log (DEBUG, INFO, WARNING, ERROR)
        API_VERSION (str): Versão da API
        API_TITLE (str): Título da API
        API_DESCRIPTION (str): Descrição da API
        ALLOWED_ORIGINS (List[str]): Lista de origens permitidas para CORS
        CACHE_TTL_SECONDS (int): TTL do cache em segundos
        ENABLE_CACHE (bool): Flag para habilitar cache
        RATE_LIMIT_REQUESTS (int): Número de requests permitidos
        RATE_LIMIT_WINDOW (int): Janela de tempo para rate limiting
        YAHOO_FINANCE_TIMEOUT (int): Timeout para requisições ao Yahoo Finance
        MAX_RETRIES (int): Número máximo de tentativas para requisições
        HOST (str): Host do servidor
        PORT (int): Porta do servidor
    """
    
    # Debug and Logging
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # API Configuration
    API_VERSION: str = "1.0.0"
    API_TITLE: str = "Market Data Service"
    API_DESCRIPTION: str = "Microserviço para dados de mercado financeiro"
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8001",
        "http://localhost:8002"
    ]
    
    # Cache Configuration
    CACHE_TTL_SECONDS: int = 300  # 5 minutes
    ENABLE_CACHE: bool = True
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # External APIs
    YAHOO_FINANCE_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8002
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True
    }


# Global settings instance
settings = Settings()
