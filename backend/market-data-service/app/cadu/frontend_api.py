from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional
from datetime import datetime

# Importa as funções de lógica, não o yfinance diretamente
from app.cadu import yfinance_logic as logic
from core.logging import get_logger

# Se você mover os modelos Pydantic para um arquivo separado (ex: models.py),
# importe-os daqui. Por enquanto, eles podem ser omitidos desta camada.

logger = get_logger(__name__)

# O router define o prefixo e as tags para agrupar os endpoints na documentação do Swagger/OpenAPI
router = APIRouter( tags=["API YFinance Personalizada para o FrontEnd"])


def handle_logic_errors(e: Exception, symbol: str = None):
    """Função auxiliar para tratar exceções da camada de lógica de forma consistente."""
    log_message = f"Erro na rota"
    if symbol:
        log_message += f" para o símbolo '{symbol}'"
    log_message += f": {str(e)}"

    if isinstance(e, (ValueError, KeyError)):
        logger.warning(log_message)
        raise HTTPException(status_code=404, detail=str(e))
    elif isinstance(e, ConnectionError):
        logger.error(log_message)
        raise HTTPException(status_code=503, detail=str(e)) # 503 Service Unavailable
    else:
        logger.error(log_message)
        raise HTTPException(status_code=500, detail="Ocorreu um erro interno inesperado no servidor.")


# ==================== ENDPOINTS ====================


# ==================== ENDPOINTS DE DADOS HISTÓRICOS ====================
@router.get("/multi-info", summary="Obter informações básicas de múltiplos tickers")
async def get_multiple_tickers_info(
    symbols: str = Query(..., description="Símbolos dos tickers separados por vírgula (ex: AAPL,MSFT,PETR4.SA)")
):
    """
    Obtém informações básicas para múltiplos tickers simultaneamente.
    
    Exemplo de uso:
    ```
    GET /api/v1/frontend/multi-info?symbols=PETR4.SA,VALE3.SA,ITUB4.SA
    ```
    
    Retorna informações básicas como preço, volume, market cap, etc. para cada ticker.
    """
    symbol_list = [s.strip().upper() for s in symbols.split(',') if s.strip()]
    if not symbol_list:
        raise HTTPException(status_code=400, detail="Nenhum símbolo válido fornecido.")
    if len(symbol_list) > 5:
        raise HTTPException(status_code=400, detail="Número máximo de 5 tickers permitido por requisição.")

    try:
        return logic.get_multiple_tickers_info_logic(symbol_list)

    except Exception as e:
        handle_logic_errors(e)

@router.get("/multi-history")
async def get_multiple_historical_data(
    symbols: str = Query(..., description="Símbolos dos tickers separados por vírgula (ex: AAPL,MSFT,PETR4.SA)"),
    period: str = Query("1mo", description="Período: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max"),
    interval: str = Query("1d", description="Intervalo: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo"),
    start: Optional[str] = Query(None, description="Data início (YYYY-MM-DD)"),
    end: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)"),
    prepost: bool = Query(False, description="Incluir pre/post market"),
    auto_adjust: bool = Query(True, description="Ajustar dividendos/splits"),
):
    """
    Obtém dados históricos de preços para múltiplos tickers simultaneamente.
    """
    symbol_list = [s.strip().upper() for s in symbols.split(',') if s.strip()]
    if not symbol_list:
        raise HTTPException(status_code=400, detail="Nenhum símbolo válido fornecido.")
    if len(symbol_list) > 5:
        raise HTTPException(status_code=400, detail="Número máximo de 5 tickers permitido por requisição.")

    try:
        return logic.get_multiple_historical_data_logic(symbol_list, period, interval, start, end, prepost, auto_adjust)
        
    except Exception as e:
        handle_logic_errors(e)

@router.get("/{symbol}/history")
async def get_historical_data(
    symbol: str = Path(..., description="Símbolo do ticker (ex: AAPL, PETR4.SA)"),
    period: str = Query("1mo", description="Período: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max"),
    interval: str = Query("1d", description="Intervalo: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo"),
    start: Optional[str] = Query(None, description="Data início (YYYY-MM-DD)"),
    end: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)"),
    prepost: bool = Query(False, description="Incluir pre/post market"),
    auto_adjust: bool = Query(True, description="Ajustar dividendos/splits"),
):
    """
    Obtém dados históricos de preços para um ticker.
    
    Retorna: Open, High, Low, Close, Volume, Dividends, Stock Splits
    """
    try:
        return logic.get_historical_data_logic(symbol, period, interval, start, end, prepost, auto_adjust)
    except Exception as e:
        handle_logic_errors(e, symbol)


# ==================== ENDPOINTS DE INFO COMPLETAS ====================

@router.get("/{symbol}/fulldata")
async def get_ticker_fulldata (symbol: str = Path(..., description="Símbolo do ticker")):
    """
    Obtém todas informações 

    """
    try:
        return logic.get_ticker_fulldata_logic(symbol)
    except Exception as e:
        handle_logic_errors(e, symbol)

# ==================== ENDPOINT DE INFO ESSENCIAIS ====================

@router.get("/{symbol}/info")
async def get_ticker_info(symbol: str = Path(..., description="Símbolo do ticker")):
    """
    Obtém informações principais.
    """
    try:
        return logic.get_ticker_info_logic(symbol)
    except Exception as e:
        handle_logic_errors(e, symbol)

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
    q: str = Query(..., description="Termo de busca", min_length=1),
    limit: int = Query(10, ge=1, le=50, description="Número máximo de resultados (máx: 50)")
):
    """
    Busca por tickers, empresas, setores ou países no Yahoo Finance.
    """
    try:
        return logic.search_tickers_logic(q, limit)
    except Exception as e:
        handle_logic_errors(e)

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
    query: str = Query(..., description="Termo de busca (ex: petrobras, ishares, etc)"),
    type: str = Query("all", description="Tipo do instrumento (all, stock, etf, future, index, mutualfund, currency, cryptocurrency)"),
    count: int = Query(25, ge=1, le=100, description="Número de resultados"),
):
    """
    Realiza lookup de instrumentos financeiros por tipo e query.
    """
    try:
        # Chama a função de lógica, passando os parâmetros da requisição
        results = logic.lookup_instruments_logic(
            query=query.strip(), 
            instrument_type=type, 
            count=count
        )
        return results
    except Exception as e:
        # A função auxiliar centralizada trata os erros da camada de lógica
        handle_logic_errors(e)

@router.get("/{symbol}/dividends")
async def get_dividends(symbol: str = Path(..., description="Símbolo do ticker")):
    """Obtém histórico de dividendos pagos."""
    try:
        return logic.get_dividends_logic(symbol)
    except Exception as e:
        handle_logic_errors(e, symbol)

# ==================== ENDPOINT DE RECOMENDAÇÕES ====================

@router.get("/{symbol}/recommendations")
async def get_recommendations(symbol: str = Path(..., description="Símbolo do ticker")):
    """Obtém recomendações detalhadas de analistas."""
    try:
        return logic.get_recommendations_logic(symbol)
    except Exception as e:
        handle_logic_errors(e, symbol)


# ==================== ENDPOINT DE CALENDARIO ====================

@router.get("/{symbol}/calendar")
async def get_calendar(symbol: str = Path(..., description="Símbolo do ticker")):
    """Obtém calendário de eventos corporativos."""
    try:
        return logic.get_calendar_logic(symbol)
    except Exception as e:
        handle_logic_errors(e, symbol)

# ==================== ENDPOINT DE NEWS ====================

@router.get("/{symbol}/news")
async def get_news(symbol: str = Path(..., description="Símbolo do ticker"), 
                   num: int = Query(5, ge=1, le=20, description="Contagem de noticias")):
    """Obtém notícias relacionadas ao ticker."""
    try:
        return logic.get_news_logic(symbol, num)
    except Exception as e:
        handle_logic_errors(e, symbol)


# ==================== ENDPOINT DE TRENDING ====================

@router.get("/categorias")
async def listar_categorias():
    """Lista todas as categorias disponíveis para screening."""
    return logic.list_categories_logic()

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
async def obter_trending(
    categoria: str,
    setor: Optional[str] = Query(None, description="Filtrar por setor específico (opcional)"),
    limit: Optional[int] = Query(25, ge=1, le=100, description="Número de resultados"),
    offset: Optional[int] = Query(0, ge=0, description="Offset dos resultados"),
    sort_field: Optional[str] = Query("percentchange", description="Campo para ordenação"),
    sort_asc: Optional[bool] = Query(False, description="Ordenar de forma ascendente")
):
    """
    Obtém lista de ações baseada na categoria de screening selecionada.
    """
    try:
        return logic.get_trending_logic(categoria, setor, limit, offset, sort_field, sort_asc)
    except Exception as e:
        handle_logic_errors(e)


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
async def get_market_overview(
    category: str = Path(..., description="Categoria de mercado"),
):
    """
    Obtém visão geral do mercado para uma categoria específica.
    """
    try:
        return logic.get_market_overview_logic(category.lower())
    except Exception as e:
        handle_logic_errors(e)
        
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
    symbols: str = Query(..., description="Lista de símbolos separados por vírgula (máx 5). Ex: PETR4.SA,VALE3.SA,^BVSP")
):
    symbol_list = [s.strip().upper() for s in symbols.split(',') if s.strip()]
    if not symbol_list:
        raise HTTPException(status_code=400, detail="Nenhum símbolo válido fornecido.")
    if len(symbol_list) > 5:
        raise HTTPException(status_code=400, detail="Número máximo de 5 tickers permitido por requisição.")

    try:
        performance_data = logic.get_period_performance_logic(symbol_list)
        return {
            "timestamp": datetime.now().isoformat(),
            "symbols_count": len(symbol_list),
            "results": performance_data
        }
    except Exception as e:
        handle_logic_errors(e)
        
# ==================== ENDPOINT DE HEALTH CHECK ====================

@router.get("/health")
async def yfinance_health_check():
    """Health check específico para os endpoints do yfinance."""
    try:
        return logic.yfinance_health_check_logic()
    except Exception as e:
        handle_logic_errors(e)
        

