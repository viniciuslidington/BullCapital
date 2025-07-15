#!/usr/bin/env python3
"""
🧪 Script Interativo de Testes - Market Data API

Execute este script para testar a API de forma interativa e fácil!
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8002/api/v1/market-data"

class APITester:
    def __init__(self):
        self.base_url = BASE_URL
        
    def print_header(self, title: str):
        print(f"\n{'='*60}")
        print(f"🎯 {title}")
        print(f"{'='*60}")
    
    def print_result(self, response: requests.Response, endpoint: str):
        print(f"\n📡 {endpoint}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Sucesso!")
                
                # Mostrar dados relevantes baseado no endpoint
                if "/stocks/" in endpoint:
                    self.show_stock_data(data)
                elif "/search" in endpoint:
                    self.show_search_data(data)
                elif "/trending" in endpoint:
                    self.show_trending_data(data)
                elif "/validate" in endpoint:
                    self.show_validation_data(data)
                elif "/bulk" in endpoint:
                    self.show_bulk_data(data)
                else:
                    print(f"Dados: {json.dumps(data, indent=2)[:500]}...")
                    
            except json.JSONDecodeError:
                print(f"Resposta: {response.text[:200]}...")
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"Resposta: {response.text[:200]}...")
    
    def show_stock_data(self, data: Dict[Any, Any]):
        symbol = data.get('symbol', 'N/A')
        price = data.get('current_price', 'N/A')
        change = data.get('change', 'N/A')
        volume = data.get('volume', 'N/A')
        
        print(f"📈 Ação: {symbol}")
        print(f"💰 Preço: {price}")
        print(f"📊 Variação: {change}")
        print(f"📦 Volume: {volume}")
    
    def show_search_data(self, data: Dict[Any, Any]):
        results = data.get('results', [])
        print(f"🔍 Encontradas: {len(results)} ações")
        for i, result in enumerate(results[:5]):
            symbol = result.get('symbol', 'N/A')
            name = result.get('name', 'N/A')
            print(f"  {i+1}. {symbol} - {name}")
    
    def show_trending_data(self, data: Dict[Any, Any]):
        market = data.get('market', 'N/A')
        stocks = data.get('trending_stocks', [])
        print(f"📊 Mercado: {market}")
        print(f"🔥 Trending: {len(stocks)} ações")
        for i, stock in enumerate(stocks[:5]):
            symbol = stock.get('symbol', 'N/A')
            print(f"  {i+1}. {symbol}")
    
    def show_validation_data(self, data: Dict[Any, Any]):
        symbol = data.get('symbol', 'N/A')
        is_valid = data.get('is_valid', False)
        market = data.get('market', 'N/A')
        
        status = "✅ Válido" if is_valid else "❌ Inválido"
        print(f"🔍 Símbolo: {symbol}")
        print(f"📊 Status: {status}")
        print(f"🌍 Mercado: {market}")
    
    def show_bulk_data(self, data: Dict[Any, Any]):
        results = data.get('results', [])
        print(f"📦 Dados de: {len(results)} ações")
        for result in results[:3]:
            symbol = result.get('symbol', 'N/A')
            price = result.get('current_price', 'N/A')
            print(f"  📈 {symbol}: {price}")

    def test_health(self):
        """Teste do health check"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            self.print_result(response, "GET /health")
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"❌ Erro na conexão: {e}")
            return False
    
    def test_stocks(self):
        """Teste de dados de ações"""
        test_cases = [
            ("PETR4.SA", "1mo", "Petrobras - 1 mês"),
            ("AAPL", "1y", "Apple - 1 ano"),
            ("VALE3.SA", "6mo", "Vale - 6 meses"),
            ("SPY", "3mo", "S&P 500 ETF - 3 meses")
        ]
        
        for symbol, period, description in test_cases:
            try:
                url = f"{self.base_url}/stocks/{symbol}?period={period}"
                response = requests.get(url, timeout=10)
                self.print_result(response, f"GET /stocks/{symbol} ({description})")
                time.sleep(1)  # Rate limiting
            except requests.RequestException as e:
                print(f"❌ Erro: {e}")
    
    def test_search(self):
        """Teste de busca"""
        test_cases = [
            ("petrobras", 5, "Busca por Petrobras"),
            ("banco", 10, "Busca por bancos"),
            ("AAPL", 3, "Busca por Apple"),
            ("tecnologia", 15, "Setor tecnologia")
        ]
        
        for query, limit, description in test_cases:
            try:
                url = f"{self.base_url}/search?q={query}&limit={limit}"
                response = requests.get(url, timeout=10)
                self.print_result(response, f"GET /search ({description})")
                time.sleep(1)
            except requests.RequestException as e:
                print(f"❌ Erro: {e}")
    
    def test_trending(self):
        """Teste de ações em tendência"""
        test_cases = [
            ("BR", 10, "Top 10 Brasil"),
            ("US", 15, "Top 15 EUA"),
            ("BR", 5, "Top 5 Brasil")
        ]
        
        for market, limit, description in test_cases:
            try:
                url = f"{self.base_url}/trending?market={market}&limit={limit}"
                response = requests.get(url, timeout=10)
                self.print_result(response, f"GET /trending ({description})")
                time.sleep(1)
            except requests.RequestException as e:
                print(f"❌ Erro: {e}")
    
    def test_validation(self):
        """Teste de validação"""
        test_cases = [
            ("PETR4.SA", "Petrobras - válida"),
            ("AAPL", "Apple - válida"),
            ("INVALID", "Símbolo inválido"),
            ("FAKE123", "Símbolo falso")
        ]
        
        for symbol, description in test_cases:
            try:
                url = f"{self.base_url}/validate/{symbol}"
                response = requests.get(url, timeout=10)
                self.print_result(response, f"GET /validate/{symbol} ({description})")
                time.sleep(1)
            except requests.RequestException as e:
                print(f"❌ Erro: {e}")
    
    def test_bulk(self):
        """Teste de dados em lote"""
        test_cases = [
            {
                "data": {
                    "symbols": ["PETR4.SA", "VALE3.SA", "ITUB4.SA"],
                    "period": "1mo"
                },
                "description": "Top 3 Brasil"
            },
            {
                "data": {
                    "symbols": ["AAPL", "MSFT", "GOOGL"],
                    "period": "1y"
                },
                "description": "Big Tech"
            },
            {
                "data": {
                    "symbols": ["SPY", "QQQ"],
                    "period": "6mo"
                },
                "description": "ETFs"
            }
        ]
        
        for test_case in test_cases:
            try:
                url = f"{self.base_url}/bulk"
                response = requests.post(url, json=test_case["data"], timeout=15)
                self.print_result(response, f"POST /bulk ({test_case['description']})")
                time.sleep(2)  # Bulk requests take longer
            except requests.RequestException as e:
                print(f"❌ Erro: {e}")
    
    def test_utilities(self):
        """Teste de utilitários"""
        # Info da API
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            self.print_result(response, "GET / (Info da API)")
        except requests.RequestException as e:
            print(f"❌ Erro: {e}")
        
        time.sleep(1)
        
        # Clear cache
        try:
            response = requests.delete(f"{self.base_url}/cache", timeout=5)
            self.print_result(response, "DELETE /cache (Limpar cache)")
        except requests.RequestException as e:
            print(f"❌ Erro: {e}")
    
    def run_interactive_tests(self):
        """Executa todos os testes interativamente"""
        print("🚀 TESTADOR INTERATIVO - MARKET DATA API")
        print(f"Base URL: {self.base_url}")
        print("\nIniciando testes...")
        
        # 1. Health Check
        self.print_header("1. Health Check")
        if not self.test_health():
            print("❌ API não está funcionando! Verifique se o serviço está rodando.")
            return
        
        # 2. Dados de Ações
        self.print_header("2. Teste de Dados de Ações")
        self.test_stocks()
        
        # 3. Busca
        self.print_header("3. Teste de Busca")
        self.test_search()
        
        # 4. Trending
        self.print_header("4. Teste de Trending")
        self.test_trending()
        
        # 5. Validação
        self.print_header("5. Teste de Validação")
        self.test_validation()
        
        # 6. Bulk
        self.print_header("6. Teste de Dados em Lote")
        self.test_bulk()
        
        # 7. Utilitários
        self.print_header("7. Teste de Utilitários")
        self.test_utilities()
        
        # Conclusão
        self.print_header("🎉 TESTES CONCLUÍDOS!")
        print("✅ Todos os endpoints foram testados!")
        print("📊 Verifique os resultados acima")
        print("📖 Documentação: http://localhost:8002/docs")
        print("🔧 Swagger UI: http://localhost:8002/docs")

def run_quick_test():
    """Teste rápido para verificar se está funcionando"""
    print("⚡ TESTE RÁPIDO")
    tester = APITester()
    
    if tester.test_health():
        print("✅ API funcionando!")
        
        # Teste rápido de uma ação
        try:
            response = requests.get(f"{BASE_URL}/stocks/PETR4.SA", timeout=5)
            if response.status_code == 200:
                data = response.json()
                symbol = data.get('symbol', 'N/A')
                price = data.get('current_price', 'N/A')
                print(f"📈 {symbol}: {price}")
                print("🎉 API está funcionando perfeitamente!")
            else:
                print("⚠️ API online mas com problemas nos dados")
        except:
            print("⚠️ API online mas com problemas de conexão")
    else:
        print("❌ API não está funcionando")

def interactive_menu():
    """Menu interativo para escolher testes"""
    tester = APITester()
    
    while True:
        print("\n" + "="*50)
        print("🧪 TESTADOR MARKET DATA API")
        print("="*50)
        print("1. 🚀 Teste Rápido")
        print("2. 🔍 Teste Completo")
        print("3. 📈 Testar Ações Específicas")
        print("4. 🔍 Testar Busca")
        print("5. 📊 Testar Trending")
        print("6. ✅ Testar Validação")
        print("7. 📦 Testar Bulk")
        print("8. 🔧 Testar Utilitários")
        print("9. ❌ Sair")
        
        choice = input("\nEscolha uma opção (1-9): ").strip()
        
        if choice == "1":
            run_quick_test()
        elif choice == "2":
            tester.run_interactive_tests()
        elif choice == "3":
            tester.test_stocks()
        elif choice == "4":
            tester.test_search()
        elif choice == "5":
            tester.test_trending()
        elif choice == "6":
            tester.test_validation()
        elif choice == "7":
            tester.test_bulk()
        elif choice == "8":
            tester.test_utilities()
        elif choice == "9":
            print("👋 Até mais!")
            break
        else:
            print("❌ Opção inválida!")

if __name__ == "__main__":
    print("🧪 TESTADOR INTERATIVO - MARKET DATA API")
    print("Certifique-se que o serviço está rodando em localhost:8002")
    
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print("\n👋 Teste interrompido pelo usuário!")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
