import yfinance as yf
import pandas as pd
import logging
from typing import Union
import os

logger = logging.getLogger(__name__)

# Configurações de download via env vars
DOWNLOAD_START_DATE = os.getenv('DOWNLOAD_START_DATE') or None
DOWNLOAD_END_DATE = os.getenv('DOWNLOAD_END_DATE') or None
DOWNLOAD_PERIOD = os.getenv('DOWNLOAD_PERIOD', '1y')
DOWNLOAD_INTERVAL = os.getenv('DOWNLOAD_INTERVAL', '1d')


def download_and_normalize_ticker_data(
    ticker_symbol: str,
    start_date=DOWNLOAD_START_DATE,
    end_date=DOWNLOAD_END_DATE,
    period=DOWNLOAD_PERIOD,
    interval=DOWNLOAD_INTERVAL
) -> Union[pd.DataFrame, None]:
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
        # Se as colunas forem MultiIndex, transforme em colunas simples
        if isinstance(final_df.columns, pd.MultiIndex):
            final_df.columns = [col[-1] if isinstance(col, tuple) else col for col in final_df.columns]
        else:
            final_df.columns = [str(col) for col in final_df.columns]
            print(final_df.head())  # Debug: imprime as primeiras linhas do DataFrame


        logger.info(f"Dados para {ticker_symbol} formatados para armazenamento. Total de {len(final_df)} registros.")
        return final_df

    except Exception as e:
        logger.error(f"Erro ao baixar ou processar dados para {ticker_symbol}: {e}", exc_info=True)
        return None
