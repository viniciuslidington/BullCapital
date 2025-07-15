from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from services.market_download import download_and_normalize_ticker_data
import logging
import requests
import os
import json
import pandas as pd

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_STORAGE_URL = os.getenv("STORAGE_SERVICE_URL", "http://data_storage_service:8000/data/bulk")

class TickerInput(BaseModel):
    tickers: List[str]

@app.post("/download-tickers/")
async def download_tickers(payload: TickerInput):
    resultados = []

    # Chama a função passando a lista de tickers de uma vez
    ticker_data_dict = download_and_normalize_ticker_data(payload.tickers)
    for df in ticker_data_dict.values():
        if df is not None:
            # Sanitização de valores inválidos
            df.replace([float("inf"), float("-inf")], None, inplace=True)
            df = df.fillna(0)
            registros = df.to_dict(orient="records")
            resultados.extend(registros)
        else:
            logger.warning(f"Um dos tickers não retornou dados válidos.")

    if not resultados:
        raise HTTPException(status_code=404, detail="Nenhum dado foi retornado para os tickers informados.")

    try:
        # Envia os dados via POST para o serviço de armazenamento
        response = requests.post(DATA_STORAGE_URL, json=resultados)
        response.raise_for_status()
        logger.info(f"Dados enviados com sucesso para o serviço de armazenamento. Total: {len(resultados)} registros.")
    except Exception as e:
        logger.error(f"Erro inesperado ao enviar dados para data_storage_service: {e}")
        raise HTTPException(status_code=500, detail="Erro ao enviar dados para o serviço de armazenamento.")

    return {"result": resultados, "total": len(resultados)}
