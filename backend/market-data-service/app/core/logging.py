"""
Sistema de logging estruturado para o Market Data Service.

Este módulo configura o sistema de logging da aplicação, fornecendo
logs estruturados e configuráveis para diferentes ambientes.

Example:
    from core.logging import get_logger
    
    logger = get_logger(__name__)
    logger.info("Processando requisição", extra={"ticker": "PETR4.SA"})
"""

import logging
import sys

from core.config import settings


class StructuredFormatter(logging.Formatter):
    """
    Formatter personalizado para logs estruturados.
    
    Cria logs em formato estruturado, incluindo informações contextuais
    e metadados úteis para debugging e monitoramento.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Formata o registro de log em formato estruturado.
        
        Args:
            record: Registro de log a ser formatado
            
        Returns:
            String formatada do log
        """
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Adicionar informações extras se disponíveis
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)
            
        return str(log_data)


def setup_logging() -> None:
    """
    Configura o sistema de logging da aplicação.
    
    Define o nível de log, formato e handlers baseado nas configurações
    do ambiente. Em modo debug, usa formato mais verboso.
    """
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Configurar formato baseado no ambiente
    if settings.DEBUG:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    else:
        formatter = StructuredFormatter()
    
    # Configurar handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    # Configurar logger raiz
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(handler)
    
    # Silenciar logs verbosos de bibliotecas externas
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("yfinance").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Obtém um logger configurado para o módulo especificado.
    
    Args:
        name: Nome do módulo/logger (geralmente __name__)
        
    Returns:
        Logger configurado para o módulo
        
    Example:
        logger = get_logger(__name__)
        logger.info("Operação iniciada")
    """
    return logging.getLogger(name)


class LoggerMixin:
    """
    Mixin para adicionar capacidades de logging a classes.
    
    Fornece um logger configurado automaticamente para a classe,
    facilitando o uso de logs estruturados.
    
    Example:
        class MyService(LoggerMixin):
            def process(self):
                self.logger.info("Processando dados")
    """
    
    @property
    def logger(self) -> logging.Logger:
        """
        Retorna um logger configurado para a classe.
        
        Returns:
            Logger configurado com o nome da classe
        """
        return get_logger(self.__class__.__module__ + "." + self.__class__.__name__)


# Configurar logging na importação do módulo
setup_logging()
