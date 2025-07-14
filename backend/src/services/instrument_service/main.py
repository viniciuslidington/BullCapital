from fastapi import FastAPI, UploadFile, File, HTTPException
import pandas as pd
import logging
import json
import io
import yfinance as yf
import time
from confluent_kafka import Producer

from utils.utils import standardize_b3_ticker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


def get_kafka_producer_with_retry(retries=5, delay=3):
    for attempt in range(retries):
        try:
            conf = {
                'bootstrap.servers': 'kafka:9092'
            }
            producer = Producer(conf)
            logger.info("Kafka Producer (confluent_kafka) inicializado com sucesso.")
            return producer
        except Exception as e:
            logger.warning(f"Tentativa {attempt + 1}: Kafka indisponível. Erro: {e}")
            time.sleep(delay)
    raise RuntimeError("Kafka Producer não pôde ser inicializado.")


@app.post("/process-instruments/")
async def process_instruments_endpoint(csv_file: UploadFile = File(...)):
    """
    Endpoint para processar um arquivo CSV de instrumentos da B3.
    Realiza padronização de tickers e envia apenas os válidos para Kafka.
    """
    producer = get_kafka_producer_with_retry()

    if not csv_file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="O arquivo deve ser um CSV.")

    try:
        content = await csv_file.read()
        df = pd.read_csv(io.BytesIO(content), encoding="latin1", sep=";", low_memory=False, skiprows=1)
        logger.info(f"Arquivo '{csv_file.filename}' recebido e lido. Tamanho: {len(content)} bytes.")
    except Exception as e:
        logger.error(f"Erro ao ler o arquivo CSV de upload: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Erro ao ler o arquivo CSV: {e}")

    try:
        acoes_b3 = df[
            (df["SctyCtgyNm"] == "SHARES") &
            (df["MktNm"] == "EQUITY-CASH") &
            (df["SgmtNm"] == "CASH")
        ].copy()

        resultado = acoes_b3[["TckrSymb", "CrpnNm", "ISIN", "MktCptlstn"]]
        resultado.columns = ["Ticker", "Nome", "ISIN", "MarketCap"]

        temp_df = resultado.copy()
        valid_indices = []

        for index, row in temp_df.iterrows():
            ticker_padronizado = standardize_b3_ticker(row["Ticker"])
            if not ticker_padronizado:
                continue

            try:
                # Validação via Yahoo Finance
                ticker_obj = yf.Ticker(ticker_padronizado)
                info = ticker_obj.info
                if info and info.get("regularMarketPrice") is not None:
                    resultado.at[index, "Ticker"] = ticker_padronizado
                    valid_indices.append(index)
                else:
                    logger.warning(f"[Filtro] Ticker sem info válida no Yahoo Finance: {ticker_padronizado}")
            except Exception as e:
                logger.warning(f"[Filtro] Erro ao validar ticker {ticker_padronizado} via Ticker.info: {e}")

        resultado = resultado.loc[valid_indices]
        logger.info(f"Total de tickers válidos com info no Yahoo Finance: {len(resultado)}")

        if len(resultado) == 0:
            raise HTTPException(status_code=400, detail="Nenhum ticker válido foi encontrado.")

        for _, row in resultado.iterrows():
            message = row.to_dict()
            producer.produce('standardized_instruments_topic', value=json.dumps(message).encode('utf-8'))
            logger.debug(f"Enviado para Kafka: {message['Ticker']}")

        producer.flush()
        logger.info("Todos os instrumentos padronizados válidos foram enviados para o Kafka.")

        return {
            "message": "Processamento concluído com sucesso.",
            "valid_tickers": len(resultado)
        }

    except Exception as e:
        logger.error(f"Erro durante o processamento dos instrumentos: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro interno no processamento: {e}")
