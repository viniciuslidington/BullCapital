FROM python:3.11-slim

WORKDIR /app

COPY . /app
COPY .env /app/.env

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

EXPOSE 8001

CMD ["uvicorn", "app.api_server:app", "--host", "0.0.0.0", "--port", "8001"]
