"""
Exemplo de uso da API com sistema de chat.
Demonstra como usar a API com histórico de mensagens.
"""

import requests
import json
from datetime import datetime

# URL base da API
BASE_URL = "http://localhost:8001"

def exemplo_chat_simples():
    """Exemplo de chat simples."""
    
    print("💬 Exemplo de Chat Simples")
    print("=" * 40)
    
    # Primeira mensagem
    payload = {
        "sender": "user",
        "content": "Olá, tudo bem?"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        if response.status_code == 200:
            result = response.json()
            print("✅ Resposta:")
            for message in result['messages']:
                print(f"   {message['sender']}: {message['content']}")
        else:
            print(f"❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")

def exemplo_conversa_continua():
    """Exemplo de conversa contínua com histórico."""
    
    print("\n🔄 Exemplo de Conversa Contínua")
    print("=" * 40)
    
    mensagens = [
        "O que é margem de segurança?",
        "Como calcular o valor intrínseco?",
        "Quais são os principais indicadores fundamentalistas?"
    ]
    
    for i, mensagem in enumerate(mensagens, 1):
        print(f"\n📝 Mensagem {i}: {mensagem}")
        
        payload = {
            "sender": "user",
            "content": mensagem
        }
        
        try:
            response = requests.post(f"{BASE_URL}/chat", json=payload)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Resposta {i}:")
                # Mostrar apenas a última resposta do bot
                bot_messages = [msg for msg in result['messages'] if msg['sender'] == 'bot']
                if bot_messages:
                    print(f"   Bot: {bot_messages[-1]['content'][:100]}...")
                print(f"   Total de mensagens na conversa: {len(result['messages'])}")
            else:
                print(f"❌ Erro: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")

def exemplo_analise_acoes():
    """Exemplo de análise de ações com histórico."""
    
    print("\n📊 Exemplo de Análise de Ações")
    print("=" * 40)
    
    acoes = [
        ("PETR4", "Analise esta ação e me dê uma recomendação"),
        ("VALE3", "Faça uma análise completa desta ação"),
    ]
    
    for ticker, pergunta in acoes:
        print(f"\n📈 Análise da {ticker}")
        print(f"❓ Pergunta: {pergunta}")
        
        payload = {
            "sender": "user",
            "content": pergunta,
            "ticker": ticker
        }
        
        try:
            response = requests.post(f"{BASE_URL}/analyze", json=payload)
            if response.status_code == 200:
                result = response.json()
                print("✅ Análise:")
                # Mostrar apenas a última resposta do bot
                bot_messages = [msg for msg in result['messages'] if msg['sender'] == 'bot']
                if bot_messages:
                    print(f"   Bot: {bot_messages[-1]['content'][:200]}...")
                print(f"   Total de mensagens: {len(result['messages'])}")
            else:
                print(f"❌ Erro: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")

def exemplo_gerenciamento_conversas():
    """Exemplo de gerenciamento de conversas."""
    
    print("\n🗂️ Exemplo de Gerenciamento de Conversas")
    print("=" * 40)
    
    try:
        # Listar conversas
        response = requests.get(f"{BASE_URL}/conversations")
        if response.status_code == 200:
            result = response.json()
            print("✅ Conversas disponíveis:")
            for conv_id in result['conversations']:
                print(f"   - {conv_id}")
            
            # Recuperar uma conversa específica
            if result['conversations']:
                conv_id = result['conversations'][0]
                response_get = requests.get(f"{BASE_URL}/conversations/{conv_id}")
                if response_get.status_code == 200:
                    conv_result = response_get.json()
                    print(f"\n📋 Detalhes da conversa '{conv_id}':")
                    print(f"   Mensagens: {len(conv_result['messages'])}")
                    for msg in conv_result['messages'][-3:]:  # Últimas 3 mensagens
                        print(f"   {msg['sender']}: {msg['content'][:50]}...")
        else:
            print(f"❌ Erro ao listar conversas: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")

def exemplo_curl_commands():
    """Exemplo de comandos curl para testar a API."""
    
    print("\n🔧 Exemplos de Comandos curl")
    print("=" * 40)
    
    print("1. Chat simples:")
    print(f"""curl -X POST "{BASE_URL}/chat" \\
  -H "Content-Type: application/json" \\
  -d '{{"sender": "user", "content": "Olá, tudo bem?"}}'""")
    
    print("\n2. Análise de ação:")
    print(f"""curl -X POST "{BASE_URL}/analyze" \\
  -H "Content-Type: application/json" \\
  -d '{{"sender": "user", "content": "Analise esta ação", "ticker": "PETR4"}}'""")
    
    print("\n3. Listar conversas:")
    print(f"""curl "{BASE_URL}/conversations" """)
    
    print("\n4. Recuperar conversa:")
    print(f"""curl "{BASE_URL}/conversations/default" """)
    
    print("\n5. Health check:")
    print(f"""curl "{BASE_URL}/health" """)

if __name__ == "__main__":
    print("🚀 Exemplos de Uso da API com Sistema de Chat")
    print("=" * 50)
    
    # Executar exemplos
    exemplo_chat_simples()
    exemplo_conversa_continua()
    exemplo_analise_acoes()
    exemplo_gerenciamento_conversas()
    exemplo_curl_commands()
    
    print("\n✅ Exemplos concluídos!")
    print("\n💡 Dicas:")
    print("   - Cada requisição mantém o histórico")
    print("   - Use /conversations para gerenciar conversas")
    print("   - Timestamps são adicionados automaticamente")
    print("   - Respostas incluem todo o histórico da conversa") 