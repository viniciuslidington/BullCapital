from modules.dataExtraction import download_tickers
from modules.instrumentProcess import process_instrument_data
import logging
import os
from dotenv import load_dotenv
load_dotenv()
csv_path = os.getenv("B3_CADASTRO_PATH")

def pipeline(start_date=None, end_date=None, period=None, interval='1d'):
    """
    Orchestra a pipeline de extração e processamento de dados de ações.

    Args:
        tickers (list): lista de tickers de ações a serem processados.
        start_date (str): começo do período de extração de dados.
        end_date (str): fim do período de extração de dados.
        period (str): período para o qual os dados serão extraídos (ex: '1mo', '3mo', '6mo', '1y').
        interval (str): intervalo de tempo para os dados (ex: '1d', '1wk', '1mo').

    Returns:
        pd.DataFrame: DataFrame contendo os dados processados dos instrumentos, ou None se não houver dados válidos.
    """
    #passo 1: Extração de dados
    logging.info("Iniciando a extração de dados dos tickers.")
    data_df = process_instrument_data(csv_path)

    if data_df.empty:
        logging.warning("Nenhum dado encontrado no arquivo CSV. Verifique o caminho do arquivo ou o conteúdo.")
        return None
    
    #passo 2: Filtra os tickers que retornam
    valid_tickers = download_tickers(
        data_df['Ticker'].tolist(),
        start_date=start_date,
        end_date=end_date,
        period=period,
        interval=interval
    )


    if valid_tickers is None or valid_tickers.empty:
        logging.warning("Nenhum ticker válido encontrado ou erro na extração de dados.")
        return None
    
    long_df = valid_tickers.stack(level='Ticker').reset_index()

    # Transpõe os níveis de coluna para "empilhar" o nível 'Ticker'
    long_df = valid_tickers.stack(level='Ticker').reset_index()
 
    melted = long_df.melt(id_vars=['Date', 'Ticker'], var_name='PriceType', value_name='Value')
    final_df = melted.pivot_table(index=['Date', 'Ticker'], columns='PriceType', values='Value').reset_index()
    final_df.columns.name = None

    return final_df
