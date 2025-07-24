from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class StockDataResponse(BaseModel):
    symbol: str
    company_name: str
    current_price: float
    previous_close: float
    change: Optional[float] = None  # change é null no JSON, então Optional
    change_percent: Optional[float] = None  # change_percent é null no JSON, então Optional
    volume: int
    avg_volume: Optional[int] = None # avg_volume é null no JSON, então Optional
    currency: str
    timezone: Optional[str] = None # timezone é null no JSON, então Optional
    last_updated: str # Pode ser datetime.date ou datetime.datetime se você quiser parsear datas


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
