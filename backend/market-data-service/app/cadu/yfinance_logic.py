from datetime import datetime
from typing import List, Optional
import yfinance as yf
from yfinance import EquityQuery
import pandas as pd
import numpy as np
from deep_translator import GoogleTranslator
from concurrent.futures import ThreadPoolExecutor

from .caching import cache_manager  # Importa o gerenciador de cache
from core.logging import get_logger

logger = get_logger(__name__)

# ==================== CONSTANTES DE LÓGICA ====================

BR_PREDEFINED_SCREENER_QUERIES = {
    "mercado_todo": EquityQuery('and', [
        EquityQuery('is-in', ['region', 'br', 'us', 'gb', 'jp']),
        EquityQuery("gte", ["intradaymarketcap", 1000000000]),
    ]),
    "mercado_br": EquityQuery('and', [
        EquityQuery('eq', ['region', 'br']),
        EquityQuery('eq', ['exchange', 'SAO']),
        EquityQuery('gte', ['intradaymarketcap', 100000000]),
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

MARKET_OVERVIEW_SYMBOLS = {
    "all": [
        "^BVSP", "SMLL.SA", "IFIX.SA", "WEGE3.SA", "PETR4.SA", "VALE3.SA", "ITUB4.SA",
        "^GSPC", "^IXIC", "^DJI", "^VIX", "^RUT",
        "^STOXX", "^GDAXI", "^FTSE", "^FCHI", "^STOXX50E",
        "^N225", "000001.SS", "^HSI", "^NSEI", "^BSESN",
        "USDBRL=X", "EURBRL=X", "GBPBRL=X", "JPYBRL=X", "AUDBRL=X"
    ],
    "brasil": ["^BVSP", "SMLL.SA", "IFIX.SA", "WEGE3.SA", "PETR4.SA", "VALE3.SA", "ITUB4.SA"],
    "eua": ["^GSPC", "^IXIC", "^DJI", "^VIX", "^RUT"],
    "europa": ["^STOXX", "^GDAXI", "^FTSE", "^FCHI", "^STOXX50E"],
    "asia": ["^N225", "000001.SS", "^HSI", "^NSEI", "^BSESN"],
    "moedas": ["USDBRL=X", "EURBRL=X", "GBPBRL=X", "JPYBRL=X", "AUDBRL=X"]
}

SYMBOL_NAMES = {
    "^BVSP": "Ibovespa", "SMLL.SA": "Small Cap", "IFIX.SA": "IND FDO IMOB", "WEGE3.SA": "WEG ON",
    "PETR4.SA": "Petrobras PN", "VALE3.SA": "Vale ON", "ITUB4.SA": "Itaú PN", "^GSPC": "S&P 500",
    "^IXIC": "Nasdaq", "^DJI": "Dow Jones", "^VIX": "VIX", "^RUT": "Russell 2000", "^STOXX": "STOXX 600",
    "^GDAXI": "DAX", "^FTSE": "FTSE 100", "^FCHI": "CAC 40", "^STOXX50E": "Euro STOXX 50",
    "^N225": "Nikkei 225", "000001.SS": "SSE Composite", "^HSI": "Hang Seng", "^NSEI": "Nifty 50",
    "^BSESN": "Sensex", "USDBRL=X": "Dólar/Real", "EURBRL=X": "Euro/Real", "GBPBRL=X": "Libra/Real",
    "JPYBRL=X": "Iene/Real", "AUDBRL=X": "Dólar Australiano/Real"
}


# ==================== UTILITÁRIOS ====================

def safe_ticker_operation(symbol: str, operation):
    """
    Executa operação no ticker com tratamento de erro e logging detalhado.
    """
    try:
        logger.debug(f"Criando objeto yf.Ticker para '{symbol}'")
        ticker = yf.Ticker(symbol.upper())

        # --- Bloco de Validação Detalhado ---
        try:
            logger.debug(f"Tentando validar o ticker '{symbol}' com history(period='1d')")
            history_df = ticker.history(period="1d")

            if history_df.empty:
                logger.warning(f"Validação falhou para '{symbol}': history() retornou um DataFrame vazio.")
                raise ValueError(f"Não foi possível obter dados para o ticker '{symbol}'. Ele pode ser inválido ou não estar mais listado.")

            logger.debug(f"Ticker '{symbol}' validado com sucesso. History retornou {len(history_df)} linha(s).")

        except Exception as validation_error:
            logger.error(f"Erro específico durante a validação de history() para '{symbol}': {validation_error}", exc_info=True)
            raise ValueError(f"Falha na validação do ticker '{symbol}': {validation_error}")
        # --- Fim do Bloco de Validação ---

        logger.debug(f"Executando a operação solicitada para o ticker '{symbol}'")
        result = operation(ticker)

        # Validação adicional do resultado
        if result is None:
            raise ValueError(f"A operação não retornou dados para o ticker '{symbol}'.")
        if isinstance(result, dict) and not result:
             raise ValueError(f"Nenhum dado encontrado para o ticker '{symbol}'.")
        if isinstance(result, pd.DataFrame) and result.empty:
             raise ValueError(f"Nenhum dado histórico encontrado para o ticker '{symbol}'.")

        return result
        
    except Exception as e:
        if isinstance(e, ValueError):
            raise e # Propaga o ValueError que já criamos
        else:
            # Encapsula exceções inesperadas em um ValueError
            logger.error(f"Erro inesperado na operação do yfinance para {symbol}: {str(e)}", exc_info=True)
            raise ValueError(f"Erro inesperado ao obter dados para {symbol}: {str(e)}")

def convert_to_serializable(data):
    """Converte dados pandas/numpy para formato serializável (lógica original)."""
    if isinstance(data, pd.DataFrame):
        if isinstance(data.index, pd.DatetimeIndex):
            data.index = data.index.strftime('%Y-%m-%d %H:%M:%S')
        return data.reset_index().fillna(0).to_dict(orient='records')
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
        try:
            if pd.isna(data):
                return None
        except (ValueError, TypeError):
            pass
        return str(data)

# ==================== LÓGICA DOS ENDPOINTS ====================

@cache_manager.cached(ttl=600)  # Cache de 10 minutos
def get_multiple_tickers_info_logic(symbol_list: List[str]):
    """Lógica para obter informações básicas para múltiplos tickers."""
    result = {}
    for symbol in symbol_list:
        try:
            def get_info(ticker):
                info = ticker.info
                logo = f"https://t1.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&size=128&url={info.get('website')}" if info.get("website") else None
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
                    "logo": logo
                }
            ticker_info = safe_ticker_operation(symbol, get_info)
            result[symbol] = {"success": True, "data": ticker_info}
        except Exception as e:
            logger.error(f"Erro ao obter dados para {symbol} em multi-info: {str(e)}")
            result[symbol] = {"success": False, "error": str(e), "data": None}
    return result

@cache_manager.cached(ttl=300) # Cache de 5 minutos
def get_multiple_historical_data_logic(symbol_list: List[str], period: str, interval: str, start: Optional[str], end: Optional[str], prepost: bool, auto_adjust: bool):
    """Lógica para obter dados históricos de preços para múltiplos tickers."""
    result = {}
    for symbol in symbol_list:
        try:
            ticker_data = safe_ticker_operation(symbol, lambda t: t.history(
                period=period, interval=interval, start=start, end=end, prepost=prepost, auto_adjust=auto_adjust
            ))
            result[symbol] = {
                "success": True,
                "data": convert_to_serializable(ticker_data)
            }
        except Exception as e:
            logger.error(f"Erro ao obter histórico para {symbol}: {str(e)}")
            result[symbol] = {"success": False, "error": str(e), "data": []}
    return result

@cache_manager.cached(ttl=300) # Cache de 5 minutos
def get_historical_data_logic(symbol: str, period: str, interval: str, start: Optional[str], end: Optional[str], prepost: bool, auto_adjust: bool):
    """Lógica para obter dados históricos de um ticker."""
    data = safe_ticker_operation(symbol, lambda t: t.history(
        period=period, interval=interval, start=start, end=end, prepost=prepost, auto_adjust=auto_adjust
    ))
    return convert_to_serializable(data)


# ==================== ENDPOINTS DE INFO COMPLETAS ====================

@cache_manager.cached(ttl=3600) # Cache de 1 hora
def get_ticker_fulldata_logic(symbol: str):
    """Lógica para obter todas as informações de um ticker."""
    info = safe_ticker_operation(symbol, lambda t: t.info)
    return convert_to_serializable(info)

# ==================== ENDPOINT DE INFO ESSENCIAIS ====================

@cache_manager.cached(ttl=3600) # Cache de 1 hora
def get_ticker_info_logic(symbol: str):
    """Lógica para obter informações principais de um ticker."""
    def get_ticker_details(ticker):
        info = ticker.info
        logo = f"https://t1.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&size=128&url={info.get('website')}" if info.get("website") else None
        
        summary = info.get("longBusinessSummary", "Resumo não disponível")
        translated_summary = GoogleTranslator(source='auto', target='pt').translate(summary)

        return {
            "longName": info.get("longName"), "sector": info.get("sector"), "industry": info.get("industry"),
            "employees": info.get("fullTimeEmployees"), "website": info.get("website"), "country": info.get("country"),
            "business_summary": translated_summary, "fullExchangeName": info.get("fullExchangeName"),
            "type": info.get("quoteType"), "currency": info.get("currency"), "logo": logo,
            "priceAndVariation": {
                "currentPrice": info.get("currentPrice"), "previousClose": info.get("previousClose"),
                "dayLow": info.get("dayLow"), "dayHigh": info.get("dayHigh"), "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
                "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"), "fiftyTwoWeekChangePercent": info.get("fiftyTwoWeekChangePercent"),
                "regularMarketChangePercent": info.get("regularMarketChangePercent"), "fiftyDayAverage": info.get("fiftyDayAverage"),
                "twoHundredDayAverage": info.get("twoHundredDayAverage")
            },
            "volumeAndLiquidity": {
                "volume": info.get("regularMarketVolume"), "averageVolume10days": info.get("averageVolume10days"),
                "averageDailyVolume3Month": info.get("averageDailyVolume3Month"), "bid": info.get("bid"), "ask": info.get("ask")
            },
            "riskAndMarketOpinion": {
                "beta": info.get("beta"), "recommendationKey": info.get("recommendationKey"),
                "recommendationMean": info.get("recommendationMean"), "targetHighPrice": info.get("targetHighPrice"),
                "targetLowPrice": info.get("targetLowPrice"), "targetMeanPrice": info.get("targetMeanPrice"),
                "numberOfAnalystOpinions": info.get("numberOfAnalystOpinions")
            },
            "valuation": {
                "marketCap": info.get("marketCap"), "enterpriseValue": info.get("enterpriseValue"), "trailingPE": info.get("trailingPE"),
                "forwardPE": info.get("forwardPE"), "priceToBook": info.get("priceToBook"),
                "priceToSalesTrailing12Months": info.get("priceToSalesTrailing12Months"), "enterpriseToRevenue": info.get("enterpriseToRevenue"),
                "enterpriseToEbitda": info.get("enterpriseToEbitda")
            },
            "rentability": {
                "returnOnEquity": info.get("returnOnEquity"), "returnOnAssets": info.get("returnOnAssets"),
                "profitMargins": info.get("profitMargins"), "grossMargins": info.get("grossMargins"),
                "operatingMargins": info.get("operatingMargins"), "ebitdaMargins": info.get("ebitdaMargins")
            },
            "eficiencyAndCashflow": {
                "revenuePerShare": info.get("revenuePerShare"), "grossProfits": info.get("grossProfits"), "ebitda": info.get("ebitda"),
                "operatingCashflow": info.get("operatingCashflow"), "freeCashflow": info.get("freeCashflow"),
                "earningsQuarterlyGrowth": info.get("earningsQuarterlyGrowth"), "revenueGrowth": info.get("revenueGrowth"),
                "totalRevenue": info.get("totalRevenue")
            },
            "debtAndSolvency": {
                "totalDebt": info.get("totalDebt"), "debtToEquity": info.get("debtToEquity"),
                "quickRatio": info.get("quickRatio"), "currentRatio": info.get("currentRatio")
            },
            "dividends": {
                "dividendRate": info.get("dividendRate"), "dividendYield": info.get("dividendYield"),
                "payoutRatio": info.get("payoutRatio"), "lastDividendValue": info.get("lastDividendValue"),
                "exDividendDate": info.get("exDividendDate")
            },
            "ShareholdingAndProfit": {
                "sharesOutstanding": info.get("sharesOutstanding"), "floatShares": info.get("floatShares"),
                "heldPercentInsiders": info.get("heldPercentInsiders"), "heldPercentInstitutions": info.get("heldPercentInstitutions"),
                "epsTrailingTwelveMonths": info.get("epsTrailingTwelveMonths"), "epsForward": info.get("epsForward"),
                "netIncomeToCommon": info.get("netIncomeToCommon")
            }
        }
    profile = safe_ticker_operation(symbol, get_ticker_details)
    return convert_to_serializable(profile)

# ==================== ENDPOINT DE SEARCH ====================

@cache_manager.cached(ttl=1800) # Cache de 30 minutos
def search_tickers_logic(q: str, limit: int):
    """Lógica para buscar por tickers, empresas, etc."""
    try:
        search = yf.Search(query=q, max_results=limit, news_count=0, lists_count=0, enable_fuzzy_query=True, recommended=0, raise_errors=True)
        quotes = search.quotes
        if not quotes:
            return {"query": q, "count": 0, "results": []}
        
        formatted_results = []
        for item in quotes:
            logo = f"https://t1.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&size=128&url={item.get('website')}" if item.get("website") else None
            result = {
                "symbol": str(item.get("symbol", "")), "name": str(item.get("longname", "") or item.get("shortname", "")),
                "exchange": str(item.get("exchange", "")), "type": str(item.get("quoteType", "")),
                "score": float(item.get("score", 0) or 0), "sector": str(item.get("sector", "")),
                "industry": str(item.get("industry", "")), "logo": logo
            }
            formatted_results.append(result)
            
        formatted_results.sort(key=lambda x: x["score"], reverse=True)
        return {"query": q, "count": len(formatted_results), "results": formatted_results}
    except Exception as e:
        logger.error(f"Erro na lógica de busca por '{q}': {str(e)}")
        raise RuntimeError(f"Erro ao realizar busca: {str(e)}")

@cache_manager.cached(ttl=3600)  # Cache de 1 hora para buscas de lookup
def lookup_instruments_logic(query: str, instrument_type: str, count: int):
    """
    Lógica de negócio para buscar instrumentos financeiros usando yf.Lookup.
    Levanta erros Python padrão em caso de falha.
    """
    # 1. Validação do tipo de instrumento
    valid_types = ["all", "stock", "etf", "future", "index", "mutualfund", "currency", "cryptocurrency"]
    instrument_type_lower = instrument_type.lower()
    
    if instrument_type_lower not in valid_types:
        raise ValueError(f"Tipo inválido: '{instrument_type}'. Tipos válidos são: {', '.join(valid_types)}")

    # 2. Chamada à biblioteca yfinance e tratamento de erros
    try:
        lookup = yf.Lookup(query=query, raise_errors=True)

        # Mapeamento de tipo para a função correspondente
        get_function_map = {
            "all": lookup.get_all,
            "stock": lookup.get_stock,
            "etf": lookup.get_etf,
            "future": lookup.get_future,
            "index": lookup.get_index,
            "mutualfund": lookup.get_mutualfund,
            "currency": lookup.get_currency,
            "cryptocurrency": lookup.get_cryptocurrency,
        }
        
        # Chama a função correta do mapa
        results = get_function_map[instrument_type_lower](count=count)
        
        # 3. Formatação do resultado para JSON
        if isinstance(results, pd.DataFrame):
            # Converte para lista de dicionários, preenchendo valores nulos
            return results.fillna("").to_dict(orient='records')
        else:
            # Retorna uma lista vazia se não houver resultados
            return []

    except Exception as e:
        logger.error(f"Erro na lógica de yf.Lookup para query='{query}': {str(e)}")
        # Lança um erro genérico que a camada da API irá capturar
        raise RuntimeError(f"Erro ao realizar lookup: {str(e)}")

@cache_manager.cached(ttl=3600) # Cache de 1 hora
def get_dividends_logic(symbol: str):
    """Lógica para obter histórico de dividendos."""
    data = safe_ticker_operation(symbol, lambda t: t.dividends)
    return convert_to_serializable(data)

@cache_manager.cached(ttl=86400) # Cache de 24 horas para dados que mudam pouco
def get_recommendations_logic(symbol: str):
    """Lógica para obter recomendações de analistas."""
    data = safe_ticker_operation(symbol, lambda t: t.recommendations)
    return convert_to_serializable(data)

@cache_manager.cached(ttl=86400) # Cache de 24 horas
def get_calendar_logic(symbol: str):
    """Lógica para obter calendário de eventos corporativos."""
    data = safe_ticker_operation(symbol, lambda t: t.calendar)
    return convert_to_serializable(data)

@cache_manager.cached(ttl=1800) # Cache de 30 minutos para notícias
def get_news_logic(symbol: str, num: int):
    """Lógica para obter notícias relacionadas ao ticker."""
    def process_news(ticker):
        news = ticker.get_news(count=num)
        simplified_news = []
        for item in news:
            news_content = item.get('content', {})
            simplified_item = {
                "id": news_content.get('id'),
                "title": GoogleTranslator(source='auto', target='pt').translate(news_content.get('title', "Título não disponível")),
                "date": news_content.get('pubDate'),
                "summary": GoogleTranslator(source='auto', target='pt').translate(news_content.get('summary', "Resumo não disponível")),
                "url": news_content.get('canonicalUrl', {}).get('url'),
                "thumbnail": news_content.get('thumbnail', {}).get('resolutions', [{}])[0].get('url') if news_content.get('thumbnail') else None
            }
            simplified_news.append(simplified_item)
        return simplified_news
    return safe_ticker_operation(symbol, process_news)

def list_categories_logic():
    """Lógica para listar as categorias de screening disponíveis."""
    return {
        "categorias": list(BR_PREDEFINED_SCREENER_QUERIES.keys()),
        "descricoes": {
            "alta_do_dia": "Ações em alta no dia (>3%)", "baixa_do_dia": "Ações em baixa no dia (<-2.5%)",
            "mais_negociadas": "Ações mais negociadas por volume", "small_caps_crescimento": "Small Caps com alto crescimento",
            "valor_dividendos": "Ações pagadoras de dividendos", "baixo_pe": "Ações com baixo P/L",
            "alta_liquidez": "Ações de alta liquidez", "crescimento_lucros": "Ações com crescimento de lucros",
            "baixo_risco": "Ações de baixo risco"
        }
    }

@cache_manager.cached(ttl=900) # Cache de 15 minutos para screeners
def get_trending_logic(categoria: str, setor: Optional[str], limit: int, offset: int, sort_field: str, sort_asc: bool):
    """Lógica para obter lista de ações baseada na categoria de screening."""
    if categoria not in BR_PREDEFINED_SCREENER_QUERIES:
        raise KeyError(f"Categoria '{categoria}' não encontrada.")
        
    base_query = BR_PREDEFINED_SCREENER_QUERIES[categoria]
    query = EquityQuery('and', [base_query, EquityQuery('eq', ['sector', setor])]) if setor else base_query
    
    try:
        results = yf.screen(query=query, size=limit, offset=offset, sortField=sort_field, sortAsc=sort_asc)
    except Exception as e:
        logger.error(f"Erro no yf.screen() para categoria '{categoria}': {str(e)}")
        raise RuntimeError(f"Erro ao executar screening: {str(e)}")
        
    quotes = results.get('quotes', [])
    if not quotes:
        return {"categoria": categoria, "resultados": [], "total": 0, "total_disponivel": 0}

    formatted_results = []
    for item in quotes:
        if not isinstance(item, dict): continue
        info = safe_ticker_operation(str(item.get("symbol", "")), lambda t: t.info)
        website = str(info.get("website", ""))
        logo = f"https://t1.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&size=128&url={website}" if website else None
        formatted_results.append({
            "symbol": str(item.get("symbol", "")), "name": str(item.get("longName", "") or item.get("shortName", "")),
            "sector": str(item.get("sector", "")), "price": float(item.get("regularMarketPrice", 0) or 0),
            "change": float(item.get("regularMarketChangePercent", 0) or 0), "volume": int(item.get("regularMarketVolume", 0) or 0),
            "market_cap": float(item.get("marketCap", 0) or 0), "pe_ratio": float(item.get("trailingPE", 0) or 0),
            "dividend_yield": float(item.get("dividendYield", 0) or 0), "fiftyTwoWeekChangePercent": float(item.get("fiftyTwoWeekChangePercent", 0)or 0),
            "avg_volume_3m": int(item.get("averageDailyVolume3Month", 0) or 0), "returnOnEquity": float(item.get("returnOnEquity", 0) or 0),
            "book_value": float(item.get("bookValue", 0) or 0), "exchange": str(item.get("exchange", "")),
            "fullExchangeName": str(item.get("fullExchangeName", "")), "currency": str(item.get("currency", "")),
            "website": website, "logo": logo
        })
    
    return {
        "categoria": categoria, "resultados": formatted_results, "total": len(formatted_results),
        "total_disponivel": int(results.get("total", len(formatted_results))), "offset": offset, "limit": limit,
        "ordenacao": {"campo": sort_field, "ascendente": sort_asc}
    }

@cache_manager.cached(ttl=600) # Cache de 10 minutos
def get_market_overview_logic(category: str):
    """Lógica para obter visão geral do mercado para uma categoria."""
    if category not in MARKET_OVERVIEW_SYMBOLS:
        raise KeyError(f"Categoria '{category}' inválida.")

    symbols = MARKET_OVERVIEW_SYMBOLS[category]
    
    def process_symbol(symbol):
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            logo = f"https://t1.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&size=128&url={info.get('website')}" if info.get("website") else None
            return {
                "symbol": symbol, "name": SYMBOL_NAMES.get(symbol, info.get("shortName", "N/A")),
                "price": info.get("regularMarketPrice", 0), "change": info.get("regularMarketChangePercent", 0),
                "website": info.get("website", None), "currency": info.get("currency", "N/A"), "logo": logo
            }
        except Exception as e:
            logger.warning(f"Erro ao processar {symbol} em market-overview: {str(e)}")
            return None

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(process_symbol, symbols))
    
    market_data = [r for r in results if r is not None]
    return {"category": category, "timestamp": datetime.now().isoformat(), "count": len(market_data), "data": market_data}

@cache_manager.cached(ttl=300) # Cache de 5 minutos
def get_period_performance_logic(symbol_list: List[str]):
    """Lógica para calcular a performance de múltiplos ativos em diferentes períodos."""
    periods = {"1D": ("1d", "1d"), "7D": ("7d", "1d"), "1M": ("1mo", "1d"), "3M": ("3mo", "1d"), "6M": ("6mo", "1d"), "1Y": ("1y", "1d")}
    results = {}
    for symbol in symbol_list:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            logo = f"https://t1.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&size=128&url={info.get('website')}" if info.get("website") else None
            
            ticker_data = {
                "name": info.get("shortName", "") or info.get("longName", ""), "current_price": info.get("regularMarketPrice", 0),
                "currency": info.get("currency", ""), "logo": logo, "performance": {}
            }

            for period_name, (period, interval) in periods.items():
                try:
                    hist = ticker.history(period=period, interval=interval)
                    if not hist.empty:
                        first_price = hist['Close'].iloc[0]
                        last_price = hist['Close'].iloc[-1]
                        change_percent = ((last_price - first_price) / first_price) * 100
                        ticker_data["performance"][period_name] = {
                            "change_percent": round(change_percent, 2), "start_price": round(first_price, 2),
                            "end_price": round(last_price, 2), "start_date": hist.index[0].strftime('%Y-%m-%d'),
                            "end_date": hist.index[-1].strftime('%Y-%m-%d')
                        }
                    else:
                        ticker_data["performance"][period_name] = None
                except Exception:
                    ticker_data["performance"][period_name] = None
            results[symbol] = {"success": True, "data": ticker_data}
        except Exception as e:
            logger.error(f"Erro ao processar performance para {symbol}: {str(e)}")
            results[symbol] = {"success": False, "error": str(e), "data": None}
    return results

def yfinance_health_check_logic():
    """Lógica para o health check."""
    try:
        test_ticker = yf.Ticker("AAPL")
        test_info = test_ticker.info
        if not test_info.get("symbol"):
            raise ConnectionError("Falha ao obter dados do ticker de teste (AAPL).")
        return {
            "status": "healthy", "service": "YFinance Logic Layer", "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check do YFinance falhou: {str(e)}")
        raise ConnectionError(f"Serviço YFinance indisponível: {str(e)}")