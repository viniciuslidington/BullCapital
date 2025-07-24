"""
Serviço principal de Market Data.

Este módulo implementa a lógica de negócio principal do microserviço,
coordenando diferentes provedores de dados, cache e rate limiting.
Segue os princípios SOLID e oferece uma interface unificada.

Example:
    from services.market_data_service import MarketDataService
    
    service = MarketDataService()
    data = service.get_stock_data("PETR4.SA", request)
"""

import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.config import settings
from core.logging import LoggerMixin
from models.requests import BulkDataRequest, SearchRequest, StockDataRequest
from models.responses import (
    BulkDataResponse,
    SearchResponse,
    SearchResultItem,
    StockDataResponse,
    ValidationResponse,
)
from services.interfaces import (
    ICacheService,
    IMarketDataProvider,
    IRateLimiter,
    ProviderException,
    RateLimitException,
)
from services.yahoo_finance_provider import YahooFinanceProvider



class InMemoryCache(ICacheService):
    """
    Implementação simples de cache em memória.
    
    Para produção, recomenda-se usar Redis ou Memcached.
    """
    
    def __init__(self):
        """Inicializa o cache em memória."""
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache verificando TTL."""
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        if time.time() > entry['expires_at']:
            del self._cache[key]
            return None
        
        return entry['value']
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Armazena valor no cache com TTL."""
        try:
            self._cache[key] = {
                'value': value,
                'expires_at': time.time() + ttl
            }
            return True
        except Exception:
            return False
    
    def delete(self, key: str) -> bool:
        """Remove chave do cache."""
        try:
            if key in self._cache:
                del self._cache[key]
            return True
        except Exception:
            return False
    
    def clear(self) -> bool:
        """Limpa todo o cache."""
        try:
            self._cache.clear()
            return True
        except Exception:
            return False


class SimpleRateLimiter(IRateLimiter):
    """
    Implementação simples de rate limiter baseado em sliding window.
    
    Para produção, recomenda-se usar Redis para distribuição.
    """
    
    def __init__(
        self,
        max_requests: int = None,
        window_seconds: int = None
    ):
        """
        Inicializa o rate limiter.
        
        Args:
            max_requests: Número máximo de requisições por janela
            window_seconds: Tamanho da janela em segundos
        """
        self.max_requests = max_requests or settings.RATE_LIMIT_REQUESTS
        self.window_seconds = window_seconds or settings.RATE_LIMIT_WINDOW
        self._requests: Dict[str, List[float]] = {}
    
    def is_allowed(self, identifier: str) -> bool:
        """Verifica se requisição é permitida."""
        now = time.time()
        
        # Inicializar lista se não existe
        if identifier not in self._requests:
            self._requests[identifier] = []
        
        # Limpar requisições antigas
        self._requests[identifier] = [
            req_time for req_time in self._requests[identifier]
            if now - req_time < self.window_seconds
        ]
        
        # Verificar limite
        if len(self._requests[identifier]) >= self.max_requests:
            return False
        
        # Adicionar requisição atual
        self._requests[identifier].append(now)
        return True
    
    def get_remaining_requests(self, identifier: str) -> int:
        """Obtém número de requisições restantes."""
        if identifier not in self._requests:
            return self.max_requests
        
        now = time.time()
        recent_requests = [
            req_time for req_time in self._requests[identifier]
            if now - req_time < self.window_seconds
        ]
        
        return max(0, self.max_requests - len(recent_requests))
    
    def reset_limit(self, identifier: str) -> bool:
        """Reseta limite para um identificador."""
        try:
            if identifier in self._requests:
                del self._requests[identifier]
            return True
        except Exception:
            return False


class MarketDataService(LoggerMixin):
    """
    Serviço principal de Market Data.
    
    Coordena diferentes provedores de dados, implementa cache e rate limiting,
    e oferece uma interface unificada para obtenção de dados de mercado.
    
    Attributes:
        provider: Provedor de dados de mercado
        cache_service: Serviço de cache
        rate_limiter: Limitador de taxa de requisições
    """
    
    def __init__(
        self,
        provider: Optional[IMarketDataProvider] = None,
        cache_service: Optional[ICacheService] = None,
        rate_limiter: Optional[IRateLimiter] = None
    ):
        """
        Inicializa o serviço de market data.
        
        Args:
            provider: Provedor de dados (padrão: YahooFinanceProvider)
            cache_service: Serviço de cache (padrão: InMemoryCache)
            rate_limiter: Rate limiter (padrão: SimpleRateLimiter)
        """
        self.provider = provider or YahooFinanceProvider()
        self.cache_service = cache_service or InMemoryCache()
        self.rate_limiter = rate_limiter or SimpleRateLimiter()
        
        self.logger.info("MarketDataService inicializado com sucesso")
    
    def get_stock_data(
        self,
        symbol: str,
        request: StockDataRequest,
        client_id: str = "default",
    ) -> StockDataResponse:
        """
        Obtém dados completos de uma ação específica.
        
        Args:
            symbol: Símbolo da ação
            request: Parâmetros da requisição
            client_id: Identificador do cliente para rate limiting
            
        Returns:
            Dados completos da ação
            
        Raises:
            RateLimitException: Se o rate limit for excedido
            ProviderException: Erro na obtenção de dados
        """
        # Verificar rate limit
        if not self.rate_limiter.is_allowed(client_id):
            raise RateLimitException(
                f"Rate limit excedido para cliente {client_id}",
                remaining=self.rate_limiter.get_remaining_requests(client_id)
            )
        
        # Tentar obter do cache primeiro
        cache_key = self._generate_cache_key("stock_data", symbol, request)
        if settings.ENABLE_CACHE:
            cached_data = self.cache_service.get(cache_key)
            if cached_data:
                self.logger.info(f"Dados obtidos do cache para {symbol}")
                return StockDataResponse(**cached_data)
        
        try:
            # Obter dados do provedor
            self.logger.info(f"Obtendo dados do provedor para {symbol}")
            start_time = time.time()
            
            data = self.provider.get_stock_data(symbol, request)
            
            processing_time = (time.time() - start_time) * 1000
            self.logger.info(
                f"Dados obtidos em {processing_time:.2f}ms para {symbol}"
            )
            
            # Armazenar no cache
            if settings.ENABLE_CACHE:
                self.cache_service.set(
                    cache_key,
                    data.dict(),
                    ttl=settings.CACHE_TTL_SECONDS
                )
            
            return data
            
        except ProviderException:
            # Re-raise provider exceptions
            raise
        except Exception as e:
            error_msg = f"Erro interno ao obter dados para {symbol}: {str(e)}"
            self.logger.error(error_msg)
            raise ProviderException(
                message=error_msg,
                provider="market_data_service",
                error_code="INTERNAL_ERROR"
            )
    
    def search_stocks(
        self,
        request: SearchRequest,
        client_id: str = "default",
    ) -> SearchResponse:
        """
        Busca ações por nome ou símbolo.
        
        Args:
            request: Parâmetros da busca
            client_id: Identificador do cliente
            
        Returns:
            Resultados da busca formatados
        """
        # Verificar rate limit
        if not self.rate_limiter.is_allowed(client_id):
            raise RateLimitException()
        
        try:
            start_time = time.time()
            
            search_results = []
            
            results = self.provider.search_tickers(request.query, request.limit)
            for result in results:
                search_results.append(SearchResultItem(
                    symbol=result["symbol"],
                    name=result["name"],
                    sector=result.get("sector"),
                    market=result.get("market"),
                    current_price=result.get("current_price"),
                    currency=result.get("currency"),
                    relevance_score=result.get("relevance_score")
                ))
            
            search_time = (time.time() - start_time) * 1000
            
            return SearchResponse(
                query=request.query,
                results_found=len(search_results),
                results=search_results,
                filters_applied=getattr(request, "filters", None),
                search_time_ms=search_time
            )
            
        except Exception as e:
            error_msg = f"Erro na busca: {str(e)}"
            self.logger.error(error_msg)
            raise ProviderException(
                message=error_msg,
                provider="market_data_service",
                error_code="SEARCH_ERROR"
            )
    
    def get_bulk_data(
        self,
        request: BulkDataRequest,
        client_id: str = "default",
    ) -> BulkDataResponse:
        """
        Obtém dados em lote para múltiplos tickers.
        
        Args:
            request: Parâmetros da requisição em lote
            client_id: Identificador do cliente
            
        Returns:
            Dados organizados por ticker com estatísticas
        """
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        self.logger.info(
            f"Iniciando requisição em lote {request_id} "
            f"para {len(request.tickers)} tickers"
        )
        
        # Verificar rate limit (usar limite maior para bulk)
        if not self.rate_limiter.is_allowed(f"{client_id}_bulk"):
            raise RateLimitException()
        
        successful_data = {}
        errors = {}
        
        # Processar cada ticker
        for symbol in request.symbols:  # Corrigido: usar 'symbols' em vez de 'tickers'
            try:
                # Criar requisição individual simplificada
                stock_request = StockDataRequest(
                    symbol=symbol,
                    period=request.period
                )
                
                # Obter dados (sem verificar rate limit novamente)
                data = self.provider.get_stock_data(symbol, stock_request)
                successful_data[symbol] = data
            except Exception as e:
                self.logger.warning(f"Erro ao obter dados para {symbol}: {e}")
                errors[symbol] = str(e)
        
        processing_time = (time.time() - start_time) * 1000
        
        self.logger.info(
            f"Requisição em lote {request_id} concluída: "
            f"{len(successful_data)} sucessos, {len(errors)} erros "
            f"em {processing_time:.2f}ms"
        )
        
        return BulkDataResponse(
            request_id=request_id,
            total_tickers=len(request.tickers),
            successful_requests=len(successful_data),
            failed_requests=len(errors),
            data=successful_data,
            errors=errors if errors else None,
            processing_time_ms=processing_time,
            metadata={
                "request_params": request.dict(),
                "client_id": client_id,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def validate_ticker(
        self,
        symbol: str,
        client_id: str = "default",
    ) -> ValidationResponse:
        """
        Valida se um ticker existe e é válido.
        
        Args:
            symbol: Símbolo do ticker
            client_id: Identificador do cliente
            
        Returns:
            Resultado da validação
        """
        # Verificar rate limit
        if not self.rate_limiter.is_allowed(client_id):
            raise RateLimitException()
        
        # Verificar cache primeiro
        cache_key = f"validation:{symbol}"
        
        if settings.ENABLE_CACHE:
            cached_result = self.cache_service.get(cache_key)
            if cached_result:
                return ValidationResponse(**cached_result)
        
        try:
            # Obter validação do provedor
            result = self.provider.validate_ticker(symbol)
            
            # Cache resultado por mais tempo (validação não muda frequentemente)
            if settings.ENABLE_CACHE:
                self.cache_service.set(
                    cache_key,
                    result.dict(),
                    ttl=settings.CACHE_TTL_SECONDS * 4  # 4x o TTL normal
                )
            
            return result
            
        except Exception as e:
            error_msg = f"Erro na validação: {str(e)}"
            self.logger.error(error_msg)
            raise ProviderException(
                message=error_msg,
                provider="market_data_service",
                error_code="VALIDATION_ERROR"
            )
    
    def get_trending_stocks(
        self,
        market: str = "BR",
        client_id: str = "default",
    ) -> List[Dict[str, Any]]:
        """
        Obtém ações em tendência.
        
        Args:
            market: Mercado alvo
            client_id: Identificador do cliente
            
        Returns:
            Lista de ações em tendência
        """
        # Verificar rate limit
        if not self.rate_limiter.is_allowed(client_id):
            raise RateLimitException()
        
        # Verificar cache
        cache_key = f"trending:{market}"
        
        if settings.ENABLE_CACHE:
            cached_data = self.cache_service.get(cache_key)
            if cached_data:
                return cached_data
        
        try:
            trending_data = self.provider.get_trending_stocks(market)
            
            if settings.ENABLE_CACHE:
                self.cache_service.set(f"trending:{market}", trending_data, ttl=60)
            
            return trending_data
        except Exception as e:
            error_msg = f"Erro ao obter trending: {str(e)}"
            self.logger.error(error_msg)
            raise ProviderException(
                message=error_msg,
                provider="market_data_service",
                error_code="TRENDING_ERROR"
            )
    
    def get_service_health(self) -> Dict[str, Any]:
        """
        Verifica a saúde do serviço e dependências.
        
        Returns:
            Status detalhado do serviço
        """
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": settings.API_VERSION,
            "cache_status": "unknown",
            "provider_status": "unknown"
        }
        
        try:
            # Testar cache
            test_key = "health_check"
            self.cache_service.set(test_key, "test", ttl=1)
            if self.cache_service.get(test_key) == "test":
                health_data["cache_status"] = "healthy"
            else:
                health_data["cache_status"] = "unhealthy"
            self.cache_service.delete(test_key)
            
        except Exception as e:
            health_data["cache_status"] = f"error: {str(e)}"
        
        try:
            # Testar provedor com ticker simples
            test_validation = self.provider.validate_ticker("PETR4.SA")
            if test_validation.symbol:
                health_data["provider_status"] = "healthy"
            else:
                health_data["provider_status"] = "unhealthy"
                
        except Exception as e:
            health_data["provider_status"] = f"error: {str(e)}"
        
        # Determinar status geral
        if (
            health_data["cache_status"] == "healthy" and
            health_data["provider_status"] == "healthy"
        ):
            health_data["status"] = "healthy"
        else:
            health_data["status"] = "degraded"
        
        return health_data
    
    def clear_cache(self) -> bool:
        """
        Limpa todo o cache do serviço.
        
        Returns:
            True se o cache foi limpo com sucesso
        """
        try:
            result = self.cache_service.clear()
            self.logger.info("Cache limpo com sucesso")
            return result
        except Exception as e:
            self.logger.error(f"Erro ao limpar cache: {e}")
            return False
    
    # Métodos auxiliares privados
    
    def _generate_cache_key(
        self,
        operation: str,
        symbol: str,
        request: StockDataRequest
    ) -> str:
        """Gera chave única para cache baseada nos parâmetros."""
        # Para modelos simplificados, usar apenas os campos disponíveis
        key_parts = [
            operation,
            symbol,
            getattr(request, 'period', 'default'),
        ]
        
        # Adicionar campos opcionais se existirem
        if hasattr(request, 'interval'):
            key_parts.append(getattr(request, 'interval', 'none'))
        if hasattr(request, 'query'):
            key_parts.append(getattr(request, 'query', 'none'))
        if hasattr(request, 'limit'):
            key_parts.append(str(getattr(request, 'limit', 10)))
            
        return ":".join(key_parts)
