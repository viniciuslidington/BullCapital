# 🧪 Guia de Testes Práticos - Market Data API

Este guia mostra como testar todos os endpoints com exemplos reais e práticos.

## 🚀 Preparação

1. **Certifique-se que o serviço está rodando:**
   ```bash
   # Verificar se está online
   curl http://localhost:8002/api/v1/market-data/health
   ```

2. **Acesse a documentação interativa:**
   - Swagger UI: http://localhost:8002/docs
   - ReDoc: http://localhost:8002/redoc

## 📊 1. Dados de Ações (/stocks/{symbol})

### Testes Básicos
```bash
# Petrobras - dados básicos (1 mês)
curl "http://localhost:8002/api/v1/market-data/stocks/PETR4.SA"

# Apple - tendência anual
curl "http://localhost:8002/api/v1/market-data/stocks/AAPL?period=1y"

# Vale - análise semestral
curl "http://localhost:8002/api/v1/market-data/stocks/VALE3.SA?period=6mo"
```

### Portfolio Brasileiro
```bash
curl "http://localhost:8002/api/v1/market-data/stocks/ITUB4.SA?period=3mo"  # Itaú
curl "http://localhost:8002/api/v1/market-data/stocks/BBDC4.SA?period=3mo"  # Bradesco
curl "http://localhost:8002/api/v1/market-data/stocks/ABEV3.SA?period=6mo"  # Ambev
```

### Big Tech US
```bash
curl "http://localhost:8002/api/v1/market-data/stocks/MSFT?period=1y"    # Microsoft
curl "http://localhost:8002/api/v1/market-data/stocks/GOOGL?period=1y"   # Google
curl "http://localhost:8002/api/v1/market-data/stocks/AMZN?period=1y"    # Amazon
curl "http://localhost:8002/api/v1/market-data/stocks/TSLA?period=6mo"   # Tesla
```

### ETFs e Índices
```bash
curl "http://localhost:8002/api/v1/market-data/stocks/SPY?period=1y"     # S&P 500
curl "http://localhost:8002/api/v1/market-data/stocks/QQQ?period=6mo"    # NASDAQ
curl "http://localhost:8002/api/v1/market-data/stocks/IVV?period=3mo"    # iShares Core S&P 500
```

## 🔍 2. Busca de Ações (/search)

### Busca por Empresa
```bash
# Buscar Petrobras
curl "http://localhost:8002/api/v1/market-data/search?q=petrobras&limit=5"

# Buscar Apple
curl "http://localhost:8002/api/v1/market-data/search?q=apple&limit=3"

# Buscar Microsoft
curl "http://localhost:8002/api/v1/market-data/search?q=microsoft&limit=3"
```

### Busca por Setor
```bash
# Bancos brasileiros
curl "http://localhost:8002/api/v1/market-data/search?q=banco&limit=15"

# Empresas de energia
curl "http://localhost:8002/api/v1/market-data/search?q=energia&limit=10"

# Tecnologia
curl "http://localhost:8002/api/v1/market-data/search?q=tecnologia&limit=20"
```

### Busca por Símbolo
```bash
# Símbolos começando com PETR
curl "http://localhost:8002/api/v1/market-data/search?q=PETR&limit=10"

# Símbolos começando com BB (bancos)
curl "http://localhost:8002/api/v1/market-data/search?q=BB&limit=8"

# Símbolos com VALE
curl "http://localhost:8002/api/v1/market-data/search?q=VALE&limit=5"
```

## 📈 3. Ações em Tendência (/trending)

### Mercado Brasileiro
```bash
# Top 5 Brasil
curl "http://localhost:8002/api/v1/market-data/trending?market=BR&limit=5"

# Top 15 Brasil (análise ampla)
curl "http://localhost:8002/api/v1/market-data/trending?market=BR&limit=15"

# Top 30 Brasil (visão completa)
curl "http://localhost:8002/api/v1/market-data/trending?market=BR&limit=30"
```

### Mercado Americano
```bash
# Top 10 EUA
curl "http://localhost:8002/api/v1/market-data/trending?market=US&limit=10"

# Top 20 EUA
curl "http://localhost:8002/api/v1/market-data/trending?market=US&limit=20"

# Top 5 EUA (foco nas principais)
curl "http://localhost:8002/api/v1/market-data/trending?market=US&limit=5"
```

## ✅ 4. Validação de Símbolos (/validate/{symbol})

### Símbolos Válidos (Brasil)
```bash
curl "http://localhost:8002/api/v1/market-data/validate/PETR4.SA"
curl "http://localhost:8002/api/v1/market-data/validate/VALE3.SA"
curl "http://localhost:8002/api/v1/market-data/validate/ITUB4.SA"
curl "http://localhost:8002/api/v1/market-data/validate/BBDC4.SA"
```

### Símbolos Válidos (EUA)
```bash
curl "http://localhost:8002/api/v1/market-data/validate/AAPL"
curl "http://localhost:8002/api/v1/market-data/validate/MSFT"
curl "http://localhost:8002/api/v1/market-data/validate/GOOGL"
curl "http://localhost:8002/api/v1/market-data/validate/SPY"
```

### Símbolos Inválidos (para testar erro)
```bash
curl "http://localhost:8002/api/v1/market-data/validate/INVALID"
curl "http://localhost:8002/api/v1/market-data/validate/FAKE123"
curl "http://localhost:8002/api/v1/market-data/validate/NOTREAL"
```

## 📦 5. Dados em Lote (/bulk)

### Portfolio Diversificado Brasil
```bash
curl -X POST "http://localhost:8002/api/v1/market-data/bulk" \
     -H "Content-Type: application/json" \
     -d '{
       "symbols": ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "ABEV3.SA"],
       "period": "1mo"
     }'
```

### Big Tech Portfolio
```bash
curl -X POST "http://localhost:8002/api/v1/market-data/bulk" \
     -H "Content-Type: application/json" \
     -d '{
       "symbols": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"],
       "period": "1y"
     }'
```

### ETFs Diversificados
```bash
curl -X POST "http://localhost:8002/api/v1/market-data/bulk" \
     -H "Content-Type: application/json" \
     -d '{
       "symbols": ["SPY", "QQQ", "IVV", "VTI"],
       "period": "6mo"
     }'
```

### Setor Bancário Brasil
```bash
curl -X POST "http://localhost:8002/api/v1/market-data/bulk" \
     -H "Content-Type: application/json" \
     -d '{
       "symbols": ["ITUB4.SA", "BBDC4.SA", "SANB11.SA", "BBAS3.SA"],
       "period": "3mo"
     }'
```

### Energia Brasil
```bash
curl -X POST "http://localhost:8002/api/v1/market-data/bulk" \
     -H "Content-Type: application/json" \
     -d '{
       "symbols": ["PETR4.SA", "PETR3.SA", "EGIE3.SA", "ENGI11.SA"],
       "period": "1y"
     }'
```

## 🔧 6. Utilitários

### Health Check
```bash
# Verificar saúde do serviço
curl "http://localhost:8002/api/v1/market-data/health"
```

### Informações da API
```bash
# Ver todos os endpoints
curl "http://localhost:8002/api/v1/market-data/"
```

### Limpeza de Cache
```bash
# Limpar cache (forçar atualização)
curl -X DELETE "http://localhost:8002/api/v1/market-data/cache"
```

## 🎯 Cenários de Teste Completos

### Cenário 1: Análise de Portfólio
```bash
# 1. Verificar se API está funcionando
curl "http://localhost:8002/api/v1/market-data/health"

# 2. Ver ações em tendência
curl "http://localhost:8002/api/v1/market-data/trending?market=BR&limit=10"

# 3. Validar símbolos do portfólio
curl "http://localhost:8002/api/v1/market-data/validate/PETR4.SA"
curl "http://localhost:8002/api/v1/market-data/validate/VALE3.SA"

# 4. Obter dados em lote
curl -X POST "http://localhost:8002/api/v1/market-data/bulk" \
     -H "Content-Type: application/json" \
     -d '{"symbols": ["PETR4.SA", "VALE3.SA", "ITUB4.SA"], "period": "1y"}'
```

### Cenário 2: Descoberta de Investimentos
```bash
# 1. Buscar empresas de tecnologia
curl "http://localhost:8002/api/v1/market-data/search?q=tecnologia&limit=15"

# 2. Ver trending US para oportunidades
curl "http://localhost:8002/api/v1/market-data/trending?market=US&limit=20"

# 3. Analisar ações específicas
curl "http://localhost:8002/api/v1/market-data/stocks/AAPL?period=1y"
curl "http://localhost:8002/api/v1/market-data/stocks/MSFT?period=1y"
```

### Cenário 3: Day Trading
```bash
# 1. Ver trending para identificar movimentação
curl "http://localhost:8002/api/v1/market-data/trending?market=BR&limit=5"

# 2. Dados de curto prazo para análise
curl "http://localhost:8002/api/v1/market-data/stocks/PETR4.SA?period=5d"
curl "http://localhost:8002/api/v1/market-data/stocks/VALE3.SA?period=1d"
```

## 💡 Dicas de Teste

1. **Sempre comece com /health** para verificar se está funcionando
2. **Use /validate** antes de chamar /stocks para evitar erros
3. **Combine /trending + /stocks** para análise completa
4. **Use /bulk** para comparar múltiplas ações
5. **Periods recomendados:**
   - Análise rápida: `1mo`
   - Tendências: `1y`
   - Day trading: `1d` ou `5d`
   - Comparações: `6mo`

## 🐛 Troubleshooting

Se algo não funcionar:
1. Verifique `/health`
2. Limpe o cache com `DELETE /cache`
3. Verifique se o símbolo é válido com `/validate`
4. Veja os logs do serviço
5. Consulte a documentação em `/docs`
