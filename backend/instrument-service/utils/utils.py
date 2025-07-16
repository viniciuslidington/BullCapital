# instrument_ingestion_service/utils/data_standardization.py
import re


def standardize_b3_ticker(ticker_symbol):
    """
    Padroniza tickers de ações da B3 para o formato do Yahoo Finance (ex: VALE3.SA).
    Mantém apenas tickers que terminam em 3, 4, 5, 6 ou 11 e adiciona '.SA' se necessário.
    Retorna None para tickers que não se encaixam nesse padrão, permitindo filtragem posterior.
    """
    if not isinstance(ticker_symbol, str):
        return None

    ticker_symbol = ticker_symbol.upper()

    # Regex mais genérica para sufixos de 1 a 4 letras
    ticker_symbol_clean = re.sub(r'\.[A-Z]{1,4}$', '', ticker_symbol) 

    # Regex para verificar se o ticker limpo termina com 3, 4, 5, 6 ou 11
    match = re.match(r'^([A-Z0-9]+?)(\d{1,2})$', ticker_symbol_clean)

    if match:
        base_name = match.group(1)
        suffix_digits = match.group(2)

        # Sufixos numéricos comuns de ações e units da B3
        if suffix_digits in ['3', '4', '5', '6', '11']:
            return f"{base_name}{suffix_digits}.SA"
        else:
            return None # Ticker termina com número, mas não é um tipo de ação B3 esperado

    elif ticker_symbol.endswith('.SA'):
        ticker_without_sa_for_check = ticker_symbol.replace('.SA', '')
        match_sa_pre = re.match(r'^([A-Z0-9]+?)(\d{1,2})$', ticker_without_sa_for_check)
        if match_sa_pre and match_sa_pre.group(2) in ['3', '4', '5', '6', '11']:
            return ticker_symbol # Já está no formato correto e é válido
        else:
            return None # Ticker com .SA mas sem número válido (ex: VALE.SA)

    return None # Se não corresponde a nenhum padrão de B3 válido, retorna None