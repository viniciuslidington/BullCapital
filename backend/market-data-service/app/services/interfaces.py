"""
Interface abstrata para provedores de dados de mercado.

Este módulo define contratos (interfaces) que devem ser implementados
por diferentes provedores de dados financeiros, seguindo o princípio
da inversão de dependência (SOLID).

Example:
    from services.interfaces import IMarketDataProvider
    
    class YahooFinanceProvider(IMarketDataProvider):
        def get_stock_data(self, symbol: str) -> Dict[str, Any]:
            # implementação específica
            pass
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from models.requests import StockDataRequest
from models.responses import StockDataResponse, ValidationResponse


class IMarketDataProvider(ABC):
    """
    Interface para provedores de dados de mercado.
    
    Define os métodos que devem ser implementados por qualquer
    provedor de dados financeiros (Yahoo Finance, Alpha Vantage, etc.).
    """
    
    @abstractmethod
    def get_stock_data(
        self,
        symbol: str,
        request: StockDataRequest
    ) -> StockDataResponse:
        """
        Obtém dados de uma ação específica.
        
        Args:
            symbol: Símbolo da ação
            request: Parâmetros da requisição
            
        Returns:
            Dados formatados da ação
            
        Raises:
            ProviderException: Erro na comunicação com o provedor
        """
        pass
    
    @abstractmethod
    def validate_ticker(self, symbol: str) -> ValidationResponse:
        """
        Valida se um ticker existe e é válido.
        
        Args:
            symbol: Símbolo do ticker
            
        Returns:
            Resultado da validação
        """
        pass
    
    @abstractmethod
    def search_tickers(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Busca tickers por nome ou símbolo.
        
        Args:
            query: Termo de busca
            limit: Número máximo de resultados
            
        Returns:
            Lista de tickers encontrados
        """
        pass
    
    @abstractmethod
    def get_trending_stocks(self, market: str = "BR") -> List[Dict[str, Any]]:
        """
        Obtém ações em tendência para um mercado específico.
        
        Args:
            market: Código do mercado (BR, US, etc.)
            
        Returns:
            Lista de ações em tendência
        """
        pass


class ICacheService(ABC):
    """
    Interface para serviços de cache.
    
    Define os métodos necessários para implementar diferentes
    estratégias de cache (Redis, Memcached, in-memory, etc.).
    """
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """
        Obtém um valor do cache.
        
        Args:
            key: Chave do cache
            
        Returns:
            Valor armazenado ou None se não encontrado
        """
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """
        Armazena um valor no cache.
        
        Args:
            key: Chave do cache
            value: Valor a ser armazenado
            ttl: Tempo de vida em segundos
            
        Returns:
            True se armazenado com sucesso
        """
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """
        Remove uma chave do cache.
        
        Args:
            key: Chave a ser removida
            
        Returns:
            True se removida com sucesso
        """
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """
        Limpa todo o cache.
        
        Returns:
            True se limpo com sucesso
        """
        pass


class IRateLimiter(ABC):
    """
    Interface para rate limiters.
    
    Define métodos para controle de taxa de requisições,
    prevenindo sobrecarga dos serviços externos.
    """
    
    @abstractmethod
    def is_allowed(self, identifier: str) -> bool:
        """
        Verifica se uma requisição é permitida.
        
        Args:
            identifier: Identificador único (IP, usuário, etc.)
            
        Returns:
            True se a requisição é permitida
        """
        pass
    
    @abstractmethod
    def get_remaining_requests(self, identifier: str) -> int:
        """
        Obtém o número de requisições restantes.
        
        Args:
            identifier: Identificador único
            
        Returns:
            Número de requisições restantes
        """
        pass
    
    @abstractmethod
    def reset_limit(self, identifier: str) -> bool:
        """
        Reseta o limite para um identificador.
        
        Args:
            identifier: Identificador único
            
        Returns:
            True se resetado com sucesso
        """
        pass


class IDataProcessor(ABC):
    """
    Interface para processadores de dados.
    
    Define métodos para processamento e transformação
    de dados financeiros brutos.
    """
    
    @abstractmethod
    def process_historical_data(
        self,
        raw_data: Any,
        symbol: str
    ) -> List[Dict[str, Any]]:
        """
        Processa dados históricos brutos.
        
        Args:
            raw_data: Dados brutos do provedor
            symbol: Símbolo da ação
            
        Returns:
            Dados históricos processados
        """
        pass
    
    @abstractmethod
    def calculate_technical_indicators(
        self,
        data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calcula indicadores técnicos.
        
        Args:
            data: Dados históricos
            
        Returns:
            Indicadores técnicos calculados
        """
        pass
    
    @abstractmethod
    def normalize_symbol(self, symbol: str, market: str = "BR") -> str:
        """
        Normaliza símbolos para diferentes mercados.
        
        Args:
            symbol: Símbolo original
            market: Mercado de destino
            
        Returns:
            Símbolo normalizado
        """
        pass


class ProviderException(Exception):
    """
    Exceção base para erros de provedores de dados.
    
    Attributes:
        message: Mensagem de erro
        provider: Nome do provedor
        error_code: Código de erro específico
        details: Detalhes adicionais do erro
    """
    
    def __init__(
        self,
        message: str,
        provider: str = "unknown",
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializa a exceção do provedor.
        
        Args:
            message: Mensagem de erro
            provider: Nome do provedor
            error_code: Código de erro
            details: Detalhes adicionais
        """
        super().__init__(message)
        self.message = message
        self.provider = provider
        self.error_code = error_code
        self.details = details or {}


class CacheException(Exception):
    """Exceção para erros de cache."""
    pass


class RateLimitException(Exception):
    """
    Exceção para quando o rate limit é excedido.
    
    Attributes:
        reset_time: Timestamp quando o limite será resetado
        remaining: Número de requisições restantes
    """
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        reset_time: Optional[int] = None,
        remaining: int = 0
    ):
        """
        Inicializa a exceção de rate limit.
        
        Args:
            message: Mensagem de erro
            reset_time: Timestamp de reset
            remaining: Requisições restantes
        """
        super().__init__(message)
        self.reset_time = reset_time
        self.remaining = remaining
