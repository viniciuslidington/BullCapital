"""
Modelos de request simplificados para o Market Data Service.

Versão ultra-simplificada focada na facilidade de uso.
Removidos args, kwargs e validações complexas.
"""

from typing import List, Optional
from pydantic import BaseModel



class StockRequest(BaseModel):
    """Requisição simples para dados de ação."""
    symbol: str
    period: str = "1mo"
    interval: str = "1d"


class SearchRequest(BaseModel):
    """Requisição simples para busca de ações."""
    query: str
    limit: int = 10


class BulkRequest(BaseModel):
    """Requisição simples para múltiplas ações."""
    symbols: List[str]
    period: str = "1mo"
    interval: str = "1d"

class TickerSymbolsRequest(BaseModel):
    """
    Model for validating the request query parameters.
    """
    symbols: List[str]

    # ==================== MODELOS PYDANTIC ====================

    class TickerInfo(BaseModel):
        """Modelo para informações básicas do ticker"""
        symbol: str
        name: str = None
        sector: str = None
        industry: str = None
        market_cap: float = None
        pe_ratio: float = None
        dividend_yield: float = None
        beta: float = None
        
    class HistoricalDataRequest(BaseModel):
        """Modelo para requisição de dados históricos"""
        period: str
        interval: str 
        start: Optional[str] 
        end: Optional[str] 
        prepost: bool 
        auto_adjust: bool
        repair: bool

    class MultiTickerRequest(BaseModel):
        """Modelo para requisições de múltiplos tickers"""
        symbols: List[str]
        period: str
        interval: str



# Aliases para compatibilidade
StockDataRequest = StockRequest
BulkDataRequest = BulkRequest
AdvancedSearchRequest = SearchRequest
TickerValidationRequest = StockRequest
