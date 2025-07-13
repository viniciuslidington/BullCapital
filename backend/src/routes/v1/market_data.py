from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional
from pydantic import BaseModel
from services.ticker_service import TickerService
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

router = APIRouter()

# Instanciar o serviço de tickers
ticker_service = TickerService()

# Modelos Pydantic para requests POST
class TickerSearchRequest(BaseModel):
    query: str
    limit: int = 10
    filters: Optional[dict] = None

class MarketDataRequest(BaseModel):
    tickers: list[str]
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    period: Optional[str] = None
    interval: str = "1d"
    include_fundamentals: bool = False


@router.get("/acoes/{ticker}", summary="Obter dados de uma ação específica")
def get_acoes_data(
    ticker: str,
    start_date: Optional[str] = Query(None, description="Data de início (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Data de fim (YYYY-MM-DD)"),
    interval: Optional[str] = Query('1d', description="Intervalo (ex: '1d', '1wk')")
):
    """
    Endpoint para obter dados de uma ação específica da B3.
    
    **Parâmetros:**
    - **ticker**: O código da ação (ex: 'PETR3', 'VALE3')
    - **start_date**: Data de início no formato YYYY-MM-DD
    - **end_date**: Data de fim no formato YYYY-MM-DD  
    - **interval**: Intervalo dos dados (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
    
    **Nota:** Os dados são obtidos diretamente do Yahoo Finance.
    """
    try:
        # Obter dados da ação usando yfinance
        acao = yf.Ticker(ticker)
        
        # Definir datas padrão se não forem fornecidas
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        # Obter histórico da ação
        df = acao.history(start=start_date, end=end_date, interval=interval)
        
        if df is None or df.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nenhum dado encontrado para o ticker fornecido"
            )
        
        # Converter DataFrame para dict para serialização JSON
        data = df.reset_index().to_dict('records')
        
        return {
            "data": data,
            "total_records": len(data),
            "parameters": {
                "ticker": ticker,
                "start_date": start_date,
                "end_date": end_date,
                "interval": interval
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar dados da ação: {str(e)}"
        )

@router.get("/stock/{symbol}", summary="Obter informações de uma ação específica")
def get_stock_info(
    symbol: str,
    include_history: bool = Query(False, description="Incluir histórico de preços"),
    period: str = Query("1mo", description="Período do histórico (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)"),
    interval: str = Query("1d", description="Intervalo (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)")
):
    """
    Obtém informações detalhadas de uma ação específica.
    
    **Parâmetros:**
    - **symbol**: Símbolo da ação (ex: PETR4.SA, VALE3.SA, ITUB4.SA)
    - **include_history**: Se deve incluir histórico de preços
    - **period**: Período do histórico
    - **interval**: Intervalo dos dados
    
    **Retorna:**
    - Informações da empresa
    - Preço atual
    - Histórico (se solicitado)
    """
    try:
        # Adicionar .SA se não estiver presente (ações brasileiras)
        if not symbol.endswith('.SA') and '.' not in symbol:
            symbol = f"{symbol}.SA"
        
        ticker = yf.Ticker(symbol)
        
        # Obter informações básicas
        info = ticker.info
        
        if not info or 'symbol' not in info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ação '{symbol}' não encontrada"
            )
        
        # Dados básicos da ação
        stock_data = {
            "symbol": symbol,
            "company_name": info.get('longName', info.get('shortName', 'N/A')),
            "sector": info.get('sector', 'N/A'),
            "industry": info.get('industry', 'N/A'),
            "current_price": info.get('currentPrice', info.get('regularMarketPrice', 'N/A')),
            "previous_close": info.get('previousClose', 'N/A'),
            "market_cap": info.get('marketCap', 'N/A'),
            "pe_ratio": info.get('trailingPE', 'N/A'),
            "dividend_yield": info.get('dividendYield', 'N/A'),
            "52_week_high": info.get('fiftyTwoWeekHigh', 'N/A'),
            "52_week_low": info.get('fiftyTwoWeekLow', 'N/A'),
            "volume": info.get('volume', 'N/A'),
            "avg_volume": info.get('averageVolume', 'N/A')
        }
        
        # Incluir histórico se solicitado
        if include_history:
            try:
                hist = ticker.history(period=period, interval=interval)
                if not hist.empty:
                    # Resetar index para incluir datas
                    hist = hist.reset_index()
                    # Converter para formato JSON serializável
                    hist_data = []
                    for _, row in hist.iterrows():
                        hist_data.append({
                            "date": row['Date'].strftime('%Y-%m-%d') if hasattr(row['Date'], 'strftime') else str(row['Date']),
                            "open": round(float(row['Open']), 2),
                            "high": round(float(row['High']), 2),
                            "low": round(float(row['Low']), 2),
                            "close": round(float(row['Close']), 2),
                            "volume": int(row['Volume']) if pd.notna(row['Volume']) else 0
                        })
                    
                    stock_data["history"] = {
                        "period": period,
                        "interval": interval,
                        "data": hist_data
                    }
                else:
                    stock_data["history"] = {"message": "Nenhum dado histórico disponível"}
            except Exception as e:
                stock_data["history"] = {"error": f"Erro ao obter histórico: {str(e)}"}
        
        return stock_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao consultar ação: {str(e)}"
        )

@router.get("/stocks/search", summary="Buscar ações por nome ou símbolo")
def search_stocks(
    query: str = Query(..., description="Nome da empresa ou símbolo da ação"),
    limit: int = Query(10, description="Número máximo de resultados", ge=1, le=50)
):
    """
    Busca ações por nome da empresa ou símbolo.
    
    **Parâmetros:**
    - **query**: Termo de busca (nome da empresa ou símbolo)
    - **limit**: Número máximo de resultados (1-50)
    
    **Exemplo:**
    - /stocks/search?query=Petrobras
    - /stocks/search?query=PETR4
    """
    try:
        # Lista de ações brasileiras mais comuns para demonstração
        # Em um ambiente real, você poderia integrar com uma API de busca
        brazilian_stocks = [
            {"symbol": "PETR4.SA", "name": "Petróleo Brasileiro S.A. - Petrobras", "sector": "Energy"},
            {"symbol": "VALE3.SA", "name": "Vale S.A.", "sector": "Materials"},
            {"symbol": "ITUB4.SA", "name": "Itaú Unibanco Holding S.A.", "sector": "Financial Services"},
            {"symbol": "BBDC4.SA", "name": "Banco Bradesco S.A.", "sector": "Financial Services"},
            {"symbol": "B3SA3.SA", "name": "B3 S.A. - Brasil, Bolsa, Balcão", "sector": "Financial Services"},
            {"symbol": "MGLU3.SA", "name": "Magazine Luiza S.A.", "sector": "Consumer Cyclical"},
            {"symbol": "WEGE3.SA", "name": "WEG S.A.", "sector": "Industrials"},
            {"symbol": "ABEV3.SA", "name": "Ambev S.A.", "sector": "Consumer Staples"},
            {"symbol": "JBSS3.SA", "name": "JBS S.A.", "sector": "Consumer Staples"},
            {"symbol": "RENT3.SA", "name": "Localiza Rent a Car S.A.", "sector": "Industrials"}
        ]
        
        # Filtrar baseado na query
        query_lower = query.lower()
        results = []
        
        for stock in brazilian_stocks:
            if (query_lower in stock["name"].lower() or 
                query_lower in stock["symbol"].lower() or
                query_lower.replace('.sa', '') in stock["symbol"].lower()):
                
                # Obter preço atual
                try:
                    ticker = yf.Ticker(stock["symbol"])
                    info = ticker.info
                    current_price = info.get('currentPrice', info.get('regularMarketPrice'))
                    
                    results.append({
                        "symbol": stock["symbol"],
                        "name": stock["name"],
                        "sector": stock["sector"],
                        "current_price": current_price,
                        "currency": "BRL"
                    })
                    
                    if len(results) >= limit:
                        break
                        
                except Exception:
                    # Se não conseguir obter o preço, incluir sem preço
                    results.append({
                        "symbol": stock["symbol"],
                        "name": stock["name"],
                        "sector": stock["sector"],
                        "current_price": "N/A",
                        "currency": "BRL"
                    })
                    
                    if len(results) >= limit:
                        break
        
        return {
            "query": query,
            "results_found": len(results),
            "stocks": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro na busca: {str(e)}"
        )

@router.get("/stocks/trending", summary="Ações em tendência do mercado brasileiro")
def get_trending_stocks():
    """
    Retorna as principais ações do mercado brasileiro com suas cotações atuais.
    
    **Retorna:**
    - Top ações do Ibovespa
    - Preços atuais
    - Variação do dia
    """
    try:
        # Lista das principais ações do Ibovespa
        top_stocks = [
            "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "B3SA3.SA",
            "ABEV3.SA", "WEGE3.SA", "MGLU3.SA", "JBSS3.SA", "RENT3.SA"
        ]
        
        trending_data = []
        
        for symbol in top_stocks:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                current_price = info.get('currentPrice', info.get('regularMarketPrice'))
                previous_close = info.get('previousClose')
                
                # Calcular variação percentual
                change_percent = None
                if current_price and previous_close:
                    change_percent = round(((current_price - previous_close) / previous_close) * 100, 2)
                
                trending_data.append({
                    "symbol": symbol,
                    "name": info.get('longName', info.get('shortName', symbol)),
                    "current_price": current_price,
                    "previous_close": previous_close,
                    "change_percent": change_percent,
                    "volume": info.get('volume'),
                    "market_cap": info.get('marketCap')
                })
                
            except Exception as e:
                # Se falhar para uma ação específica, continuar com as outras
                print(f"Erro ao obter dados para {symbol}: {e}")
                continue
        
        return {
            "timestamp": datetime.now().isoformat(),
            "market": "Brasil",
            "trending_stocks": trending_data,
            "total_stocks": len(trending_data)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter ações em tendência: {str(e)}"
        )



# Novos endpoints para descoberta de tickers

@router.get("/tickers", summary="Listar todos os tickers disponíveis")
def get_tickers(
    market: Optional[str] = Query(None, description="Filtrar por mercado (B3, NASDAQ, NYSE)"),
    sector: Optional[str] = Query(None, description="Filtrar por setor")
):
    """
    Lista todos os tickers disponíveis no sistema.
    
    **Parâmetros:**
    - **market**: Filtrar por mercado específico (B3, NASDAQ, NYSE)
    - **sector**: Filtrar por setor específico
    
    **Retorna:**
    - Lista completa de tickers com informações básicas
    """
    try:
        if sector:
            tickers = ticker_service.get_tickers_by_sector(sector, market)
        else:
            tickers = ticker_service.get_all_tickers(market)
        
        return {
            "total_tickers": len(tickers),
            "filters": {
                "market": market,
                "sector": sector
            },
            "tickers": tickers
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter tickers: {str(e)}"
        )

@router.get("/tickers/search", summary="Buscar tickers por nome ou símbolo")
def search_tickers_endpoint(
    query: str = Query(..., description="Termo de busca (nome ou símbolo)"),
    limit: int = Query(10, description="Número máximo de resultados", ge=1, le=50)
):
    """
    Busca tickers por nome da empresa ou símbolo.
    
    **Parâmetros:**
    - **query**: Termo de busca
    - **limit**: Número máximo de resultados (1-50)
    
    **Exemplo:**
    - /tickers/search?query=Petrobras
    - /tickers/search?query=PETR4
    """
    try:
        results = ticker_service.search_tickers(query, limit)
        
        return {
            "query": query,
            "results_found": len(results),
            "tickers": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro na busca de tickers: {str(e)}"
        )

@router.get("/tickers/validate/{symbol}", summary="Validar um ticker específico")
def validate_ticker_endpoint(symbol: str):
    """
    Valida se um ticker existe e retorna informações básicas.
    
    **Parâmetros:**
    - **symbol**: Símbolo do ticker para validar
    
    **Retorna:**
    - Informações de validação e dados básicos do ticker
    """
    try:
        validation_result = ticker_service.validate_ticker(symbol)
        
        if not validation_result.get("valid", False):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=validation_result.get("error", "Ticker não encontrado")
            )
        
        return validation_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao validar ticker: {str(e)}"
        )

@router.get("/tickers/sectors", summary="Listar setores disponíveis")
def get_sectors(
    market: Optional[str] = Query(None, description="Filtrar por mercado (B3, NASDAQ, NYSE)")
):
    """
    Lista todos os setores disponíveis.
    
    **Parâmetros:**
    - **market**: Filtrar por mercado específico
    
    **Retorna:**
    - Lista de setores únicos disponíveis
    """
    try:
        sectors = ticker_service.get_available_sectors(market)
        
        return {
            "market_filter": market,
            "total_sectors": len(sectors),
            "sectors": sectors
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter setores: {str(e)}"
        )

@router.get("/tickers/markets", summary="Listar mercados disponíveis")
def get_markets():
    """
    Lista todos os mercados disponíveis.
    
    **Retorna:**
    - Lista de mercados únicos disponíveis
    """
    try:
        markets = ticker_service.get_available_markets()
        
        return {
            "total_markets": len(markets),
            "markets": markets
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter mercados: {str(e)}"
        )

@router.get("/tickers/{symbol}/live", summary="Obter dados em tempo real de um ticker")
def get_ticker_live_data(symbol: str):
    """
    Obtém informações completas de um ticker com dados em tempo real.
    
    **Parâmetros:**
    - **symbol**: Símbolo do ticker
    
    **Retorna:**
    - Informações completas com preços atuais e dados de mercado
    """
    try:
        live_data = ticker_service.get_ticker_with_live_data(symbol)
        
        if "error" in live_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=live_data["error"]
            )
        
        return live_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter dados em tempo real: {str(e)}"
        )

# Endpoints POST para operações mais complexas

@router.post("/tickers/search-advanced", summary="Busca avançada de tickers")
def advanced_ticker_search(request: TickerSearchRequest):
    """
    Busca avançada de tickers com filtros complexos via POST.
    
    **Body da requisição:**
    ```json
    {
        "query": "banco",
        "limit": 20,
        "filters": {
            "market": "B3",
            "sector": "Financial Services",
            "min_market_cap": 1000000000
        }
    }
    ```
    
    **Retorna:**
    - Lista de tickers com filtros aplicados
    """
    try:
        # Busca básica
        results = ticker_service.search_tickers(request.query, request.limit)
        
        # Aplicar filtros adicionais se fornecidos
        if request.filters:
            filtered_results = []
            for ticker in results:
                include = True
                
                # Filtrar por mercado
                if request.filters.get("market") and ticker.get("market") != request.filters["market"]:
                    include = False
                
                # Filtrar por setor
                if request.filters.get("sector") and request.filters["sector"].lower() not in ticker.get("sector", "").lower():
                    include = False
                
                if include:
                    # Adicionar dados em tempo real se solicitado
                    if request.filters.get("include_live_data"):
                        live_data = ticker_service.get_ticker_with_live_data(ticker["symbol"])
                        if "error" not in live_data:
                            ticker.update(live_data)
                    
                    filtered_results.append(ticker)
            
            results = filtered_results
        
        return {
            "query": request.query,
            "filters_applied": request.filters,
            "results_found": len(results),
            "tickers": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro na busca avançada: {str(e)}"
        )

@router.post("/market-data/bulk", summary="Obter dados de múltiplos tickers")
def get_bulk_market_data(request: MarketDataRequest):
    """
    Obtém dados de mercado para múltiplos tickers via POST.
    
    **Body da requisição:**
    ```json
    {
        "tickers": ["PETR4.SA", "VALE3.SA", "ITUB4.SA"],
        "start_date": "2025-01-01",
        "end_date": "2025-07-10",
        "interval": "1d",
        "include_fundamentals": true
    }
    ```
    
    **Retorna:**
    - Dados de mercado para todos os tickers solicitados
    """
    try:
        results = {}
        
        for symbol in request.tickers:
            try:
                ticker = yf.Ticker(symbol)
                
                # Dados básicos
                ticker_data = {
                    "symbol": symbol,
                    "last_updated": datetime.now().isoformat()
                }
                
                # Dados históricos
                if request.start_date and request.end_date:
                    hist = ticker.history(start=request.start_date, end=request.end_date, interval=request.interval)
                elif request.period:
                    hist = ticker.history(period=request.period, interval=request.interval)
                else:
                    hist = ticker.history(period="1mo", interval=request.interval)
                
                if not hist.empty:
                    hist = hist.reset_index()
                    hist_data = []
                    for _, row in hist.iterrows():
                        hist_data.append({
                            "date": row['Date'].strftime('%Y-%m-%d') if hasattr(row['Date'], 'strftime') else str(row['Date']),
                            "open": round(float(row['Open']), 2),
                            "high": round(float(row['High']), 2),
                            "low": round(float(row['Low']), 2),
                            "close": round(float(row['Close']), 2),
                            "volume": int(row['Volume']) if pd.notna(row['Volume']) else 0
                        })
                    ticker_data["historical_data"] = hist_data
                
                # Dados fundamentais se solicitado
                if request.include_fundamentals:
                    info = ticker.info
                    ticker_data["fundamentals"] = {
                        "market_cap": info.get('marketCap'),
                        "pe_ratio": info.get('trailingPE'),
                        "dividend_yield": info.get('dividendYield'),
                        "52_week_high": info.get('fiftyTwoWeekHigh'),
                        "52_week_low": info.get('fiftyTwoWeekLow'),
                        "sector": info.get('sector'),
                        "industry": info.get('industry')
                    }
                
                results[symbol] = ticker_data
                
            except Exception as e:
                results[symbol] = {
                    "symbol": symbol,
                    "error": str(e)
                }
        
        return {
            "request_parameters": {
                "tickers": request.tickers,
                "start_date": request.start_date,
                "end_date": request.end_date,
                "period": request.period,
                "interval": request.interval,
                "include_fundamentals": request.include_fundamentals
            },
            "total_tickers": len(request.tickers),
            "successful_requests": len([r for r in results.values() if "error" not in r]),
            "data": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter dados em bulk: {str(e)}"
        )
