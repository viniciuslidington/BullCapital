"""
Validadores para o Market Data Service.

Este módulo contém validadores customizados para diferentes tipos
de dados financeiros e parâmetros da API.

Example:
    from utils.validators import validate_ticker_symbol, validate_date_range
    
    is_valid = validate_ticker_symbol("PETR4.SA")
    date_valid = validate_date_range("2024-01-01", "2024-12-31")
"""

import re
from datetime import datetime, timedelta
from typing import Optional, Tuple


def validate_ticker_symbol(symbol: str) -> bool:
    """
    Valida se um símbolo de ticker está em formato válido.
    
    Args:
        symbol: Símbolo do ticker a ser validado
        
    Returns:
        True se o símbolo é válido, False caso contrário
        
    Example:
        >>> validate_ticker_symbol("PETR4.SA")
        True
        >>> validate_ticker_symbol("INVALID_SYMBOL!")
        False
    """
    if not symbol or not isinstance(symbol, str):
        return False
    
    # Remover espaços e converter para maiúscula
    symbol = symbol.strip().upper()
    
    # Padrões válidos para diferentes mercados
    patterns = [
        r'^[A-Z]{3,5}\d?\.SA$',     # Ações brasileiras (ex: PETR4.SA)
        r'^[A-Z]{1,5}$',            # Ações americanas (ex: AAPL, MSFT)
        r'^[A-Z]{1,5}\.[A-Z]{1,3}$' # Outros mercados (ex: VOD.L)
    ]
    
    return any(re.match(pattern, symbol) for pattern in patterns)


def validate_date_range(
    start_date: Optional[str],
    end_date: Optional[str]
) -> Tuple[bool, Optional[str]]:
    """
    Valida um intervalo de datas.
    
    Args:
        start_date: Data de início no formato YYYY-MM-DD
        end_date: Data de fim no formato YYYY-MM-DD
        
    Returns:
        Tupla (é_válido, mensagem_erro)
        
    Example:
        >>> validate_date_range("2024-01-01", "2024-12-31")
        (True, None)
        >>> validate_date_range("2024-12-31", "2024-01-01")
        (False, "Data de início deve ser anterior à data de fim")
    """
    # Se ambas são None, é válido (sem filtro de data)
    if start_date is None and end_date is None:
        return True, None
    
    # Se apenas uma é fornecida, é inválido
    if (start_date is None) != (end_date is None):
        return False, "Ambas as datas (início e fim) devem ser fornecidas"
    
    try:
        # Validar formato das datas
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Verificar se start_date é anterior a end_date
        if start_dt >= end_dt:
            return False, "Data de início deve ser anterior à data de fim"
        
        # Verificar se as datas não são muito antigas (limite de 10 anos)
        ten_years_ago = datetime.now() - timedelta(days=365 * 10)
        if start_dt < ten_years_ago:
            return False, "Data de início não pode ser anterior a 10 anos"
        
        # Verificar se as datas não são futuras
        if end_dt > datetime.now():
            return False, "Data de fim não pode ser futura"
        
        return True, None
        
    except ValueError:
        return False, "Formato de data inválido. Use YYYY-MM-DD"


def validate_period(period: str) -> bool:
    """
    Valida se um período é válido.
    
    Args:
        period: Período a ser validado
        
    Returns:
        True se o período é válido
        
    Example:
        >>> validate_period("1mo")
        True
        >>> validate_period("invalid")
        False
    """
    valid_periods = {
        "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"
    }
    return period in valid_periods


def validate_interval(interval: str) -> bool:
    """
    Valida se um intervalo é válido.
    
    Args:
        interval: Intervalo a ser validado
        
    Returns:
        True se o intervalo é válido
        
    Example:
        >>> validate_interval("1d")
        True
        >>> validate_interval("invalid")
        False
    """
    valid_intervals = {
        "1m", "2m", "5m", "15m", "30m", "60m", "90m",
        "1h", "1d", "5d", "1wk", "1mo", "3mo"
    }
    return interval in valid_intervals


def validate_market_code(market: str) -> bool:
    """
    Valida se um código de mercado é válido.
    
    Args:
        market: Código do mercado
        
    Returns:
        True se o código é válido
        
    Example:
        >>> validate_market_code("BR")
        True
        >>> validate_market_code("INVALID")
        False
    """
    valid_markets = {"BR", "US", "UK", "CA", "AU", "DE", "FR", "JP"}
    return market.upper() in valid_markets


def sanitize_symbol(symbol: str) -> str:
    """
    Sanitiza e normaliza um símbolo de ticker.
    
    Args:
        symbol: Símbolo a ser sanitizado
        
    Returns:
        Símbolo sanitizado e normalizado
        
    Example:
        >>> sanitize_symbol("  petr4  ")
        "PETR4"
        >>> sanitize_symbol("petr4.sa")
        "PETR4.SA"
    """
    if not symbol:
        return ""
    
    # Remover espaços e converter para maiúscula
    symbol = symbol.strip().upper()
    
    # Remover caracteres inválidos
    symbol = re.sub(r'[^A-Z0-9.]', '', symbol)
    
    return symbol


def normalize_brazilian_ticker(symbol: str) -> str:
    """
    Normaliza tickers brasileiros para o formato padrão do Yahoo Finance.
    
    Args:
        symbol: Símbolo brasileiro
        
    Returns:
        Símbolo normalizado com sufixo .SA
        
    Example:
        >>> normalize_brazilian_ticker("PETR4")
        "PETR4.SA"
        >>> normalize_brazilian_ticker("PETR4.SA")
        "PETR4.SA"
    """
    symbol = sanitize_symbol(symbol)
    
    if not symbol:
        return symbol
    
    # Se já tem .SA, retornar como está
    if symbol.endswith('.SA'):
        return symbol
    
    # Se não tem ponto e parece ser ticker brasileiro, adicionar .SA
    if '.' not in symbol and len(symbol) >= 4 and symbol[-1].isdigit():
        return f"{symbol}.SA"
    
    return symbol


def validate_bulk_request_size(tickers: list) -> Tuple[bool, Optional[str]]:
    """
    Valida o tamanho de uma requisição em lote.
    
    Args:
        tickers: Lista de tickers
        
    Returns:
        Tupla (é_válido, mensagem_erro)
        
    Example:
        >>> validate_bulk_request_size(["PETR4.SA", "VALE3.SA"])
        (True, None)
        >>> validate_bulk_request_size([])
        (False, "Lista de tickers não pode estar vazia")
    """
    if not tickers:
        return False, "Lista de tickers não pode estar vazia"
    
    if len(tickers) > 50:
        return False, "Máximo de 50 tickers por requisição em lote"
    
    # Verificar se há duplicatas
    if len(tickers) != len(set(tickers)):
        return False, "Lista contém tickers duplicados"
    
    # Validar cada ticker individualmente
    for ticker in tickers:
        if not validate_ticker_symbol(ticker):
            return False, f"Ticker inválido: {ticker}"
    
    return True, None


def calculate_cache_key(*args) -> str:
    """
    Calcula uma chave de cache baseada nos argumentos fornecidos.
    
    Args:
        *args: Argumentos para gerar a chave
        
    Returns:
        Chave de cache única
        
    Example:
        >>> calculate_cache_key("stock_data", "PETR4.SA", "1mo")
        "stock_data:PETR4.SA:1mo"
    """
    # Converter argumentos para strings e filtrar None
    string_args = [str(arg) for arg in args if arg is not None]
    
    # Juntar com : e normalizar
    cache_key = ":".join(string_args)
    
    # Remover caracteres problemáticos
    cache_key = re.sub(r'[^\w:.-]', '_', cache_key)
    
    return cache_key.lower()


def format_currency(value: Optional[float], currency: str = "BRL") -> str:
    """
    Formata um valor monetário de acordo com a moeda.
    
    Args:
        value: Valor a ser formatado
        currency: Código da moeda
        
    Returns:
        Valor formatado como string
        
    Example:
        >>> format_currency(25.30, "BRL")
        "R$ 25,30"
        >>> format_currency(100.50, "USD")
        "$ 100.50"
    """
    if value is None:
        return "N/A"
    
    if currency.upper() == "BRL":
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    elif currency.upper() == "USD":
        return f"$ {value:,.2f}"
    else:
        return f"{currency} {value:,.2f}"


def calculate_percentage_change(
    current: Optional[float],
    previous: Optional[float]
) -> Optional[float]:
    """
    Calcula a variação percentual entre dois valores.
    
    Args:
        current: Valor atual
        previous: Valor anterior
        
    Returns:
        Variação percentual ou None se não for possível calcular
        
    Example:
        >>> calculate_percentage_change(110.0, 100.0)
        10.0
        >>> calculate_percentage_change(90.0, 100.0)
        -10.0
    """
    if current is None or previous is None or previous == 0:
        return None
    
    return round(((current - previous) / previous) * 100, 2)


def is_market_open(market: str = "BR") -> bool:
    """
    Verifica se um mercado está aberto (aproximação simples).
    
    Args:
        market: Código do mercado
        
    Returns:
        True se o mercado provavelmente está aberto
        
    Note:
        Esta é uma implementação simplificada. Em produção,
        seria necessário considerar feriados e horários específicos.
        
    Example:
        >>> is_market_open("BR")  # Depende do horário atual
        True
    """
    now = datetime.now()
    
    # Verificar se é dia útil (segunda a sexta)
    if now.weekday() >= 5:  # 5 = sábado, 6 = domingo
        return False
    
    current_hour = now.hour
    
    if market.upper() == "BR":
        # B3: 10:00 às 17:00 (horário de Brasília)
        return 10 <= current_hour <= 17
    elif market.upper() == "US":
        # NYSE/NASDAQ: 9:30 às 16:00 (EST, aproximação)
        return 9 <= current_hour <= 16
    else:
        # Assumir horário comercial padrão
        return 9 <= current_hour <= 17
    