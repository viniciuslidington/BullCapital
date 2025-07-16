from fastapi import FastAPI, status
import logging
from typing import List, Dict
from collections import defaultdict

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Armazenamento em memória
market_data_store: Dict[str, List[dict]] = defaultdict(list)

@app.post("/data/bulk", status_code=status.HTTP_201_CREATED)
async def receive_bulk_market_data(market_data_list: List[dict]):
    logger.info(f"[MOCK] Recebido POST com {len(market_data_list)} registros.")
    for entry in market_data_list:
        ticker = entry.get("ticker")
        if ticker:
            market_data_store[ticker].append(entry)
    return {"message": "Mock: dados recebidos com sucesso.", "received": len(market_data_list)}

@app.get("/api/data/{ticker}")
async def get_market_data(ticker: str):
    logger.info(f"[MOCK] Consulta GET para ticker: {ticker}")
    data = market_data_store.get(ticker.upper(), [])
    if not data:
        return {"message": f"Nenhum dado encontrado para o ticker {ticker}."}
    return data

@app.get("/api/tickers")
async def get_all_tickers():
    logger.info("[MOCK] Consulta GET para todos os tickers.")
    return {"tickers": list(market_data_store.keys())}

@app.get("/api/tickers/summary")
async def get_ticker_summary():
    return {
        ticker: len(records)
        for ticker, records in market_data_store.items()
    }

