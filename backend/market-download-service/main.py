from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from services.market_download import download_and_normalize_ticker_data
import logging
import requests
import os
import json
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_STORAGE_URL = os.getenv("STORAGE_SERVICE_URL", "http://data_storage_service:8000/data/bulk")

class TickerInput(BaseModel):
    tickers: List[str]

@app.post("/download-tickers/")
async def download_tickers(payload: TickerInput):
    import yfinance as yf
    resultados = []
    tickers = payload.tickers

    # Chama a função passando a lista de tickers de uma vez
    ticker_data_dict = download_and_normalize_ticker_data(tickers)

    # Função para buscar info de um ticker
    def fetch_info(ticker):
        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info
            return ticker, {
                'symbol': info.get('symbol', ticker),
                'shortName': info.get('shortName'),
                'longName': info.get('longName'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'exchange': info.get('exchange'),
            }
        except Exception as e:
            logger.warning(f"Não foi possível obter info para {ticker}: {e}")
            return ticker, {'symbol': ticker}

    # Busca info de todos os tickers em paralelo
    info_dict = {}
    with ThreadPoolExecutor(max_workers=min(8, len(tickers))) as executor:
        future_to_ticker = {executor.submit(fetch_info, ticker): ticker for ticker in tickers}
        for future in as_completed(future_to_ticker):
            ticker, info_fields = future.result()
            info_dict[ticker] = info_fields

    # Monta os resultados
    for ticker, df in ticker_data_dict.items():
        if df is not None:
            df.replace([float("inf"), float("-inf")], None, inplace=True)
            df = df.fillna(0)
            registros = df.to_dict(orient="records")
            info_fields = info_dict.get(ticker, {'symbol': ticker})
            cleaned_info_fields = {
                k: (v if v is not None else "N/A")
                for k, v in info_fields.items()
            }
            for r in registros:
                r.update(cleaned_info_fields)
            resultados.extend(registros)
        else:
            logger.warning(f"Um dos tickers não retornou dados válidos.")

    if not resultados:
        raise HTTPException(status_code=404, detail="Nenhum dado foi retornado para os tickers informados.")

    try:
        payload_json = json.dumps(resultados, default=str)
        response = requests.post(DATA_STORAGE_URL, data=payload_json, headers={"Content-Type": "application/json"})
        logger.info(f"Resposta do storage: {response.status_code} - {response.content}")
        response.raise_for_status()
        logger.info(f"Dados enviados com sucesso para o serviço de armazenamento. Total: {len(resultados)} registros.")
    except Exception as e:
        logger.error(f"Erro inesperado ao enviar dados para data_storage_service: {e}")
        raise HTTPException(status_code=500, detail="Erro ao enviar dados para o serviço de armazenamento.")

    return {"result": resultados, "total": len(resultados)}
