#!/usr/bin/env python3
"""
Script de teste para Google OAuth integration.

Este script demonstra como testar a integração com Google OAuth
e pode ser usado para validar se a configuração está funcionando corretamente.
"""

import requests
import json
from urllib.parse import urlparse, parse_qs

# Configurações
BASE_URL = "http://localhost:8001/api/v1/auth"

def test_google_auth_url():
    """Testa o endpoint que retorna a URL de autenticação do Google."""
    print("🔍 Testando endpoint de URL de autenticação...")
    
    try:
        response = requests.get(f"{BASE_URL}/google/auth-url")
        response.raise_for_status()
        
        data = response.json()
        auth_url = data.get("auth_url")
        
        if auth_url:
            print("✅ URL de autenticação obtida com sucesso!")
            print(f"🔗 URL: {auth_url}")
            print("\n📋 Próximos passos:")
            print("1. Abra esta URL no navegador")
            print("2. Faça login com sua conta Google")
            print("3. Copie o código da URL de redirecionamento")
            print("4. Use o código no teste de callback")
            return auth_url
        else:
            print("❌ Erro: Nenhuma URL retornada")
            return None
            
    except requests.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        return None

def test_google_callback(code, redirect_uri):
    """Testa o endpoint de callback com um código de autorização."""
    print("\n🔍 Testando callback do Google OAuth...")
    
    try:
        payload = {
            "code": code,
            "redirect_uri": redirect_uri
        }
        
        response = requests.post(
            f"{BASE_URL}/google/callback",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Autenticação com Google bem-sucedida!")
            print(f"👤 Usuário: {data['user']['nome_completo']}")
            print(f"📧 Email: {data['user']['email']}")
            print(f"🆔 ID: {data['user']['id']}")
            print(f"🔑 Token: {data['access_token'][:20]}...")
            return data
        else:
            print(f"❌ Erro no callback: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return None
            
    except requests.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        return None

def test_protected_endpoint(token):
    """Testa um endpoint protegido usando o token obtido."""
    print("\n🔍 Testando endpoint protegido...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/profile", headers=headers)
        response.raise_for_status()
        
        data = response.json()
        print("✅ Acesso ao perfil autorizado!")
        print(f"👤 Nome: {data['nome_completo']}")
        print(f"📧 Email: {data['email']}")
        print(f"🎨 Foto: {data.get('profile_picture', 'Não disponível')}")
        return data
        
    except requests.RequestException as e:
        print(f"❌ Erro ao acessar perfil: {e}")
        return None

def interactive_test():
    """Executa um teste interativo completo."""
    print("🚀 Iniciando teste interativo do Google OAuth")
    print("=" * 50)
    
    # Passo 1: Obter URL de autenticação
    auth_url = test_google_auth_url()
    if not auth_url:
        return
    
    # Passo 2: Aguardar código do usuário
    print("\n⏳ Aguardando código de autorização...")
    print("Após fazer login no Google, você será redirecionado para uma URL como:")
    print("http://localhost:8001/api/v1/auth/google/callback?code=SEU_CODIGO&...")
    print()
    
    code = input("Cole o código de autorização aqui: ").strip()
    if not code:
        print("❌ Código não fornecido. Teste cancelado.")
        return
    
    # Passo 3: Testar callback
    redirect_uri = "http://localhost:8001/api/v1/auth/google/callback"
    auth_data = test_google_callback(code, redirect_uri)
    if not auth_data:
        return
    
    # Passo 4: Testar endpoint protegido
    token = auth_data.get("access_token")
    if token:
        test_protected_endpoint(token)
    
    print("\n🎉 Teste concluído!")

def validate_environment():
    """Valida se o ambiente está configurado corretamente."""
    print("🔧 Validando configuração do ambiente...")
    
    try:
        # Tenta acessar endpoint de health check
        response = requests.get(f"{BASE_URL.replace('/api/v1/auth', '')}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor está rodando")
        else:
            print(f"⚠️  Servidor respondeu com status: {response.status_code}")
    except requests.RequestException:
        print("❌ Servidor não está acessível")
        print(f"📍 Verificar se o servidor está rodando em: {BASE_URL}")
        return False
    
    # Verifica se endpoint de auth URL responde
    try:
        response = requests.get(f"{BASE_URL}/google/auth-url", timeout=5)
        if response.status_code == 200:
            print("✅ Endpoints de autenticação acessíveis")
            return True
        else:
            print(f"❌ Endpoint de auth retornou: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Erro ao acessar endpoints: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Script de Teste - Google OAuth Integration")
    print("=" * 50)
    
    # Validar ambiente antes de começar
    if not validate_environment():
        print("\n💡 Dicas para resolver:")
        print("1. Certifique-se de que o servidor está rodando:")
        print("   uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload")
        print("2. Verifique se as variáveis de ambiente estão configuradas")
        print("3. Confirme se a migração do banco foi executada")
        exit(1)
    
    print("\nEscolha uma opção:")
    print("1. Teste interativo completo")
    print("2. Apenas obter URL de autenticação")
    print("3. Testar callback (necessário código)")
    
    choice = input("\nDigite sua escolha (1-3): ").strip()
    
    if choice == "1":
        interactive_test()
    elif choice == "2":
        test_google_auth_url()
    elif choice == "3":
        code = input("Digite o código de autorização: ").strip()
        redirect_uri = input("Digite a redirect URI (ou Enter para padrão): ").strip()
        if not redirect_uri:
            redirect_uri = "http://localhost:8001/api/v1/auth/google/callback"
        test_google_callback(code, redirect_uri)
    else:
        print("❌ Opção inválida")
