# market_data_downloader_service/Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
RUN pip install uv
RUN uv pip install -r pyproject.toml --system
COPY . .
CMD ["python", "main.py"]