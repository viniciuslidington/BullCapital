# API de Descoberta de Tickers - BullCapital Backend

## Visão Geral

A API de descoberta de tickers foi integrada ao endpoint `/api/v1/market/` e oferece funcionalidades completas para gerenciamento e consulta de tickers de ações brasileiras (B3) e americanas (NASDAQ/NYSE).

## Novos Endpoints Implementados

### 1. Listar Todos os Tickers
**GET** `/api/v1/market/tickers`

Lista todos os tickers disponíveis no sistema com opções de filtro.

**Parâmetros de Query:**
- `market` (opcional): Filtrar por mercado (B3, NASDAQ, NYSE)
- `sector` (opcional): Filtrar por setor específico

**Exemplo de Uso:**
```bash
# Listar todos os tickers
curl "http://localhost:8000/api/v1/market/tickers"

# Filtrar apenas ações brasileiras
curl "http://localhost:8000/api/v1/market/tickers?market=B3"

# Filtrar por setor de energia
curl "http://localhost:8000/api/v1/market/tickers?sector=Energy"
```

**Resposta de Exemplo:**
```json
{
    "total_tickers": 41,
    "filters": {
        "market": "B3",
        "sector": null
    },
    "tickers": [
        {
            "symbol": "PETR4.SA",
            "name": "Petróleo Brasileiro S.A. - Petrobras",
            "sector": "Energy",
            "market": "B3"
        }
    ]
}
```

### 2. Buscar Tickers
**GET** `/api/v1/market/tickers/search`

Busca tickers por nome da empresa ou símbolo.

**Parâmetros de Query:**
- `query` (obrigatório): Termo de busca
- `limit` (opcional): Número máximo de resultados (1-50, padrão: 10)

**Exemplo de Uso:**
```bash
curl "http://localhost:8000/api/v1/market/tickers/search?query=Petrobras&limit=3"
```

**Resposta de Exemplo:**
```json
{
    "query": "Petrobras",
    "results_found": 2,
    "tickers": [
        {
            "symbol": "PETR4.SA",
            "name": "Petróleo Brasileiro S.A. - Petrobras",
            "sector": "Energy",
            "market": "B3"
        }
    ]
}
```

### 3. Validar Ticker
**GET** `/api/v1/market/tickers/validate/{symbol}`

Valida se um ticker existe e retorna informações básicas.

**Parâmetros de Path:**
- `symbol`: Símbolo do ticker para validar

**Exemplo de Uso:**
```bash
curl "http://localhost:8000/api/v1/market/tickers/validate/PETR4"
```

**Resposta de Exemplo:**
```json
{
    "valid": true,
    "symbol": "PETR4.SA",
    "name": "Petróleo Brasileiro S.A. - Petrobras",
    "sector": "Energy",
    "market": "B3"
}
```

### 4. Listar Setores Disponíveis
**GET** `/api/v1/market/tickers/sectors`

Lista todos os setores disponíveis no sistema.

**Parâmetros de Query:**
- `market` (opcional): Filtrar por mercado específico

**Exemplo de Uso:**
```bash
curl "http://localhost:8000/api/v1/market/tickers/sectors?market=B3"
```

**Resposta de Exemplo:**
```json
{
    "market_filter": "B3",
    "total_sectors": 11,
    "sectors": [
        "Communication Services",
        "Consumer Cyclical",
        "Consumer Staples",
        "Energy",
        "Financial Services",
        "Healthcare",
        "Industrials",
        "Materials",
        "Real Estate",
        "Technology",
        "Utilities"
    ]
}
```

### 5. Listar Mercados Disponíveis
**GET** `/api/v1/market/tickers/markets`

Lista todos os mercados disponíveis no sistema.

**Exemplo de Uso:**
```bash
curl "http://localhost:8000/api/v1/market/tickers/markets"
```

**Resposta de Exemplo:**
```json
{
    "total_markets": 3,
    "markets": [
        "B3",
        "NASDAQ",
        "NYSE"
    ]
}
```

### 6. Dados em Tempo Real
**GET** `/api/v1/market/tickers/{symbol}/live`

Obtém informações completas de um ticker com dados em tempo real do Yahoo Finance.

**Parâmetros de Path:**
- `symbol`: Símbolo do ticker

**Exemplo de Uso:**
```bash
curl "http://localhost:8000/api/v1/market/tickers/PETR4.SA/live"
```

**Resposta de Exemplo:**
```json
{
    "symbol": "PETR4.SA",
    "name": "Petróleo Brasileiro S.A. - Petrobras",
    "sector": "Energy",
    "industry": "Oil & Gas Integrated",
    "market": "B3",
    "current_price": 32.26,
    "previous_close": 32.12,
    "market_cap": 435013189632,
    "volume": 5259200,
    "currency": "BRL",
    "last_updated": "2025-07-10T23:51:45.656704"
}
```

## Integração com Outros Endpoints

Os novos endpoints de descoberta de tickers podem ser utilizados em conjunto com os endpoints existentes:

### Fluxo de Uso Recomendado:

1. **Descobrir tickers**: Use `/tickers/search` para encontrar símbolos relevantes
2. **Validar ticker**: Use `/tickers/validate/{symbol}` para confirmar que o ticker é válido
3. **Obter dados históricos**: Use `/stock/{symbol}` para dados detalhados com histórico
4. **Obter dados em tempo real**: Use `/tickers/{symbol}/live` para preços atuais

### Exemplo de Integração:
```bash
# 1. Buscar tickers relacionados a "banco"
curl "http://localhost:8000/api/v1/market/tickers/search?query=banco"

# 2. Validar um ticker específico encontrado
curl "http://localhost:8000/api/v1/market/tickers/validate/ITUB4"

# 3. Obter dados detalhados com histórico
curl "http://localhost:8000/api/v1/market/stock/ITUB4.SA?include_history=true"

# 4. Obter dados em tempo real
curl "http://localhost:8000/api/v1/market/tickers/ITUB4.SA/live"
```

## Estrutura de Dados

### Ticker Object
```json
{
    "symbol": "string",      // Símbolo do ticker (ex: "PETR4.SA")
    "name": "string",        // Nome da empresa
    "sector": "string",      // Setor da empresa
    "market": "string"       // Mercado (B3, NASDAQ, NYSE)
}
```

### Live Data Object
```json
{
    "symbol": "string",
    "name": "string",
    "sector": "string",
    "industry": "string",
    "market": "string",
    "current_price": "number",
    "previous_close": "number",
    "market_cap": "number",
    "volume": "number",
    "currency": "string",
    "last_updated": "string"
}
```

## Base de Dados de Tickers

Atualmente o sistema conta com:
- **41 ações brasileiras (B3)**: Principais ações do Ibovespa
- **15 ações americanas**: Principais ações do S&P 500
- **11 setores diferentes**: Cobrindo diversos segmentos da economia

### Setores Disponíveis:
- Communication Services
- Consumer Cyclical
- Consumer Staples
- Energy
- Financial Services
- Healthcare
- Industrials
- Materials
- Real Estate
- Technology
- Utilities

## Tratamento de Erros

Todos os endpoints retornam códigos de status HTTP apropriados:

- **200 OK**: Sucesso
- **404 Not Found**: Ticker não encontrado
- **422 Unprocessable Entity**: Parâmetros inválidos
- **500 Internal Server Error**: Erro interno do servidor

### Exemplo de Resposta de Erro:
```json
{
    "detail": "Ticker 'INVALID' não encontrado"
}
```

## Próximos Passos

1. **Expansão da Base de Dados**: Integração com APIs externas para aumentar o número de tickers
2. **Cache**: Implementar cache Redis para melhorar performance
3. **Rate Limiting**: Adicionar limitação de taxa para APIs externas
4. **Websockets**: Dados em tempo real via websockets
5. **Alertas**: Sistema de alertas baseado em preços

## Acesso à Documentação Interativa

Após iniciar o servidor, você pode acessar:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Estes endpoints estarão listados na seção "Market Data" da documentação interativa.
