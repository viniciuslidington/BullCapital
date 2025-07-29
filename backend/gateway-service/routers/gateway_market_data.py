from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel
import httpx
from typing import List, Optional

from models.responses.market_data_response import StockDataResponse, StockSearchResponse, SearchResult, TredingDataResponse, BulkDataResponse, HistoricalDataPoint, ValidationResponse

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
