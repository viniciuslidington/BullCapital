"""
Script de teste para a API do Agente Financeiro.
Demonstra como fazer requisições HTTP para o agente.
"""

import requests
import json

# URL base da API
BASE_URL = "http://localhost:8001"

def test_chat_endpoint():
    """Testa o endpoint /chat - conversa geral com o agente."""
    
    url = f"{BASE_URL}/chat"
    
    # Exemplo 1: Pergunta geral sobre análise fundamentalista
    payload = {
        "question": "O que é margem de segurança na análise fundamentalista?",
        "ticker": None
    }
    
    print("🔍 Testando endpoint /chat...")
    print(f"Pergunta: {payload['question']}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            print("✅ Resposta do agente:")
            print(result["response"])
        else:
            print(f"❌ Erro: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")

def test_analyze_endpoint():
    """Testa o endpoint /analyze - análise específica de ação."""
    
    url = f"{BASE_URL}/analyze"
    
    # Exemplo 2: Análise específica da Petrobras
    payload = {
        "question": "Analise esta ação e me dê uma recomendação",
        "ticker": "PETR4"
    }
    
    print("\n📊 Testando endpoint /analyze...")
    print(f"Ação: {payload['ticker']}")
    print(f"Pergunta: {payload['question']}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            print("✅ Análise completa:")
            print(result["response"])
        else:
            print(f"❌ Erro: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")

def test_health_endpoint():
    """Testa o endpoint /health."""
    
    url = f"{BASE_URL}/health"
    
    print("\n🏥 Testando endpoint /health...")
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            print("✅ Status da API:")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")

def test_root_endpoint():
    """Testa o endpoint raiz."""
    
    url = f"{BASE_URL}/"
    
    print("\n🏠 Testando endpoint raiz...")
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            print("✅ Informações da API:")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")

def test_agent_directly():
    """Testa o agente diretamente (sem API)."""
    
    print("\n🤖 Testando agente diretamente...")
    print("-" * 50)
    
    try:
        from ia.Agent.financial_agent import agent
        
        # Teste de chat
        question = "O que é margem de segurança?"
        print(f"Pergunta: {question}")
        response = agent.chat(question)
        print("✅ Resposta direta do agente:")
        print(response)
        
        # Teste de análise
        print(f"\n📊 Análise da PETR4:")
        analysis = agent.analyze_stock("Analise esta ação", "PETR4")
        print("✅ Análise direta do agente:")
        print(analysis)
        
    except Exception as e:
        print(f"❌ Erro no teste direto: {e}")

if __name__ == "__main__":
    print("🚀 Testando Agente Financeiro (Modularizado)")
    print("=" * 50)
    
    # Testar agente diretamente
    test_agent_directly()
    
    # Testar API
    test_root_endpoint()
    test_health_endpoint()
    test_chat_endpoint()
    test_analyze_endpoint()
    
    print("\n✅ Testes concluídos!")
    print("\n📖 Para mais informações, acesse:")
    print(f"   Documentação: {BASE_URL}/docs")
    print(f"   ReDoc: {BASE_URL}/redoc")
    print("\n🔄 Para executar a API:")
    print("   python api_server.py") 