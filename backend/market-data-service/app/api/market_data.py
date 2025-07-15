"""
Endpoints principais do Market Data Service.

Este módulo implementa todos os endpoints da API REST para obtenção
de dados de mercado, seguindo as melhores práticas de design de APIs.

Example:
    from api.market_data import router
    
    app.include_router(router, prefix="/api/v1/market-data")
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse

from core.config import settings
from core.logging import get_logger
from models.requests import BulkDataRequest, SearchRequest, StockDataRequest
from models.responses import (
    BulkDataResponse,
    ErrorResponse,
    HealthResponse,
    SearchResponse,
    StockDataResponse,
    ValidationResponse,
)
from services.interfaces import ProviderException, RateLimitException
from services.market_data_service import MarketDataService

# Configurar logger e router
logger = get_logger(__name__)
router = APIRouter()

# Instância global do serviço (em produção, usar dependency injection)
market_data_service = MarketDataService()


def get_client_identifier(request: Request) -> str:
    """
    Extrai identificador único do cliente para rate limiting.
    
    Args:
        request: Request HTTP
        
    Returns:
        Identificador único (IP address ou header personalizado)
    """
    # Tentar obter de header personalizado primeiro
    client_id = request.headers.get("X-Client-ID")
    if client_id:
        return client_id
    
    # Usar IP address como fallback
    forwarded_ip = request.headers.get("X-Forwarded-For")
    if forwarded_ip:
        return forwarded_ip.split(",")[0].strip()
    
    return request.client.host if request.client else "unknown"


def handle_service_exceptions(func):
    """
    Decorator para tratamento centralizado de exceções dos serviços.
    
    Args:
        func: Função do endpoint a ser decorada
        
    Returns:
        Função decorada com tratamento de exceções
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RateLimitException as e:
            logger.warning(f"Rate limit excedido: {e}")
            error_response = ErrorResponse(
                error="RATE_LIMIT_EXCEEDED",
                message="Taxa de requisições excedida. Tente novamente mais tarde.",
                details={
                    "remaining_requests": e.remaining,
                    "reset_time": e.reset_time
                },
                timestamp=str(HTTPException)
            )
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content=error_response.dict()
            )
        except ProviderException as e:
            logger.error(f"Erro do provedor: {e}")
            error_response = ErrorResponse(
                error=e.error_code or "PROVIDER_ERROR",
                message=e.message,
                details=e.details,
                timestamp=str(HTTPException)
            )
            return JSONResponse(
                status_code=status.HTTP_502_BAD_GATEWAY,
                content=error_response.dict()
            )
        except ValueError as e:
            logger.warning(f"Erro de validação: {e}")
            error_response = ErrorResponse(
                error="VALIDATION_ERROR",
                message=str(e),
                timestamp=str(HTTPException)
            )
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=error_response.dict()
            )
        except Exception as e:
            logger.error(f"Erro interno: {e}")
            error_response = ErrorResponse(
                error="INTERNAL_SERVER_ERROR",
                message="Erro interno do servidor",
                details={"original_error": str(e)} if settings.DEBUG else None,
                timestamp=str(HTTPException)
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=error_response.dict()
            )
    
    return wrapper


@router.get(
    "/stocks/{symbol}",
    response_model=StockDataResponse,
    summary="Obter dados de uma ação específica",
    description="""
    Obtém dados completos de uma ação específica, incluindo preço atual,
    dados fundamentais opcionais e histórico de preços.
    
    **Parâmetros de Path:**
    - **symbol**: Símbolo da ação (ex: PETR4.SA, AAPL, MSFT)
    
    **Parâmetros de Query:**
    - **period**: Período do histórico (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
    - **interval**: Intervalo dos dados (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
    - **start_date**: Data de início para histórico (YYYY-MM-DD)
    - **end_date**: Data de fim para histórico (YYYY-MM-DD)
    - **include_fundamentals**: Incluir dados fundamentais
    - **include_history**: Incluir histórico de preços
    
    **Exemplos:**
    - `/stocks/PETR4.SA` - Dados básicos da Petrobras
    - `/stocks/PETR4.SA?period=1y&include_fundamentals=true` - Dados de 1 ano com fundamentals
    - `/stocks/AAPL?start_date=2024-01-01&end_date=2024-12-31` - Apple com período específico
    """
)
@handle_service_exceptions
def get_stock_data(
    symbol: str,
    request: Request,
    period: Optional[str] = Query(
        default="1mo",
        description="Período do histórico",
        regex=r"^(1d|5d|1mo|3mo|6mo|1y|2y|5y|10y|ytd|max)$"
    ),
    interval: str = Query(
        default="1d",
        description="Intervalo dos dados",
        regex=r"^(1m|2m|5m|15m|30m|60m|90m|1h|1d|5d|1wk|1mo|3mo)$"
    ),
    start_date: Optional[str] = Query(
        default=None,
        description="Data de início (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = Query(
        default=None,
        description="Data de fim (YYYY-MM-DD)"
    ),
    include_fundamentals: bool = Query(
        default=False,
        description="Incluir dados fundamentais"
    ),
    include_history: bool = Query(
        default=True,
        description="Incluir histórico de preços"
    )
) -> StockDataResponse:
    """Endpoint para obter dados de uma ação específica."""
    logger.info(f"Requisição de dados para {symbol}")
    
    # Criar objeto de requisição
    stock_request = StockDataRequest(
        symbol=symbol,
        period=period,
        interval=interval,
        start_date=start_date,
        end_date=end_date,
        include_fundamentals=include_fundamentals,
        include_history=include_history
    )
    
    # Obter identificador do cliente
    client_id = get_client_identifier(request)
    
    # Chamar serviço
    return market_data_service.get_stock_data(symbol, stock_request, client_id)


@router.get(
    "/stocks/search",
    response_model=SearchResponse,
    summary="Buscar ações por nome ou símbolo",
    description="""
    Busca ações por nome da empresa ou símbolo do ticker.
    Suporta busca parcial e fuzzy matching.
    
    **Parâmetros:**
    - **query**: Termo de busca (nome da empresa ou símbolo)
    - **limit**: Número máximo de resultados (1-100)
    
    **Exemplos:**
    - `/stocks/search?query=Petrobras` - Buscar por nome da empresa
    - `/stocks/search?query=PETR` - Buscar por símbolo parcial
    - `/stocks/search?query=banco&limit=20` - Buscar bancos com limite de 20 resultados
    """
)
@handle_service_exceptions
def search_stocks(
    request: Request,
    query: str = Query(..., min_length=1, description="Termo de busca"),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Número máximo de resultados"
    )
) -> SearchResponse:
    """Endpoint para buscar ações por nome ou símbolo."""
    logger.info(f"Busca por: {query}")
    
    # Criar objeto de requisição
    search_request = SearchRequest(
        query=query,
        limit=limit
    )
    
    # Obter identificador do cliente
    client_id = get_client_identifier(request)
    
    # Chamar serviço
    return market_data_service.search_stocks(search_request, client_id)


@router.get(
    "/stocks/trending",
    summary="Obter ações em tendência",
    description="""
    Retorna as principais ações em tendência para um mercado específico.
    
    **Parâmetros:**
    - **market**: Código do mercado (BR para Brasil, US para Estados Unidos)
    - **limit**: Número máximo de ações retornadas
    
    **Exemplos:**
    - `/stocks/trending` - Top ações brasileiras
    - `/stocks/trending?market=US&limit=20` - Top 20 ações americanas
    """
)
@handle_service_exceptions
def get_trending_stocks(
    request: Request,
    market: str = Query(default="BR", description="Código do mercado"),
    limit: int = Query(default=10, ge=1, le=50, description="Número de resultados")
):
    """Endpoint para obter ações em tendência."""
    logger.info(f"Trending stocks para mercado {market}")
    
    # Obter identificador do cliente
    client_id = get_client_identifier(request)
    
    # Chamar serviço
    trending_data = market_data_service.get_trending_stocks(market, client_id)
    
    # Limitar resultados
    limited_data = trending_data[:limit]
    
    return {
        "market": market,
        "timestamp": str(HTTPException),
        "total_stocks": len(limited_data),
        "trending_stocks": limited_data
    }


@router.get(
    "/tickers/{symbol}/validate",
    response_model=ValidationResponse,
    summary="Validar um ticker específico",
    description="""
    Valida se um ticker existe e é válido para negociação.
    Retorna informações detalhadas sobre o status do ticker.
    
    **Parâmetros:**
    - **symbol**: Símbolo do ticker para validar
    
    **Exemplos:**
    - `/tickers/PETR4.SA/validate` - Validar ticker da Petrobras
    - `/tickers/INVALID/validate` - Testar ticker inválido
    """
)
@handle_service_exceptions
def validate_ticker(
    symbol: str,
    request: Request
) -> ValidationResponse:
    """Endpoint para validar um ticker específico."""
    logger.info(f"Validando ticker {symbol}")
    
    # Obter identificador do cliente
    client_id = get_client_identifier(request)
    
    # Chamar serviço
    return market_data_service.validate_ticker(symbol, client_id)


@router.post(
    "/bulk",
    response_model=BulkDataResponse,
    summary="Obter dados em lote para múltiplos tickers",
    description="""
    Obtém dados de mercado para múltiplos tickers em uma única requisição.
    Otimizado para processamento eficiente de grandes volumes de dados.
    
    **Body da requisição:**
    ```json
    {
        "tickers": ["PETR4.SA", "VALE3.SA", "ITUB4.SA"],
        "period": "1mo",
        "interval": "1d",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "include_fundamentals": true
    }
    ```
    
    **Limites:**
    - Máximo de 50 tickers por requisição
    - Rate limiting mais restritivo aplicado
    """
)
@handle_service_exceptions
def get_bulk_data(
    bulk_request: BulkDataRequest,
    request: Request
) -> BulkDataResponse:
    """Endpoint para obter dados em lote."""
    logger.info(f"Requisição em lote para {len(bulk_request.tickers)} tickers")
    
    # Obter identificador do cliente
    client_id = get_client_identifier(request)
    
    # Chamar serviço
    return market_data_service.get_bulk_data(bulk_request, client_id)


@router.post(
    "/search/advanced",
    response_model=SearchResponse,
    summary="Busca avançada de tickers",
    description="""
    Busca avançada com filtros complexos e opções de ordenação.
    
    **Body da requisição:**
    ```json
    {
        "query": "banco",
        "limit": 20,
        "filters": {
            "market": "BR",
            "sector": "Financial Services",
            "min_market_cap": 1000000000
        },
        "include_live_data": true
    }
    ```
    """
)
@handle_service_exceptions
def advanced_search(
    search_request: SearchRequest,
    request: Request
) -> SearchResponse:
    """Endpoint para busca avançada de tickers."""
    logger.info(f"Busca avançada: {search_request.query}")
    
    # Obter identificador do cliente
    client_id = get_client_identifier(request)
    
    # Chamar serviço (implementação básica, pode ser expandida)
    return market_data_service.search_stocks(search_request, client_id)


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Verificar saúde do serviço",
    description="""
    Endpoint de health check que verifica o status do serviço
    e suas dependências (cache, provedores externos, etc.).
    
    **Retorna:**
    - Status geral do serviço
    - Status de cada componente
    - Métricas de performance
    - Informações de versão
    """
)
def health_check() -> HealthResponse:
    """Endpoint de health check."""
    health_data = market_data_service.get_service_health()
    
    return HealthResponse(
        status=health_data["status"],
        timestamp=health_data["timestamp"],
        version=health_data["version"],
        uptime_seconds=0.0,  # Implementar se necessário
        external_services={
            "yahoo_finance": health_data["provider_status"],
            "cache": health_data["cache_status"]
        }
    )


@router.get(
    "/",
    summary="Informações do serviço",
    description="Retorna informações básicas sobre o Market Data Service."
)
def service_info():
    """Endpoint de informações do serviço."""
    return {
        "service": "Market Data Service",
        "version": settings.API_VERSION,
        "description": settings.API_DESCRIPTION,
        "status": "running",
        "endpoints": {
            "stocks": "/api/v1/market-data/stocks/{symbol}",
            "search": "/api/v1/market-data/stocks/search",
            "trending": "/api/v1/market-data/stocks/trending",
            "validate": "/api/v1/market-data/tickers/{symbol}/validate",
            "bulk": "/api/v1/market-data/bulk",
            "health": "/api/v1/market-data/health"
        },
        "documentation": "/docs"
    }


@router.delete(
    "/cache",
    summary="Limpar cache do serviço",
    description="""
    Endpoint administrativo para limpar todo o cache do serviço.
    Útil para forçar atualização de dados ou resolver problemas de cache.
    
    **Nota:** Este endpoint deve ser protegido em produção.
    """
)
def clear_cache():
    """Endpoint para limpar cache (administrativo)."""
    logger.info("Limpeza de cache solicitada")
    
    success = market_data_service.clear_cache()
    
    if success:
        return {"message": "Cache limpo com sucesso", "status": "success"}
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Erro ao limpar cache", "status": "error"}
        )
