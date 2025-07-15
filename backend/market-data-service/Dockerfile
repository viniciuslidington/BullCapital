# Multi-stage build para otimizar tamanho da imagem
FROM python:3.12-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy and install dependencies (better caching)
COPY pyproject.toml ./
RUN pip install --no-cache-dir --user -e .

# Production stage
FROM python:3.12-slim as production

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user with specific UID
RUN useradd --create-home --shell /bin/bash --uid 1001 app

# Copy installed packages from builder stage
COPY --from=builder /root/.local /home/app/.local

# Set working directory to app subdirectory
WORKDIR /app/app

# Copy environment configuration and application code
COPY --chown=app:app .env /app/
COPY --chown=app:app app/ ./

# Switch to non-root user
USER app

# Set environment variables with correct paths for the app structure
ENV PATH=/home/app/.local/bin:$PATH \
    PYTHONPATH=/app/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # Default environment variables (can be overridden)
    DEBUG=false \
    LOG_LEVEL=INFO \
    HOST=0.0.0.0 \
    PORT=8002 \
    CACHE_TTL_SECONDS=300 \
    ENABLE_CACHE=true \
    RATE_LIMIT_REQUESTS=100 \
    RATE_LIMIT_WINDOW=60 \
    YAHOO_FINANCE_TIMEOUT=30 \
    MAX_RETRIES=3

# Health check with environment variable support
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port (using environment variable)
EXPOSE ${PORT}

# Run from the correct directory with relative imports
CMD ["sh", "-c", "uvicorn main:app --host ${HOST} --port ${PORT} --workers 1"]
