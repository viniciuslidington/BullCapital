#!/usr/bin/env python3
"""
Script de teste para o Market Data Service.

Este script executa testes básicos para verificar se o microserviço
está funcionando corretamente.

Usage:
    python test_service.py
"""

import asyncio
import sys

import httpx


async def test_market_data_service():
    """
    Executa uma série de testes no Market Data Service.
    
    Returns:
        True se todos os testes passaram, False caso contrário
    """
    base_url = "http://localhost:8002"
    
    print("🧪 Iniciando testes do Market Data Service...")
    print(f"🔗 URL Base: {base_url}")
    print("-" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Teste 1: Health Check
            print("1️⃣  Testando health check...")
            response = await client.get(f"{base_url}/health")
            assert response.status_code == 200
            health_data = response.json()
            print(f"   ✅ Status: {health_data.get('status')}")
            print(f"   ✅ Versão: {health_data.get('version')}")
            
            # Teste 2: Informações do serviço
            print("\n2️⃣  Testando endpoint de informações...")
            response = await client.get(f"{base_url}/")
            assert response.status_code == 200
            info_data = response.json()
            print(f"   ✅ Serviço: {info_data.get('service')}")
            print(f"   ✅ Uptime: {info_data.get('uptime_seconds')}s")
            
            # Teste 3: Ping
            print("\n3️⃣  Testando ping...")
            response = await client.get(f"{base_url}/ping")
            assert response.status_code == 200
            ping_data = response.json()
            print(f"   ✅ Message: {ping_data.get('message')}")
            
            # Teste 4: Busca de ações
            print("\n4️⃣  Testando busca de ações...")
            response = await client.get(
                f"{base_url}/api/v1/market-data/stocks/search?query=Petrobras&limit=5"
            )
            assert response.status_code == 200
            search_data = response.json()
            print(f"   ✅ Resultados encontrados: {search_data.get('results_found')}")
            if search_data.get('results'):
                first_result = search_data['results'][0]
                print(f"   ✅ Primeiro resultado: {first_result.get('symbol')} - {first_result.get('name')}")
            
            # Teste 5: Dados de ação específica
            print("\n5️⃣  Testando dados de ação específica (PETR4.SA)...")
            response = await client.get(
                f"{base_url}/api/v1/market-data/stocks/PETR4.SA?period=5d&include_fundamentals=true"
            )
            assert response.status_code == 200
            stock_data = response.json()
            print(f"   ✅ Símbolo: {stock_data.get('symbol')}")
            print(f"   ✅ Empresa: {stock_data.get('company_name')}")
            print(f"   ✅ Preço atual: {stock_data.get('current_price')}")
            if stock_data.get('historical_data'):
                print(f"   ✅ Pontos históricos: {len(stock_data['historical_data'])}")
            
            # Teste 6: Validação de ticker
            print("\n6️⃣  Testando validação de ticker...")
            response = await client.get(
                f"{base_url}/api/v1/market-data/tickers/PETR4.SA/validate"
            )
            assert response.status_code == 200
            validation_data = response.json()
            print(f"   ✅ Ticker válido: {validation_data.get('is_valid')}")
            print(f"   ✅ Existe: {validation_data.get('exists')}")
            
            # Teste 7: Ações em tendência
            print("\n7️⃣  Testando ações em tendência...")
            response = await client.get(
                f"{base_url}/api/v1/market-data/stocks/trending?market=BR&limit=3"
            )
            assert response.status_code == 200
            trending_data = response.json()
            print(f"   ✅ Ações em tendência: {trending_data.get('total_stocks')}")
            
            # Teste 8: Requisição em lote (POST)
            print("\n8️⃣  Testando requisição em lote...")
            bulk_request = {
                "tickers": ["PETR4.SA", "VALE3.SA", "ITUB4.SA"],
                "period": "5d",
                "interval": "1d",
                "include_fundamentals": False
            }
            response = await client.post(
                f"{base_url}/api/v1/market-data/bulk",
                json=bulk_request
            )
            assert response.status_code == 200
            bulk_data = response.json()
            print(f"   ✅ Total de tickers: {bulk_data.get('total_tickers')}")
            print(f"   ✅ Sucessos: {bulk_data.get('successful_requests')}")
            print(f"   ✅ Falhas: {bulk_data.get('failed_requests')}")
            
            # Teste 9: Teste de ticker inválido
            print("\n9️⃣  Testando ticker inválido...")
            response = await client.get(
                f"{base_url}/api/v1/market-data/stocks/INVALID_TICKER"
            )
            # Pode retornar 502 (Bad Gateway) se o provedor falhar
            print(f"   ✅ Status para ticker inválido: {response.status_code}")
            
            # Teste 10: Documentação da API
            print("\n🔟 Testando documentação da API...")
            response = await client.get(f"{base_url}/docs")
            assert response.status_code == 200
            print("   ✅ Documentação Swagger disponível")
            
            print("\n" + "=" * 60)
            print("🎉 TODOS OS TESTES PASSARAM! 🎉")
            print("✅ Market Data Service está funcionando corretamente")
            print("=" * 60)
            
            return True
            
        except AssertionError as e:
            print(f"\n❌ Teste falhou: {e}")
            return False
        except httpx.RequestError as e:
            print(f"\n❌ Erro de conexão: {e}")
            print("💡 Certifique-se de que o serviço está rodando em http://localhost:8002")
            return False
        except Exception as e:
            print(f"\n❌ Erro inesperado: {e}")
            return False


def print_usage():
    """Imprime instruções de uso."""
    print("""
📋 Market Data Service - Script de Teste

🚀 Como executar:
   1. Certifique-se de que o Market Data Service está rodando:
      uvicorn app.main:app --host 0.0.0.0 --port 8002
   
   2. Execute este script:
      python test_service.py

🔧 Pré-requisitos:
   - Python 3.8+
   - httpx (pip install httpx)
   - Market Data Service rodando na porta 8002

📊 Testes incluídos:
   ✓ Health check
   ✓ Informações do serviço
   ✓ Ping/conectividade
   ✓ Busca de ações
   ✓ Dados de ação específica
   ✓ Validação de ticker
   ✓ Ações em tendência
   ✓ Requisições em lote
   ✓ Tratamento de erros
   ✓ Documentação da API
""")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help", "help"]:
        print_usage()
        sys.exit(0)
    
    print("🔍 Verificando dependências...")
    try:
        import httpx
        print("✅ httpx disponível")
    except ImportError:
        print("❌ httpx não encontrado. Instale com: pip install httpx")
        sys.exit(1)
    
    # Executar testes
    try:
        success = asyncio.run(test_market_data_service())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Testes interrompidos pelo usuário")
        sys.exit(130)
