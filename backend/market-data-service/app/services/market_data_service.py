

import time
import uuid
from datetime import datetime
import os
import yfinance as yf
import pandas as pd
from yfinance import EquityQuery
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional
from deep_translator import GoogleTranslator

from core.config import settings
from core.logging import LoggerMixin
from models.requests import BulkDataRequest, SearchRequest, StockDataRequest
from models.responses import (
    BulkDataResponse,
    SearchResponse,
    SearchResultItem,
    StockDataResponse,
    ValidationResponse,
    HistoricalDataPoint,
)
from services.interfaces import (
    ICacheService,
    IMarketDataProvider,
    IRateLimiter,
    ProviderException,
    RateLimitException,
)
from services.yahoo_finance_provider import YahooFinanceProvider
from utils.Ticker_ops import convert_to_serializable, safe_ticker_operation


# Adicionar constantes para os símbolos por categoria
MARKET_OVERVIEW_SYMBOLS = {
        "all": [
            "^BVSP", "^SMLL", "SELIC", "IFIX11.SA", "WEGE3.SA", "PETR4.SA", "VALE3.SA", "ITUB4.SA",  # Brasil
            "^GSPC", "^IXIC", "^DJI", "^VIX", "^RUT",  # EUA
            "^STOXX", "^GDAXI", "^FTSE", "^FCHI", "^STOXX50E",  # Europa
            "^N225", "000001.SS", "^HSI", "^NSEI", "^BSESN",  # Ásia
            "USDBRL=X", "EURBRL=X", "GBPBRL=X", "JPYBRL=X", "AUDBRL=X"  # Moedas
        ],
        "brasil": ["^BVSP", "^SMLL", "SELIC", "IFIX11.SA", "WEGE3.SA", "PETR4.SA", "VALE3.SA", "ITUB4.SA"],
        "eua": ["^GSPC", "^IXIC", "^DJI", "^VIX", "^RUT"],
        "europa": ["^STOXX", "^GDAXI", "^FTSE", "^FCHI", "^STOXX50E"],
        "asia": ["^N225", "000001.SS", "^HSI", "^NSEI", "^BSESN"],
        "moedas": ["USDBRL=X", "EURBRL=X", "GBPBRL=X", "JPYBRL=X", "AUDBRL=X"]
    }

SYMBOL_NAMES = {
        "^BVSP": "Ibovespa",
        "^SMLL": "Small Cap",
        "SELIC": "Taxa Selic",
        "IFIX11.SA": "Índice Fundos Imobiliários",
        "WEGE3.SA": "WEG ON",
        "PETR4.SA": "Petrobras PN",
        "VALE3.SA": "Vale ON",
        "ITUB4.SA": "Itaú PN",
        "^GSPC": "S&P 500",
        "^IXIC": "Nasdaq",
        "^DJI": "Dow Jones",
        "^VIX": "VIX",
        "^RUT": "Russell 2000",
        "^STOXX": "STOXX 600",
        "^GDAXI": "DAX",
        "^FTSE": "FTSE 100",
        "^FCHI": "CAC 40",
        "^STOXX50E": "Euro STOXX 50",
        "^N225": "Nikkei 225",
        "000001.SS": "SSE Composite",
        "^HSI": "Hang Seng",
        "^NSEI": "Nifty 50",
        "^BSESN": "Sensex",
        "USDBRL=X": "Dólar/Real",
        "EURBRL=X": "Euro/Real",
        "GBPBRL=X": "Libra/Real",
        "JPYBRL=X": "Iene/Real",
        "AUDBRL=X": "Dólar Australiano/Real"
    }



BR_PREDEFINED_SCREENER_QUERIES = {
        "mercado_todo": EquityQuery('and', [
            EquityQuery('is-in', ['region', 'br', 'us', 'gb', 'jp']),
            EquityQuery("gte", ["intradaymarketcap", 1000000000]),
        ]),
        "mercado_br": EquityQuery('and', [
            EquityQuery('eq', ['region', 'br']),
            EquityQuery('eq', ['exchange', 'SAO']),
        ]),
        "alta_do_dia": EquityQuery('and', [
            EquityQuery('gt', ['percentchange', 3]),
            EquityQuery('eq', ['region', 'br']),
            EquityQuery('eq', ['exchange', 'SAO']),
            EquityQuery('gte', ['intradaymarketcap', 1000000000]),
            EquityQuery('gt', ['dayvolume', 15000])
        ]),
        
        "baixa_do_dia": EquityQuery('and', [
            EquityQuery('lt', ['percentchange', -2.5]),
            EquityQuery('eq', ['region', 'br']),
            EquityQuery('eq', ['exchange', 'SAO']),
            EquityQuery('gte', ['intradaymarketcap', 1000000000]),
            EquityQuery('gt', ['dayvolume', 20000])
        ]),
        
        "mais_negociadas": EquityQuery('and', [
            EquityQuery('eq', ['region', 'br']),
            EquityQuery('eq', ['exchange', 'SAO']),
            EquityQuery('gte', ['intradaymarketcap', 1000000000]),
            EquityQuery('gt', ['dayvolume', 2000000])
        ]),
        
        "small_caps_crescimento": EquityQuery('and', [
            EquityQuery('eq', ['region', 'br']),
            EquityQuery('eq', ['exchange', 'SAO']),
            EquityQuery('lt', ['intradaymarketcap', 2000000000]),
            EquityQuery('gte', ['quarterlyrevenuegrowth.quarterly', 15])
        ]),
        
        "valor_dividendos": EquityQuery('and', [
            EquityQuery('eq', ['region', 'br']),
            EquityQuery('eq', ['exchange', 'SAO']),
            EquityQuery('gt', ['forward_dividend_yield', 5]),
            EquityQuery('gt', ['intradaymarketcap', 1000000000])
        ]),
        
        "baixo_pe": EquityQuery('and', [
            EquityQuery('eq', ['region', 'br']),
            EquityQuery('eq', ['exchange', 'SAO']),
            EquityQuery('btwn', ['peratio.lasttwelvemonths', 1, 15]),
            EquityQuery('gt', ['intradaymarketcap', 1000000000])
        ]),
        
        "alta_liquidez": EquityQuery('and', [
            EquityQuery('eq', ['region', 'br']),
            EquityQuery('eq', ['exchange', 'SAO']),
            EquityQuery('gt', ['avgdailyvol3m', 5000000]),
            EquityQuery('gt', ['intradaymarketcap', 5000000000])
        ]),
        
        "crescimento_lucros": EquityQuery('and', [
            EquityQuery('eq', ['region', 'br']),
            EquityQuery('eq', ['exchange', 'SAO']),
            EquityQuery('gt', ['epsgrowth.lasttwelvemonths', 20]),
            EquityQuery('gt', ['netincomemargin.lasttwelvemonths', 10])
        ]),
        
        "baixo_risco": EquityQuery('and', [
            EquityQuery('eq', ['region', 'br']),
            EquityQuery('eq', ['exchange', 'SAO']),
            EquityQuery('lt', ['beta', 0.8]),
            EquityQuery('gt', ['intradaymarketcap', 5000000000]),
            EquityQuery('gt', ['forward_dividend_yield', 3])
        ])
    }



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

    def get_stock_history(
        self,
        symbol: str,
        period: str = "1mo",
        interval: str = "1d",
        client_id: str = "default"
    ) -> List[HistoricalDataPoint]:
        """
        Obtém a série histórica de uma ação para o período especificado.
        Args:
            symbol: Símbolo da ação
            period: Período (ex: '1mo', '1y', etc)
            interval: Intervalo (ex: '1d', '1h', etc)
            client_id: Identificador do cliente
        Returns:
            Lista de pontos históricos
        """
        from models.requests import StockDataRequest
        from models.responses import HistoricalDataPoint
        import yfinance as yf

        # Rate limit opcional
        if not self.rate_limiter.is_allowed(client_id):
            raise RateLimitException(
                f"Rate limit excedido para cliente {client_id}",
                remaining=self.rate_limiter.get_remaining_requests(client_id)
            )

        try:
            request = StockDataRequest(symbol=symbol, period=period, interval=interval)
            ticker = yf.Ticker(symbol)
            return self.provider._get_historical_data(ticker, request, symbol)
        except Exception as e:
            self.logger.error(f"Erro ao obter histórico para {symbol}: {e}")
            return []

    

    def list_available_stocks(self, client_id: str = "default", market: str = "BR") -> list:
        """
        Lista todos os tickers disponíveis para o mercado especificado.
        """
        return self.provider.get_all_tickers(market=market)
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
            f"para {len(request.symbols)} tickers"
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
                    period=request.period,
                    interval=request.interval,
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
            total_tickers=len(request.symbols),
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
    
    # ==================== ENDPOINTS DE DADOS HISTÓRICOS ====================
  
    def get_multiple_tickers_info(
        self,
        symbols: str
    ):
        """
        Obtém informações básicas para múltiplos tickers simultaneamente.
        
        Exemplo de uso:
        ```
        GET /api/v1/frontend/multi-info?symbols=PETR4.SA,VALE3.SA,ITUB4.SA
        ```
        
        Retorna informações básicas como preço, volume, market cap, etc. para cada ticker.
        """
        try:
            # Limpa e valida os símbolos
            symbol_list = [s.strip().upper() for s in symbols.split(',') if s.strip()]
            if not symbol_list:
                raise ValueError(f"Nenhum símbolo válido fornecido")

            result = {}
            # Processa cada símbolo individualmente
            for symbol in symbol_list:
                try:
                    def get_info(ticker):
                        info = ticker.info
                        if info.get("website", False):
                            logo = f"https://t1.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&size=128&url={info.get('website', None)}"
                        else:
                            logo = None
                        return {
                            "symbol": symbol,
                            "name": str(info.get("shortName", "") or info.get("longName", "")),
                            "sector": str(info.get("sector", "")),
                            "price": float(info.get("regularMarketPrice", 0) or 0),
                            "change": float(info.get("regularMarketChangePercent", 0) or 0),
                            "volume": int(info.get("regularMarketVolume", 0) or 0),
                            "market_cap": float(info.get("marketCap", 0) or 0),
                            "pe_ratio": float(info.get("trailingPE", 0) or 0),
                            "dividend_yield": float(info.get("dividendYield", 0) or 0),
                            "beta": float(info.get("beta", 0) or 0),
                            "fiftyTwoWeekChangePercent": float(info.get("fiftyTwoWeekChangePercent", 0)or 0),
                            "avg_volume_3m": int(info.get("averageDailyVolume3Month", 0) or 0),
                            "returnOnEquity": float(info.get("returnOnEquity", 0) or 0),
                            "book_value": float(info.get("bookValue", 0) or 0),
                            "exchange": str(info.get("exchange", "")),
                            "fullExchangeName": str(info.get("fullExchangeName", "")),
                            "currency": str(info.get("currency", "")),
                            "website": str(info.get("website", "")),
                            "logo": logo
                        }

                    ticker_info = safe_ticker_operation(symbol, get_info)
                    result[symbol] = {
                        "success": True,
                        "data": ticker_info
                    }

                except Exception as e:
                    self.logger.error(f"Erro ao obter dados para {symbol}: {str(e)}")
                    result[symbol] = {
                        "success": False,
                        "error": str(e),
                        "data": None
                    }

            return {
                "symbols": symbol_list,
                "timestamp": datetime.now().isoformat(),
                "results": result
            }

        except Exception as e:
            self.logger.error(f"Erro ao obter informações múltiplas: {str(e)}")
            raise ValueError(
                
                f"Erro ao obter informações dos tickers: {str(e)}"
            )

    def get_multiple_historical_data(
        self,
        symbols: str,
        period: str,
        interval: str,
        start: Optional[str],
        end: Optional[str],
        prepost: bool,
        auto_adjust: bool
    ):
        """
        Obtém dados históricos de preços para múltiplos tickers simultaneamente.
        """
        try:
            # Limpa e valida os símbolos
            symbol_list = [s.strip().upper() for s in symbols.split(',') if s.strip()]
            if not symbol_list:
                raise ValueError(
                    
                    f"Nenhum símbolo válido fornecido"
                )

            result = {}
            # Processa cada símbolo individualmente para garantir maior confiabilidade
            for symbol in symbol_list:
                try:
                    # Usa o safe_ticker_operation que já temos
                    ticker_data = safe_ticker_operation(symbol, lambda t: t.history(
                        period=period,
                        interval=interval,
                        start=start,
                        end=end,
                        prepost=prepost,
                        auto_adjust=auto_adjust
                    ))

                    # Processa os dados
                    if isinstance(ticker_data, pd.DataFrame) and not ticker_data.empty:
                        # Converte o índice de datetime para string
                        ticker_data.index = ticker_data.index.strftime('%Y-%m-%d %H:%M:%S')
                        
                        # Converte para o formato desejado
                        result[symbol] = {
                            "success": True,
                            "data": ticker_data.reset_index().fillna(0).to_dict(orient='records')
                        }
                    else:
                        result[symbol] = {
                            "success": False,
                            "error": "Dados não encontrados",
                            "data": []
                        }
                        
                except Exception as e:
                    self.logger.error(f"Erro ao obter dados para {symbol}: {str(e)}")
                    result[symbol] = {
                        "success": False,
                        "error": str(e),
                        "data": []
                    }

            return {
                "symbols": symbol_list,
                "period": period,
                "interval": interval,
                "results": result
            }

        except Exception as e:
            self.logger.error(f"Erro ao obter dados históricos múltiplos: {str(e)}")
            raise ValueError(
                
               f"Erro ao obter dados históricos dos tickers: {str(e)}"
            )


    def get_historical_data(
        symbol: str,
        period: str,
        interval: str,
        start: Optional[str],
        end: Optional[str],
        prepost: bool,
        auto_adjust: bool
    ):
        """
        Obtém dados históricos de preços para um ticker.
        
        Retorna: Open, High, Low, Close, Volume, Dividends, Stock Splits
        """
        def get_history(ticker):
            return ticker.history(
                period=period,
                interval=interval,
                start=start,
                end=end,
                prepost=prepost,
                auto_adjust=auto_adjust
            )
        
        data = safe_ticker_operation(symbol, get_history)
        return {
            "symbol": symbol.upper(),
            "period": period,
            "interval": interval,
            "data": convert_to_serializable(data)
        }


    # ==================== ENDPOINTS DE INFO COMPLETAS ====================


    def get_ticker_fulldata (symbol: str):
        """
        Obtém todas informações 

        """
        def get_info(ticker):
            return ticker.info
        
        info = safe_ticker_operation(symbol, get_info)
        return {
            "symbol": symbol.upper(),
            "info": convert_to_serializable(info)
        }

    # ==================== ENDPOINT DE INFO ESSENCIAIS ====================


    def get_ticker_info(symbol: str):
        """
        Obtém informações principais.
        """
        def get_profile(ticker):
            info = ticker.info
            if info.get("website", False):
                logo = f"https://t1.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&size=128&url={info.get('website', None)}"
            else:
                logo = None
            return {
            "longName": info.get("longName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "employees": info.get("fullTimeEmployees"),
            "website": info.get("website"),
            "country": info.get("country"),
            "business_summary": GoogleTranslator(source='auto', target='pt').translate(info.get("longBusinessSummary", "Resumo não disponível"), dest='pt'),
            "fullExchangeName": info.get("fullExchangeName"),
            "type": info.get("quoteType"),
            "currency": info.get("currency"),
            "logo": logo,

            "priceAndVariation": {
                "currentPrice": info.get("currentPrice"),
                "previousClose": info.get("previousClose"),
                "dayLow": info.get("dayLow"),
                "dayHigh": info.get("dayHigh"),
                "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
                "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
                "fiftyTwoWeekChangePercent": info.get("fiftyTwoWeekChangePercent"),
                "regularMarketChangePercent": info.get("regularMarketChangePercent"),
                "fiftyDayAverage": info.get("fiftyDayAverage"),
                "twoHundredDayAverage": info.get("twoHundredDayAverage")
            },

            "volumeAndLiquidity": {
                "volume": info.get("regularMarketVolume"),
                "averageVolume10days": info.get("averageVolume10days"),
                "averageDailyVolume3Month": info.get("averageDailyVolume3Month"),
                "bid": info.get("bid"),
                "ask": info.get("ask")
            },

            "riskAndMarketOpinion": {
                "beta": info.get("beta"),
                "recommendationKey": info.get("recommendationKey"),
                "recommendationMean": info.get("recommendationMean"),
                "targetHighPrice": info.get("targetHighPrice"),
                "targetLowPrice": info.get("targetLowPrice"),
                "targetMeanPrice": info.get("targetMeanPrice"),
                "numberOfAnalystOpinions": info.get("numberOfAnalystOpinions")
            },

            "valuation": {
                "marketCap": info.get("marketCap"),
                "enterpriseValue": info.get("enterpriseValue"),
                "trailingPE": info.get("trailingPE"),
                "forwardPE": info.get("forwardPE"),
                "priceToBook": info.get("priceToBook"),
                "priceToSalesTrailing12Months": info.get("priceToSalesTrailing12Months"),
                "enterpriseToRevenue": info.get("enterpriseToRevenue"),
                "enterpriseToEbitda": info.get("enterpriseToEbitda")
            },

            "rentability": {
                "returnOnEquity": info.get("returnOnEquity"),
                "returnOnAssets": info.get("returnOnAssets"),
                "profitMargins": info.get("profitMargins"),
                "grossMargins": info.get("grossMargins"),
                "operatingMargins": info.get("operatingMargins"),
                "ebitdaMargins": info.get("ebitdaMargins")
            },

            "eficiencyAndCashflow": {
                "revenuePerShare": info.get("revenuePerShare"),
                "grossProfits": info.get("grossProfits"),
                "ebitda": info.get("ebitda"),
                "operatingCashflow": info.get("operatingCashflow"),
                "freeCashflow": info.get("freeCashflow"),
                "earningsQuarterlyGrowth": info.get("earningsQuarterlyGrowth"),
                "revenueGrowth": info.get("revenueGrowth"),
                "totalRevenue": info.get("totalRevenue")
            },

            "debtAndSolvency": {
                "totalDebt": info.get("totalDebt"),
                "debtToEquity": info.get("debtToEquity"),
                "quickRatio": info.get("quickRatio"),
                "currentRatio": info.get("currentRatio")
            },

            "dividends": {
                "dividendRate": info.get("dividendRate"),
                "dividendYield": info.get("dividendYield"),
                "payoutRatio": info.get("payoutRatio"),
                "lastDividendValue": info.get("lastDividendValue"),
                "exDividendDate": info.get("exDividendDate")
            },

            "ShareholdingAndProfit": {
                "sharesOutstanding": info.get("sharesOutstanding"),
                "floatShares": info.get("floatShares"),
                "heldPercentInsiders": info.get("heldPercentInsiders"),
                "heldPercentInstitutions": info.get("heldPercentInstitutions"),
                "epsTrailingTwelveMonths": info.get("epsTrailingTwelveMonths"),
                "epsForward": info.get("epsForward"),
                "netIncomeToCommon": info.get("netIncomeToCommon")
            }
        }

        
        profile = safe_ticker_operation(symbol, get_profile)
        return {
            "symbol": symbol.upper(),
            "profile": convert_to_serializable(profile)
        }

    # ==================== ENDPOINT DE SEARCH ====================

    def search_tickers(
        self,
        query: str,
        limit: int
    ):
        """
        Busca por tickers, empresas, setores ou países no Yahoo Finance.
        """
        try:
            # Inicializa a busca com os parâmetros corretos
            search = yf.Search(
                query=query,
                max_results=limit,
                news_count=0,  # Não precisamos de notícias
                lists_count=0,  # Não precisamos de listas
                enable_fuzzy_query=True,  # Permite busca aproximada
                recommended=0,  # Não precisamos de recomendados
                raise_errors=True
            )

            quotes = search.quotes
            if not quotes:
                return {
                    "query": query,
                    "count": 0,
                    "results": []
                }
            
            # Formata os resultados
            formatted_results = []
            for item in quotes:
                try:
                    if item.get("website", False):
                        logo = f"https://t1.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&size=128&url={item.get('website', None)}"
                    else:
                        logo = None
                    result = {
                        "symbol": str(item.get("symbol", "")),
                        "name": str(item.get("shortname", "") or item.get("longname", "")),
                        "exchange": str(item.get("exchange", "")),
                        "type": str(item.get("quoteType", "")),
                        "score": float(item.get("score", 0) or 0),
                        "sector": str(item.get("sector", "")),
                        "industry": str(item.get("industry", "")),
                        "logo": logo
                    }
                    formatted_results.append(result)
                except (TypeError, ValueError) as e:
                    self.logger.warning(f"Erro ao formatar resultado da busca: {str(e)}")
                    continue
                    
            # Ordena por score (relevância) descendente
            formatted_results.sort(key=lambda x: x["score"], reverse=True)
            
            return {
                "query": query,
                "count": len(formatted_results),
                "results": formatted_results
            }
        except Exception as e:
            self.logger.error(f"Erro na busca por '{query}': {str(e)}")
            raise ValueError(
                
                f"Erro ao buscar tickers: {str(e)}"
            )

    # ==================== ENDPOINT DE EXPERIMENTAL DE LOOKUP ====================

    def lookup_instruments(
        self,
        query: str,
        type: str,
        count: int
    ):
        """
        Realiza lookup de instrumentos financeiros por tipo e query.
        """
        try:
            # Validar o tipo de lookup
            valid_types = ["all", "stock", "etf", "future", "index", "mutualfund", "currency", "cryptocurrency"]
            if type.lower() not in valid_types:
                raise ValueError(
                    
                    f"Tipo de lookup inválido. Use um dos seguintes: {', '.join(valid_types)}"
                )

            # Realizar o lookup
            try:
                lookup = yf.Lookup(
                    query=query,
                    raise_errors=True
                )

                # Obter resultados baseado no tipo
                if type == "all":
                    results = lookup.get_all(count=count)
                elif type == "stock":
                    results = lookup.get_stock(count=count)
                elif type == "etf":
                    results = lookup.get_etf(count=count)
                elif type == "future":
                    results = lookup.get_future(count=count)
                elif type == "index":
                    results = lookup.get_index(count=count)
                elif type == "mutualfund":
                    results = lookup.get_mutualfund(count=count)
                elif type == "currency":
                    results = lookup.get_currency(count=count)
                elif type == "cryptocurrency":
                    results = lookup.get_cryptocurrency(count=count)
                
                # Converter DataFrame para formato serializável
                if isinstance(results, pd.DataFrame):
                    results = results.fillna("").to_dict(orient='records')
                else:
                    results = []
                
                return results

            except Exception as e:
                self.logger.error(f"Erro no lookup: {str(e)}")
                raise ValueError(
                    
                    f"Erro ao realizar lookup: {str(e)}"
                )

        except Exception as e:
            self.logger.error(f"Erro no endpoint lookup: {str(e)}")
            raise ValueError(
                
                f"Erro no endpoint lookup: {str(e)}"
            )


    def get_dividends(symbol: str):
        """Obtém histórico de dividendos pagos."""
        def get_dividends(ticker):
            return ticker.dividends
        
        data = safe_ticker_operation(symbol, get_dividends)
        return {
            "symbol": symbol.upper(),
            "dividends": convert_to_serializable(data)
        }

    # ==================== ENDPOINT DE RECOMENDAÇÕES ====================

    def get_recommendations(symbol: str):
        """Obtém recomendações detalhadas de analistas."""
        def get_recommendations(ticker):
            return ticker.recommendations
        
        data = safe_ticker_operation(symbol, get_recommendations)
        return {
            "symbol": symbol.upper(),
            "recommendations": convert_to_serializable(data)
        }

    # ==================== ENDPOINT DE CALENDARIO ====================

    def get_calendar(symbol: str):
        """Obtém calendário de eventos corporativos."""
        def get_calendar(ticker):
            return ticker.calendar
        
        data = safe_ticker_operation(symbol, get_calendar)
        return {
            "symbol": symbol.upper(),
            "calendar": convert_to_serializable(data)
        }

    # ==================== ENDPOINT DE NEWS ====================


    def get_news(symbol: str, num: int):
        """Obtém notícias relacionadas ao ticker."""
        def get_news(ticker):
            news = ticker.get_news(count=num)
            simplified_news = []
            for item in news:
                news_content = item.get('content', {})
                simplified_item = {
                    "id": news_content.get('id'),
                    "title": GoogleTranslator(source='auto', target='pt').translate(news_content.get('title', "Resumo não disponível"), dest='pt'),
                    "date": news_content.get('pubDate'),
                    "summary": GoogleTranslator(source='auto', target='pt').translate(news_content.get('summary', "Resumo não disponível"), dest='pt'),
                    "url": news_content.get('canonicalUrl', {}).get('url'),
                    "thumbnail": news_content.get('thumbnail', {}).get('resolutions', [{}])[0].get('url') if news_content.get('thumbnail') else None
                }
                simplified_news.append(simplified_item)
            return simplified_news
        
        data = safe_ticker_operation(symbol, get_news)
        return {
            "symbol": symbol.upper(),
            "news": convert_to_serializable(data)
        }


    # ==================== ENDPOINT DE TRENDING ====================
    def listar_categorias():
        """Lista todas as categorias disponíveis para screening."""
        return {
            "categorias": list(BR_PREDEFINED_SCREENER_QUERIES.keys()),
            "descricoes": {
                "alta_do_dia": "Ações em alta no dia (>3%)",
                "baixa_do_dia": "Ações em baixa no dia (<-2.5%)",
                "mais_negociadas": "Ações mais negociadas por volume",
                "small_caps_crescimento": "Small Caps com alto crescimento",
                "valor_dividendos": "Ações pagadoras de dividendos",
                "baixo_pe": "Ações com baixo P/L",
                "alta_liquidez": "Ações de alta liquidez",
                "crescimento_lucros": "Ações com crescimento de lucros",
                "baixo_risco": "Ações de baixo risco"
            }
        }

    def obter_trending(
        self,
        categoria: str,
        setor: Optional[str],
        limit: Optional[int],
        offset: Optional[int],
        sort_field: Optional[str],
        sort_asc: Optional[bool]
    ):
        """
        Obtém lista de ações baseada na categoria de screening selecionada.
        """
        try:
            if categoria not in BR_PREDEFINED_SCREENER_QUERIES:
                raise ValueError(
                    f"Categoria '{categoria}' não encontrada. Use /categorias para ver as opções disponíveis."
                )
                
            base_query = BR_PREDEFINED_SCREENER_QUERIES[categoria]
            
            # Adicionar filtro de setor se especificado
            if setor:
                query = EquityQuery('and', [
                    base_query,
                    EquityQuery('eq', ['sector', setor])
                ])
            else:
                query = base_query
            
            # Executar screening com try/except específico
            try:
                results = yf.screen(
                    query=query,
                    size=limit,
                    offset=offset,
                    sortField=sort_field,
                    sortAsc=sort_asc
                )
            except Exception as e:
                self.logger.error(f"Erro no yf.screen(): {str(e)}")
                raise ValueError(
                    f"Erro ao executar screening: {str(e)}"
                )
                
            # Extrair quotes do resultado
            if isinstance(results, dict) and 'quotes' in results:
                quotes = results['quotes']
            else:
                quotes = results if isinstance(results, (list, tuple)) else []
                
            if not quotes:
                self.logger.warning(f"Nenhum resultado encontrado para a categoria: {categoria}")
                return {
                    "categoria": categoria,
                    "resultados": [],
                    "total": 0,
                    "offset": offset,
                    "limit": limit,
                    "ordenacao": {
                        "campo": sort_field,
                        "ascendente": sort_asc
                    }
                }
            
            # Processar e formatar resultados com validação
            formatted_results = []
            for item in quotes:
                if not isinstance(item, dict):
                    self.logger.warning(f"Item inválido no resultado: {item}")
                    continue
                
                if item.get("website", False):
                    logo = f"https://t1.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&size=128&url={item.get('website', None)}"
                else:
                    logo = None
                    
                try:
                    formatted_results.append({
                            "symbol": str(item.get("symbol", "")),
                            "name": str(item.get("shortName", "") or item.get("longName", "")),
                            "sector": str(item.get("sector", "")),
                            "price": float(item.get("regularMarketPrice", 0) or 0),
                            "change": float(item.get("regularMarketChangePercent", 0) or 0),
                            "volume": int(item.get("regularMarketVolume", 0) or 0),
                            "market_cap": float(item.get("marketCap", 0) or 0),
                            "pe_ratio": float(item.get("trailingPE", 0) or 0),
                            "dividend_yield": float(item.get("dividendYield", 0) or 0),
                            "fiftyTwoWeekChangePercent": float(item.get("fiftyTwoWeekChangePercent", 0)or 0),
                            "avg_volume_3m": int(item.get("averageDailyVolume3Month", 0) or 0),
                            "returnOnEquity": float(item.get("returnOnEquity", 0) or 0),
                            "book_value": float(item.get("bookValue", 0) or 0),
                            "exchange": str(item.get("exchange", "")),
                            "fullExchangeName": str(item.get("fullExchangeName", "")),
                            "currency": str(item.get("currency", "")),
                            "website": str(item.get("website", "")),
                            "logo": logo
                    })
                except (TypeError, ValueError) as e:
                    self.logger.warning(f"Erro ao formatar item: {str(e)}")
                    continue
                
            return {
                "categoria": categoria,
                "resultados": formatted_results,
                "total": len(formatted_results),
                "total_disponivel": int(results.get("total", len(formatted_results))),
                "offset": offset,
                "limit": limit,
                "ordenacao": {
                    "campo": sort_field,
                    "ascendente": sort_asc
                }
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao executar screening '{categoria}': {str(e)}")
            raise ValueError(
                f"Erro ao executar screening: {str(e)}"
            )

    # ==================== ENDPOINT DE BUSCA-PERSONALIZADA ====================

    def busca_personalizada(
        self,
        min_price: Optional[float],
        max_price: Optional[float],
        min_volume: Optional[int],
        min_market_cap: Optional[float],
        max_pe: Optional[float],
        min_dividend_yield: Optional[float],
        setor: Optional[str],
        limit: Optional[int]
    ):
        """
        Realiza uma busca personalizada com múltiplos critérios.
        """
        try:
            # Construir query dinamicamente
            conditions = [
                EquityQuery('eq', ['region', 'br']),
                EquityQuery('eq', ['exchange', 'SAO'])
            ]
            
            if min_price:
                conditions.append(EquityQuery('gte', ['intradayprice', min_price]))
            if max_price:
                conditions.append(EquityQuery('lte', ['intradayprice', max_price]))
            if min_volume:
                conditions.append(EquityQuery('gt', ['dayvolume', min_volume]))
            if min_market_cap:
                conditions.append(EquityQuery('gte', ['intradaymarketcap', min_market_cap]))
            if max_pe:
                conditions.append(EquityQuery('lte', ['peratio.lasttwelvemonths', max_pe]))
            if min_dividend_yield:
                conditions.append(EquityQuery('gte', ['forward_dividend_yield', min_dividend_yield]))
            if setor:
                conditions.append(EquityQuery('eq', ['sector', setor]))
                
            query = EquityQuery('and', conditions)
            
            results = yf.screen(
                query=query,
                size=limit,
                sortField="marketCap",
                sortAsc=False
            )
            
            formatted_results = []
            for item in results:
                formatted_results.append({
                    "symbol": item.get("symbol"),
                    "name": item.get("shortName") or item.get("longName"),
                    "sector": item.get("sector"),
                    "price": item.get("regularMarketPrice"),
                    "change": item.get("regularMarketChangePercent"),
                    "volume": item.get("regularMarketVolume"),
                    "market_cap": item.get("marketCap"),
                    "pe_ratio": item.get("trailingPE"),
                    "dividend_yield": item.get("dividendYield")
                })
                
            return {
                "tipo": "busca_personalizada",
                "criterios": {
                    "min_price": min_price,
                    "max_price": max_price,
                    "min_volume": min_volume,
                    "min_market_cap": min_market_cap,
                    "max_pe": max_pe,
                    "min_dividend_yield": min_dividend_yield,
                    "setor": setor
                },
                "resultados": formatted_results,
                "total": len(formatted_results)
            }
            
        except Exception as e:
            self.logger.error(f"Erro na busca personalizada: {str(e)}")
            raise ValueError(
                f"Erro na busca personalizada: {str(e)}"
            )
        

    # ==================== ENDPOINT MARKET-OVERVIEW ====================

    def get_market_overview(
        self,
        category: str,
    ):
        """
        Obtém visão geral do mercado para uma categoria específica.
        """
        try:
            category = category.lower()
            if category not in MARKET_OVERVIEW_SYMBOLS:
                raise ValueError(
                    f"Categoria '{category}' inválida. Categorias disponíveis: {', '.join(MARKET_OVERVIEW_SYMBOLS.keys())}"
                )

            symbols = MARKET_OVERVIEW_SYMBOLS[category]
            
            # Função para processar um símbolo
            def process_symbol(symbol):
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    
                    if info.get("website", False):
                        logo = f"https://t1.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&size=128&url={info.get('website', None)}"
                    else:
                        logo = None
                    
                    return {
                        "symbol": symbol,
                        "name": SYMBOL_NAMES.get(symbol, info.get("shortName", "N/A")),
                        "price": info.get("regularMarketPrice", 0),
                        "change": info.get("regularMarketChangePercent", 0),
                        "website": info.get("website", None),
                        "currency": info.get("currency", "N/A"),
                        "logo": logo
                    }
                except Exception as e:
                    self.logger.warning(f"Erro ao processar {symbol}: {str(e)}")
                    return None

            # Processar símbolos em paralelo para melhor performance
            with ThreadPoolExecutor(max_workers=10) as executor:
                results = list(executor.map(process_symbol, symbols))
            
            # Filtrar resultados None e organizar por categoria
            market_data = [r for r in results if r is not None]
            
            # Adicionar metadados
            response = {
                "category": category,
                "timestamp": datetime.now().isoformat(),
                "count": len(market_data),
                "data": market_data
            }

            if not market_data:
                self.logger.warning(f"Nenhum dado encontrado para a categoria: {category}")
                
            return response

        except Exception as e:
            self.logger.error(f"Erro ao obter visão geral do mercado: {str(e)}")
            raise ValueError(
                
                f"Erro ao obter visão geral do mercado: {str(e)}"
            )
            
    # ==================== ENDPOINT PERIOD-PERFORMANCE ====================   
    def get_period_performance(
        self,
        symbols: str,
    ):
        """
        Calcula a performance de múltiplos ativos em diferentes períodos.
        """
        try:
            # Limpar e validar símbolos
            symbol_list = [s.strip().upper() for s in symbols.split(',') if s.strip()]
            
            # Validar número máximo de tickers
            if len(symbol_list) > 5:
                raise ValueError(
                    
                   f"Número máximo de tickers excedido. Máximo permitido: 5, fornecido: {len(symbol_list)}"
                )
                
            # Limpar e validar símbolos
            symbol_list = [s.strip().upper() for s in symbols.split(',') if s.strip()]
            if not symbol_list:
                raise ValueError(
                    
                   f"Nenhum símbolo válido fornecido"
                )

            # Definir períodos e intervalos para os cálculos
            periods = {
                "1D": ("1d", "1d"),    # período, intervalo
                "7D": ("7d", "1d"),
                "1M": ("1mo", "1d"),
                "3M": ("3mo", "1d"),
                "6M": ("6mo", "1d"),
                "1Y": ("1y", "1d")
            }

            results = {}
            for symbol in symbol_list:
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    
                    # Pegar logo se disponível
                    if info.get("website", False):
                        logo = f"https://t1.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&size=128&url={info.get('website', None)}"
                    else:
                        logo = None

                    # Inicializar dados do ticker
                    ticker_data = {
                        "name": info.get("shortName", "") or info.get("longName", ""),
                        "current_price": info.get("regularMarketPrice", 0),
                        "currency": info.get("currency", ""),
                        "logo": logo,
                        "performance": {}
                    }

                    # Calcular performance para cada período
                    for period_name, (period, interval) in periods.items():
                        try:
                            hist = ticker.history(period=period, interval=interval)
                            if not hist.empty:
                                first_price = hist['Close'].iloc[0]
                                last_price = hist['Close'].iloc[-1]
                                change_percent = ((last_price - first_price) / first_price) * 100
                                
                                ticker_data["performance"][period_name] = {
                                    "change_percent": round(change_percent, 2),
                                    "start_price": round(first_price, 2),
                                    "end_price": round(last_price, 2),
                                    "start_date": hist.index[0].strftime('%Y-%m-%d'),
                                    "end_date": hist.index[-1].strftime('%Y-%m-%d')
                                }
                            else:
                                ticker_data["performance"][period_name] = None
                        except Exception as e:
                            self.logger.warning(f"Erro ao calcular {period_name} para {symbol}: {str(e)}")
                            ticker_data["performance"][period_name] = None

                    results[symbol] = {
                        "success": True,
                        "data": ticker_data
                    }

                except Exception as e:
                    self.logger.error(f"Erro ao processar {symbol}: {str(e)}")
                    results[symbol] = {
                        "success": False,
                        "error": str(e),
                        "data": None
                    }

            return {
                "timestamp": datetime.now().isoformat(),
                "symbols_count": len(symbol_list),
                "results": results
            }

        except Exception as e:
            self.logger.error(f"Erro ao calcular performance dos ativos: {str(e)}")
            raise ValueError(
                
                f'Erro ao calcular performance dos ativos: {str(e)}'
            )
            
    # ==================== ENDPOINT DE HEALTH CHECK ====================

    def yfinance_health_check():
        """Health check específico para os endpoints do yfinance."""
        try:
            # Teste simples com um ticker conhecido
            test_ticker = yf.Ticker("AAPL")
            test_info = test_ticker.info
            
            return {
                "status": "healthy",
                "service": "YFinance API",
                "timestamp": datetime.now().isoformat(),
                "test_ticker": "AAPL",
                "test_successful": bool(test_info.get("symbol"))
            }
        except Exception as e:
            raise ValueError(
                f"YFinance service unhealthy: {str(e)}"
            )
            

