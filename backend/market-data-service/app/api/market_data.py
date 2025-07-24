
"""
Endpoints ULTRA-SIMPLIFICADOS do Market Data Service.

Removidos args, kwargs, validações complexas e middleware desnecessário.
Foco na simplicidade e facilidade de uso.
"""

from fastapi import APIRouter
from fastapi import Depends


from typing import List
from core.config import settings
from sqlalchemy.orm import Session
from models.database import get_db
from models.schemas import MarketData as MarketDataSchema
from models.market_data import MarketData as MarketDataORM
from core.logging import get_logger
from models.requests import BulkDataRequest, SearchRequest, StockDataRequest
from models.responses import (
    BulkDataResponse,
    HealthResponse,
    SearchResponse,
    StockDataResponse,
    ValidationResponse,
)
from services.market_data_service import MarketDataService

# Logger e router
logger = get_logger(__name__)
router = APIRouter()

# Serviço
market_data_service = MarketDataService()



@router.get(
    "/stocks/{symbol}",
    response_model=StockDataResponse,
    summary="Obter dados de uma ação",
    description="""
    Obtém dados de uma ação específica. Muito simples de usar!
    
    **Parâmetros:**
    - **symbol**: Símbolo da ação (obrigatório)
    - **period**: Período dos dados (opcional, padrão: 1mo)
    
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
    
    **Exemplos de teste:**
    ```
    /stocks/PETR4.SA                    # Petrobras, último mês
    /stocks/AAPL?period=1y             # Apple, último ano
    /stocks/VALE3.SA?period=6mo        # Vale, 6 meses
    /stocks/MSFT?period=3mo            # Microsoft, 3 meses
    /stocks/SPY?period=1d              # S&P 500 ETF, 1 dia
    ```
    
    **Dicas:**
    - Para análise rápida: use period=1mo
    - Para tendências: use period=1y
    - Para day trading: use period=1d ou 5d
    """
)
def get_stock_data(
    symbol: str,
    period: str = "1mo",
) -> StockDataResponse:
    """Endpoint ultra-simplificado para dados de ação."""
    logger.info(f"Dados para {symbol}, período {period}")
    stock_request = StockDataRequest(symbol=symbol, period=period)
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
    """
)
def search_stocks(
    q: str,
    limit: int = 10
) -> SearchResponse:
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
    """
)
def get_trending_stocks(
    market: str = "BR",
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Endpoint ultra-simplificado para trending."""
    logger.info(f"Trending para {market}")
    trending_data = market_data_service.get_trending_stocks(market, "simple-client", db=db)
    return {
        "market": market,
        "trending_stocks": trending_data[:limit]
    }


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
    """
)
def validate_ticker(symbol: str, db: Session = Depends(get_db)) -> ValidationResponse:
    """Endpoint ultra-simplificado para validação."""
    logger.info(f"Validando {symbol}")
    return market_data_service.validate_ticker(symbol, "simple-client", db=db)


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
    ```json
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
    """
)
def get_bulk_data(bulk_request: BulkDataRequest, db: Session = Depends(get_db)) -> BulkDataResponse:
    """Endpoint ultra-simplificado para dados em lote."""
    logger.info(f"Bulk para {len(bulk_request.symbols)} ações")
    return market_data_service.get_bulk_data(bulk_request, "simple-client", db=db)




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
    """
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
            "cache": health_data["cache_status"]
        }
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
    """
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
            "bulk": "POST /bulk (JSON: {symbols: [...], period: '1mo'})"
        },
        "examples": {
            "get_stock": "/stocks/PETR4.SA?period=1y",
            "search": "/search?q=petrobras&limit=5",
            "trending": "/trending?market=US&limit=15",
            "validate": "/validate/AAPL",
            "bulk": 'POST /bulk {"symbols": ["PETR4.SA", "VALE3.SA"], "period": "1mo"}'
        }
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
    """
)
def clear_cache():
    """Endpoint simples para limpar cache."""
    logger.info("Limpando cache")
    
    success = market_data_service.clear_cache()
    
    return {
        "message": "Cache limpo!" if success else "Erro ao limpar cache",
        "success": success
    }
