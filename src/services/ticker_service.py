"""
Serviço para gerenciamento de tickers e informações de mercado.
"""
import yfinance as yf
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TickerService:
    """Serviço para operações relacionadas a tickers e dados de mercado."""
    
    def __init__(self):
        # Lista principal de ações brasileiras (B3)
        self.brazilian_stocks = [
            {"symbol": "PETR4.SA", "name": "Petróleo Brasileiro S.A. - Petrobras", "sector": "Energy", "market": "B3"},
            {"symbol": "PETR3.SA", "name": "Petróleo Brasileiro S.A. - Petrobras", "sector": "Energy", "market": "B3"},
            {"symbol": "VALE3.SA", "name": "Vale S.A.", "sector": "Materials", "market": "B3"},
            {"symbol": "ITUB4.SA", "name": "Itaú Unibanco Holding S.A.", "sector": "Financial Services", "market": "B3"},
            {"symbol": "ITUB3.SA", "name": "Itaú Unibanco Holding S.A.", "sector": "Financial Services", "market": "B3"},
            {"symbol": "BBDC4.SA", "name": "Banco Bradesco S.A.", "sector": "Financial Services", "market": "B3"},
            {"symbol": "BBDC3.SA", "name": "Banco Bradesco S.A.", "sector": "Financial Services", "market": "B3"},
            {"symbol": "B3SA3.SA", "name": "B3 S.A. - Brasil, Bolsa, Balcão", "sector": "Financial Services", "market": "B3"},
            {"symbol": "MGLU3.SA", "name": "Magazine Luiza S.A.", "sector": "Consumer Cyclical", "market": "B3"},
            {"symbol": "WEGE3.SA", "name": "WEG S.A.", "sector": "Industrials", "market": "B3"},
            {"symbol": "ABEV3.SA", "name": "Ambev S.A.", "sector": "Consumer Staples", "market": "B3"},
            {"symbol": "JBSS3.SA", "name": "JBS S.A.", "sector": "Consumer Staples", "market": "B3"},
            {"symbol": "RENT3.SA", "name": "Localiza Rent a Car S.A.", "sector": "Industrials", "market": "B3"},
            {"symbol": "SUZB3.SA", "name": "Suzano S.A.", "sector": "Materials", "market": "B3"},
            {"symbol": "RAIL3.SA", "name": "Rumo S.A.", "sector": "Industrials", "market": "B3"},
            {"symbol": "UGPA3.SA", "name": "Ultrapar Participações S.A.", "sector": "Energy", "market": "B3"},
            {"symbol": "VIVT3.SA", "name": "Telefônica Brasil S.A.", "sector": "Communication Services", "market": "B3"},
            {"symbol": "GGBR4.SA", "name": "Gerdau S.A.", "sector": "Materials", "market": "B3"},
            {"symbol": "CSNA3.SA", "name": "Companhia Siderúrgica Nacional", "sector": "Materials", "market": "B3"},
            {"symbol": "USIM5.SA", "name": "Usiminas", "sector": "Materials", "market": "B3"},
            {"symbol": "EMBR3.SA", "name": "Embraer S.A.", "sector": "Industrials", "market": "B3"},
            {"symbol": "GOAU4.SA", "name": "Metalúrgica Gerdau S.A.", "sector": "Materials", "market": "B3"},
            {"symbol": "BEEF3.SA", "name": "Minerva S.A.", "sector": "Consumer Staples", "market": "B3"},
            {"symbol": "MRFG3.SA", "name": "Marfrig Global Foods S.A.", "sector": "Consumer Staples", "market": "B3"},
            {"symbol": "BRFS3.SA", "name": "BRF S.A.", "sector": "Consumer Staples", "market": "B3"},
            {"symbol": "CSAN3.SA", "name": "Cosan S.A.", "sector": "Energy", "market": "B3"},
            {"symbol": "EQTL3.SA", "name": "Equatorial Energia S.A.", "sector": "Utilities", "market": "B3"},
            {"symbol": "ELET3.SA", "name": "Centrais Elétricas Brasileiras S.A. - Eletrobrás", "sector": "Utilities", "market": "B3"},
            {"symbol": "ELET6.SA", "name": "Centrais Elétricas Brasileiras S.A. - Eletrobrás", "sector": "Utilities", "market": "B3"},
            {"symbol": "CPFE3.SA", "name": "CPFL Energia S.A.", "sector": "Utilities", "market": "B3"},
            {"symbol": "SBSP3.SA", "name": "Sabesp", "sector": "Utilities", "market": "B3"},
            {"symbol": "CPLE6.SA", "name": "Copel", "sector": "Utilities", "market": "B3"},
            {"symbol": "TOTS3.SA", "name": "TOTVS S.A.", "sector": "Technology", "market": "B3"},
            {"symbol": "LREN3.SA", "name": "Lojas Renner S.A.", "sector": "Consumer Cyclical", "market": "B3"},
            {"symbol": "HAPV3.SA", "name": "Hapvida Participações e Investimentos S.A.", "sector": "Healthcare", "market": "B3"},
            {"symbol": "RDOR3.SA", "name": "Rede D'Or São Luiz S.A.", "sector": "Healthcare", "market": "B3"},
            {"symbol": "FLRY3.SA", "name": "Fleury S.A.", "sector": "Healthcare", "market": "B3"},
            {"symbol": "QUAL3.SA", "name": "Qualicorp S.A.", "sector": "Healthcare", "market": "B3"},
            {"symbol": "CCRO3.SA", "name": "CCR S.A.", "sector": "Industrials", "market": "B3"},
            {"symbol": "CYRE3.SA", "name": "Cyrela Brazil Realty S.A.", "sector": "Real Estate", "market": "B3"},
            {"symbol": "MRVE3.SA", "name": "MRV Engenharia e Participações S.A.", "sector": "Real Estate", "market": "B3"}
        ]
        
        # Ações americanas populares
        self.us_stocks = [
            {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology", "market": "NASDAQ"},
            {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology", "market": "NASDAQ"},
            {"symbol": "GOOGL", "name": "Alphabet Inc.", "sector": "Communication Services", "market": "NASDAQ"},
            {"symbol": "AMZN", "name": "Amazon.com Inc.", "sector": "Consumer Cyclical", "market": "NASDAQ"},
            {"symbol": "TSLA", "name": "Tesla Inc.", "sector": "Consumer Cyclical", "market": "NASDAQ"},
            {"symbol": "META", "name": "Meta Platforms Inc.", "sector": "Communication Services", "market": "NASDAQ"},
            {"symbol": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology", "market": "NASDAQ"},
            {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financial Services", "market": "NYSE"},
            {"symbol": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare", "market": "NYSE"},
            {"symbol": "V", "name": "Visa Inc.", "sector": "Financial Services", "market": "NYSE"},
            {"symbol": "PG", "name": "Procter & Gamble Co.", "sector": "Consumer Staples", "market": "NYSE"},
            {"symbol": "UNH", "name": "UnitedHealth Group Inc.", "sector": "Healthcare", "market": "NYSE"},
            {"symbol": "HD", "name": "Home Depot Inc.", "sector": "Consumer Cyclical", "market": "NYSE"},
            {"symbol": "MA", "name": "Mastercard Inc.", "sector": "Financial Services", "market": "NYSE"},
            {"symbol": "BAC", "name": "Bank of America Corp.", "sector": "Financial Services", "market": "NYSE"}
        ]
    
    def get_all_tickers(self, market: Optional[str] = None) -> List[Dict]:
        """
        Retorna todos os tickers disponíveis.
        
        Args:
            market: Filtrar por mercado específico ('B3', 'NASDAQ', 'NYSE')
        
        Returns:
            Lista de dicionários com informações dos tickers
        """
        all_tickers = self.brazilian_stocks + self.us_stocks
        
        if market:
            market_upper = market.upper()
            return [ticker for ticker in all_tickers if ticker["market"] == market_upper]
        
        return all_tickers
    
    def get_tickers_by_sector(self, sector: str, market: Optional[str] = None) -> List[Dict]:
        """
        Retorna tickers filtrados por setor.
        
        Args:
            sector: Setor para filtrar
            market: Mercado específico (opcional)
        
        Returns:
            Lista de tickers do setor especificado
        """
        all_tickers = self.get_all_tickers(market)
        return [ticker for ticker in all_tickers 
                if sector.lower() in ticker["sector"].lower()]
    
    def search_tickers(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Busca tickers por nome ou símbolo.
        
        Args:
            query: Termo de busca
            limit: Número máximo de resultados
        
        Returns:
            Lista de tickers correspondentes à busca
        """
        all_tickers = self.get_all_tickers()
        query_lower = query.lower()
        results = []
        
        for ticker in all_tickers:
            if (query_lower in ticker["name"].lower() or 
                query_lower in ticker["symbol"].lower() or
                query_lower.replace('.sa', '') in ticker["symbol"].lower()):
                results.append(ticker)
                
                if len(results) >= limit:
                    break
        
        return results
    
    def validate_ticker(self, symbol: str) -> Dict:
        """
        Valida se um ticker existe e retorna informações básicas.
        
        Args:
            symbol: Símbolo do ticker
        
        Returns:
            Dicionário com informações de validação
        """
        try:
            # Adicionar .SA para ações brasileiras se necessário
            if not symbol.endswith('.SA') and '.' not in symbol and len(symbol) <= 6:
                test_symbol = f"{symbol}.SA"
            else:
                test_symbol = symbol
            
            ticker = yf.Ticker(test_symbol)
            info = ticker.info
            
            if info and 'symbol' in info:
                return {
                    "valid": True,
                    "symbol": test_symbol,
                    "name": info.get('longName', info.get('shortName', 'N/A')),
                    "sector": info.get('sector', 'N/A'),
                    "market": self._get_market_from_symbol(test_symbol)
                }
            else:
                # Tentar símbolo original se falhou com .SA
                if test_symbol != symbol:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    
                    if info and 'symbol' in info:
                        return {
                            "valid": True,
                            "symbol": symbol,
                            "name": info.get('longName', info.get('shortName', 'N/A')),
                            "sector": info.get('sector', 'N/A'),
                            "market": self._get_market_from_symbol(symbol)
                        }
                
                return {"valid": False, "symbol": symbol, "error": "Ticker não encontrado"}
                
        except Exception as e:
            return {"valid": False, "symbol": symbol, "error": str(e)}
    
    def get_available_sectors(self, market: Optional[str] = None) -> List[str]:
        """
        Retorna lista de setores disponíveis.
        
        Args:
            market: Filtrar por mercado específico
        
        Returns:
            Lista única de setores
        """
        all_tickers = self.get_all_tickers(market)
        sectors = list(set(ticker["sector"] for ticker in all_tickers))
        return sorted(sectors)
    
    def get_available_markets(self) -> List[str]:
        """
        Retorna lista de mercados disponíveis.
        
        Returns:
            Lista única de mercados
        """
        all_tickers = self.get_all_tickers()
        markets = list(set(ticker["market"] for ticker in all_tickers))
        return sorted(markets)
    
    def _get_market_from_symbol(self, symbol: str) -> str:
        """
        Determina o mercado baseado no símbolo.
        
        Args:
            symbol: Símbolo do ticker
        
        Returns:
            Nome do mercado
        """
        if symbol.endswith('.SA'):
            return 'B3'
        elif '.' not in symbol:
            # Assumir NASDAQ/NYSE para símbolos americanos sem sufixo
            return 'US'
        else:
            return 'Unknown'
    
    def get_ticker_with_live_data(self, symbol: str) -> Dict:
        """
        Obtém informações de um ticker com dados em tempo real.
        
        Args:
            symbol: Símbolo do ticker
        
        Returns:
            Informações completas do ticker com preços atuais
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info or 'symbol' not in info:
                return {"error": f"Ticker '{symbol}' não encontrado"}
            
            return {
                "symbol": symbol,
                "name": info.get('longName', info.get('shortName', 'N/A')),
                "sector": info.get('sector', 'N/A'),
                "industry": info.get('industry', 'N/A'),
                "market": self._get_market_from_symbol(symbol),
                "current_price": info.get('currentPrice', info.get('regularMarketPrice')),
                "previous_close": info.get('previousClose'),
                "market_cap": info.get('marketCap'),
                "volume": info.get('volume'),
                "currency": info.get('currency', 'N/A'),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Erro ao obter dados: {str(e)}"}
