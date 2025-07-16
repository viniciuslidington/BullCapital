# Market Data Service

Microserviço responsável por fornecer dados de mercado financeiro em tempo real e históricos.

## Características

- 🚀 FastAPI com documentação automática
- 📊 Integração com Yahoo Finance
- 🔍 Busca avançada de tickers
- 📈 Dados históricos e em tempo real
- 🏗️ Arquitetura baseada em princípios SOLID
- 📝 Documentação completa com docstrings
- ⚡ Alta performance e escalabilidade

## Funcionalidades

### Endpoints Principais

- **GET /api/v1/market-data/stocks/{symbol}** - Dados de uma ação específica
- **GET /api/v1/market-data/stocks/search** - Busca de ações por nome/símbolo
- **GET /api/v1/market-data/stocks/trending** - Ações em tendência
- **GET /api/v1/market-data/tickers** - Lista todos os tickers disponíveis
- **POST /api/v1/market-data/bulk** - Dados em lote para múltiplos tickers

### Recursos Avançados

- Validação de tickers
- Filtros por setor e mercado
- Dados fundamentais opcionais
- Cache inteligente
- Rate limiting
- Logs estruturados

## Execução

```bash
# Instalar dependências
pip install -e .

# Executar o serviço
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

## Documentação da API

Acesse `http://localhost:8002/docs` para a documentação interativa da API.

## Arquitetura

```
app/
├── api/           # Endpoints da API
├── core/          # Configurações e utilitários
├── models/        # Modelos Pydantic
├── services/      # Lógica de negócio
└── utils/         # Utilitários gerais
```
