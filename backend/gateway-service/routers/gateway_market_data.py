from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel
import httpx
from typing import List, Optional

from models.responses.market_data_response import (StockDataResponse, StockSearchResponse,
SearchResult, TredingDataResponse, BulkDataResponse, HistoricalDataPoint, ValidationResponse)

router = APIRouter()

MARKET_DATA_SERVICE_URL = "http://market-data-service:8002"  # URL do serviço de Market Data, deve ser configurado corretamente

@router.get(
    "/stocks/{symbol}",
    response_model=StockDataResponse,
    summary="Obter dados de uma ação específica",
    description="Retorna os dados de mercado de uma ação específica, incluindo preço atual, volume e outras informações relevantes.",
)
async def get_stock_data(
    symbol: str,
    period: Optional[str] = Query("1mo", description="Período para o qual os dados devem ser retornados, ex: '1d', '1w', '1m'")
) -> StockDataResponse:
    async with httpx.AsyncClient() as client:
        try:
            # Note o prefixo /api/v1/market-data que o microsserviço usa INTERNAMENTE
            response = await client.get(
                f"{MARKET_DATA_SERVICE_URL}/api/v1/market-data/stocks/{symbol}",
                params={"period": period}
            )
            response.raise_for_status()
            return StockDataResponse(**response.json())
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Erro no serviço de Market Data: {e.response.text}"
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Serviço de Market Data indisponível: {e}"
            )

@router.get(
    "/",
    summary="Informações do Gateway",
    description="Retorna informações básicas sobre o API Gateway."
)
async def gateway_info():
    return {
        "service": "API Gateway para Market Data",
        "version": "1.0.0",
        "description": "Gateway para o Market Data Service",
        "endpoints_exposed_from_market_data": [ # Melhor nome
            "/stocks/{symbol}",
            "/search",
            "/trending",
            "/validate/{symbol}",
            "/bulk",
            "/health",
            "/cache"
        ],
        "market_data_service_internal_url": MARKET_DATA_SERVICE_URL # Deixar explícito que é a interna
    }

@router.get(
    "/health",
    summary="Verificar saúde do Gateway",
    description="Endpoint para verificar a saúde do API Gateway."
)
async def health_check():
    return {"status": "healthy"}

@router.get(
    "/search",
    summary="Buscar ações",
    description="Busca ações por nome ou símbolo.",
    response_model=StockSearchResponse
)
async def search_stocks(
    query: str = Query(..., description="Termo de busca para ações, pode ser nome ou símbolo"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de resultados a serem retornados")
) -> StockSearchResponse:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{MARKET_DATA_SERVICE_URL}/api/v1/market-data/search",
                params={"q": query, "limit": limit}
            )
            response.raise_for_status()
            return StockSearchResponse(**response.json())
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Erro no serviço de Market Data: {e.response.text}"
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Serviço de Market Data indisponível: {e}"
            )
        
@router.get(
    "/trending",
    summary="Ações em alta",
    description="Retorna uma lista de ações que estão em alta no mercado.",
    response_model=List[TredingDataResponse]
)
async def get_trending_stocks() -> List[TredingDataResponse]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{MARKET_DATA_SERVICE_URL}/api/v1/market-data/trending"
            )
            response.raise_for_status()
            return [TredingDataResponse(**stock) for stock in response.json()]
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Erro no serviço de Market Data: {e.response.text}"
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Serviço de Market Data indisponível: {e}"
            )
        
from fastapi import Body

class BulkGatewayRequest(BaseModel):
    symbols: List[str]
    period: str = "1mo"

@router.post(
    "/bulk",
    summary="Obter dados de múltiplas ações",
    description="Retorna dados de múltiplas ações com base em uma lista de símbolos.",
    response_model=List[StockDataResponse]
)
async def get_bulk_stock_data(
    bulk: BulkGatewayRequest = Body(..., description="Objeto com lista de símbolos e período para as ações")
) -> List[StockDataResponse]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{MARKET_DATA_SERVICE_URL}/api/v1/market-data/bulk",
                json=bulk.dict()
            )
            response.raise_for_status()
            bulk_response = response.json()
            # Extrai os dados do campo 'data' (dict de símbolos)
            return [StockDataResponse(**stock) for stock in bulk_response.get("data", {}).values()]
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Erro no serviço de Market Data: {e.response.text}"
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Serviço de Market Data indisponível: {e}"
            )
        
@router.get(
    "/stocks-all",
    summary="Obter todos os tickers disponíveis",
    description="Retorna todos os tickers disponíveis no serviço de Market Data.",
    response_model=List[SearchResult]
)
async def get_all_tickers() -> List[SearchResult]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{MARKET_DATA_SERVICE_URL}/api/v1/market-data/stocks-all"
            )
            response.raise_for_status()
            return [SearchResult(**stock) for stock in response.json()]
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Erro no serviço de Market Data: {e.response.text}"
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Serviço de Market Data indisponível: {e}"
            )
        
@router.get(
    "stocks/{symbol}/history",
    summary="Obter histórico de dados de uma ação",
    description="Retorna a série histórica de dados de uma ação específica.",
    response_model=List[HistoricalDataPoint]
)
async def get_stock_history(
    symbol: str,
    period: str = Query("1mo", description="Período para o qual os dados devem ser retornados, ex: '1d', '1w', '1m'")
) -> List[HistoricalDataPoint]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{MARKET_DATA_SERVICE_URL}/api/v1/market-data/stocks/{symbol}/history",
                params={"period": period}
            )
            response.raise_for_status()
            return [HistoricalDataPoint(**data) for data in response.json()]
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Erro no serviço de Market Data: {e.response.text}"
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Serviço de Market Data indisponível: {e}"
            )

@router.get(
    "/validate/{symbol}",
    summary="Validar símbolo de ação",
    description="Verifica se um símbolo de ação é válido.",
    response_model=ValidationResponse
)
async def validate_symbol(symbol: str) -> ValidationResponse:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{MARKET_DATA_SERVICE_URL}/api/v1/market-data/validate/{symbol}"
            )
            response.raise_for_status()
            return ValidationResponse(**response.json())
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Erro no serviço de Market Data: {e.response.text}"
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Serviço de Market Data indisponível: {e}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erro inesperado: {str(e)}"
            )
        
@router.get("/multi-info",
    summary="Obter informações de múltiplos tickers",
    description="""
    Símbolos dos tickers separados por vírgula (ex: AAPL,MSFT,PETR4.SA)
    """
)
async def get_multiple_tickers_info(tickers: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{MARKET_DATA_SERVICE_URL}/api/v1/market-data/multi-info",
                params={"tickers": tickers}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Erro no serviço de Market Data: {e.response.text}"
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Serviço de Market Data indisponível: {e}"
            )
    return response

@router.get("/multi-history")
def get_multiple_tickers_history(tickers: str, period: str = "1mo", interval: str = "1d", start: str = "2020-01-01", end: str = "2025-01-01", PrePost: bool = False, autoAdjust: bool = True):
    """
    Obtém o histórico de múltiplos tickers.
    """
    response = market_data_service.get_multiple_historical_data(tickers, period, interval, start, end, PrePost, autoAdjust)
    logger.info(f"Obtendo histórico para múltiplos tickers: {tickers}")
    if not response:
        logger.warning(f"Nenhum ticker encontrado para: {tickers}")
        return {"message": "Nenhum ticker encontrado", "data": []}
    return response

@router.get("/{symbol}/history")
def get_ticker_history(symbol: str, period: str = "1mo", interval: str = "1d", start: str = "2020-01-01", end: str = "2025-01-01", PrePost: bool = False, autoAdjust: bool = True):
    response = market_data_service.get_historical_data(symbol, period, interval, start, end, PrePost, autoAdjust)
    logger.info(f"Obtendo histórico para {symbol}, período {period}, intervalo {interval}")
    if not response:
        logger.warning(f"Nenhum histórico encontrado para: {symbol}")
        return {"message": "Nenhum histórico encontrado", "data": []}
    return response


# ==================== ENDPOINTS DE INFO COMPLETAS ====================

@router.get("/{symbol}/fulldata")
def get_ticker_full_data(symbol: str):
    response = market_data_service.get_ticker_fulldata(symbol)
    logger.info(f"Obtendo dados completos para {symbol}")
    if not response:
        logger.warning(f"Nenhum dado completo encontrado para: {symbol}")
        return {"message": "Nenhum dado completo encontrado", "data": []}
    return response

# ==================== ENDPOINT DE INFO ESSENCIAIS ====================

@router.get("/{symbol}/info")
def get_ticker_info(symbol: str):
    response = market_data_service.get_ticker_info(symbol)
    logger.info(f"Obtendo informações para {symbol}")
    if not response:
        logger.warning(f"Nenhuma informação encontrada para: {symbol}")
        return {"message": "Nenhuma informação encontrada", "data": []}
    return response


# ==================== ENDPOINT DE SEARCH ====================

@router.get("/search", 
    summary="Buscar tickers e empresas",
    description="""
Busca por empresas, setores, símbolos ou países.

**Exemplos de busca:**
- 🏢 Empresas: "petrobras", "vale", "apple", "microsoft"
- 🏦 Setores: "banco", "energia", "tecnologia", "mineração"
- 📊 Símbolos: "PETR", "VALE", "AAPL", "MSFT"
- 🌎 Países: "brazil", "usa", "american"
""")
def search_tickers(query: str, limit: int = 10):
    response = market_data_service.search_tickers(query, limit)
    logger.info(f"Realizando busca para: {query}")
    if not response:
        logger.warning(f"Nenhum ticker encontrado para a busca: {query}")
        return {"message": "Nenhum ticker encontrado", "data": []}
    return response


# ==================== ENDPOINT DE EXPERIMENTAL DE LOOKUP ====================

@router.get("/lookup",
    summary="Lookup de instrumentos financeiros",
    description="""
Busca informações detalhadas sobre instrumentos financeiros.

**Tipos disponíveis:**
- all: Todos os tipos
- stock: Ações
- etf: ETFs
- future: Futuros
- index: Índices
- mutualfund: Fundos Mútuos
- currency: Moedas
- cryptocurrency: Criptomoedas

**Exemplos de busca:**
- Ações brasileiras: "petrobras"
- ETFs: "ishares"
- Índices: "ibovespa"
""")
def lookup(query: str, tipo: str = "all", limit: int = 10):
    response = market_data_service.lookup_instruments(query, tipo, limit)
    logger.info(f"Realizando lookup para: {query}, tipo: {tipo}")
    if not response:
        logger.warning(f"Nenhum instrumento encontrado para a busca: {query}, tipo: {tipo}")
        return {"message": "Nenhum instrumento encontrado", "data": []}
    return response


@router.get("/{symbol}/dividends",
            description="Obter dividendos de um ticker específico")

def get_ticker_dividends(symbol: str):
    response = market_data_service.get_dividends(symbol)
    logger.info(f"Obtendo dividendos para {symbol}")
    if not response:
        logger.warning(f"Nenhum dividendo encontrado para: {symbol}")
        return {"message": "Nenhum dividendo encontrado", "data": []}
    return response


# ==================== ENDPOINT DE RECOMENDAÇÕES ====================

@router.get("/{symbol}/recommendations")
def get_ticker_recommendations(symbol: str):
    response = market_data_service.get_recommendations(symbol)
    logger.info(f"Obtendo recomendações para {symbol}")
    if not response:
        logger.warning(f"Nenhuma recomendação encontrada para: {symbol}")
        return {"message": "Nenhuma recomendação encontrada", "data": []}
    return response


# ==================== ENDPOINT DE CALENDARIO ====================

@router.get("/{symbol}/calendar")
def get_ticker_calendar(symbol: str):
    response = market_data_service.get_calendar(symbol)
    logger.info(f"Obtendo calendário para {symbol}")
    if not response:
        logger.warning(f"Nenhum calendário encontrado para: {symbol}")
        return {"message": "Nenhum calendário encontrado", "data": []}
    return response


# ==================== ENDPOINT DE NEWS ====================

@router.get("/{symbol}/news")
def get_ticker_news(symbol: str, limit: int = 10):
    response = market_data_service.get_news(symbol, limit)
    logger.info(f"Obtendo notícias para {symbol}")
    if not response:
        logger.warning(f"Nenhuma notícia encontrada para: {symbol}")
        return {"message": "Nenhuma notícia encontrada", "data": []}
    return response

# ==================== ENDPOINT DE TRENDING ====================


@router.get("/categorias")
def get_categorias():
    response = market_data_service.get_categorias()
    logger.info(f"Obtendo categorias")
    if not response:
        logger.warning(f"Nenhuma categoria encontrada")
        return {"message": "Nenhuma categoria encontrada", "data": []}
    return response


@router.get("/categorias/{categoria}",
    summary="Listar tickers por categorias predefinidas e adicionar sorting por atributo",
    description="""
Categorias disponíveis:

- **alta_do_dia** (sort: `percentchange`, asc: `false`): Ações em alta no dia (>3%)
- **baixa_do_dia** (sort: `percentchange`, asc: `true`): Ações em baixa no dia (<-2.5%)
- **mais_negociadas** (sort: `dayvolume`, asc: `false`): Ações mais negociadas por volume
- **valor_dividendos** (sort: `forward_dividend_yield`, asc: `false`): Ações pagadoras de dividendos
- **small_caps_crescimento**: Small Caps com alto crescimento
- **baixo_pe**: Ações com baixo P/L
- **alta_liquidez**: Ações de alta liquidez
- **crescimento_lucros**: Ações com crescimento de lucros
- **baixo_risco**: Ações de baixo risco
- **mercado_br**: Lista sem filtros ações do Brasil
- **mercado_todo**: Lista sem filtros ações do Brasil, EUA, Japão, Europa

Setores disponíveis:

- Basic Materials
- Communication Services
- Consumer Cyclical
- Consumer Defensive
- Energy
- Financial Services
- Healthcare
- Industrials
- Real Estate
- Technology
- Utilities
""")
def get_tickers_by_category(
    categoria: str,
    setor: str = None,
    limit: int = 20,
    offset: int = 0,
    sort_field: str = "percentchange",
    sort_asc: bool = False
):
    """
    Endpoint para obter tickers por categoria, com lógica de filtro/sort correta.
    """
    # Garantir que categoria existe
    categorias_validas = market_data_service.get_categorias()["categorias"]
    if categoria not in categorias_validas:
        logger.warning(f"Categoria inválida: {categoria}")
        return {"message": "Categoria inválida", "data": []}

    # Chamar serviço com argumentos corretos
    response = market_data_service.get_trending(
        categoria=categoria,
        setor=setor,
        limit=limit,
        offset=offset,
        sort_field=sort_field,
        sort_asc=sort_asc
    )
    logger.info(f"Obtendo tickers para a categoria: {categoria}, ordenando por {sort_field}, ascendente: {sort_asc}")
    if not response or not response.get("resultados"):
        logger.warning(f"Nenhum ticker encontrado para a categoria: {categoria}")
        return {"message": "Nenhum ticker encontrado", "data": []}
    return response


# ==================== ENDPOINT DE BUSCA-PERSONALIZADA ====================

@router.get("/busca-personalizada")
def search_tickers( min_price: float = None, max_price: float = None, 
                   min_volume: int = None, min_market_cap: float = None, max_pe: float = None, 
                   min_dividend_yield: float = None, setor: str = None, limit: int = 20):
    # Verifica se pelo menos um filtro foi fornecido
    if all(
        x is None for x in [min_price, max_price, min_volume, min_market_cap, max_pe, min_dividend_yield, setor]
    ):
        logger.warning("Busca personalizada requer pelo menos um filtro além do mercado padrão.")
        return {"message": "Forneça pelo menos um filtro para busca personalizada.", "data": []}

    response = market_data_service.get_custom_search(
        min_price, max_price, min_volume, min_market_cap, max_pe, min_dividend_yield, setor, limit
    )
    logger.info(f"Realizando busca personalizada com filtros: "
                f"min_price={min_price}, max_price={max_price}, ")
    if not response:
        logger.warning(f"Nenhum ticker encontrado para a busca personalizada.")
        return {"message": "Nenhum ticker encontrado", "data": []}
    return response


# ==================== ENDPOINT MARKET-OVERVIEW ====================


@router.get("/market-overview/{category}",
    summary="Visão geral do mercado por categoria",
    description="""
Retorna uma visão geral do mercado para a categoria selecionada.

Categorias disponíveis:
- **all**: Todos os mercados
- **brasil**: IBOV, SMLL, SELIC, IFIX, PETR4, VALE3, ITUB4
- **eua**: SPX, IXIC, DJI, VIX, RUT
- **europa**: STOXX, DAX, FTSE, CAC40, EURO STOXX 50
- **asia**: Nikkei, SSE Composite, Hang Seng, Nifty 50, Sensex
- **moedas**: USD/BRL, EUR/BRL, GBP/BRL, JPY/BRL, AUD/BRL
""")
def get_market_overview(category: str):
    response = market_data_service.get_market_overview(category)
    logger.info(f"Obtendo visão geral do mercado para a categoria: {category}")
    if not response:
        logger.warning(f"Nenhuma visão geral encontrada para a categoria: {category}")
        return {"message": "Nenhuma visão geral encontrada", "data": []}
    return response

        
# ==================== ENDPOINT PERIOD-PERFORMANCE ====================   
     
@router.get("/period-performance",
        summary="Tabela de variação de ativos por período",
        description="""
    Retorna a performance de múltiplos ativos em diferentes períodos de tempo.

    **Períodos calculados:**
    - 1D: Variação de 1 dia
    - 7D: Variação de 7 dias
    - 1M: Variação de 1 mês
    - 3M: Variação de 3 meses
    - 6M: Variação de 6 meses
    - 1Y: Variação de 1 ano

    **Exemplo de uso:**""")
def get_period_performance(tickers: str):
    response = market_data_service.get_period_performance(tickers)
    logger.info(f"Obtendo performance de períodos para os tickers: {tickers}")
    if not response:
        logger.warning(f"Nenhuma performance encontrada para os tickers: {tickers}")
        return {"message": "Nenhuma performance encontrada", "data": []}
    return response

 
        
# ==================== ENDPOINT DE HEALTH CHECK ====================

@router.get("/health")
def health_check():
    """
    Endpoint de health check - verifica se tudo está funcionando.
    
    **Para que serve:**
    - ✅ Verificar se a API está online
    - 📊 Status dos provedores de dados (Yahoo Finance)
    - 💾 Status do cache
    - ⏱️ Tempo de resposta do serviço
    
    **Exemplo de teste:**
    ```
    /health
    ```
    
    **Resposta esperada:**
    ```json
    {
        "status": "healthy",
        "timestamp": "2025-01-15T10:30:00",
        "version": "1.0.0",
        "external_services": {
            "yahoo_finance": "healthy",
            "cache": "healthy"
        }
    }
    ```
    
    **Status possíveis:**
    - "healthy" = Tudo funcionando ✅
    - "degraded" = Funcionando com problemas ⚠️
    - "unhealthy" = Com falhas ❌
    
    **Dica:** Chame este endpoint primeiro se algo não estiver funcionando!
    """
    health_data = market_data_service.get_service_health()

    return HealthResponse(
        status=health_data["status"],
        timestamp=health_data["timestamp"],
        version=health_data["version"],
        uptime_seconds=0.0,  # Implementar se necessário
        external_services={
            "yahoo_finance": health_data["provider_status"],
            "cache": health_data["cache_status"],
        },
    )



