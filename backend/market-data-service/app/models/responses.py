"""
Modelos de response para o Market Data Service.

Este módulo define os modelos Pydantic para estruturação de dados
de saída nas respostas da API.

Example:
    from models.responses import StockDataResponse
    
    response = StockDataResponse(
        symbol="PETR4.SA",
        company_name="Petrobras",
        current_price=25.30,
        ...
    )
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class HistoricalDataPoint(BaseModel):
    """
    Modelo para um ponto de dados históricos.
    
    Attributes:
        date: Data do ponto de dados
        open: Preço de abertura
        high: Preço máximo
        low: Preço mínimo
        close: Preço de fechamento
        volume: Volume negociado
        adj_close: Preço de fechamento ajustado
    """
    
    date: str = Field(..., description="Data no formato YYYY-MM-DD")
    open: float = Field(..., description="Preço de abertura")
    high: float = Field(..., description="Preço máximo")
    low: float = Field(..., description="Preço mínimo")
    close: float = Field(..., description="Preço de fechamento")
    volume: int = Field(..., description="Volume negociado")
    adj_close: Optional[float] = Field(
        default=None,
        description="Preço de fechamento ajustado"
    )


class FundamentalData(BaseModel):
    """
    Modelo para dados fundamentais de uma ação.
    
    Attributes:
        market_cap: Valor de mercado
        pe_ratio: Índice P/L
        dividend_yield: Dividend yield
        eps: Lucro por ação
        book_value: Valor patrimonial
        debt_to_equity: Relação dívida/patrimônio
        roe: Return on Equity
        roa: Return on Assets
        sector: Setor da empresa
        industry: Indústria da empresa
    """
    
    market_cap: Optional[float] = Field(default=None, description="Valor de mercado")
    pe_ratio: Optional[float] = Field(default=None, description="Índice P/L")
    dividend_yield: Optional[float] = Field(default=None, description="Dividend yield")
    eps: Optional[float] = Field(default=None, description="Lucro por ação")
    book_value: Optional[float] = Field(default=None, description="Valor patrimonial")
    debt_to_equity: Optional[float] = Field(
        default=None,
        description="Relação dívida/patrimônio"
    )
    roe: Optional[float] = Field(default=None, description="Return on Equity")
    roa: Optional[float] = Field(default=None, description="Return on Assets")
    sector: Optional[str] = Field(default=None, description="Setor da empresa")
    industry: Optional[str] = Field(default=None, description="Indústria da empresa")
    fifty_two_week_high: Optional[float] = Field(
        default=None,
        description="Máxima de 52 semanas"
    )
    fifty_two_week_low: Optional[float] = Field(
        default=None,
        description="Mínima de 52 semanas"
    )


class StockDataResponse(BaseModel):
    """
    Modelo de resposta para dados de uma ação específica.
    
    Attributes:
        symbol: Símbolo da ação
        company_name: Nome da empresa
        current_price: Preço atual
        previous_close: Preço de fechamento anterior
        change: Variação absoluta
        change_percent: Variação percentual
        volume: Volume atual
        avg_volume: Volume médio
        currency: Moeda de negociação
        timezone: Fuso horário
        last_updated: Timestamp da última atualização
        fundamentals: Dados fundamentais (opcional)
        historical_data: Dados históricos (opcional)
        metadata: Metadados adicionais
    """
    
    symbol: str = Field(..., description="Símbolo da ação")
    company_name: Optional[str] = Field(default=None, description="Nome da empresa")
    current_price: Optional[float] = Field(default=None, description="Preço atual")
    previous_close: Optional[float] = Field(
        default=None,
        description="Preço de fechamento anterior"
    )
    change: Optional[float] = Field(default=None, description="Variação absoluta")
    change_percent: Optional[float] = Field(
        default=None,
        description="Variação percentual"
    )
    volume: Optional[int] = Field(default=None, description="Volume atual")
    avg_volume: Optional[int] = Field(default=None, description="Volume médio")
    currency: Optional[str] = Field(default=None, description="Moeda de negociação")
    timezone: Optional[str] = Field(default=None, description="Fuso horário")
    last_updated: str = Field(..., description="Timestamp da última atualização")
    sector: Optional[str] = Field(default=None, description="Setor da empresa")
    type: Optional[str] = Field(default=None, description="Tipo do ativo (Ação, BDR, Outro)")
    fundamentals: Optional[FundamentalData] = Field(
        default=None,
        description="Dados fundamentais"
    )
    historical_data: Optional[List[HistoricalDataPoint]] = Field(
        default=None,
        description="Dados históricos"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Metadados adicionais"
    )


class SearchResultItem(BaseModel):
    """
    Modelo para um item nos resultados de busca.
    
    Attributes:
        symbol: Símbolo da ação
        name: Nome da empresa
        sector: Setor
        market: Mercado
        current_price: Preço atual (opcional)
        currency: Moeda
        relevance_score: Score de relevância da busca
    """
    
    symbol: str = Field(..., description="Símbolo da ação")
    name: str = Field(..., description="Nome da empresa")
    sector: Optional[str] = Field(default=None, description="Setor")
    market: Optional[str] = Field(default=None, description="Mercado")
    current_price: Optional[float] = Field(default=None, description="Preço atual")
    currency: Optional[str] = Field(default=None, description="Moeda")
    relevance_score: Optional[float] = Field(
        default=None,
        description="Score de relevância"
    )


class SearchResponse(BaseModel):
    """
    Modelo de resposta para busca de tickers.
    
    Attributes:
        query: Termo de busca utilizado
        results_found: Número de resultados encontrados
        total_results: Número total de resultados disponíveis
        results: Lista de resultados
        filters_applied: Filtros aplicados na busca
        search_time_ms: Tempo de execução da busca em milissegundos
    """
    
    query: str = Field(..., description="Termo de busca utilizado")
    results_found: int = Field(..., description="Número de resultados encontrados")
    total_results: Optional[int] = Field(
        default=None,
        description="Número total de resultados disponíveis"
    )
    results: List[SearchResultItem] = Field(..., description="Lista de resultados")
    filters_applied: Optional[Dict[str, str]] = Field(
        default=None,
        description="Filtros aplicados"
    )
    search_time_ms: Optional[float] = Field(
        default=None,
        description="Tempo de execução em ms"
    )


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
        description="Dados organizados por ticker"
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


class ValidationResponse(BaseModel):
    """
    Modelo de resposta para validação de ticker.
    
    Attributes:
        symbol: Símbolo validado
        is_valid: Se o ticker é válido
        exists: Se o ticker existe
        market: Mercado do ticker
        tradeable: Se o ticker é negociável
        last_trade_date: Data da última negociação
        validation_time: Timestamp da validação
        error_message: Mensagem de erro (se houver)
        suggestions: Sugestões de tickers similares
    """
    
    symbol: str = Field(..., description="Símbolo validado")
    is_valid: bool = Field(..., description="Se o ticker é válido")
    exists: bool = Field(..., description="Se o ticker existe")
    market: Optional[str] = Field(default=None, description="Mercado do ticker")
    tradeable: Optional[bool] = Field(default=None, description="Se é negociável")
    last_trade_date: Optional[str] = Field(
        default=None,
        description="Data da última negociação"
    )
    validation_time: str = Field(..., description="Timestamp da validação")
    error_message: Optional[str] = Field(
        default=None,
        description="Mensagem de erro"
    )
    suggestions: Optional[List[str]] = Field(
        default=None,
        description="Sugestões de tickers similares"
    )


class HealthResponse(BaseModel):
    """
    Modelo de resposta para health check.
    
    Attributes:
        status: Status geral do serviço
        timestamp: Timestamp da verificação
        version: Versão da API
        uptime_seconds: Tempo de atividade em segundos
        external_services: Status dos serviços externos
        cache_status: Status do cache
        memory_usage: Uso de memória
    """
    
    status: str = Field(..., description="Status geral do serviço")
    timestamp: str = Field(..., description="Timestamp da verificação")
    version: str = Field(..., description="Versão da API")
    uptime_seconds: float = Field(..., description="Tempo de atividade")
    external_services: Optional[Dict[str, str]] = Field(
        default=None,
        description="Status dos serviços externos"
    )
    cache_status: Optional[str] = Field(default=None, description="Status do cache")
    memory_usage: Optional[Dict[str, float]] = Field(
        default=None,
        description="Uso de memória"
    )


class ErrorResponse(BaseModel):
    """
    Modelo padrão para respostas de erro.
    
    Attributes:
        error: Tipo do erro
        message: Mensagem descritiva do erro
        details: Detalhes adicionais do erro
        timestamp: Timestamp do erro
        request_id: ID da requisição (se disponível)
    """
    
    error: str = Field(..., description="Tipo do erro")
    message: str = Field(..., description="Mensagem descritiva")
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Detalhes adicionais"
    )
    timestamp: str = Field(..., description="Timestamp do erro")
    request_id: Optional[str] = Field(default=None, description="ID da requisição")
