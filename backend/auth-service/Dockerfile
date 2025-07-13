FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables with your Supabase configuration
ENV PYTHONPATH=/app
ENV user=postgres.qijzmfwejylkxhflkssd
ENV password=bullcapital2025!
ENV host=aws-0-sa-east-1.pooler.supabase.com
ENV port=6543
ENV dbname=postgres
ENV SECRET_KEY=8f2a9c5e7b1d4f6a3e8c9f2b5d7a1c4e6f9b2d5a8c1e4f7a0d3c6f9e2b5a8d1c4f7
ENV ALGORITHM=HS256
ENV ACCESS_TOKEN_EXPIRE_MINUTES=30
ENV DEBUG_SQL=false
ENV ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8000"]

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]
