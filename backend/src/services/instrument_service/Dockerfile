# instrument_ingestion_service/Dockerfile
FROM python:3.9-slim-buster

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo de dependências para o diretório de trabalho
# É importante copiar primeiro apenas o que muda com menos frequência para aproveitar o cache do Docker
COPY pyproject.toml ./

# Instala o UV (se ainda não estiver na imagem base, ou para garantir a versão)
RUN pip install uv

# Instala as dependências usando uv
# O --system é para garantir que ele instale no ambiente do contêiner, não em um venv interno
RUN uv pip install -r pyproject.toml --system

# Copia todo o restante do código do seu projeto para o contêiner
COPY . .

# Expõe a porta que o FastAPI vai usar
EXPOSE 8000

# Comando para iniciar a aplicação FastAPI usando Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]