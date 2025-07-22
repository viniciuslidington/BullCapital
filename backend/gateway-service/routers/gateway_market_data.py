from fastapi import APIRouter, HTTPException, Query, Body
import httpx
from typing import List, Optional

from models.responses.market_data_response import StockDataResponse  # Ensure this is a class, not a variable or instance

router = APIRouter()

MARKET_DATA_SERVICE_URL = "http://localhost:8003"  # URL do serviço de Market Data, deve ser configurado corretamente

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