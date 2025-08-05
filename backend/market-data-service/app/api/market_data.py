"""
Endpoints ULTRA-SIMPLIFICADOS do Market Data Service.

Removidos args, kwargs, validações complexas e middleware desnecessário.
Foco na simplicidade e facilidade de uso.
"""
from fastapi import APIRouter
from typing import List
from core.config import settings
from core.logging import get_logger
from models.requests import BulkDataRequest, SearchRequest, StockDataRequest

from models.responses import (
    BulkDataResponse,
    HealthResponse,
    SearchResponse,
    StockDataResponse,
    ValidationResponse,
    SearchResultItem,
    HistoricalDataPoint,
)
from services.market_data_service import MarketDataService

# Logger e router
logger = get_logger(__name__)
router = APIRouter()

# Serviço
market_data_service = MarketDataService()


@router.get(
    "/stocks-all",
    response_model=List[SearchResultItem],
    summary="Listar todos os tickers disponíveis",
    description="Retorna todos os tickers disponíveis para o frontend.",
)
def list_available_stocks() -> List[SearchResultItem]:
    tickers = market_data_service.list_available_stocks("simple-client")
    results = []
    for t in tickers:
        # Garante valores válidos para os campos obrigatórios
        t = dict(t)
        t["market"] = t.get("market") or ""
        t["current_price"] = (
            t.get("current_price") if t.get("current_price") is not None else 0.0
        )
        results.append(SearchResultItem(**t))
    return results


@router.get(
    "/stocks/{symbol}/history",
    response_model=List[HistoricalDataPoint],
    summary="Obter histórico de dados de uma ação",
    description="Retorna a série histórica de dados de uma ação específica.",
)
def get_stock_history(symbol: str, period: str = "1mo", interval: str = "1d") -> List[HistoricalDataPoint]:
    """
    Endpoint para obter o histórico de dados de uma ação.
    :param symbol: Símbolo da ação (ex: PETR4.SA, AAPL)
    :param period: Período dos dados (ex: 1mo, 1y, etc)
    :param interval: Intervalo dos dados (ex: 1d, 1h, etc)
    :return: Lista de pontos históricos de dados
    """
    logger.info(f"Obtendo histórico para {symbol}, período {period}, intervalo {interval}")
    return market_data_service.get_stock_history(
        symbol, period, interval, client_id="simple-client"
    )


@router.get(
    "/stocks/{symbol}",
    response_model=StockDataResponse,
    summary="Obter dados de uma ação",
    description="""
    Obtém dados de uma ação específica. Muito simples de usar!
    
    **Parâmetros:**
    - **symbol**: Símbolo da ação (obrigatório)
    - **period**: Período dos dados (opcional, padrão: 1mo)
    - **interval**: Intervalo dos dados (opcional, padrão: 1d)
    
    **Símbolos para testar:**
    - 🇧🇷 Brasil: PETR4.SA, VALE3.SA, ITUB4.SA, BBDC4.SA, ABEV3.SA
    - 🇺🇸 EUA: AAPL, MSFT, GOOGL, AMZN, TSLA, NVDA, META
    - 📈 ETFs: SPY, QQQ, IVV, VTI
    
    **Períodos disponíveis:**
    - 1d = 1 dia (dados intraday)
    - 5d = 5 dias (útil para análise semanal)
    - 1mo = 1 mês (padrão, boa para análise mensal)
    - 3mo = 3 meses (tendência trimestral)
    - 6mo = 6 meses (análise semestral)
    - 1y = 1 ano (tendência anual, recomendado)
    
    **Intervalos disponíveis:**
    - 1m = 1 minuto (apenas para períodos ≤ 7 dias)
    - 2m = 2 minutos (apenas para períodos ≤ 60 dias)
    - 5m = 5 minutos (apenas para períodos ≤ 60 dias)
    - 15m = 15 minutos (apenas para períodos ≤ 60 dias)
    - 30m = 30 minutos (apenas para períodos ≤ 60 dias)
    - 1h = 1 hora (apenas para períodos ≤ 730 dias)
    - 1d = 1 dia (padrão, funciona com todos os períodos)
    - 5d = 5 dias
    - 1wk = 1 semana
    - 1mo = 1 mês
    - 3mo = 3 meses
    
    **Exemplos de teste:**
    ```
    /stocks/PETR4.SA                           # Petrobras, último mês, dados diários
    /stocks/AAPL?period=1y                     # Apple, último ano, dados diários
    /stocks/VALE3.SA?period=6mo                # Vale, 6 meses, dados diários
    /stocks/MSFT?period=3mo                    # Microsoft, 3 meses, dados diários
    /stocks/SPY?period=1d&interval=1h          # S&P 500 ETF, 1 dia, dados por hora
    /stocks/AAPL?period=1y&interval=1h         # Apple, último ano, dados por hora
    /stocks/PETR4.SA?period=7d&interval=15m    # Petrobras, 7 dias, dados de 15 min
    /stocks/TSLA?period=1mo&interval=1d        # Tesla, 1 mês, dados diários
    /stocks/NVDA?period=5d&interval=5m         # Nvidia, 5 dias, dados de 5 min
    ```
    
    **Dicas:**
    - Para análise rápida: use period=1mo
    - Para tendências: use period=1y
    - Para day trading: use period=1d ou 5d
    """,
)
def get_stock_data(
    symbol: str,
    period: str = "1mo",
    interval: str = "1d",
) -> StockDataResponse:
    """Endpoint ultra-simplificado para dados de ação com suporte a intervalos."""
    logger.info(f"Dados para {symbol}, período {period}, intervalo {interval}")
    stock_request = StockDataRequest(symbol=symbol, period=period, interval=interval)
    return market_data_service.get_stock_data(symbol, stock_request, "simple-client")


@router.get(
    "/search",
    response_model=SearchResponse,
    summary="Buscar ações",
    description="""
    Busca ações por nome ou símbolo. Muito simples!
    
    **Parâmetros:**
    - **q**: Termo de busca (obrigatório)
    - **limit**: Máximo de resultados (opcional, padrão: 10, máx: 50)
    
    **Termos para testar:**
    - 🏢 Por empresa: "petrobras", "vale", "apple", "microsoft", "google"
    - 🏦 Por setor: "banco", "energia", "tecnologia", "mineração"
    - 📊 Por símbolo: "PETR", "VALE", "AAPL", "MSFT", "GOOGL"
    - 🌎 Por país: "brazil", "usa", "american"
    
    **Limites recomendados:**
    - limit=5: Busca rápida, resultados principais
    - limit=10: Padrão, bom equilíbrio
    - limit=20: Busca ampla
    - limit=50: Máximo permitido
    
    **Exemplos de teste:**
    ```
    /search?q=petrobras                 # Busca por Petrobras
    /search?q=banco&limit=15           # Top 15 bancos
    /search?q=AAPL                     # Apple por símbolo
    /search?q=tecnologia&limit=20      # 20 empresas de tech
    /search?q=energia&limit=10         # Setor energético
    /search?q=PETR&limit=5             # Símbolos começando com PETR
    ```
    
    **Dicas:**
    - Use nomes em português para empresas BR
    - Use nomes em inglês para empresas US
    - Símbolos parciais também funcionam
    - Quanto menor o limit, mais rápida a resposta
    """,
)
def search_stocks(q: str, limit: int = 10) -> SearchResponse:
    """Endpoint ultra-simplificado para busca."""
    logger.info(f"Busca por: {q}")
    search_request = SearchRequest(query=q, limit=limit)
    return market_data_service.search_stocks(search_request, "simple-client")


@router.get(
    "/trending",
    summary="Ações em tendência",
    description="""
    Retorna ações em tendência. Super simples!
    
    **Parâmetros:**
    - **market**: Mercado (opcional, padrão: BR)
    - **limit**: Número de ações (opcional, padrão: 10, máx: 30)
    
    **Mercados disponíveis:**
    - "BR" = Brasil 🇧🇷 (Bovespa - ações .SA)
    - "US" = Estados Unidos 🇺🇸 (NYSE, NASDAQ)
    
    **Limites recomendados:**
    - limit=5: Top 5 ações mais quentes
    - limit=10: Padrão, bom overview
    - limit=15: Análise ampla
    - limit=30: Máximo, visão completa do mercado
    
    **Exemplos de teste:**
    ```
    /trending                          # Top 10 Brasil
    /trending?market=BR               # Top 10 Brasil (explícito)
    /trending?market=US               # Top 10 EUA
    /trending?market=BR&limit=20      # Top 20 Brasil
    /trending?market=US&limit=5       # Top 5 EUA
    /trending?limit=30                # Top 30 Brasil
    ```
    
    **Quando usar:**
    - 🌅 Manhã: Ver abertura do mercado
    - 🌆 Tarde: Acompanhar movimentações
    - 📊 Análise: Identificar oportunidades
    - 🔥 Day trading: Ações com volume alto
    
    **Dica:** Combine com /stocks/{symbol} para detalhes das trending!
    """,
)
def get_trending_stocks(
    market: str = "BR",
    limit: int = 10,
):
    """Endpoint ultra-simplificado para trending."""
    logger.info(f"Trending para {market}")
    try:
        trending_data = market_data_service.get_trending_stocks(market, "simple-client")
        if not trending_data:
            logger.info(f"Nenhuma ação trending encontrada para {market}.")
            return []
        return trending_data[:limit]
    except Exception as e:
        logger.error(f"Erro inesperado no endpoint /trending: {e}")
        # Retornar 200 com lista vazia em caso de erro inesperado
        return []


@router.get(
    "/validate/{symbol}",
    response_model=ValidationResponse,
    summary="Validar símbolo",
    description="""
    Valida se um símbolo de ação é válido e negociável.
    
    **Parâmetro:**
    - **symbol**: Símbolo da ação para validar
    
    **Símbolos para testar (válidos):**
    - 🇧🇷 Brasil: PETR4.SA, VALE3.SA, ITUB4.SA, BBDC4.SA, ABEV3.SA
    - 🇺🇸 EUA: AAPL, MSFT, GOOGL, AMZN, TSLA, NVDA, META, SPY
    - 📈 Criptos: BTC-USD, ETH-USD (se suportado)
    
    **Símbolos para testar (inválidos):**
    - INVALID, FAKE123, NOTREAL, TESTE.SA, XXXX
    
    **Exemplos de teste:**
    ```
    /validate/PETR4.SA                 # ✅ Petrobras (válida)
    /validate/AAPL                     # ✅ Apple (válida)
    /validate/INVALID                  # ❌ Símbolo inválido
    /validate/FAKE123                  # ❌ Não existe
    /validate/VALE3.SA                 # ✅ Vale (válida)
    /validate/SPY                      # ✅ S&P 500 ETF (válida)
    ```
    
    **Formato esperado:**
    - 🇧🇷 Brasil: CODIGO4.SA (ex: PETR4.SA, VALE3.SA)
    - 🇺🇸 EUA: CODIGO (ex: AAPL, MSFT)
    - 💱 Forex: XXX=X (ex: EURUSD=X)
    - 🪙 Crypto: XXX-USD (ex: BTC-USD)
    
    **Retorna:**
    - is_valid: true/false
    - symbol: símbolo validado
    - market: mercado (BR/US/etc)
    - exchange: bolsa (BOVESPA/NYSE/etc)
    
    **Dica:** Use antes de chamar /stocks/{symbol} para evitar erros!
    """,
)
def validate_ticker(symbol: str) -> ValidationResponse:
    """Endpoint ultra-simplificado para validação."""
    logger.info(f"Validando {symbol}")
    return market_data_service.validate_ticker(symbol, "simple-client")


@router.post(
    "/bulk",
    response_model=BulkDataResponse,
    summary="Dados de múltiplas ações",
    description="""
    Obtém dados de várias ações de uma vez. JSON super simples!
    
    **JSON de entrada:**
    ```json
    {
        "symbols": ["PETR4.SA", "VALE3.SA"],
        "period": "1mo"
    }
    ```
    
    **Campos:**
    - **symbols**: Lista de símbolos (obrigatório, máx: 20 ações)
    - **period**: Período dos dados (opcional, padrão: 1mo)
    
    **Portfolios para testar:**
    
    🇧🇷 **Top Brasil:**
    # ```json
    {
        "symbols": ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "ABEV3.SA"],
        "period": "1mo"
    }
    ```
    
    🇺🇸 **Big Tech:**
    ```json
    {
        "symbols": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"],
        "period": "1y"
    }
    ```
    
    📊 **ETFs Diversificados:**
    ```json
    {
        "symbols": ["SPY", "QQQ", "IVV", "VTI"],
        "period": "6mo"
    }
    ```
    
    🏦 **Bancos Brasil:**
    ```json
    {
        "symbols": ["ITUB4.SA", "BBDC4.SA", "SANB11.SA", "BBAS3.SA"],
        "period": "3mo"
    }
    ```
    
    ⚡ **Energia:**
    ```json
    {
        "symbols": ["PETR4.SA", "PETR3.SA", "EGIE3.SA", "ENGI11.SA"],
        "period": "1y"
    }
    ```
    
    **Períodos recomendados por caso:**
    - Análise rápida: "1mo"
    - Tendência: "1y" 
    - Comparativo: "6mo"
    - Performance: "3mo"
    
    **Limites:**
    - Máximo: 20 símbolos por requisição
    - Para mais ações: faça múltiplas requisições
    
    **Dica:** Use periods iguais para comparar performance entre ações!
    """,
)
def get_bulk_data(bulk_request: BulkDataRequest) -> BulkDataResponse:
    """Endpoint ultra-simplificado para dados em lote."""
    logger.info(f"Bulk para {len(bulk_request.symbols)} ações")
    return market_data_service.get_bulk_data(bulk_request, "simple-client")


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Verificar saúde do serviço",
    description="""
    Endpoint de health check - verifica se tudo está funcionando.
    
    **Para que serve:**
    - ✅ Verificar se a API está online
    - 📊 Status dos provedores de dados (Yahoo Finance)
    - 💾 Status do cache
    - ⏱️ Tempo de resposta do serviço
    
    **Quando usar:**
    - 🚀 Antes de usar a API (health check)
    - 🔧 Debug de problemas
    - 📈 Monitoramento de infraestrutura
    - 🔄 Deploy/CI pipelines
    
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
    """,
)
def health_check() -> HealthResponse:
    """Endpoint de health check."""
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


@router.get(
    "/",
    summary="Informações da API",
    description="""
    Informações básicas sobre a API ultra-simplificada.
    
    **Para que serve:**
    - 📋 Ver todos os endpoints disponíveis
    - 🔍 Exemplos de como usar cada endpoint
    - 📖 Links para documentação
    - ℹ️ Versão da API
    
    **Exemplo de teste:**
    ```
    /
    ```
    
    **Endpoints disponíveis:**
    1. **GET /stocks/{symbol}** - Dados de uma ação
    2. **GET /search** - Buscar ações  
    3. **GET /trending** - Ações em tendência
    4. **GET /validate/{symbol}** - Validar símbolo
    5. **POST /bulk** - Múltiplas ações
    6. **GET /health** - Health check
    7. **DELETE /cache** - Limpar cache
    
    **Fluxo recomendado:**
    1. 🔍 /health (verificar se está funcionando)
    2. 📊 /trending (ver ações em alta)
    3. ✅ /validate/{symbol} (validar antes de usar)
    4. 📈 /stocks/{symbol} (obter dados detalhados)
    
    **Dica:** Este endpoint é seu ponto de partida na API!
    """,
)
def service_info():
    """Informações da API ultra-simplificada."""
    return {
        "service": "Market Data API - Versão SUPER SIMPLES",
        "version": settings.API_VERSION,
        "description": "API ultra-simplificada para dados de ações",
        "endpoints": {
            "stock": "GET /stocks/{symbol}?period=1mo",
            "search": "GET /search?q=termo&limit=10",
            "trending": "GET /trending?market=BR&limit=10",
            "validate": "GET /validate/{symbol}",
            "bulk": "POST /bulk (JSON: {symbols: [...], period: '1mo'})",
        },
        "examples": {
            "get_stock": "/stocks/PETR4.SA?period=1y",
            "search": "/search?q=petrobras&limit=5",
            "trending": "/trending?market=US&limit=15",
            "validate": "/validate/AAPL",
            "bulk": 'POST /bulk {"symbols": ["PETR4.SA", "VALE3.SA"], "period": "1mo"}',
        },
    }


@router.delete(
    "/cache",
    summary="Limpar cache",
    description="""
    Limpa o cache do serviço para forçar atualização dos dados.
    
    **Para que serve:**
    - 🔄 Forçar atualização de dados "velhos"
    - 🐛 Resolver problemas de cache corrompido
    - 🧹 Limpeza manual do sistema
    - 🔧 Manutenção administrativa
    
    **Quando usar:**
    - Dados parecem desatualizados
    - Após mudanças no sistema
    - Debug de problemas
    - Manutenção programada
    
    **Exemplo de teste:**
    ```
    DELETE /cache
    ```
    
    **Resposta esperada:**
    ```json
    {
        "message": "Cache limpo!",
        "success": true
    }
    ```
    
    **⚠️ Atenção:**
    - Próximas requisições serão mais lentas (sem cache)
    - Cache será reconstruído automaticamente
    - Use apenas quando necessário
    
    **Dica:** Combine com /health para verificar se limpeza foi bem-sucedida!
    """,
)
def clear_cache():
    """Endpoint simples para limpar cache."""
    logger.info("Limpando cache")

    success = market_data_service.clear_cache()

    return {
        "message": "Cache limpo!" if success else "Erro ao limpar cache",
        "success": success,
    }

@router.get("/multi-info",
    summary="Obter informações de múltiplos tickers",
    description="""
    Símbolos dos tickers separados por vírgula (ex: AAPL,MSFT,PETR4.SA)
    """
)
def get_multiple_tickers_info(tickers: str):
    response = market_data_service.get_multiple_tickers_info(tickers)
    logger.info(f"Obtendo informações para múltiplos tickers: {tickers}")
    if not response:
        logger.warning(f"Nenhum ticker encontrado para: {tickers}")
        return {"message": "Nenhum ticker encontrado", "data": []}
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


