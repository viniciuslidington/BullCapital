"""
YFinance Complete API Endpoints

Este módulo fornece acesso completo a todos os métodos da biblioteca yfinance
através de endpoints REST API. Inclui dados históricos, informações financeiras,
análises, opções, dividendos e muito mais.

Endpoints disponíveis:
- Dados históricos e preços
- Informações financeiras (balanço, DRE, fluxo de caixa)
- Dividendos e splits
- Recomendações de analistas
- Opções e derivativos
- Dados ESG e sustentabilidade
- Notícias e calendário de eventos
- Comparações e análises

Author: BullCapital Team
Version: 1.0.0
"""

from datetime import datetime
from typing import List, Optional
import yfinance as yf
import pandas as pd
import numpy as np
from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel, Field

from core.logging import get_logger

# Configurar logger
logger = get_logger(__name__)

# Criar router
router = APIRouter(prefix="/api/v1/yfinance", tags=["YFinance Complete API"])


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


@router.post("/download/multiple")
async def download_multiple_tickers(request: MultiTickerRequest):
    """
    Download de dados históricos para múltiplos tickers simultaneamente.
    """
    try:
        symbols_str = " ".join([s.upper() for s in request.symbols])
        data = yf.download(
            symbols_str,
            period=request.period,
            interval=request.interval,
            group_by='ticker',
            auto_adjust=True,
            prepost=False,
            threads=True
        )
        
        return {
            "symbols": request.symbols,
            "period": request.period,
            "interval": request.interval,
            "data": convert_to_serializable(data)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao baixar dados: {str(e)}")


# ==================== ENDPOINTS DE INFORMAÇÕES GERAIS ====================

@router.get("/{symbol}/info")
async def get_ticker_info(symbol: str = Path(..., description="Símbolo do ticker")):
    """
    Obtém informações gerais e fundamentais do ticker.
    
    Inclui: Market Cap, P/E, Beta, Dividend Yield, etc.
    """
    def get_info(ticker):
        return ticker.info
    
    info = safe_ticker_operation(symbol, get_info)
    return {
        "symbol": symbol.upper(),
        "info": convert_to_serializable(info)
    }


@router.get("/{symbol}/profile")
async def get_company_profile(symbol: str = Path(..., description="Símbolo do ticker")):
    """
    Obtém perfil resumido da empresa com informações principais.
    """
    def get_profile(ticker):
        info = ticker.info
        return {
            "longName": info.get("longName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "employees": info.get("fullTimeEmployees"),
            "website": info.get("website"),
            "business_summary": info.get("longBusinessSummary"),
            "market_cap": info.get("marketCap"),
            "enterprise_value": info.get("enterpriseValue"),
            "trailing_pe": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "dividend_yield": info.get("dividendYield"),
            "beta": info.get("beta"),
            "52_week_high": info.get("fiftyTwoWeekHigh"),
            "52_week_low": info.get("fiftyTwoWeekLow")
        }
    
    profile = safe_ticker_operation(symbol, get_profile)
    return {
        "symbol": symbol.upper(),
        "profile": convert_to_serializable(profile)
    }


# ==================== ENDPOINTS FINANCEIROS ====================

@router.get("/{symbol}/financials")
async def get_financials(symbol: str = Path(..., description="Símbolo do ticker")):
    """Obtém demonstrações financeiras anuais (DRE)."""
    def get_financials(ticker):
        return ticker.financials
    
    data = safe_ticker_operation(symbol, get_financials)
    return {
        "symbol": symbol.upper(),
        "type": "annual_income_statement",
        "data": convert_to_serializable(data)
    }


@router.get("/{symbol}/financials/quarterly")
async def get_quarterly_financials(symbol: str = Path(..., description="Símbolo do ticker")):
    """Obtém demonstrações financeiras trimestrais (DRE)."""
    def get_quarterly_financials(ticker):
        return ticker.quarterly_financials
    
    data = safe_ticker_operation(symbol, get_quarterly_financials)
    return {
        "symbol": symbol.upper(),
        "type": "quarterly_income_statement",
        "data": convert_to_serializable(data)
    }


@router.get("/{symbol}/balance-sheet")
async def get_balance_sheet(symbol: str = Path(..., description="Símbolo do ticker")):
    """Obtém balanço patrimonial anual."""
    def get_balance_sheet(ticker):
        return ticker.balance_sheet
    
    data = safe_ticker_operation(symbol, get_balance_sheet)
    return {
        "symbol": symbol.upper(),
        "type": "annual_balance_sheet",
        "data": convert_to_serializable(data)
    }


@router.get("/{symbol}/balance-sheet/quarterly")
async def get_quarterly_balance_sheet(symbol: str = Path(..., description="Símbolo do ticker")):
    """Obtém balanço patrimonial trimestral."""
    def get_quarterly_balance_sheet(ticker):
        return ticker.quarterly_balance_sheet
    
    data = safe_ticker_operation(symbol, get_quarterly_balance_sheet)
    return {
        "symbol": symbol.upper(),
        "type": "quarterly_balance_sheet",
        "data": convert_to_serializable(data)
    }


@router.get("/{symbol}/cashflow")
async def get_cashflow(symbol: str = Path(..., description="Símbolo do ticker")):
    """Obtém fluxo de caixa anual."""
    def get_cashflow(ticker):
        return ticker.cashflow
    
    data = safe_ticker_operation(symbol, get_cashflow)
    return {
        "symbol": symbol.upper(),
        "type": "annual_cashflow",
        "data": convert_to_serializable(data)
    }


@router.get("/{symbol}/cashflow/quarterly")
async def get_quarterly_cashflow(symbol: str = Path(..., description="Símbolo do ticker")):
    """Obtém fluxo de caixa trimestral."""
    def get_quarterly_cashflow(ticker):
        return ticker.quarterly_cashflow
    
    data = safe_ticker_operation(symbol, get_quarterly_cashflow)
    return {
        "symbol": symbol.upper(),
        "type": "quarterly_cashflow",
        "data": convert_to_serializable(data)
    }


# ==================== ENDPOINTS DE DIVIDENDOS E SPLITS ====================

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


@router.get("/{symbol}/splits")
async def get_splits(symbol: str = Path(..., description="Símbolo do ticker")):
    """Obtém histórico de desdobramentos de ações."""
    def get_splits(ticker):
        return ticker.splits
    
    data = safe_ticker_operation(symbol, get_splits)
    return {
        "symbol": symbol.upper(),
        "splits": convert_to_serializable(data)
    }


@router.get("/{symbol}/actions")
async def get_actions(symbol: str = Path(..., description="Símbolo do ticker")):
    """Obtém todas as ações corporativas (dividendos e splits)."""
    def get_actions(ticker):
        return ticker.actions
    
    data = safe_ticker_operation(symbol, get_actions)
    return {
        "symbol": symbol.upper(),
        "actions": convert_to_serializable(data)
    }


# ==================== ENDPOINTS DE ANÁLISES E RECOMENDAÇÕES ====================

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


@router.get("/{symbol}/recommendations/summary")
async def get_recommendations_summary(symbol: str = Path(..., description="Símbolo do ticker")):
    """Obtém resumo das recomendações de analistas."""
    def get_recommendations_summary(ticker):
        return ticker.recommendations_summary
    
    data = safe_ticker_operation(symbol, get_recommendations_summary)
    return {
        "symbol": symbol.upper(),
        "recommendations_summary": convert_to_serializable(data)
    }


@router.get("/{symbol}/upgrades-downgrades")
async def get_upgrades_downgrades(symbol: str = Path(..., description="Símbolo do ticker")):
    """Obtém histórico de upgrades e downgrades."""
    def get_upgrades_downgrades(ticker):
        return ticker.upgrades_downgrades
    
    data = safe_ticker_operation(symbol, get_upgrades_downgrades)
    return {
        "symbol": symbol.upper(),
        "upgrades_downgrades": convert_to_serializable(data)
    }


# ==================== ENDPOINTS DE PROPRIEDADE E INVESTIDORES ====================

@router.get("/{symbol}/institutional-holders")
async def get_institutional_holders(symbol: str = Path(..., description="Símbolo do ticker")):
    """Obtém investidores institucionais."""
    def get_institutional_holders(ticker):
        return ticker.institutional_holders
    
    data = safe_ticker_operation(symbol, get_institutional_holders)
    return {
        "symbol": symbol.upper(),
        "institutional_holders": convert_to_serializable(data)
    }


@router.get("/{symbol}/major-holders")
async def get_major_holders(symbol: str = Path(..., description="Símbolo do ticker")):
    """Obtém principais acionistas."""
    def get_major_holders(ticker):
        return ticker.major_holders
    
    data = safe_ticker_operation(symbol, get_major_holders)
    return {
        "symbol": symbol.upper(),
        "major_holders": convert_to_serializable(data)
    }


@router.get("/{symbol}/mutualfund-holders")
async def get_mutualfund_holders(symbol: str = Path(..., description="Símbolo do ticker")):
    """Obtém fundos mútuos que possuem a ação."""
    def get_mutualfund_holders(ticker):
        return ticker.mutualfund_holders
    
    data = safe_ticker_operation(symbol, get_mutualfund_holders)
    return {
        "symbol": symbol.upper(),
        "mutualfund_holders": convert_to_serializable(data)
    }


# ==================== ENDPOINTS DE EARNINGS E CALENDÁRIO ====================

@router.get("/{symbol}/earnings")
async def get_earnings(symbol: str = Path(..., description="Símbolo do ticker")):
    """Obtém histórico de earnings anuais."""
    def get_earnings(ticker):
        return ticker.earnings
    
    data = safe_ticker_operation(symbol, get_earnings)
    return {
        "symbol": symbol.upper(),
        "earnings": convert_to_serializable(data)
    }


@router.get("/{symbol}/earnings/quarterly")
async def get_quarterly_earnings(symbol: str = Path(..., description="Símbolo do ticker")):
    """Obtém earnings trimestrais."""
    def get_quarterly_earnings(ticker):
        return ticker.quarterly_earnings
    
    data = safe_ticker_operation(symbol, get_quarterly_earnings)
    return {
        "symbol": symbol.upper(),
        "quarterly_earnings": convert_to_serializable(data)
    }


@router.get("/{symbol}/earnings/dates")
async def get_earnings_dates(symbol: str = Path(..., description="Símbolo do ticker")):
    """Obtém datas de earnings (passadas e futuras)."""
    def get_earnings_dates(ticker):
        return ticker.earnings_dates
    
    data = safe_ticker_operation(symbol, get_earnings_dates)
    return {
        "symbol": symbol.upper(),
        "earnings_dates": convert_to_serializable(data)
    }


@router.get("/{symbol}/earnings/history")
async def get_earnings_history(symbol: str = Path(..., description="Símbolo do ticker")):
    """Obtém histórico detalhado de earnings."""
    def get_earnings_history(ticker):
        return ticker.earnings_history
    
    data = safe_ticker_operation(symbol, get_earnings_history)
    return {
        "symbol": symbol.upper(),
        "earnings_history": convert_to_serializable(data)
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


# ==================== ENDPOINTS DE OPÇÕES ====================

@router.get("/{symbol}/options")
async def get_options_dates(symbol: str = Path(..., description="Símbolo do ticker")):
    """Obtém datas de expiração disponíveis para opções."""
    def get_options(ticker):
        return ticker.options
    
    data = safe_ticker_operation(symbol, get_options)
    return {
        "symbol": symbol.upper(),
        "options_expiration_dates": list(data) if data else []
    }


@router.get("/{symbol}/options/{expiration_date}")
async def get_option_chain(
    symbol: str = Path(..., description="Símbolo do ticker"),
    expiration_date: str = Path(..., description="Data de expiração (YYYY-MM-DD)")
):
    """Obtém cadeia de opções para uma data de expiração específica."""
    def get_option_chain(ticker):
        chain = ticker.option_chain(expiration_date)
        return {
            "calls": chain.calls,
            "puts": chain.puts
        }
    
    data = safe_ticker_operation(symbol, get_option_chain)
    return {
        "symbol": symbol.upper(),
        "expiration_date": expiration_date,
        "calls": convert_to_serializable(data["calls"]),
        "puts": convert_to_serializable(data["puts"])
    }


# ==================== ENDPOINTS DE NOTÍCIAS E ESG ====================

@router.get("/{symbol}/news")
async def get_news(symbol: str = Path(..., description="Símbolo do ticker")):
    """Obtém notícias relacionadas ao ticker."""
    def get_news(ticker):
        return ticker.news
    
    data = safe_ticker_operation(symbol, get_news)
    return {
        "symbol": symbol.upper(),
        "news": convert_to_serializable(data)
    }


@router.get("/{symbol}/sustainability")
async def get_sustainability(symbol: str = Path(..., description="Símbolo do ticker")):
    """Obtém dados de sustentabilidade e ESG."""
    def get_sustainability(ticker):
        return ticker.sustainability
    
    data = safe_ticker_operation(symbol, get_sustainability)
    return {
        "symbol": symbol.upper(),
        "sustainability": convert_to_serializable(data)
    }


# ==================== ENDPOINTS DE ANÁLISE TÉCNICA ====================

@router.get("/{symbol}/analysis/technical")
async def get_technical_analysis(
    symbol: str = Path(..., description="Símbolo do ticker"),
    period: str = Query("3mo", description="Período para análise")
):
    """
    Realiza análise técnica básica incluindo médias móveis e indicadores.
    """
    def get_technical_data(ticker):
        hist = ticker.history(period=period)
        
        if hist.empty:
            return None
            
        # Calcular médias móveis
        hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
        hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
        hist['EMA_12'] = hist['Close'].ewm(span=12).mean()
        hist['EMA_26'] = hist['Close'].ewm(span=26).mean()
        
        # RSI simplificado
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        hist['RSI'] = 100 - (100 / (1 + rs))
        
        # Bandas de Bollinger
        hist['BB_Middle'] = hist['Close'].rolling(window=20).mean()
        bb_std = hist['Close'].rolling(window=20).std()
        hist['BB_Upper'] = hist['BB_Middle'] + (bb_std * 2)
        hist['BB_Lower'] = hist['BB_Middle'] - (bb_std * 2)
        
        return hist
    
    data = safe_ticker_operation(symbol, get_technical_data)
    return {
        "symbol": symbol.upper(),
        "period": period,
        "technical_indicators": convert_to_serializable(data)
    }


# ==================== ENDPOINTS DE COMPARAÇÃO ====================

@router.post("/compare/performance")
async def compare_performance(request: MultiTickerRequest):
    """
    Compara performance de múltiplos tickers.
    """
    try:
        symbols = [s.upper() for s in request.symbols]
        data = {}
        
        for symbol in symbols:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=request.period)
            
            if not hist.empty:
                # Calcular métricas de performance
                returns = hist['Close'].pct_change().dropna()
                total_return = (hist['Close'][-1] / hist['Close'][0] - 1) * 100
                volatility = returns.std() * (252 ** 0.5) * 100  # Anualizada
                
                data[symbol] = {
                    "total_return_pct": round(total_return, 2),
                    "volatility_pct": round(volatility, 2),
                    "max_price": float(hist['High'].max()),
                    "min_price": float(hist['Low'].min()),
                    "current_price": float(hist['Close'][-1]),
                    "avg_volume": float(hist['Volume'].mean())
                }
        
        return {
            "comparison": data,
            "period": request.period,
            "symbols": symbols
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro na comparação: {str(e)}")


# ==================== ENDPOINT DE RESUMO COMPLETO ====================

@router.get("/{symbol}/complete")
async def get_complete_data(symbol: str = Path(..., description="Símbolo do ticker")):
    """
    Obtém um resumo completo com todas as informações principais do ticker.
    """
    def get_complete_info(ticker):
        result = {
            "basic_info": {},
            "price_data": {},
            "financials": {},
            "dividends": {},
            "recommendations": {},
            "holders": {}
        }
        
        try:
            # Informações básicas
            info = ticker.info
            result["basic_info"] = {
                "name": info.get("longName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "beta": info.get("beta"),
                "dividend_yield": info.get("dividendYield")
            }
            
            # Dados de preço recentes
            hist = ticker.history(period="1mo")
            if not hist.empty:
                result["price_data"] = {
                    "current_price": float(hist['Close'][-1]),
                    "change_1d": float(hist['Close'][-1] - hist['Close'][-2]) if len(hist) > 1 else 0,
                    "volume": float(hist['Volume'][-1]),
                    "high_52w": info.get("fiftyTwoWeekHigh"),
                    "low_52w": info.get("fiftyTwoWeekLow")
                }
            
            # Dividendos recentes
            dividends = ticker.dividends
            if not dividends.empty:
                result["dividends"] = {
                    "last_dividend": float(dividends[-1]),
                    "dividend_count_1y": len(dividends.last("1Y"))
                }
            
            # Recomendações
            try:
                rec_summary = ticker.recommendations_summary
                if rec_summary is not None and not rec_summary.empty:
                    result["recommendations"] = convert_to_serializable(rec_summary.iloc[0].to_dict())
            except Exception as e:
                logger.warning(f"Erro ao obter recomendações: {str(e)}")
                pass
            
        except Exception as e:
            logger.error(f"Erro ao obter dados completos: {str(e)}")
        
        return result
    
    data = safe_ticker_operation(symbol, get_complete_info)
    return {
        "symbol": symbol.upper(),
        "timestamp": datetime.now().isoformat(),
        "data": data
    }


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
