
from deep_translator import GoogleTranslator
from datetime import datetime
from typing import List, Optional
import yfinance as yf
from yfinance import EquityQuery
import pandas as pd
import numpy as np
from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel, Field

from core.logging import get_logger

# Configurar logger
logger = get_logger(__name__)

# Criar router
router = APIRouter(prefix="/api/v1/frontend", tags=["API YFinance Personalizada para o FrontEnd"])


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
    period: str = Field(default="1mo", description="Período: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max")
    interval: str = Field(default="1d", description="Intervalo: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo")
    start: Optional[str] = Field(default=None, description="Data início (YYYY-MM-DD)")
    end: Optional[str] = Field(default=None, description="Data fim (YYYY-MM-DD)")
    prepost: bool = Field(default=False, description="Incluir pre/post market")
    auto_adjust: bool = Field(default=True, description="Ajustar dividendos/splits")
    repair: bool = Field(default=False, description="Reparar dados inválidos")

class MultiTickerRequest(BaseModel):
    """Modelo para requisições de múltiplos tickers"""
    symbols: List[str] = Field(..., description="Lista de símbolos")
    period: str = Field(default="1mo", description="Período")
    interval: str = Field(default="1d", description="Intervalo")


# ==================== UTILITÁRIOS ====================

def safe_ticker_operation(symbol: str, operation):
    """Executa operação no ticker com tratamento de erro"""
    try:
        ticker = yf.Ticker(symbol.upper())
        result = operation(ticker)
        return result
    except Exception as e:
        logger.error(f"Erro ao obter dados para {symbol}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Erro ao obter dados para {symbol}: {str(e)}")

def convert_to_serializable(data):
    """Converte dados pandas/numpy para formato serializável"""
    if isinstance(data, pd.DataFrame):
        return data.fillna(0).to_dict(orient='records')
    elif isinstance(data, pd.Series):
        return data.fillna(0).to_dict()
    elif isinstance(data, np.ndarray):
        return data.tolist()
    elif isinstance(data, (np.integer, np.floating)):
        return float(data)
    elif isinstance(data, (int, float, str, bool, list, dict)):
        return data
    elif data is None or (hasattr(data, '__len__') and len(data) == 0):
        return None
    else:
        # Para valores únicos, verifica se é NaN
        try:
            if pd.isna(data):
                return None
        except (ValueError, TypeError):
            pass
        return str(data)  # Converte para string como fallback


# ==================== ENDPOINTS DE DADOS HISTÓRICOS ====================
@router.get("/multi-info")
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
    try:
        # Limpa e valida os símbolos
        symbol_list = [s.strip().upper() for s in symbols.split(',') if s.strip()]
        if not symbol_list:
            raise HTTPException(
                status_code=400,
                detail="Nenhum símbolo válido fornecido"
            )

        result = {}
        # Processa cada símbolo individualmente
        for symbol in symbol_list:
            try:
                def get_info(ticker):
                    info = ticker.info
                    return {
                        "symbol": symbol,
                        "name": str(info.get("shortName", "") or info.get("longName", "")),
                        "sector": str(info.get("sector", "")),
                        "price": float(info.get("regularMarketPrice", 0) or 0),
                        "change": float(info.get("regularMarketChangePercent", 0) or 0),
                        "volume": int(info.get("regularMarketVolume", 0) or 0),
                        "market_cap": float(info.get("marketCap", 0) or 0),
                        "pe_ratio": float(info.get("trailingPE", 0) or 0),
                        "dividend_yield": float(info.get("dividendYield", 0) or 0),
                        "beta": float(info.get("beta", 0) or 0),
                        "fiftyTwoWeekChangePercent": float(info.get("fiftyTwoWeekChangePercent", 0)or 0),
                        "avg_volume_3m": int(info.get("averageDailyVolume3Month", 0) or 0),
                        "returnOnEquity": float(info.get("returnOnEquity", 0) or 0),
                        "book_value": float(info.get("bookValue", 0) or 0),
                        "exchange": str(info.get("exchange", "")),
                        "fullExchangeName": str(info.get("fullExchangeName", "")),
                        "currency": str(info.get("currency", "")),
                        "website": str(info.get("website", "")),
                    }

                ticker_info = safe_ticker_operation(symbol, get_info)
                result[symbol] = {
                    "success": True,
                    "data": ticker_info
                }

            except Exception as e:
                logger.error(f"Erro ao obter dados para {symbol}: {str(e)}")
                result[symbol] = {
                    "success": False,
                    "error": str(e),
                    "data": None
                }

        return {
            "symbols": symbol_list,
            "timestamp": datetime.now().isoformat(),
            "results": result
        }

    except Exception as e:
        logger.error(f"Erro ao obter informações múltiplas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter informações dos tickers: {str(e)}"
        )

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
    try:
        # Limpa e valida os símbolos
        symbol_list = [s.strip().upper() for s in symbols.split(',') if s.strip()]
        if not symbol_list:
            raise HTTPException(
                status_code=400,
                detail="Nenhum símbolo válido fornecido"
            )

        result = {}
        # Processa cada símbolo individualmente para garantir maior confiabilidade
        for symbol in symbol_list:
            try:
                # Usa o safe_ticker_operation que já temos
                ticker_data = safe_ticker_operation(symbol, lambda t: t.history(
                    period=period,
                    interval=interval,
                    start=start,
                    end=end,
                    prepost=prepost,
                    auto_adjust=auto_adjust
                ))

                # Processa os dados
                if isinstance(ticker_data, pd.DataFrame) and not ticker_data.empty:
                    # Converte o índice de datetime para string
                    ticker_data.index = ticker_data.index.strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Converte para o formato desejado
                    result[symbol] = {
                        "success": True,
                        "data": ticker_data.reset_index().fillna(0).to_dict(orient='records')
                    }
                else:
                    result[symbol] = {
                        "success": False,
                        "error": "Dados não encontrados",
                        "data": []
                    }
                    
            except Exception as e:
                logger.error(f"Erro ao obter dados para {symbol}: {str(e)}")
                result[symbol] = {
                    "success": False,
                    "error": str(e),
                    "data": []
                }

        return {
            "symbols": symbol_list,
            "period": period,
            "interval": interval,
            "results": result
        }

    except Exception as e:
        logger.error(f"Erro ao obter dados históricos múltiplos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter dados históricos: {str(e)}"
        )

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
    def get_history(ticker):
        return ticker.history(
            period=period,
            interval=interval,
            start=start,
            end=end,
            prepost=prepost,
            auto_adjust=auto_adjust
        )
    
    data = safe_ticker_operation(symbol, get_history)
    return {
        "symbol": symbol.upper(),
        "period": period,
        "interval": interval,
        "data": convert_to_serializable(data)
    }


# ==================== ENDPOINTS DE INFORMAÇÕES GERAIS ====================

@router.get("/{symbol}/fulldata")
async def get_ticker_fulldata (symbol: str = Path(..., description="Símbolo do ticker")):
    """
    Obtém todas informações 

    """
    def get_info(ticker):
        return ticker.info
    
    info = safe_ticker_operation(symbol, get_info)
    return {
        "symbol": symbol.upper(),
        "info": convert_to_serializable(info)
    }


@router.get("/{symbol}/info")
async def get_ticker_info(symbol: str = Path(..., description="Símbolo do ticker")):
    """
    Obtém informações principais.
    """
    def get_profile(ticker):
        info = ticker.info
        return {
        "longName": info.get("longName"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "employees": info.get("fullTimeEmployees"),
        "website": info.get("website"),
        "country": info.get("country"),
        "business_summary": GoogleTranslator(source='auto', target='pt').translate(info.get("longBusinessSummary", "Resumo não disponível"), dest='pt'),
        "fullExchangeName": info.get("fullExchangeName"),
        "type": info.get("quoteType"),
        "currency": info.get("currency"),

        "priceAndVariation": {
            "currentPrice": info.get("currentPrice"),
            "previousClose": info.get("previousClose"),
            "dayLow": info.get("dayLow"),
            "dayHigh": info.get("dayHigh"),
            "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
            "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
            "fiftyTwoWeekChangePercent": info.get("fiftyTwoWeekChangePercent"),
            "regularMarketChangePercent": info.get("regularMarketChangePercent"),
            "fiftyDayAverage": info.get("fiftyDayAverage"),
            "twoHundredDayAverage": info.get("twoHundredDayAverage")
        },

        "volumeAndLiquidity": {
            "volume": info.get("regularMarketVolume"),
            "averageVolume10days": info.get("averageVolume10days"),
            "averageDailyVolume3Month": info.get("averageDailyVolume3Month"),
            "bid": info.get("bid"),
            "ask": info.get("ask")
        },

        "riskAndMarketOpinion": {
            "beta": info.get("beta"),
            "recommendationKey": info.get("recommendationKey"),
            "recommendationMean": info.get("recommendationMean"),
            "targetHighPrice": info.get("targetHighPrice"),
            "targetLowPrice": info.get("targetLowPrice"),
            "targetMeanPrice": info.get("targetMeanPrice"),
            "numberOfAnalystOpinions": info.get("numberOfAnalystOpinions")
        },

        "valuation": {
            "marketCap": info.get("marketCap"),
            "enterpriseValue": info.get("enterpriseValue"),
            "trailingPE": info.get("trailingPE"),
            "forwardPE": info.get("forwardPE"),
            "priceToBook": info.get("priceToBook"),
            "priceToSalesTrailing12Months": info.get("priceToSalesTrailing12Months"),
            "enterpriseToRevenue": info.get("enterpriseToRevenue"),
            "enterpriseToEbitda": info.get("enterpriseToEbitda")
        },

        "rentability": {
            "returnOnEquity": info.get("returnOnEquity"),
            "returnOnAssets": info.get("returnOnAssets"),
            "profitMargins": info.get("profitMargins"),
            "grossMargins": info.get("grossMargins"),
            "operatingMargins": info.get("operatingMargins"),
            "ebitdaMargins": info.get("ebitdaMargins")
        },

        "eficiencyAndCashflow": {
            "revenuePerShare": info.get("revenuePerShare"),
            "grossProfits": info.get("grossProfits"),
            "ebitda": info.get("ebitda"),
            "operatingCashflow": info.get("operatingCashflow"),
            "freeCashflow": info.get("freeCashflow"),
            "earningsQuarterlyGrowth": info.get("earningsQuarterlyGrowth"),
            "revenueGrowth": info.get("revenueGrowth"),
            "totalRevenue": info.get("totalRevenue")
        },

        "debtAndSolvency": {
            "totalDebt": info.get("totalDebt"),
            "debtToEquity": info.get("debtToEquity"),
            "quickRatio": info.get("quickRatio"),
            "currentRatio": info.get("currentRatio")
        },

        "dividends": {
            "dividendRate": info.get("dividendRate"),
            "dividendYield": info.get("dividendYield"),
            "payoutRatio": info.get("payoutRatio"),
            "lastDividendValue": info.get("lastDividendValue"),
            "exDividendDate": info.get("exDividendDate")
        },

        "ShareholdingAndProfit": {
            "sharesOutstanding": info.get("sharesOutstanding"),
            "floatShares": info.get("floatShares"),
            "heldPercentInsiders": info.get("heldPercentInsiders"),
            "heldPercentInstitutions": info.get("heldPercentInstitutions"),
            "epsTrailingTwelveMonths": info.get("epsTrailingTwelveMonths"),
            "epsForward": info.get("epsForward"),
            "netIncomeToCommon": info.get("netIncomeToCommon")
        }
    }

    
    profile = safe_ticker_operation(symbol, get_profile)
    return {
        "symbol": symbol.upper(),
        "profile": convert_to_serializable(profile)
    }

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
        # Inicializa a busca com os parâmetros corretos
        search = yf.Search(
            query=q,
            max_results=limit,
            news_count=0,  # Não precisamos de notícias
            lists_count=0,  # Não precisamos de listas
            enable_fuzzy_query=True,  # Permite busca aproximada
            recommended=0,  # Não precisamos de recomendados
            raise_errors=True
        )

        quotes = search.quotes
        if not quotes:
            return {
                "query": q,
                "count": 0,
                "results": []
            }
        
        # Formata os resultados
        formatted_results = []
        for item in quotes:
            try:
                result = {
                    "symbol": str(item.get("symbol", "")),
                    "name": str(item.get("shortname", "") or item.get("longname", "")),
                    "exchange": str(item.get("exchange", "")),
                    "type": str(item.get("quoteType", "")),
                    "score": float(item.get("score", 0) or 0),
                    "sector": str(item.get("sector", "")),
                    "industry": str(item.get("industry", "")),
                }
                formatted_results.append(result)
            except (TypeError, ValueError) as e:
                logger.warning(f"Erro ao formatar resultado da busca: {str(e)}")
                continue
                
        # Ordena por score (relevância) descendente
        formatted_results.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "query": q,
            "count": len(formatted_results),
            "results": formatted_results
        } 
        
    except Exception as e:
        logger.error(f"Erro na busca por '{q}': {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao realizar busca: {str(e)}"
        )

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
        # Validar o tipo de lookup
        valid_types = ["all", "stock", "etf", "future", "index", "mutualfund", "currency", "cryptocurrency"]
        if type.lower() not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo inválido. Tipos válidos: {', '.join(valid_types)}"
            )

        # Realizar o lookup
        try:
            lookup = yf.Lookup(
                query=query,
                raise_errors=True
            )

            # Obter resultados baseado no tipo
            if type == "all":
                results = lookup.get_all(count=count)
            elif type == "stock":
                results = lookup.get_stock(count=count)
            elif type == "etf":
                results = lookup.get_etf(count=count)
            elif type == "future":
                results = lookup.get_future(count=count)
            elif type == "index":
                results = lookup.get_index(count=count)
            elif type == "mutualfund":
                results = lookup.get_mutualfund(count=count)
            elif type == "currency":
                results = lookup.get_currency(count=count)
            elif type == "cryptocurrency":
                results = lookup.get_cryptocurrency(count=count)
            
            # Converter DataFrame para formato serializável
            if isinstance(results, pd.DataFrame):
                results = results.fillna("").to_dict(orient='records')
            else:
                results = []
            
            return results
            # Formatar os resultados
            formatted_results = []
            for item in results:
                try:
                    result = {
                        "symbol": str(item.get("symbol", "")),
                        "name": str(item.get("shortName", "") or item.get("longName", "")),
                        "exchange": str(item.get("exchange", "")),
                        "quoteType": str(item.get("quoteType", "")),
                        "typeDisp": str(item.get("typeDisp", "")),
                        "sector": str(item.get("sector", "")),
                        "industry": str(item.get("industry", "")),
                        "exchDisp": str(item.get("exchDisp", "")),
                        "region": str(item.get("region", "")),
                        "currency": str(item.get("currency", "")),
                        "market": str(item.get("market", "")),
                        "quoteSourceName": str(item.get("quoteSourceName", "")),
                        "triggerable": bool(item.get("triggerable", False)),
                        "firstTradeDateMilliseconds": item.get("firstTradeDateMilliseconds"),
                        "priceHint": item.get("priceHint"),
                        "marketState": str(item.get("marketState", "")),
                        "tradeable": bool(item.get("tradeable", False)),
                        "regularMarketPrice": float(item.get("regularMarketPrice", 0) or 0),
                        "regularMarketTime": item.get("regularMarketTime"),
                        "regularMarketChange": float(item.get("regularMarketChange", 0) or 0),
                        "regularMarketVolume": float(item.get("regularMarketVolume", 0) or 0),
                        "regularMarketPreviousClose": float(item.get("regularMarketPreviousClose", 0) or 0),
                        "fullExchangeName": str(item.get("fullExchangeName", ""))
                    }
                    formatted_results.append(result)
                except (TypeError, ValueError) as e:
                    logger.warning(f"Erro ao formatar resultado do lookup: {str(e)}")
                    continue
            
            return {
                "query": query,
                "type": type,
                "count": len(formatted_results),
                "results": formatted_results
            }

        except Exception as e:
            logger.error(f"Erro no lookup: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao realizar lookup: {str(e)}"
            )

    except Exception as e:
        logger.error(f"Erro no endpoint lookup: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro no endpoint lookup: {str(e)}"
        )

@router.get("/{symbol}/dividends")
async def get_dividends(symbol: str = Path(..., description="Símbolo do ticker")):
    """Obtém histórico de dividendos pagos."""
    def get_dividends(ticker):
        return ticker.dividends
    
    data = safe_ticker_operation(symbol, get_dividends)
    return {
        "symbol": symbol.upper(),
        "dividends": convert_to_serializable(data)
    }



@router.get("/{symbol}/recommendations")
async def get_recommendations(symbol: str = Path(..., description="Símbolo do ticker")):
    """Obtém recomendações detalhadas de analistas."""
    def get_recommendations(ticker):
        return ticker.recommendations
    
    data = safe_ticker_operation(symbol, get_recommendations)
    return {
        "symbol": symbol.upper(),
        "recommendations": convert_to_serializable(data)
    }


@router.get("/{symbol}/calendar")
async def get_calendar(symbol: str = Path(..., description="Símbolo do ticker")):
    """Obtém calendário de eventos corporativos."""
    def get_calendar(ticker):
        return ticker.calendar
    
    data = safe_ticker_operation(symbol, get_calendar)
    return {
        "symbol": symbol.upper(),
        "calendar": convert_to_serializable(data)
    }


@router.get("/{symbol}/news")
async def get_news(symbol: str = Path(..., description="Símbolo do ticker"), 
                   num: int = Query(5, ge=1, le=20, description="Contagem de noticias")):
    """Obtém notícias relacionadas ao ticker."""
    def get_news(ticker):
        news = ticker.get_news(count=num)
        simplified_news = []
        for item in news:
            news_content = item.get('content', {})
            simplified_item = {
                "id": news_content.get('id'),
                "title": GoogleTranslator(source='auto', target='pt').translate(news_content.get('title', "Resumo não disponível"), dest='pt'),
                "date": news_content.get('pubDate'),
                "summary": GoogleTranslator(source='auto', target='pt').translate(news_content.get('summary', "Resumo não disponível"), dest='pt'),
                "url": news_content.get('canonicalUrl', {}).get('url'),
                "thumbnail": news_content.get('thumbnail', {}).get('resolutions', [{}])[0].get('url') if news_content.get('thumbnail') else None
            }
            simplified_news.append(simplified_item)
        return simplified_news
    
    data = safe_ticker_operation(symbol, get_news)
    return {
        "symbol": symbol.upper(),
        "news": convert_to_serializable(data)
    }




BR_PREDEFINED_SCREENER_QUERIES = {
    "mercado_todo": EquityQuery('and', [
        EquityQuery('is-in', ['region', 'br', 'us', 'gb', 'jp']),
        EquityQuery("gte", ["intradaymarketcap", 1000000000]),
    ]),
    "mercado_br": EquityQuery('and', [
        EquityQuery('eq', ['region', 'br']),
        EquityQuery('eq', ['exchange', 'SAO']),
    ]),
    "alta_do_dia": EquityQuery('and', [
        EquityQuery('gt', ['percentchange', 3]),
        EquityQuery('eq', ['region', 'br']),
        EquityQuery('eq', ['exchange', 'SAO']),
        EquityQuery('gte', ['intradaymarketcap', 1000000000]),
        EquityQuery('gt', ['dayvolume', 15000])
    ]),
    
    "baixa_do_dia": EquityQuery('and', [
        EquityQuery('lt', ['percentchange', -2.5]),
        EquityQuery('eq', ['region', 'br']),
        EquityQuery('eq', ['exchange', 'SAO']),
        EquityQuery('gte', ['intradaymarketcap', 1000000000]),
        EquityQuery('gt', ['dayvolume', 20000])
    ]),
    
    "mais_negociadas": EquityQuery('and', [
        EquityQuery('eq', ['region', 'br']),
        EquityQuery('eq', ['exchange', 'SAO']),
        EquityQuery('gte', ['intradaymarketcap', 1000000000]),
        EquityQuery('gt', ['dayvolume', 2000000])
    ]),
    
    "small_caps_crescimento": EquityQuery('and', [
        EquityQuery('eq', ['region', 'br']),
        EquityQuery('eq', ['exchange', 'SAO']),
        EquityQuery('lt', ['intradaymarketcap', 2000000000]),
        EquityQuery('gte', ['quarterlyrevenuegrowth.quarterly', 15])
    ]),
    
    "valor_dividendos": EquityQuery('and', [
        EquityQuery('eq', ['region', 'br']),
        EquityQuery('eq', ['exchange', 'SAO']),
        EquityQuery('gt', ['forward_dividend_yield', 5]),
        EquityQuery('gt', ['intradaymarketcap', 1000000000])
    ]),
    
    "baixo_pe": EquityQuery('and', [
        EquityQuery('eq', ['region', 'br']),
        EquityQuery('eq', ['exchange', 'SAO']),
        EquityQuery('btwn', ['peratio.lasttwelvemonths', 1, 15]),
        EquityQuery('gt', ['intradaymarketcap', 1000000000])
    ]),
    
    "alta_liquidez": EquityQuery('and', [
        EquityQuery('eq', ['region', 'br']),
        EquityQuery('eq', ['exchange', 'SAO']),
        EquityQuery('gt', ['avgdailyvol3m', 5000000]),
        EquityQuery('gt', ['intradaymarketcap', 5000000000])
    ]),
    
    "crescimento_lucros": EquityQuery('and', [
        EquityQuery('eq', ['region', 'br']),
        EquityQuery('eq', ['exchange', 'SAO']),
        EquityQuery('gt', ['epsgrowth.lasttwelvemonths', 20]),
        EquityQuery('gt', ['netincomemargin.lasttwelvemonths', 10])
    ]),
    
    "baixo_risco": EquityQuery('and', [
        EquityQuery('eq', ['region', 'br']),
        EquityQuery('eq', ['exchange', 'SAO']),
        EquityQuery('lt', ['beta', 0.8]),
        EquityQuery('gt', ['intradaymarketcap', 5000000000]),
        EquityQuery('gt', ['forward_dividend_yield', 3])
    ])
}

@router.get("/categorias")
async def listar_categorias():
    """Lista todas as categorias disponíveis para screening."""
    return {
        "categorias": list(BR_PREDEFINED_SCREENER_QUERIES.keys()),
        "descricoes": {
            "alta_do_dia": "Ações em alta no dia (>3%)",
            "baixa_do_dia": "Ações em baixa no dia (<-2.5%)",
            "mais_negociadas": "Ações mais negociadas por volume",
            "small_caps_crescimento": "Small Caps com alto crescimento",
            "valor_dividendos": "Ações pagadoras de dividendos",
            "baixo_pe": "Ações com baixo P/L",
            "alta_liquidez": "Ações de alta liquidez",
            "crescimento_lucros": "Ações com crescimento de lucros",
            "baixo_risco": "Ações de baixo risco"
        }
    }

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
        if categoria not in BR_PREDEFINED_SCREENER_QUERIES:
            raise HTTPException(
                status_code=400,
                detail=f"Categoria '{categoria}' não encontrada. Use /categorias para ver as opções disponíveis."
            )
            
        base_query = BR_PREDEFINED_SCREENER_QUERIES[categoria]
        
        # Adicionar filtro de setor se especificado
        if setor:
            query = EquityQuery('and', [
                base_query,
                EquityQuery('eq', ['sector', setor])
            ])
        else:
            query = base_query
        
        # Executar screening com try/except específico
        try:
            results = yf.screen(
                query=query,
                size=limit,
                offset=offset,
                sortField=sort_field,
                sortAsc=sort_asc
            )
        except Exception as e:
            logger.error(f"Erro no yf.screen(): {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao executar screening: {str(e)}"
            )
            
        # Extrair quotes do resultado
        if isinstance(results, dict) and 'quotes' in results:
            quotes = results['quotes']
        else:
            quotes = results if isinstance(results, (list, tuple)) else []
            
        if not quotes:
            logger.warning(f"Nenhum resultado encontrado para a categoria: {categoria}")
            return {
                "categoria": categoria,
                "resultados": [],
                "total": 0,
                "offset": offset,
                "limit": limit,
                "ordenacao": {
                    "campo": sort_field,
                    "ascendente": sort_asc
                }
            }
        
        # Processar e formatar resultados com validação
        formatted_results = []
        for item in quotes:
            if not isinstance(item, dict):
                logger.warning(f"Item inválido no resultado: {item}")
                continue
                
            try:
                formatted_results.append({
                        "symbol": str(item.get("symbol", "")),
                        "name": str(item.get("shortName", "") or item.get("longName", "")),
                        "sector": str(item.get("sector", "")),
                        "price": float(item.get("regularMarketPrice", 0) or 0),
                        "change": float(item.get("regularMarketChangePercent", 0) or 0),
                        "volume": int(item.get("regularMarketVolume", 0) or 0),
                        "market_cap": float(item.get("marketCap", 0) or 0),
                        "pe_ratio": float(item.get("trailingPE", 0) or 0),
                        "dividend_yield": float(item.get("dividendYield", 0) or 0),
                        "fiftyTwoWeekChangePercent": float(item.get("fiftyTwoWeekChangePercent", 0)or 0),
                        "avg_volume_3m": int(item.get("averageDailyVolume3Month", 0) or 0),
                        "returnOnEquity": float(item.get("returnOnEquity", 0) or 0),
                        "book_value": float(item.get("bookValue", 0) or 0),
                        "exchange": str(item.get("exchange", "")),
                        "fullExchangeName": str(item.get("fullExchangeName", "")),
                        "currency": str(item.get("currency", "")),
                        "website": str(item.get("website", "")),
                })
            except (TypeError, ValueError) as e:
                logger.warning(f"Erro ao formatar item: {str(e)}")
                continue
            
        return {
            "categoria": categoria,
            "resultados": formatted_results,
            "total": len(formatted_results),
            "total_disponivel": int(results.get("total", len(formatted_results))),
            "offset": offset,
            "limit": limit,
            "ordenacao": {
                "campo": sort_field,
                "ascendente": sort_asc
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao executar screening '{categoria}': {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao executar screening: {str(e)}"
        )


@router.get("/busca-personalizada")
async def busca_personalizada(
    min_price: Optional[float] = Query(None, description="Preço mínimo"),
    max_price: Optional[float] = Query(None, description="Preço máximo"),
    min_volume: Optional[int] = Query(None, description="Volume mínimo"),
    min_market_cap: Optional[float] = Query(None, description="Market Cap mínimo"),
    max_pe: Optional[float] = Query(None, description="P/L máximo"),
    min_dividend_yield: Optional[float] = Query(None, description="Dividend Yield mínimo"),
    setor: Optional[str] = Query(None, description="Setor específico"),
    limit: Optional[int] = Query(50, ge=1, le=100, description="Número de resultados")
):
    """
    Realiza uma busca personalizada com múltiplos critérios.
    """
    try:
        # Construir query dinamicamente
        conditions = [
            EquityQuery('eq', ['region', 'br']),
            EquityQuery('eq', ['exchange', 'SAO'])
        ]
        
        if min_price:
            conditions.append(EquityQuery('gte', ['intradayprice', min_price]))
        if max_price:
            conditions.append(EquityQuery('lte', ['intradayprice', max_price]))
        if min_volume:
            conditions.append(EquityQuery('gt', ['dayvolume', min_volume]))
        if min_market_cap:
            conditions.append(EquityQuery('gte', ['intradaymarketcap', min_market_cap]))
        if max_pe:
            conditions.append(EquityQuery('lte', ['peratio.lasttwelvemonths', max_pe]))
        if min_dividend_yield:
            conditions.append(EquityQuery('gte', ['forward_dividend_yield', min_dividend_yield]))
        if setor:
            conditions.append(EquityQuery('eq', ['sector', setor]))
            
        query = EquityQuery('and', conditions)
        
        results = yf.screen(
            query=query,
            size=limit,
            sortField="marketCap",
            sortAsc=False
        )
        
        formatted_results = []
        for item in results:
            formatted_results.append({
                "symbol": item.get("symbol"),
                "name": item.get("shortName") or item.get("longName"),
                "sector": item.get("sector"),
                "price": item.get("regularMarketPrice"),
                "change": item.get("regularMarketChangePercent"),
                "volume": item.get("regularMarketVolume"),
                "market_cap": item.get("marketCap"),
                "pe_ratio": item.get("trailingPE"),
                "dividend_yield": item.get("dividendYield")
            })
            
        return {
            "tipo": "busca_personalizada",
            "criterios": {
                "min_price": min_price,
                "max_price": max_price,
                "min_volume": min_volume,
                "min_market_cap": min_market_cap,
                "max_pe": max_pe,
                "min_dividend_yield": min_dividend_yield,
                "setor": setor
            },
            "resultados": formatted_results,
            "total": len(formatted_results)
        }
        
    except Exception as e:
        logger.error(f"Erro na busca personalizada: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro na busca personalizada: {str(e)}"
        )
    
# ==================== ENDPOINT DE HEALTH CHECK ====================

@router.get("/health")
async def yfinance_health_check():
    """Health check específico para os endpoints do yfinance."""
    try:
        # Teste simples com um ticker conhecido
        test_ticker = yf.Ticker("AAPL")
        test_info = test_ticker.info
        
        return {
            "status": "healthy",
            "service": "YFinance API",
            "timestamp": datetime.now().isoformat(),
            "test_ticker": "AAPL",
            "test_successful": bool(test_info.get("symbol"))
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"YFinance service unhealthy: {str(e)}"
        )
