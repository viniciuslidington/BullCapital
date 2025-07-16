# test_process_instruments.py

import pandas as pd
import yfinance as yf
import logging
import io
import re
import json



def download_and_normalize_ticker_data(
    ticker_symbol: str,
    start_date=None,
    end_date=None,
    period='1y',
    interval='1d'
):
    """
    Baixa e formata os dados históricos de um ticker usando yfinance,
    retornando um DataFrame pronto para serialização e armazenamento.
    """
    if period:
        start_date = None
        end_date = None

    logger.info(f"Baixando dados para {ticker_symbol} (period={period}, interval={interval}, start={start_date}, end={end_date})...")

    try:
        # Download
        if start_date and end_date:
            data_df = yf.download(ticker_symbol, start=start_date, end=end_date, interval=interval, progress=False)
        elif period:
            data_df = yf.download(ticker_symbol, period=period, interval=interval, progress=False)
        else:
            logger.warning(f"Nenhuma data ou período fornecido para {ticker_symbol}.")
            return None

        if data_df.empty:
            logger.warning(f"Nenhum dado retornado para o ticker {ticker_symbol}.")
            return None

        # Garantir que o índice seja datetime
        data_df.index = pd.to_datetime(data_df.index)
        data_df = data_df.reset_index()

        # Colunas esperadas
        price_columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
        existing_price_columns = [col for col in price_columns if col in data_df.columns]
        if not existing_price_columns:
            logger.warning(f"Nenhuma coluna de preço válida encontrada para {ticker_symbol}. Colunas: {data_df.columns.tolist()}")
            return None

        expected_columns = ['Date'] + existing_price_columns
        cols_to_select = [col for col in expected_columns if col in data_df.columns]

        if 'Date' not in cols_to_select:
            logger.error(f"Coluna 'Date' não encontrada no DataFrame para {ticker_symbol}. Colunas disponíveis: {data_df.columns.tolist()}")
            return None

        final_df = data_df[cols_to_select].copy()
        final_df['Ticker'] = ticker_symbol

        # Renomear colunas para o padrão esperado
        rename_map = {
            'Date': 'data',
            'Open': 'open_price',
            'High': 'high_price',
            'Low': 'low_price',
            'Close': 'close_price',
            'Adj Close': 'adj_close_price',
            'Volume': 'volume'
        }
        final_df.rename(columns=rename_map, inplace=True)

        # Adiciona 'ticker' na posição certa
        final_df.insert(1, 'ticker', final_df.pop('Ticker'))

        # Converte a data para string (ISO) para evitar erro de serialização JSON
        final_df['data'] = final_df['data'].dt.strftime('%Y-%m-%d')
        final_df = final_df.reset_index(drop=True)  
        print(final_df.head())  # Debug: imprime as primeiras linhas do DataFrame


        logger.info(f"Dados para {ticker_symbol} formatados para armazenamento. Total de {len(final_df)} registros.")
        return final_df

    except Exception as e:
        logger.error(f"Erro ao baixar ou processar dados para {ticker_symbol}: {e}", exc_info=True)
        return None


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
# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Leitura simulada do CSV a partir de um string
csv_path = "data/InstrumentsConsolidated2025.csv"  # <-- ajuste aqui

def main():
    try:
        df = pd.read_csv(csv_path, sep=";", encoding="latin1", skiprows=1, low_memory=False, header=0)
        logger.info(f"Arquivo lido com sucesso: {csv_path}")
    except Exception as e:
        logger.error(f"Erro ao ler CSV: {e}")
        return

    # Filtro para ações ordinárias na B3
    acoes_b3 = df[
        (df["SctyCtgyNm"] == "SHARES") &
        (df["MktNm"] == "EQUITY-CASH") &
        (df["SgmtNm"] == "CASH")
    ].copy()

    if acoes_b3.empty:
        logger.warning("Nenhuma ação ordinária encontrada após o filtro.")
        return

    resultado = acoes_b3[["TckrSymb", "CrpnNm", "ISIN", "MktCptlstn"]].copy()
    resultado.columns = ["Ticker", "Nome", "ISIN", "MarketCap"]

    valid_indices = []

    for index, row in resultado.iterrows():
        ticker_padronizado = standardize_b3_ticker(row["Ticker"])
        if ticker_padronizado:
            resultado.at[index, "Ticker"] = ticker_padronizado
            valid_indices.append(index)

    resultado_validado = resultado.loc[valid_indices]

    logger.info(f"\nTickers válidos encontrados: {len(resultado_validado)}")
    print(resultado_validado.head())


    tickers = ["2WAV3.SA", "AALR3.SA", "ABCB4.SA"]

    for t in tickers:
        df = download_and_normalize_ticker_data(t)
        if df is not None:
            print(f"\n✅ Dados para {t}:")
        else:
            print(f"\n❌ Falha ao baixar dados para {t}")




    df = download_and_normalize_ticker_data("ABCB4.SA")
    df = df.reset_index(drop=True)  # Reset index to avoid issues with JSON serialization

    # Se as colunas forem MultiIndex, transforme em colunas simples
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[-1] if isinstance(col, tuple) else col for col in df.columns]
    else:
        df.columns = [str(col) for col in df.columns]

    if df is not None:
        data_json = df.to_dict(orient='records')
        print(df.head())
        try:
            json.dumps(data_json)  # <- Se isso não quebrar, está pronto para envio via POST
            print("✅ JSON serializável")
        except Exception as e:
            print(f"❌ JSON inválido: {e}")




if __name__ == "__main__":
    main()
