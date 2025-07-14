import asyncio
import json
import logging
import os
from fastapi import FastAPI
from confluent_kafka import Consumer, KafkaException, KafkaError
import httpx  # Para fazer HTTP async POST
from services.market_download import download_and_normalize_ticker_data
from contextlib import asynccontextmanager

logger = logging.getLogger("market_data_service")
logging.basicConfig(level=logging.INFO)

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')
INPUT_TOPIC = 'standardized_instruments_topic'
STORAGE_SERVICE_URL = os.getenv('STORAGE_SERVICE_URL', 'http://market_data_storage_api_service:8000/data/bulk')


consumer = Consumer({
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': 'market-data-downloader-group',
    'auto.offset.reset': 'earliest'
})
consumer.subscribe([INPUT_TOPIC])

async def consume_and_process():
    logger.info(f"Consumidor Kafka ativo no tópico '{INPUT_TOPIC}'")
    async with httpx.AsyncClient() as client:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                await asyncio.sleep(1)
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logger.info(f"Fim da partição alcançado {msg.topic()} [{msg.partition()}] offset {msg.offset()}")
                else:
                    logger.error(f"Erro do consumidor Kafka: {msg.error()}")
                continue

            try:
                instrument_data = json.loads(msg.value())
                ticker = instrument_data.get('Ticker')
                if not ticker:
                    logger.warning(f"Mensagem sem ticker: {instrument_data}")
                    continue

                logger.info(f"Processando ticker: {ticker}")
                df = download_and_normalize_ticker_data(ticker)
                if df is None or df.empty:
                    logger.warning(f"Sem dados para ticker {ticker}")
                    continue

                data_json = df.to_dict(orient='records')
                response = await client.post(STORAGE_SERVICE_URL, json=data_json, timeout=300)
                response.raise_for_status()
                logger.info(f"Dados enviados para Storage Service para ticker {ticker} (status {response.status_code})")

            except Exception as e:
                logger.error(f"Erro ao processar ticker ou enviar dados: {e}", exc_info=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(consume_and_process())
    logger.info("Task do consumidor Kafka iniciada com lifespan.")
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            logger.info("Task do consumidor Kafka cancelada.")
        consumer.close()
        logger.info("Kafka Consumer fechado.")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Market Data Downloader Service está rodando."}
