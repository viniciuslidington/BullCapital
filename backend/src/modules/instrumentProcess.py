import pandas as pd
import re
import logging


logging.basicConfig(level=logging.INFO)

def standardize_b3_ticker(ticker_symbol):
    """
    Padroniza tickers de ações da B3 para o formato do Yahoo Finance (ex: VALE3.SA).
    Mantém apenas tickers que terminam em 3, 4, 5, 6 ou 11 e adiciona '.SA' se necessário.
    Retorna None para tickers que não se encaixam nesse padrão, permitindo filtragem posterior.

    args:
        ticker_symbol (str): Ticker a ser padronizado.
    returns:
        str: Ticker padronizado no formato do Yahoo Finance (ex: VALE3.SA) ou None se não for válido.
    """
    if not isinstance(ticker_symbol, str):
        return None # Ignora entradas que não são strings

    ticker_symbol = ticker_symbol.upper()

    ticker_symbol_clean = re.sub(r'\.[A-Z]{1,4}$', '', ticker_symbol) # Regex mais genérica para sufixos de 1 a 4 letras

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





def process_instrument_data(csv_file) -> pd.DataFrame:
    """
    Processa os dados do instrumento a partir de um arquivo CSV.

    Args:
        csv_file (str): Caminho para o arquivo CSV contendo os dados do instrumento.

    Returns:
        pd.DataFrame: DataFrame contendo os dados processados do instrumento.
    """
    try:
        df = pd.read_csv(csv_file, encoding="latin1", sep=";", low_memory=False, skiprows=1)

        # Filtro: apenas ações (categoria SHARES), no mercado à vista
        acoes_b3 = df[
            (df["SctyCtgyNm"] == "SHARES") &
            (df["MktNm"] == "EQUITY-CASH") &
            (df["SgmtNm"] == "CASH")
        ]

        # Seleciona colunas principais
        resultado = acoes_b3[["TckrSymb", "CrpnNm", "ISIN", "MktCptlstn"]]
        resultado.columns = ["Ticker", "Nome", "ISIN", "MarketCap"]

        for row in resultado.itertuples():
            ticker = standardize_b3_ticker(row.Ticker)
            if ticker:
                resultado.at[row.Index, "Ticker"] = ticker
            else:
                resultado.drop(row.Index, inplace=True)

        return resultado

        
    except Exception as e:
        logging.error(f"Erro ao processar os dados do instrumento: {e}")
        return pd.DataFrame()


