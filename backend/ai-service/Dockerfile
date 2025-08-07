# Usa imagem base oficial do Python
FROM python:3.11-slim

# Evita buffer de logs
ENV PYTHONUNBUFFERED=1

# Cria diretório de trabalho no container
WORKDIR /app

# Copia os arquivos de requisitos e instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o conteúdo da pasta local para o container
COPY . .

# Comando padrão (já definido no docker-compose, então não obrigatório aqui)
CMD ["uvicorn", "app.api_server:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
