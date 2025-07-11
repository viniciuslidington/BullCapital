# market_data_downloader_service/services/yfinance_downloader.py
import yfinance as yf
import pandas as pd
import logging
from typing import Union

logger = logging.getLogger(__name__)

def download_and_normalize_ticker_data(
    ticker_symbol: str,
    start_date: str = None, # Ex: '2023-01-01'
    end_date: str = None,   # Ex: '2023-12-31'
    period: str = None,     # Ex: '1y', 'max'
    interval: str = '1d'    # Ex: '1d', '1wk', '1mo'
) -> Union[pd.DataFrame, None]: # Retorna DataFrame ou None: # Retorna DataFrame ou None

    """
    Baixa dados históricos para um ticker e os normaliza.
    """
    logger.info(f"Baixando dados para {ticker_symbol} (period={period}, interval={interval}, start={start_date}, end={end_date})...")

    try:
        # yfinance.download aceita diferentes combinações de data/periodo
        # Preferimos start/end se fornecidos, senão usa period
        if start_date and end_date:
            data_df = yf.download(ticker_symbol, start=start_date, end=end_date, interval=interval, progress=False)
        elif period:
            data_df = yf.download(ticker_symbol, period=period, interval=interval, progress=False)
        else:
            logger.warning(f"Nenhuma data de início/fim ou período fornecido para {ticker_symbol}.")
            return None

        if data_df.empty:
            logger.warning(f"Nenhum dado retornado para o ticker {ticker_symbol}.")
            return None

        # Reindexa para garantir que 'Date' seja um índice
        data_df.index = pd.to_datetime(data_df.index)
        data_df = data_df.reset_index() # Transforma o índice Date em coluna

        # A lógica de "stack", "melt", "pivot_table" foi adaptada.
        # yfinance já retorna um DataFrame com colunas como 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close'
        # Seu código original parece estar transpondo um DataFrame multi-indexado de download_tickers().
        # yfinance.download para um único ticker já retorna um DataFrame simples.

        # A sua lógica de pivot_table se aplica mais quando se baixa VÁRIOS tickers de uma vez
        # e o yfinance retorna um MultiIndex nas colunas.
        # Para um único ticker, as colunas já são 'Open', 'High', etc.

        # Se a intenção é ter 'PriceType' (Open, High, Close, etc.) como uma coluna,
        # e os valores correspondentes em outra coluna 'Value', o melt é apropriado.
        
        # Filtra colunas de preço relevantes para o melt
        price_columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
        
        # Garante que apenas as colunas existentes sejam consideradas
        existing_price_columns = [col for col in price_columns if col in data_df.columns]

        if not existing_price_columns:
            logger.warning(f"Nenhuma coluna de preço válida encontrada para {ticker_symbol}. Colunas: {data_df.columns.tolist()}")
            return None

        # O yfinance.download já retorna as colunas Open, High, Low, Close, Adj Close, Volume
        # Vamos apenas selecionar e renomear para o formato do banco de dados do Stage 3
        final_df = data_df[['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']].copy()
        final_df['Ticker'] = ticker_symbol # Adiciona o Ticker de volta como coluna

        # Reordena as colunas e renomeia
        final_df = final_df[['Date', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]
        final_df.columns = [
            'data',           # Para corresponder ao nome da coluna no modelo DB
            'ticker',         # Para corresponder ao nome da coluna no modelo DB
            'open_price',
            'high_price',
            'low_price',
            'close_price',
            'adj_close_price',
            'volume'
        ]
        # Converte a coluna 'data' para o tipo datetime, se ainda não for
        final_df['data'] = pd.to_datetime(final_df['data'])

        logger.info(f"Dados para {ticker_symbol} formatados para armazenamento. Total de {len(final_df)} registros.")
        return final_df

    except Exception as e:
        logger.error(f"Erro ao baixar ou normalizar dados para {ticker_symbol}: {e}", exc_info=True)
        return None