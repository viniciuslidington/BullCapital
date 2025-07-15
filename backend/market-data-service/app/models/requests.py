"""
Modelos de request simplificados para o Market Data Service.

Versão ultra-simplificada focada na facilidade de uso.
Removidos args, kwargs e validações complexas.
"""

from typing import List
from pydantic import BaseModel


class StockRequest(BaseModel):
    """Requisição simples para dados de ação."""
    symbol: str
    period: str = "1mo"


class SearchRequest(BaseModel):
    """Requisição simples para busca de ações."""
    query: str
    limit: int = 10


class BulkRequest(BaseModel):
    """Requisição simples para múltiplas ações."""
    symbols: List[str]
    period: str = "1mo"


# Aliases para compatibilidade
StockDataRequest = StockRequest
BulkDataRequest = BulkRequest
AdvancedSearchRequest = SearchRequest
TickerValidationRequest = StockRequest
