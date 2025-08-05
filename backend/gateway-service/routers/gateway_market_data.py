from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel
import httpx
from typing import List, Optional

from models.responses.market_data_response import (StockDataResponse, StockSearchResponse,
SearchResult, TredingDataResponse, BulkDataResponse, HistoricalDataPoint, ValidationResponse)

router = APIRouter()

MARKET_DATA_SERVICE_URL = "http://market-data-service:8002"  # URL do serviço de Market Data, deve ser configurado corretamente


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
async def get_multiple_tickers_history(tickers: str, period: str = "1mo", interval: str = "1d", start: str = "2020-01-01", end: str = "2025-01-01", PrePost: bool = False, autoAdjust: bool = True):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{MARKET_DATA_SERVICE_URL}/api/v1/market-data/multi-history",
                params={
                    "tickers": tickers,
                    "period": period,
                    "interval": interval,
                    "start": start,
                    "end": end,
                    "PrePost": PrePost,
                    "autoAdjust": autoAdjust
                }
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
        
@router.get("/{symbol}/history")
async def get_ticker_history(symbol: str, period: str = "1mo", interval: str = "1d", start: str = "2020-01-01", end: str = "2025-01-01", PrePost: bool = False, autoAdjust: bool = True):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{MARKET_DATA_SERVICE_URL}/api/v1/market-data/{symbol}/history",
                params={
                    "period": period,
                    "interval": interval,
                    "start": start,
                    "end": end,
                    "PrePost": PrePost,
                    "autoAdjust": autoAdjust
                }
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


# ==================== ENDPOINTS DE INFO COMPLETAS ====================

@router.get("/{symbol}/fulldata")
async def get_ticker_full_data(symbol: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{MARKET_DATA_SERVICE_URL}/api/v1/market-data/{symbol}/fulldata"
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

# ==================== ENDPOINT DE INFO ESSENCIAIS ====================

@router.get("/{symbol}/info")
async def get_ticker_info(symbol: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{MARKET_DATA_SERVICE_URL}/api/v1/market-data/{symbol}/info"
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
async def search_tickers(
    query: str = Query(..., description="Termo de busca para tickers ou empresas"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de resultados a serem retornados")
):
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
async def lookup_instruments(
    query: str,
    tipo: str = "all",
    limit: int = 10
):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{MARKET_DATA_SERVICE_URL}/api/v1/market-data/lookup",
                params={"q": query, "tipo": tipo, "limit": limit}
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


@router.get("/{symbol}/dividends",
            description="Obter dividendos de um ticker específico")

async def get_ticker_dividends(symbol: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{MARKET_DATA_SERVICE_URL}/api/v1/market-data/{symbol}/dividends"
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


# ==================== ENDPOINT DE RECOMENDAÇÕES ====================

@router.get("/{symbol}/recommendations")
async def get_ticker_recommendations(symbol: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{MARKET_DATA_SERVICE_URL}/api/v1/market-data/{symbol}/recommendations"
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

# ==================== ENDPOINT DE CALENDARIO ====================

@router.get("/{symbol}/calendar")
async def get_ticker_calendar(symbol: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{MARKET_DATA_SERVICE_URL}/api/v1/market-data/{symbol}/calendar"
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


# ==================== ENDPOINT DE NEWS ====================

@router.get("/{symbol}/news")
async def get_ticker_news(symbol: str, limit: int = 10):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{MARKET_DATA_SERVICE_URL}/api/v1/market-data/{symbol}/news",
                params={"limit": limit}
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

# ==================== ENDPOINT DE TRENDING ====================


@router.get("/categorias")
async def get_tickers_categories():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{MARKET_DATA_SERVICE_URL}/api/v1/market-data/categorias"
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
async def get_tickers_by_category(categoria: str, setor: Optional[str] = None, sort: Optional[str] = None, asc: bool = False):
    async with httpx.AsyncClient() as client:
        try:
            params = {"categoria": categoria}
            if setor:
                params["setor"] = setor
            if sort:
                params["sort"] = sort
                params["asc"] = str(asc).lower()
            response = await client.get(
                f"{MARKET_DATA_SERVICE_URL}/api/v1/market-data/categorias/{categoria}",
                params=params
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

# ==================== ENDPOINT DE BUSCA-PERSONALIZADA ====================

@router.get("/busca-personalizada")
async def get_custom_search(
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_market_cap: Optional[float] = None,
    max_market_cap: Optional[float] = None,
    min_pe_ratio: Optional[float] = None,
    max_pe_ratio: Optional[float] = None,
    min_dividend_yield: Optional[float] = None,
    max_dividend_yield: Optional[float] = None,
    limit: int = 10
):
    async with httpx.AsyncClient() as client:
        try:
            params = {
                "min_price": min_price,
                "max_price": max_price,
                "min_market_cap": min_market_cap,
                "max_market_cap": max_market_cap,
                "min_pe_ratio": min_pe_ratio,
                "max_pe_ratio": max_pe_ratio,
                "min_dividend_yield": min_dividend_yield,
                "max_dividend_yield": max_dividend_yield,
                "limit": limit
            }
            response = await client.get(
                f"{MARKET_DATA_SERVICE_URL}/api/v1/market-data/busca-personalizada",
                params=params
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
async def get_market_overview(category: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{MARKET_DATA_SERVICE_URL}/api/v1/market-data/market-overview/{category}"
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
async def get_period_performance(
    tickers: str = Query(..., description="Lista de tickers separados por vírgula (ex: AAPL,MSFT,GOOGL)"),
    period: str = Query("1d", description="Período para o qual os dados devem ser retornados, ex: '1d', '7d', '1m', '3m', '6m', '1y'")
):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{MARKET_DATA_SERVICE_URL}/api/v1/market-data/period-performance",
                params={"tickers": tickers, "period": period}
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

 
        
# ==================== ENDPOINT DE HEALTH CHECK ====================

@router.get("/health")
async def health_check():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{MARKET_DATA_SERVICE_URL}/api/v1/market-data/health"
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


