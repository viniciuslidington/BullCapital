"""
Script de teste para a API do Agente Financeiro.
Demonstra como fazer requisições HTTP para o agente com sistema de chat.
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
        "sender": "user",
        "content": "O que é margem de segurança na análise fundamentalista?"
    }
    
    print("🔍 Testando endpoint /chat...")
    print(f"Request: {json.dumps(payload, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            print("✅ Resposta do agente:")
            print(json.dumps(result, indent=2))
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
        "sender": "user",
        "content": "Analise esta ação e me dê uma recomendação",
        "ticker": "PETR4"
    }
    
    print("\n📊 Testando endpoint /analyze...")
    print(f"Request: {json.dumps(payload, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            print("✅ Análise completa:")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Erro: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")

def test_conversation_history():
    """Testa o sistema de histórico de conversas."""
    
    print("\n💬 Testando sistema de histórico...")
    
    # Primeira mensagem
    payload1 = {
        "sender": "user",
        "content": "Olá, tudo bem?"
    }
    
    try:
        response1 = requests.post(f"{BASE_URL}/chat", json=payload1)
        if response1.status_code == 200:
            result1 = response1.json()
            print("✅ Primeira mensagem:")
            print(f"   Mensagens: {len(result1['messages'])}")
            
            # Segunda mensagem
            payload2 = {
                "sender": "user",
                "content": "O que é valuation?"
            }
            
            response2 = requests.post(f"{BASE_URL}/chat", json=payload2)
            if response2.status_code == 200:
                result2 = response2.json()
                print("✅ Segunda mensagem:")
                print(f"   Mensagens: {len(result2['messages'])}")
                print("   Histórico mantido!")
            else:
                print(f"❌ Erro na segunda mensagem: {response2.status_code}")
        else:
            print(f"❌ Erro na primeira mensagem: {response1.status_code}")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")

def test_conversation_management():
    """Testa o gerenciamento de conversas."""
    
    print("\n🗂️ Testando gerenciamento de conversas...")
    
    try:
        # Listar conversas
        response = requests.get(f"{BASE_URL}/conversations")
        if response.status_code == 200:
            result = response.json()
            print("✅ Conversas disponíveis:")
            print(json.dumps(result, indent=2))
            
            # Recuperar conversa específica
            if result['conversations']:
                conversation_id = result['conversations'][0]
                response_get = requests.get(f"{BASE_URL}/conversations/{conversation_id}")
                if response_get.status_code == 200:
                    conv_result = response_get.json()
                    print(f"✅ Conversa {conversation_id}:")
                    print(f"   Mensagens: {len(conv_result['messages'])}")
        else:
            print(f"❌ Erro ao listar conversas: {response.status_code}")
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
        from financial_agent import agent
        
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
    print("🚀 Testando Agente Financeiro (Sistema de Chat)")
    print("=" * 50)
    
    # Testar agente diretamente
    test_agent_directly()
    
    # Testar API
    test_root_endpoint()
    test_health_endpoint()
    test_chat_endpoint()
    test_analyze_endpoint()
    test_conversation_history()
    test_conversation_management()
    
    print("\n✅ Testes concluídos!")
    print("\n📖 Para mais informações, acesse:")
    print(f"   Documentação: {BASE_URL}/docs")
    print(f"   ReDoc: {BASE_URL}/redoc")
    print("\n🔄 Para executar a API:")
    print("   python api_server.py") 