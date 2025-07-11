from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional
from orchestrator.tickerOrchestrator import pipeline
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/b3/data", summary="Obter dados de ações da B3")
def get_b3_market_data(
    start_date: Optional[str] = Query(None, description="Data de início (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Data de fim (YYYY-MM-DD)"),
    period: Optional[str] = Query(None, description="Período (ex: '1mo', '1y')"),
    interval: Optional[str] = Query('1d', description="Intervalo (ex: '1d', '1wk')")
):
    """
    Endpoint para obter dados de ações da B3.
    
    Executa a pipeline de processamento e retorna os dados formatados.
    
    **Parâmetros:**
    - **start_date**: Data de início no formato YYYY-MM-DD
    - **end_date**: Data de fim no formato YYYY-MM-DD  
    - **period**: Período alternativo (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
    - **interval**: Intervalo dos dados (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
    
    **Nota:** Use start_date/end_date OU period, não ambos.
    """
    try:
        # Executar a pipeline com os parâmetros fornecidos
        df = pipeline()
        
        if df is None or df.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nenhum dado encontrado para os parâmetros fornecidos"
            )
        
        # Converter DataFrame para dict para serialização JSON
        data = df.to_dict('records')
        
        return {
            "data": data,
            "total_records": len(data),
            "parameters": {
                "start_date": start_date,
                "end_date": end_date,
                "period": period,
                "interval": interval
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar dados: {str(e)}"
        )

@router.get("/health", summary="Health Check do serviço de dados")
def market_data_health():
    """
    Verificação de saúde do serviço de dados de mercado.
    """
    return {
        "service": "market_data",
        "status": "healthy",
        "version": "1.0.0"
    }

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
