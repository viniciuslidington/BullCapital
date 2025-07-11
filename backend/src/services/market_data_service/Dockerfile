# market_data_downloader_service/Dockerfile
FROM python:3.9-slim-buster
WORKDIR /app
COPY pyproject.toml ./
RUN pip install uv
RUN uv pip install -r pyproject.toml --system
COPY . .
CMD ["python", "main.py"]