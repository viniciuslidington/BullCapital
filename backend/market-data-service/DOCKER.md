# Docker Usage Guide

## Quick Start

```bash
# Build the image
./docker.sh build

# Run the container
./docker.sh run

# Check status
./docker.sh status

# View logs
./docker.sh logs

# Stop container
./docker.sh stop
```

## Environment Variables

O container carrega as variáveis de ambiente do arquivo `.env`. As seguintes variáveis podem ser configuradas:

### Configuração Básica
- `DEBUG=false` - Modo debug (true/false)
- `LOG_LEVEL=INFO` - Nível de log (DEBUG, INFO, WARNING, ERROR)
- `HOST=0.0.0.0` - Host do servidor
- `PORT=8002` - Porta do servidor

### API Configuration
- `API_VERSION=1.0.0` - Versão da API
- `API_TITLE=Market Data Service` - Título da API
- `API_DESCRIPTION=Microserviço para dados de mercado financeiro` - Descrição

### CORS
- `ALLOWED_ORIGINS=["*"]` - Origens permitidas para CORS

### Cache
- `CACHE_TTL_SECONDS=300` - TTL do cache em segundos
- `ENABLE_CACHE=true` - Habilitar cache (true/false)

### Rate Limiting
- `RATE_LIMIT_REQUESTS=100` - Número de requests permitidos
- `RATE_LIMIT_WINDOW=60` - Janela de tempo em segundos

### APIs Externas
- `YAHOO_FINANCE_TIMEOUT=30` - Timeout para Yahoo Finance
- `MAX_RETRIES=3` - Número máximo de tentativas

## Docker Commands Manual

```bash
# Build image
docker build -t market-data-service .

# Run container with environment file
docker run -d \
  --name market-data-service-container \
  -p 8002:8002 \
  --env-file .env \
  --restart unless-stopped \
  market-data-service

# View logs
docker logs -f market-data-service-container

# Stop container
docker stop market-data-service-container
docker rm market-data-service-container
```

## Health Check

O container inclui um health check automático que verifica:
- Endpoint: `http://localhost:8002/health`
- Intervalo: 30 segundos
- Timeout: 10 segundos
- Start period: 60 segundos
- Retries: 3

## Endpoints Disponíveis

- **Health Check**: `GET /health`
- **API Documentation**: `GET /docs`
- **OpenAPI Schema**: `GET /openapi.json`
- **Market Data**: `GET /api/v1/stock/{ticker}`

## Multi-stage Build

O Dockerfile usa multi-stage build para:
1. **Builder stage**: Instala dependências de build
2. **Production stage**: Cria imagem final otimizada

### Benefícios:
- Imagem final menor
- Melhor cache de layers
- Separação de dependências de build e runtime
- Melhor segurança

## Security Features

- **Non-root user**: Container roda com usuário `app` (UID 1001)
- **Minimal base image**: Python 3.12 slim
- **No build tools**: Apenas dependências de runtime na imagem final
- **Environment variables**: Configuração segura via .env
