FROM python:3.13-slim

WORKDIR /app

COPY . .

RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends gcc && \
    pip install --upgrade pip && \
    pip install --upgrade pip setuptools wheel && \
    pip install --upgrade build && \
    pip install . && \
    apt-get purge -y --auto-remove gcc && \
    rm -rf /var/lib/apt/lists/*

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]