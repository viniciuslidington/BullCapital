from fastapi import FastAPI, UploadFile, File, HTTPException
import pandas as pd
import logging
import json
import io
import yfinance as yf
import requests
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List
from utils.utils import standardize_b3_ticker
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# URL do outro serviço
DOWNLOAD_SERVICE = os.getenv("DOWNLOAD_SERVICE", "http://market_data_service:8000/download-tickers/")
MAX_WORKERS = 12  # Número ideal para evitar bloqueio

def validar_ticker(row, retries=3):
    """Valida e retorna o dicionário apenas se for um ticker válido"""
    ticker_padronizado = standardize_b3_ticker(row["Ticker"])
    if not ticker_padronizado:
        return None

    for attempt in range(retries):
        try:
            # Sleep aleatório para evitar bloqueio
            time.sleep(random.uniform(0.4, 1.2))

            ticker_obj = yf.Ticker(ticker_padronizado)
            info = ticker_obj.info

            if info and info.get("regularMarketPrice") is not None:
                return {
                    "Ticker": ticker_padronizado,
                    "Nome": row["Nome"],
                    "ISIN": row["ISIN"],
                    "MarketCap": row["MarketCap"]
                }
            else:
                logger.warning(f"[Filtro] Ticker sem preço: {ticker_padronizado}")
                return None

        except Exception as e:
            logger.warning(f"[Filtro] Tentativa {attempt+1} falhou com {ticker_padronizado}: {e}")
            time.sleep(1)

    return None


@app.post("/process-instruments/")
async def process_instruments_endpoint(csv_file: UploadFile = File(...)):
    if not csv_file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="O arquivo deve ser um CSV.")

    try:
        content = await csv_file.read()
        df = pd.read_csv(io.BytesIO(content), encoding="latin1", sep=";", low_memory=False, skiprows=1)
        logger.info(f"Arquivo '{csv_file.filename}' recebido. Tamanho: {len(content)} bytes.")
    except Exception as e:
        logger.error(f"Erro ao ler CSV: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Erro ao ler o arquivo CSV: {e}")

    try:
        acoes_b3 = df[
            (df["SctyCtgyNm"] == "SHARES") &
            (df["MktNm"] == "EQUITY-CASH") &
            (df["SgmtNm"] == "CASH")
        ].copy()

        resultado = acoes_b3[["TckrSymb", "CrpnNm", "ISIN", "MktCptlstn"]]
        resultado.columns = ["Ticker", "Nome", "ISIN", "MarketCap"]

        registros = resultado.to_dict(orient="records")
        logger.info(f"Iniciando validação paralela de {len(registros)} tickers...")

        validos: List[dict] = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_row = {executor.submit(validar_ticker, row): row for row in registros}
            for future in as_completed(future_to_row):
                result = future.result()
                if result:
                    validos.append(result)

        logger.info(f"Total de tickers válidos: {len(validos)}")

        if not validos:
            raise HTTPException(status_code=400, detail="Nenhum ticker válido foi encontrado.")

        # Envia os tickers válidos em um único POST para o serviço de download
        payload = {"tickers": [d["Ticker"] for d in validos]}

        try:
            response = requests.post(DOWNLOAD_SERVICE, json=payload)
            response.raise_for_status()
            logger.info(f"POST enviado com sucesso para market_data_service.")
        except Exception as e:
            logger.error(f"Erro ao enviar tickers para o serviço de download: {e}")
            raise HTTPException(status_code=500, detail="Erro ao enviar tickers para download.")

        return {
            "message": "Processamento concluído com sucesso.",
            "valid_tickers": len(validos)
        }

    except Exception as e:
        logger.error(f"Erro durante o processamento: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")
