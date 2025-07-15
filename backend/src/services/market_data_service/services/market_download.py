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
    ticker_symbols: list[str],
    start_date=DOWNLOAD_START_DATE,
    end_date=DOWNLOAD_END_DATE,
    period=DOWNLOAD_PERIOD,
    interval=DOWNLOAD_INTERVAL
) -> dict:
    """
    Baixa e formata os dados históricos de uma lista de tickers usando yfinance,
    retornando um dicionário {ticker: DataFrame} pronto para serialização e armazenamento.
    """
    if period:
        start_date = None
        end_date = None

    logger.info(f"Baixando dados para {ticker_symbols} (period={period}, interval={interval}, start={start_date}, end={end_date})...")

    try:
        # Download em lote
        if start_date and end_date:
            data_df = yf.download(ticker_symbols, start=start_date, end=end_date, interval=interval, progress=False, group_by='ticker')
        elif period:
            data_df = yf.download(ticker_symbols, period=period, interval=interval, progress=False, group_by='ticker')
        else:
            logger.warning(f"Nenhuma data ou período fornecido para {ticker_symbols}.")
            return {}

        if data_df.empty:
            logger.warning(f"Nenhum dado retornado para os tickers {ticker_symbols}.")
            return {}

        # Se apenas um ticker, o yfinance não cria multi-index, então padronize para dict
        if isinstance(ticker_symbols, str) or len(ticker_symbols) == 1:
            ticker = ticker_symbols[0] if isinstance(ticker_symbols, list) else ticker_symbols
            data_dict = {ticker: data_df}
        else:
            data_dict = {ticker: data_df[ticker] for ticker in ticker_symbols if ticker in data_df.columns.get_level_values(0)}

        result = {}
        for ticker, df in data_dict.items():
            if df.empty:
                logger.warning(f"Nenhum dado retornado para o ticker {ticker}.")
                continue
            df = df.copy()
            # Garantir que o índice seja datetime
            df.index = pd.to_datetime(df.index)
            df = df.reset_index()
            # Colunas esperadas
            price_columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
            existing_price_columns = [col for col in price_columns if col in df.columns]
            if not existing_price_columns:
                logger.warning(f"Nenhuma coluna de preço válida encontrada para {ticker}. Colunas: {df.columns.tolist()}")
                continue
            expected_columns = ['Date'] + existing_price_columns
            cols_to_select = [col for col in expected_columns if col in df.columns]
            if 'Date' not in cols_to_select:
                logger.error(f"Coluna 'Date' não encontrada no DataFrame para {ticker}. Colunas disponíveis: {df.columns.tolist()}")
                continue
            final_df = df[cols_to_select].copy()
            final_df['Ticker'] = ticker
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
            final_df.insert(1, 'ticker', final_df.pop('Ticker'))
            final_df['data'] = final_df['data'].dt.strftime('%Y-%m-%d')
            final_df = final_df.reset_index(drop=True)
            # Se as colunas forem MultiIndex, transforme em colunas simples
            if isinstance(final_df.columns, pd.MultiIndex):
                final_df.columns = [col[-1] if isinstance(col, tuple) else col for col in final_df.columns]
            else:
                final_df.columns = [str(col) for col in final_df.columns]
            logger.info(f"Dados para {ticker} formatados para armazenamento. Total de {len(final_df)} registros.")
            result[ticker] = final_df
        return result
    except Exception as e:
        logger.error(f"Erro ao baixar ou processar dados para {ticker_symbols}: {e}", exc_info=True)
        return {}
