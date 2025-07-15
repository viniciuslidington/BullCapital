"""
Modelos de request para o Market Data Service.

Este módulo define os modelos Pydantic para validação de dados
de entrada nas requisições da API.

Example:
    from models.requests import StockDataRequest
    
    request = StockDataRequest(
        symbol="PETR4.SA",
        period="1mo",
        include_fundamentals=True
    )
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class StockDataRequest(BaseModel):
    """
    Modelo para requisições de dados de ação.
    
    Attributes:
        symbol (str): Símbolo da ação
        period (Optional[str]): Período dos dados
        interval (str): Intervalo dos dados
        start_date (Optional[str]): Data de início
        end_date (Optional[str]): Data de fim
        include_fundamentals (bool): Incluir dados fundamentalistas
        include_dividends (bool): Incluir dividendos
        include_splits (bool): Incluir splits
    """
    
    symbol: str = Field(..., min_length=1, description="Símbolo da ação")
    period: Optional[str] = Field(
        default="1mo",
        pattern=r"^(1d|5d|1mo|3mo|6mo|1y|2y|5y|10y|ytd|max)$",
        description="Período (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)"
    )
    interval: str = Field(
        default="1d",
        pattern=r"^(1m|2m|5m|15m|30m|60m|90m|1h|1d|5d|1wk|1mo|3mo)$",
        description="Intervalo dos dados"
    )
    start_date: Optional[str] = Field(
        None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Data de início (YYYY-MM-DD)"
    )
    end_date: Optional[str] = Field(
        None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Data de fim (YYYY-MM-DD)"
    )
    include_fundamentals: bool = Field(default=False, description="Incluir dados fundamentalistas")
    include_dividends: bool = Field(default=False, description="Incluir dividendos")
    include_splits: bool = Field(default=False, description="Incluir splits")

    @validator("start_date", "end_date")
    def validate_date_format(cls, value: Optional[str]) -> Optional[str]:
        """
        Valida o formato das datas.
        
        Args:
            value: Data em string
            
        Returns:
            Data validada ou None
            
        Raises:
            ValueError: Se a data não estiver no formato correto
        """
        if value is None:
            return value
        
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            raise ValueError("Data deve estar no formato YYYY-MM-DD")


class BulkDataRequest(BaseModel):
    """
    Modelo para requisições em lote de múltiplos tickers.
    
    Attributes:
        symbols (List[str]): Lista de símbolos
        period (Optional[str]): Período dos dados
        interval (str): Intervalo dos dados
        start_date (Optional[str]): Data de início
        end_date (Optional[str]): Data de fim
        include_fundamentals (bool): Incluir dados fundamentalistas
        max_workers (int): Número máximo de workers para processamento paralelo
    """
    
    symbols: List[str] = Field(..., min_length=1, max_length=50, description="Lista de símbolos")
    period: Optional[str] = Field(
        default="1mo",
        pattern=r"^(1d|5d|1mo|3mo|6mo|1y|2y|5y|10y|ytd|max)$",
        description="Período dos dados"
    )
    interval: str = Field(
        default="1d",
        pattern=r"^(1m|2m|5m|15m|30m|60m|90m|1h|1d|5d|1wk|1mo|3mo)$",
        description="Intervalo dos dados"
    )
    start_date: Optional[str] = Field(
        None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Data de início (YYYY-MM-DD)"
    )
    end_date: Optional[str] = Field(
        None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Data de fim (YYYY-MM-DD)"
    )
    include_fundamentals: bool = Field(default=False, description="Incluir dados fundamentalistas")
    max_workers: int = Field(default=5, ge=1, le=10, description="Workers para processamento paralelo")


class SearchRequest(BaseModel):
    """
    Modelo para requisições de busca de tickers.
    
    Attributes:
        query (str): Termo de busca (nome ou símbolo)
        limit (int): Número máximo de resultados
        sector (Optional[str]): Filtro por setor
        market (Optional[str]): Filtro por mercado
        include_crypto (bool): Incluir criptomoedas
        include_forex (bool): Incluir pares de moedas
        include_etf (bool): Incluir ETFs
    """
    
    query: str = Field(..., min_length=1, description="Termo de busca")
    limit: int = Field(default=10, ge=1, le=100, description="Número máximo de resultados")
    sector: Optional[str] = Field(None, description="Filtro por setor")
    market: Optional[str] = Field(None, description="Filtro por mercado")
    include_crypto: bool = Field(default=False, description="Incluir criptomoedas")
    include_forex: bool = Field(default=False, description="Incluir forex")
    include_etf: bool = Field(default=True, description="Incluir ETFs")


class AdvancedSearchRequest(BaseModel):
    """
    Modelo para busca avançada de tickers com filtros múltiplos.
    
    Attributes:
        query (Optional[str]): Termo de busca
        sectors (Optional[List[str]]): Lista de setores
        markets (Optional[List[str]]): Lista de mercados
        market_cap_min (Optional[float]): Capitalização mínima
        market_cap_max (Optional[float]): Capitalização máxima
        volume_min (Optional[int]): Volume mínimo
        price_min (Optional[float]): Preço mínimo
        price_max (Optional[float]): Preço máximo
        limit (int): Número máximo de resultados
        sort_by (str): Campo para ordenação
        sort_order (str): Ordem da classificação
    """
    
    query: Optional[str] = Field(None, description="Termo de busca")
    sectors: Optional[List[str]] = Field(None, description="Lista de setores")
    markets: Optional[List[str]] = Field(None, description="Lista de mercados")
    market_cap_min: Optional[float] = Field(None, ge=0, description="Capitalização mínima")
    market_cap_max: Optional[float] = Field(None, ge=0, description="Capitalização máxima")
    volume_min: Optional[int] = Field(None, ge=0, description="Volume mínimo")
    price_min: Optional[float] = Field(None, ge=0, description="Preço mínimo")
    price_max: Optional[float] = Field(None, ge=0, description="Preço máximo")
    limit: int = Field(default=20, ge=1, le=100, description="Número máximo de resultados")
    sort_by: str = Field(
        default="volume",
        pattern=r"^(symbol|name|price|volume|market_cap|sector)$",
        description="Campo para ordenação"
    )
    sort_order: str = Field(
        default="desc",
        pattern=r"^(asc|desc)$",
        description="Ordem da classificação"
    )


class TickerValidationRequest(BaseModel):
    """
    Modelo para requisição de validação de ticker.
    
    Attributes:
        symbol: Símbolo do ticker para validar
        check_market_hours: Se deve verificar horário de funcionamento do mercado
    """
    
    symbol: str = Field(..., description="Símbolo do ticker para validar")
    check_market_hours: bool = Field(
        default=False,
        description="Verificar horário de funcionamento do mercado"
    )
