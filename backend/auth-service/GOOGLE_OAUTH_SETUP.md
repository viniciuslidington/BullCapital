# Configuração do Google OAuth

Este guia explica como configurar a autenticação com Google OAuth no serviço de autenticação.

## 1. Configurar Google Cloud Console

### Passo 1: Criar/Selecionar Projeto

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Anote o ID do projeto

### Passo 2: Habilitar APIs

1. Vá para "APIs e Serviços" > "Biblioteca"
2. Procure e habilite as seguintes APIs:
   - Google+ API
   - Google People API
   - Google OAuth2 API

### Passo 3: Configurar Tela de Consentimento OAuth

1. Vá para "APIs e Serviços" > "Tela de consentimento OAuth"
2. Escolha "Externo" (para testes) ou "Interno" (para uso corporativo)
3. Preencha as informações obrigatórias:
   - Nome do aplicativo: "Bull Capital Auth"
   - Email de suporte do usuário
   - Logotipo (opcional)
   - Domínio autorizado: `localhost` (para desenvolvimento)
   - Email de contato do desenvolvedor

### Passo 4: Criar Credenciais OAuth

1. Vá para "APIs e Serviços" > "Credenciais"
2. Clique em "Criar credenciais" > "ID do cliente OAuth 2.0"
3. Escolha "Aplicativo da Web"
4. Configure:
   - Nome: "Bull Capital Auth Service"
   - URIs de redirecionamento autorizadas:
     - `http://localhost:8001/api/v1/auth/google/callback` (desenvolvimento)
     - `https://seudominio.com/api/v1/auth/google/callback` (produção)
5. Anote o **Client ID** e **Client Secret**

## 2. Configurar Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e preencha as credenciais:

```bash
cp .env.example .env
```

Edite o arquivo `.env`:

```env
# Configurações Google OAuth
GOOGLE_CLIENT_ID=seu_client_id_aqui.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=seu_client_secret_aqui
GOOGLE_REDIRECT_URI=http://localhost:8001/api/v1/auth/google/callback
```

## 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

## 4. Executar Migração do Banco de Dados

```bash
cd app
python migrations/add_google_oauth_support.py
```

## 5. Testar a Integração

### Passo 1: Iniciar o Servidor

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Passo 2: Obter URL de Autenticação

```bash
curl http://localhost:8001/api/v1/auth/google/auth-url
```

### Passo 3: Testar Fluxo Completo

1. Acesse a URL retornada no navegador
2. Faça login com sua conta Google
3. Você será redirecionado com um código
4. Use o código para fazer login via API

## 6. Fluxo de Autenticação

### Frontend (JavaScript/React)

```javascript
// 1. Obter URL de autenticação
const response = await fetch('/api/v1/auth/google/auth-url');
const { auth_url } = await response.json();

// 2. Redirecionar usuário
window.location.href = auth_url;

// 3. No callback, extrair código e fazer login
const urlParams = new URLSearchParams(window.location.search);
const code = urlParams.get('code');

const loginResponse = await fetch('/api/v1/auth/google/callback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        code: code,
        redirect_uri: 'http://localhost:8001/api/v1/auth/google/callback'
    })
});

const { access_token, user } = await loginResponse.json();
```

## 7. Endpoints Disponíveis

### GET /api/v1/auth/google/auth-url

Retorna a URL para iniciar autenticação com Google.

**Resposta:**

```json
{
    "auth_url": "https://accounts.google.com/o/oauth2/auth?..."
}
```

### POST /api/v1/auth/google/callback

Processa o callback do Google e retorna token JWT.

**Corpo da Requisição:**

```json
{
    "code": "código_do_google",
    "redirect_uri": "http://localhost:8001/api/v1/auth/google/callback"
}
```

**Resposta:**

```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
        "id": 1,
        "nome_completo": "João Silva",
        "email": "joao@gmail.com",
        "cpf": null,
        "data_nascimento": null,
        "is_google_user": true,
        "profile_picture": "https://lh3.googleusercontent.com/...",
        "created_at": "2024-01-15T10:30:00",
        "updated_at": "2024-01-15T10:30:00"
    }
}
```

## 8. Considerações de Segurança

1. **HTTPS em Produção**: Configure sempre HTTPS em produção
2. **Domínios Autorizados**: Adicione apenas domínios confiáveis
3. **Validação de Email**: O sistema só aceita emails verificados pelo Google
4. **Tokens JWT**: Configure tempo de expiração apropriado
5. **Rate Limiting**: Implemente rate limiting nos endpoints OAuth

## 9. Troubleshooting

### Erro: "redirect_uri_mismatch"

- Verifique se a URI de redirecionamento está configurada corretamente no Google Cloud Console
- Certifique-se de que a URI no código corresponde exatamente à configurada

### Erro: "invalid_client"

- Verifique se CLIENT_ID e CLIENT_SECRET estão corretos
- Confirme se as APIs necessárias estão habilitadas

### Erro: "Email não verificado"

- O sistema só aceita emails verificados pelo Google
- Verifique se o email da conta Google está verificado

### Usuário não consegue completar o cadastro

- Para usuários Google, CPF e data de nascimento são opcionais inicialmente
- Implemente um fluxo para coletar essas informações posteriormente se necessário
