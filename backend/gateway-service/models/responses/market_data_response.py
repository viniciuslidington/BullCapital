from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from typing import Dict, Any


class StockDataResponse(BaseModel):
    symbol: str
    company_name: Optional[str] = None
    current_price: Optional[float] = None
    previous_close: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    volume: Optional[int] = None
    avg_volume: Optional[int] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    last_updated: str
    sector: Optional[str] = None
    type: Optional[str] = None


class SearchResult(BaseModel):
    symbol: str
    name: str
    sector: str  # Setor da ação, ex: "Technology", "Finance", etc.
    market: str  # Região do mercado, ex: "US", "BR", etc.
    current_price: float = None  # Preço atual da ação, pode ser null
    currency: Optional[str] = None  # Moeda da ação, pode ser null
    relevance_score: Optional[float] = None  # Pontuação de relevância, pode ser null


class StockSearchResponse(BaseModel):
    results: List[SearchResult]
    results_found: int
    query: str
    limit: Optional[int] = None

class TredingDataResponse(BaseModel):
    symbol: str
    company_name: str
    current_price: float
    previous_close: float
    change: Optional[float] = None  # change é null no JSON, então Optional
    change_percent: Optional[float] = None  # change_percent é null no JSON, então Optional
    volume: int
    avg_volume: Optional[int] = None  # avg_volume é null no JSON, então Optional
    currency: str
    timezone: Optional[str] = None  # timezone é null no JSON, então Optional
    last_updated: date  # Pode ser datetime.date ou datetime.datetime se você quiser parsear datas

class BulkDataResponse(BaseModel):
    """
    Modelo de resposta para dados em lote.
    
    Attributes:
        request_id: ID único da requisição
        total_tickers: Número total de tickers solicitados
        successful_requests: Número de requisições bem-sucedidas
        failed_requests: Número de requisições falhadas
        data: Dados organizados por ticker
        errors: Erros organizados por ticker
        processing_time_ms: Tempo de processamento total
        metadata: Metadados da requisição
    """
    
    request_id: str = Field(..., description="ID único da requisição")
    total_tickers: int = Field(..., description="Número total de tickers")
    successful_requests: int = Field(..., description="Requisições bem-sucedidas")
    failed_requests: int = Field(..., description="Requisições falhadas")
    data: Dict[str, StockDataResponse] = Field(
        ...,
        description="Dados organizados por ticker. Cada valor segue o modelo StockDataResponse, incluindo os campos obrigatórios: company_name, currency, last_updated, etc."
    )
    errors: Optional[Dict[str, str]] = Field(
        default=None,
        description="Erros organizados por ticker"
    )
    processing_time_ms: Optional[float] = Field(
        default=None,
        description="Tempo de processamento"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Metadados da requisição"
    )
class HistoricalDataPoint(BaseModel):
    date: date
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    adjusted_close: Optional[float] = None  # Preço ajustado de fechamento, pode ser null
    currency: Optional[str] = None  # Moeda do dado, pode ser null


class ValidationResponse(BaseModel):
    symbol: str
    is_valid: bool
    exists: bool
    market: Optional[str] = None
    tradeable: Optional[bool] = None
    last_trade_date: Optional[str] = None
    validation_time: str
    error_message: Optional[str] = None
    suggestions: Optional[List[str]] = None