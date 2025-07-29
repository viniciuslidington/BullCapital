"""
Configurações centrais do API Gateway.
"""
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv(override=True)

class Settings(BaseSettings):
    """
    Centraliza as configurações do gateway.
    """
    # URL para o serviço de autenticação
    AUTH_SERVICE_URL: str = "http://auth-service:8001"

    # URL para o serviço de dados de mercado
    MARKET_DATA_SERVICE_URL: str = "http://market-data-service:8002"

    # URL para o serviço de armazenamento de dados
    DATA_STORAGE_SERVICE_URL: str = "http://data-storage-service:8003"

    # URL para o serviço de instrumentos
    INSTRUMENT_SERVICE_URL: str = "http://instrument-service:8004"

    # URL para o serviço de download de mercado
    MARKET_DOWNLOAD_SERVICE_URL: str = "http://market-download-service:8005"
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False  # Nomes de variáveis de ambiente não diferenciam maiúsculas/minúsculas
    }

# Instância global das configurações
settings = Settings()
