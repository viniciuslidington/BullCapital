# Dockerfile para o Gateway Service (FastAPI)
FROM python:3.12-slim

# Diretório de trabalho
WORKDIR /app

# Copia o arquivo de dependências
COPY requirements.txt ./

# Instala as dependências
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

# Expõe a porta do gateway
EXPOSE 8000

# Comando para rodar o serviço
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
