# main.py do Instrument Ingestion & Standardization Service
from fastapi import FastAPI, UploadFile, File, HTTPException
import pandas as pd
import logging
import json
import io
from kafka import KafkaProducer

from utils import standardize_b3_ticker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configuração do Kafka Producer (ajuste 'kafka:9092' para o seu broker Kafka)
# O tópico 'standardized_instruments_topic' será o output para o próximo serviço
try:
    producer = KafkaProducer(
        bootstrap_servers='kafka:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        api_version=(0, 10, 1)
    )
    logger.info("Kafka Producer inicializado com sucesso.")
except Exception as e:
    logger.error(f"Falha ao inicializar Kafka Producer: {e}. Verifique se o Kafka está rodando.")
    # Dependendo da estratégia de erro, pode ser um erro fatal ou tentar reconectar

@app.post("/process-instruments/")
async def process_instruments_endpoint(csv_file: UploadFile = File(...)): # <--- Mudança aqui: File(...) agora é obrigatório
    """
    Endpoint para processar um arquivo CSV de instrumentos da B3.
    Recebe o arquivo CSV diretamente via upload.
    """
    if not csv_file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="O arquivo deve ser um CSV.")

    try:
        content = await csv_file.read()
        df = pd.read_csv(io.BytesIO(content), encoding="latin1", sep=";", low_memory=False, skiprows=1)
        logger.info(f"Arquivo '{csv_file.filename}' recebido e lido. Tamanho: {len(content)} bytes.")
    except Exception as e:
        logger.error(f"Erro ao ler o arquivo CSV de upload: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Erro ao ler o arquivo CSV: {e}")

    # --- Lógica de Processamento do seu código original ---
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
            if ticker_padronizado:
                resultado.at[index, "Ticker"] = ticker_padronizado
                valid_indices.append(index)
        
        resultado = resultado.loc[valid_indices]
        
        logger.info(f"Processamento concluído. {len(resultado)} instrumentos padronizados encontrados.")

        if producer.bootstrap_connected(): # Verifica se o produtor está conectado antes de enviar
            for _, row in resultado.iterrows():
                message = row.to_dict()
                producer.send('standardized_instruments_topic', message)
                logger.debug(f"Enviado para Kafka: {message['Ticker']}")
            
            producer.flush()
            logger.info("Todos os instrumentos padronizados foram enviados para o Kafka.")
        else:
            logger.error("Kafka Producer não conectado. Mensagens não enviadas.")
            raise HTTPException(status_code=500, detail="Serviço Kafka indisponível para enviar dados processados.")
        
        return {"message": "Processamento concluído e dados enviados para o pipeline.", "count": len(resultado)}

    except Exception as e:
        logger.error(f"Erro no processamento principal do instrumento: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro interno no processamento: {e}")