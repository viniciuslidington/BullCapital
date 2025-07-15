"""
Implementação do provedor Yahoo Finance.

Este módulo implementa a interface IMarketDataProvider para o Yahoo Finance,
fornecendo dados de mercado em tempo real e históricos através da biblioteca yfinance.

Example:
    from services.yahoo_finance_provider import YahooFinanceProvider
    
    provider = YahooFinanceProvider()
    data = provider.get_stock_data("PETR4.SA", request)
"""

import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
import yfinance as yf

from core.config import settings
from core.logging import LoggerMixin
from models.requests import StockDataRequest
from models.responses import (
    FundamentalData,
    HistoricalDataPoint,
    StockDataResponse,
    ValidationResponse,
)
from services.interfaces import IMarketDataProvider, ProviderException


class YahooFinanceProvider(IMarketDataProvider, LoggerMixin):
    """
    Provedor de dados do Yahoo Finance.
    
    Implementa a interface IMarketDataProvider utilizando a biblioteca yfinance
    para obter dados de mercado financeiro. Inclui tratamento de erros,
    retry automático e normalização de dados.
    
    Attributes:
        timeout: Timeout para requisições HTTP
        max_retries: Número máximo de tentativas
        retry_delay: Delay entre tentativas em segundos
    """
    
    def __init__(
        self,
        timeout: int = None,
        max_retries: int = None,
        retry_delay: float = 1.0
    ):
        """
        Inicializa o provedor Yahoo Finance.
        
        Args:
            timeout: Timeout para requisições (padrão: configuração global)
            max_retries: Número máximo de tentativas (padrão: configuração global)
            retry_delay: Delay entre tentativas em segundos
        """
        self.timeout = timeout or settings.YAHOO_FINANCE_TIMEOUT
        self.max_retries = max_retries or settings.MAX_RETRIES
        self.retry_delay = retry_delay
        
        # Cache de tickers brasileiros para otimização
        self._brazilian_stocks_cache: Optional[List[Dict[str, str]]] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = timedelta(hours=24)  # Cache válido por 24h
    
    def get_stock_data(
        self,
        symbol: str,
        request: StockDataRequest
    ) -> StockDataResponse:
        """
        Obtém dados completos de uma ação específica.
        
        Args:
            symbol: Símbolo da ação (ex: "PETR4.SA")
            request: Parâmetros da requisição
            
        Returns:
            Dados formatados da ação com informações atuais e históricas
            
        Raises:
            ProviderException: Erro na comunicação com Yahoo Finance
        """
        try:
            self.logger.info(f"Obtendo dados para {symbol}")
            
            # Normalizar símbolo
            normalized_symbol = self._normalize_symbol(symbol)
            
            # Criar ticker object
            ticker = self._create_ticker_with_retry(normalized_symbol)
            
            # Obter informações básicas
            info = self._get_ticker_info_with_retry(ticker, normalized_symbol)
            
            # Construir resposta base
            response = StockDataResponse(
                symbol=normalized_symbol,
                company_name=info.get('longName') or info.get('shortName'),
                current_price=self._safe_get_price(info, 'currentPrice', 'regularMarketPrice'),
                previous_close=info.get('previousClose'),
                volume=info.get('volume'),
                avg_volume=info.get('averageVolume'),
                currency=info.get('currency', 'BRL'),
                timezone=info.get('timeZone'),
                last_updated=datetime.now().isoformat()
            )
            
            # Calcular variação se possível
            if response.current_price and response.previous_close:
                response.change = round(
                    response.current_price - response.previous_close, 2
                )
                response.change_percent = round(
                    (response.change / response.previous_close) * 100, 2
                )
            
            # Sempre incluir dados fundamentais e históricos para API simplificada
            response.fundamentals = self._extract_fundamental_data(info)
            
            # Sempre incluir dados históricos
            response.historical_data = self._get_historical_data(
                ticker, request, normalized_symbol
            )
            
            # Adicionar metadados
            response.metadata = {
                "provider": "yahoo_finance",
                "data_delay": info.get('regularMarketDataDelay', 'unknown'),
                "market_state": info.get('marketState', 'unknown'),
                "request_params": {
                    "period": request.period,
                    "interval": "1d",  # Padrão simplificado
                    "start_date": None,  # Sempre usar período em vez de datas
                    "end_date": None
                }
            }
            
            self.logger.info(f"Dados obtidos com sucesso para {symbol}")
            return response
            
        except Exception as e:
            error_msg = f"Erro ao obter dados para {symbol}: {str(e)}"
            self.logger.error(error_msg)
            raise ProviderException(
                message=error_msg,
                provider="yahoo_finance",
                error_code="GET_STOCK_DATA_ERROR",
                details={"symbol": symbol, "original_error": str(e)}
            )
    
    def validate_ticker(self, symbol: str) -> ValidationResponse:
        """
        Valida se um ticker existe e é válido no Yahoo Finance.
        
        Args:
            symbol: Símbolo do ticker para validar
            
        Returns:
            Resultado detalhado da validação
        """
        try:
            self.logger.info(f"Validando ticker {symbol}")
            
            normalized_symbol = self._normalize_symbol(symbol)
            ticker = self._create_ticker_with_retry(normalized_symbol)
            
            # Tentar obter informações básicas
            try:
                info = ticker.info
                
                # Verificar se o ticker existe e tem dados válidos
                is_valid = bool(
                    info and 
                    'symbol' in info and 
                    info.get('regularMarketPrice') is not None
                )
                
                # Verificar se é negociável
                tradeable = info.get('tradeable', False) if is_valid else False
                
                # Obter data da última negociação
                last_trade_date = None
                if is_valid and 'regularMarketTime' in info:
                    last_trade_date = datetime.fromtimestamp(
                        info['regularMarketTime']
                    ).strftime('%Y-%m-%d')
                
                return ValidationResponse(
                    symbol=normalized_symbol,
                    is_valid=is_valid,
                    exists=is_valid,
                    market=self._extract_market_from_symbol(normalized_symbol),
                    tradeable=tradeable,
                    last_trade_date=last_trade_date,
                    validation_time=datetime.now().isoformat()
                )
                
            except Exception as e:
                # Ticker não encontrado ou inválido
                suggestions = self._generate_ticker_suggestions(symbol)
                
                return ValidationResponse(
                    symbol=normalized_symbol,
                    is_valid=False,
                    exists=False,
                    validation_time=datetime.now().isoformat(),
                    error_message=f"Ticker não encontrado: {str(e)}",
                    suggestions=suggestions
                )
                
        except Exception as e:
            error_msg = f"Erro na validação do ticker {symbol}: {str(e)}"
            self.logger.error(error_msg)
            
            return ValidationResponse(
                symbol=symbol,
                is_valid=False,
                exists=False,
                validation_time=datetime.now().isoformat(),
                error_message=error_msg
            )
    
    def search_tickers(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Busca tickers por nome ou símbolo.
        
        Args:
            query: Termo de busca
            limit: Número máximo de resultados
            
        Returns:
            Lista de tickers encontrados com informações básicas
        """
        try:
            self.logger.info(f"Buscando tickers para query: {query}")
            
            # Obter lista de ações brasileiras
            brazilian_stocks = self._get_brazilian_stocks()
            
            # Filtrar baseado na query
            query_lower = query.lower()
            results = []
            
            for stock in brazilian_stocks:
                # Verificar se a query corresponde ao símbolo ou nome
                if (query_lower in stock["name"].lower() or 
                    query_lower in stock["symbol"].lower() or
                    query_lower.replace('.sa', '') in stock["symbol"].lower()):
                    
                    # Adicionar à lista de resultados
                    results.append({
                        "symbol": stock["symbol"],
                        "name": stock["name"],
                        "sector": stock.get("sector", "Unknown"),
                        "market": "B3",
                        "currency": "BRL",
                        "relevance_score": self._calculate_relevance_score(
                            query_lower, stock
                        )
                    })
                    
                    if len(results) >= limit:
                        break
            
            # Ordenar por relevância
            results.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            self.logger.info(f"Encontrados {len(results)} resultados para '{query}'")
            return results
            
        except Exception as e:
            error_msg = f"Erro na busca de tickers: {str(e)}"
            self.logger.error(error_msg)
            raise ProviderException(
                message=error_msg,
                provider="yahoo_finance",
                error_code="SEARCH_ERROR",
                details={"query": query, "limit": limit}
            )
    
    def get_trending_stocks(self, market: str = "BR") -> List[Dict[str, Any]]:
        """
        Obtém ações em tendência para um mercado específico.
        
        Args:
            market: Código do mercado (BR, US, etc.)
            
        Returns:
            Lista de ações em tendência com dados atuais
        """
        try:
            self.logger.info(f"Obtendo ações em tendência para mercado {market}")
            
            if market.upper() == "BR":
                # Principais ações do Ibovespa
                trending_symbols = [
                    "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "B3SA3.SA",
                    "ABEV3.SA", "WEGE3.SA", "MGLU3.SA", "JBSS3.SA", "RENT3.SA",
                    "SUZB3.SA", "RAIL3.SA", "USIM5.SA", "CSNA3.SA", "GOAU4.SA"
                ]
            else:
                # Para outros mercados, implementar conforme necessário
                trending_symbols = []
            
            trending_data = []
            
            for symbol in trending_symbols:
                try:
                    ticker = self._create_ticker_with_retry(symbol)
                    info = self._get_ticker_info_with_retry(ticker, symbol)
                    
                    current_price = self._safe_get_price(
                        info, 'currentPrice', 'regularMarketPrice'
                    )
                    previous_close = info.get('previousClose')
                    
                    # Calcular variação percentual
                    change_percent = None
                    if current_price and previous_close:
                        change_percent = round(
                            ((current_price - previous_close) / previous_close) * 100, 2
                        )
                    
                    trending_data.append({
                        "symbol": symbol,
                        "name": info.get('longName', info.get('shortName', symbol)),
                        "current_price": current_price,
                        "previous_close": previous_close,
                        "change_percent": change_percent,
                        "volume": info.get('volume'),
                        "market_cap": info.get('marketCap'),
                        "sector": info.get('sector', 'Unknown')
                    })
                    
                except Exception as e:
                    self.logger.warning(f"Erro ao obter dados para {symbol}: {e}")
                    continue
            
            # Ordenar por volume ou market cap
            trending_data.sort(
                key=lambda x: x.get('market_cap', 0) or 0, 
                reverse=True
            )
            
            self.logger.info(f"Obtidas {len(trending_data)} ações em tendência")
            return trending_data
            
        except Exception as e:
            error_msg = f"Erro ao obter ações em tendência: {str(e)}"
            self.logger.error(error_msg)
            raise ProviderException(
                message=error_msg,
                provider="yahoo_finance",
                error_code="TRENDING_ERROR",
                details={"market": market}
            )
    
    # Métodos privados auxiliares
    
    def _normalize_symbol(self, symbol: str) -> str:
        """Normaliza símbolos para o formato do Yahoo Finance."""
        symbol = symbol.upper().strip()
        
        # Adicionar .SA para ações brasileiras se não presente
        if not symbol.endswith('.SA') and '.' not in symbol:
            # Verificar se é símbolo brasileiro comum
            if len(symbol) >= 4 and symbol[-1].isdigit():
                symbol = f"{symbol}.SA"
        
        return symbol
    
    def _create_ticker_with_retry(self, symbol: str) -> yf.Ticker:
        """Cria objeto Ticker com retry automático."""
        for attempt in range(self.max_retries):
            try:
                return yf.Ticker(symbol)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise e
                time.sleep(self.retry_delay * (attempt + 1))
        
        raise ProviderException(
            f"Falha ao criar ticker após {self.max_retries} tentativas"
        )
    
    def _get_ticker_info_with_retry(
        self, 
        ticker: yf.Ticker, 
        symbol: str
    ) -> Dict[str, Any]:
        """Obtém informações do ticker com retry automático."""
        for attempt in range(self.max_retries):
            try:
                info = ticker.info
                if not info or 'symbol' not in info:
                    raise ProviderException(f"Dados inválidos para {symbol}")
                return info
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise ProviderException(
                        f"Falha ao obter informações para {symbol}: {str(e)}"
                    )
                time.sleep(self.retry_delay * (attempt + 1))
        
        raise ProviderException(
            f"Falha ao obter informações após {self.max_retries} tentativas"
        )
    
    def _safe_get_price(self, info: Dict[str, Any], *keys: str) -> Optional[float]:
        """Obtém preço de forma segura usando múltiplas chaves."""
        for key in keys:
            price = info.get(key)
            if price is not None and isinstance(price, (int, float)):
                return float(price)
        return None
    
    def _extract_fundamental_data(self, info: Dict[str, Any]) -> FundamentalData:
        """Extrai dados fundamentais do objeto info."""
        return FundamentalData(
            market_cap=info.get('marketCap'),
            pe_ratio=info.get('trailingPE'),
            dividend_yield=info.get('dividendYield'),
            eps=info.get('trailingEps'),
            book_value=info.get('bookValue'),
            debt_to_equity=info.get('debtToEquity'),
            roe=info.get('returnOnEquity'),
            roa=info.get('returnOnAssets'),
            sector=info.get('sector'),
            industry=info.get('industry'),
            fifty_two_week_high=info.get('fiftyTwoWeekHigh'),
            fifty_two_week_low=info.get('fiftyTwoWeekLow')
        )
    
    def _get_historical_data(
        self,
        ticker: yf.Ticker,
        request: StockDataRequest,
        symbol: str
    ) -> List[HistoricalDataPoint]:
        """Obtém dados históricos formatados."""
        try:
            # Usar sempre o período especificado com intervalo padrão
            hist = ticker.history(
                period=request.period,
                interval="1d"  # Sempre usar intervalo diário para simplificar
            )
            
            if hist.empty:
                return []
            
            # Converter para lista de pontos históricos
            hist = hist.reset_index()
            historical_points = []
            
            for _, row in hist.iterrows():
                try:
                    point = HistoricalDataPoint(
                        date=row['Date'].strftime('%Y-%m-%d') if hasattr(row['Date'], 'strftime') else str(row['Date']),
                        open=round(float(row['Open']), 2),
                        high=round(float(row['High']), 2),
                        low=round(float(row['Low']), 2),
                        close=round(float(row['Close']), 2),
                        volume=int(row['Volume']) if pd.notna(row['Volume']) else 0,
                        adj_close=round(float(row.get('Adj Close', row['Close'])), 2)
                    )
                    historical_points.append(point)
                except (ValueError, TypeError) as e:
                    self.logger.warning(f"Erro ao processar ponto histórico: {e}")
                    continue
            
            return historical_points
            
        except Exception as e:
            self.logger.error(f"Erro ao obter dados históricos para {symbol}: {e}")
            return []
    
    def _get_brazilian_stocks(self) -> List[Dict[str, str]]:
        """Obtém lista de ações brasileiras com cache."""
        # Verificar se o cache é válido
        if (self._brazilian_stocks_cache and 
            self._cache_timestamp and 
            datetime.now() - self._cache_timestamp < self._cache_ttl):
            return self._brazilian_stocks_cache
        
        # Lista estática de principais ações brasileiras
        # Em produção, isso poderia vir de uma API ou banco de dados
        brazilian_stocks = [
            {"symbol": "PETR4.SA", "name": "Petróleo Brasileiro S.A. - Petrobras", "sector": "Energy"},
            {"symbol": "PETR3.SA", "name": "Petróleo Brasileiro S.A. - Petrobras", "sector": "Energy"},
            {"symbol": "VALE3.SA", "name": "Vale S.A.", "sector": "Materials"},
            {"symbol": "ITUB4.SA", "name": "Itaú Unibanco Holding S.A.", "sector": "Financial Services"},
            {"symbol": "ITUB3.SA", "name": "Itaú Unibanco Holding S.A.", "sector": "Financial Services"},
            {"symbol": "BBDC4.SA", "name": "Banco Bradesco S.A.", "sector": "Financial Services"},
            {"symbol": "BBDC3.SA", "name": "Banco Bradesco S.A.", "sector": "Financial Services"},
            {"symbol": "B3SA3.SA", "name": "B3 S.A. - Brasil, Bolsa, Balcão", "sector": "Financial Services"},
            {"symbol": "MGLU3.SA", "name": "Magazine Luiza S.A.", "sector": "Consumer Cyclical"},
            {"symbol": "WEGE3.SA", "name": "WEG S.A.", "sector": "Industrials"},
            {"symbol": "ABEV3.SA", "name": "Ambev S.A.", "sector": "Consumer Staples"},
            {"symbol": "JBSS3.SA", "name": "JBS S.A.", "sector": "Consumer Staples"},
            {"symbol": "RENT3.SA", "name": "Localiza Rent a Car S.A.", "sector": "Industrials"},
            {"symbol": "SUZB3.SA", "name": "Suzano S.A.", "sector": "Materials"},
            {"symbol": "RAIL3.SA", "name": "Rumo S.A.", "sector": "Industrials"},
            {"symbol": "USIM5.SA", "name": "Usinas Siderúrgicas de Minas Gerais S.A.", "sector": "Materials"},
            {"symbol": "CSNA3.SA", "name": "Companhia Siderúrgica Nacional", "sector": "Materials"},
            {"symbol": "GOAU4.SA", "name": "Metalúrgica Gerdau S.A.", "sector": "Materials"},
            {"symbol": "BBAS3.SA", "name": "Banco do Brasil S.A.", "sector": "Financial Services"},
            {"symbol": "SANB11.SA", "name": "Banco Santander (Brasil) S.A.", "sector": "Financial Services"},
        ]
        
        # Atualizar cache
        self._brazilian_stocks_cache = brazilian_stocks
        self._cache_timestamp = datetime.now()
        
        return brazilian_stocks
    
    def _calculate_relevance_score(
        self, 
        query: str, 
        stock: Dict[str, str]
    ) -> float:
        """Calcula score de relevância para busca."""
        score = 0.0
        
        # Score baseado em correspondência no símbolo
        if query in stock["symbol"].lower():
            score += 1.0
        
        # Score baseado em correspondência no nome
        if query in stock["name"].lower():
            score += 0.8
        
        # Score baseado em correspondência parcial
        words = query.split()
        for word in words:
            if word in stock["name"].lower():
                score += 0.3
        
        return score
    
    def _extract_market_from_symbol(self, symbol: str) -> str:
        """Extrai mercado baseado no símbolo."""
        if symbol.endswith('.SA'):
            return 'B3'
        elif '.' not in symbol:
            return 'NYSE'  # Assumir NYSE para símbolos sem sufixo
        else:
            return 'Unknown'
    
    def _generate_ticker_suggestions(self, invalid_symbol: str) -> List[str]:
        """Gera sugestões de tickers similares."""
        suggestions = []
        
        # Se não tem .SA, sugerir versão com .SA
        if not invalid_symbol.endswith('.SA') and '.' not in invalid_symbol:
            suggestions.append(f"{invalid_symbol}.SA")
        
        # Buscar símbolos similares na lista brasileira
        brazilian_stocks = self._get_brazilian_stocks()
        invalid_lower = invalid_symbol.lower().replace('.sa', '')
        
        for stock in brazilian_stocks:
            symbol_base = stock["symbol"].replace('.SA', '').lower()
            if invalid_lower in symbol_base or symbol_base in invalid_lower:
                suggestions.append(stock["symbol"])
        
        return suggestions[:3]  # Retornar até 3 sugestões
