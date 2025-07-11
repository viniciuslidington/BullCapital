# market_data_downloader_service/main.py
import logging
import json
import os
import pandas as pd
# Removido: from kafka import KafkaConsumer, KafkaProducer
# Adicionado:
from confluent_kafka import Consumer, Producer, KafkaException, KafkaError
import sys # Adicionado para sys.stderr

# Importa a função de download e normalização
from services.market_download import download_and_normalize_ticker_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configurações do Kafka (obtidas de variáveis de ambiente) ---
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')
INPUT_TOPIC = 'standardized_instruments_topic'
OUTPUT_TOPIC = 'normalized_market_data_topic'

# --- Parâmetros de Download de Dados (obtidas de variáveis de ambiente) ---
START_DATE = os.getenv('DOWNLOAD_START_DATE', None)
END_DATE = os.getenv('DOWNLOAD_END_DATE', None)
PERIOD = os.getenv('DOWNLOAD_PERIOD', '1y')
INTERVAL = os.getenv('DOWNLOAD_INTERVAL', '1d')

# Inicialização do Kafka Consumer (usando confluent_kafka)
try:
    consumer = Consumer({
        'bootstrap.servers': KAFKA_BROKER,
        'group.id': 'market-data-downloader-group',
        'auto.offset.reset': 'earliest' # Começa a ler do início se não houver offset salvo
    })
    consumer.subscribe([INPUT_TOPIC]) # O consumidor deve ser explicitamente inscrito no tópico
    logger.info(f"Kafka Consumer inicializado para o tópico '{INPUT_TOPIC}'.")
except Exception as e:
    logger.error(f"Falha ao inicializar Kafka Consumer: {e}. Verifique se o Kafka está rodando.", exc_info=True)
    sys.exit(1) # Usa sys.exit para sair em caso de erro crítico

# Inicialização do Kafka Producer (usando confluent_kafka)
try:
    producer = Producer({'bootstrap.servers': KAFKA_BROKER})
    logger.info(f"Kafka Producer inicializado para o tópico '{OUTPUT_TOPIC}'.")
except Exception as e:
    logger.error(f"Falha ao inicializar Kafka Producer: {e}. Verifique se o Kafka está rodando.", exc_info=True)
    sys.exit(1) # Usa sys.exit para sair em caso de erro crítico

# Callback para reportar erros de entrega do produtor (opcional, mas boa prática)
def delivery_report(err, msg):
    """ Chamado uma vez para cada mensagem produzida para reportar o status de entrega.
        Falhas de entrega são reportadas em 'err'. """
    if err is not None:
        logger.error(f"Falha na entrega da mensagem para o tópico {msg.topic()}: {err}")
    else:
        logger.debug(f"Mensagem entregue para o tópico {msg.topic()} [{msg.partition()}] @ offset {msg.offset()}")


def main():
    logger.info(f"Serviço de Download de Dados de Mercado iniciado, aguardando mensagens do tópico '{INPUT_TOPIC}'...")
    
    while True: # Loop contínuo para consumir mensagens
        msg = consumer.poll(timeout=1.0) # Espera por uma mensagem por 1 segundo

        if msg is None:
            # Nenhuma mensagem em 1 segundo, continua esperando
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # Fim da partição (não é um erro grave, apenas sinaliza que não há mais mensagens por enquanto)
                logger.info(f"Fim da partição alcançado para {msg.topic()} [{msg.partition()}] em offset {msg.offset()}")
            else:
                # Outros erros do consumidor
                logger.error(f"Erro do consumidor: {msg.error()}", exc_info=True)
            continue

        try:
            # Decodifica e desserializa a mensagem JSON
            instrument_data = json.loads(msg.value().decode('utf-8'))
            ticker = instrument_data.get('Ticker')
            
            if not ticker:
                logger.warning(f"Mensagem recebida sem Ticker válido: {instrument_data}. Ignorando.")
                continue

            logger.info(f"Recebido instrumento para processar: {ticker}")

            # Baixa e normaliza os dados históricos para o ticker
            normalized_df = download_and_normalize_ticker_data(
                ticker,
                start_date=START_DATE,
                end_date=END_DATE,
                period=PERIOD,
                interval=INTERVAL
            )

            if normalized_df is not None and not normalized_df.empty:
                # Publica cada linha do DataFrame normalizado no tópico de saída
                for _, row in normalized_df.iterrows():
                    # Confluent Kafka precisa que a mensagem seja um objeto bytes
                    producer.produce(OUTPUT_TOPIC, value=json.dumps(row.to_dict()).encode('utf-8'), callback=delivery_report)
                
                # O poll do produtor é importante para processar callbacks de entrega e evitar que a fila interna do produtor cresça indefinidamente
                producer.poll(0)
                producer.flush() # Garante que todas as mensagens sejam enviadas antes de continuar
                logger.info(f"Dados históricos para {ticker} enviados para o tópico '{OUTPUT_TOPIC}'.")
            else:
                logger.warning(f"Nenhum dado normalizado para enviar para {ticker}.")
        
        except Exception as e:
            logger.error(f"Erro ao processar mensagem do Kafka: {e}", exc_info=True)
        
        # Não é necessário time.sleep(0.1) com consumer.poll(timeout=...)

if __name__ == '__main__':
    main()