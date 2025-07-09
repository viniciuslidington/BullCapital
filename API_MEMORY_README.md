# API de Autenticação - BullCapital (Versão sem Banco de Dados)

API de autenticação usando armazenamento em memória (temporário) para desenvolvimento e testes.

## 🚀 Configuração Rápida

### 1. Instalar dependências
```bash
uv sync
```

### 2. Rodar o servidor
```bash
uvicorn src.main:app --reload
```

**✅ Pronto! Não precisa configurar banco de dados.**

## 📋 Endpoints da API

### 🔐 Autenticação

#### POST `/auth/registrar`
Cria um novo usuário no sistema (armazenado em memória).

**Body:**
```json
{
  "nome_completo": "João Silva",
  "data_nascimento": "1990-01-01",
  "email": "joao@exemplo.com",
  "senha": "minhasenha123"
}
```

#### POST `/auth/login`
Realiza login e retorna token JWT.

**Body:**
```json
{
  "email": "joao@exemplo.com",
  "senha": "minhasenha123"
}
```

#### GET `/auth/perfil`
Retorna informações do usuário autenticado (requer token).

**Headers:**
```
Authorization: Bearer <seu_token_aqui>
```

#### GET `/auth/usuarios` (Debug)
Lista todos os usuários cadastrados (para desenvolvimento).

## 🧪 Teste Rápido

### 1. Acesse a documentação:
```
http://127.0.0.1:8000/docs
```

### 2. Ou teste via curl:
```bash
# 1. Registrar usuário
curl -X POST "http://127.0.0.1:8000/auth/registrar" \
  -H "Content-Type: application/json" \
  -d '{
    "nome_completo": "João Silva",
    "data_nascimento": "1990-01-01",
    "email": "joao@exemplo.com",
    "senha": "minhasenha123"
  }'

# 2. Fazer login
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "joao@exemplo.com",
    "senha": "minhasenha123"
  }'

# 3. Ver usuários cadastrados
curl -X GET "http://127.0.0.1:8000/auth/usuarios"
```

## ⚠️ Importante

- **Dados temporários**: Os usuários são armazenados apenas em memória
- **Reiniciar = Perder dados**: Ao reiniciar o servidor, todos os usuários são perdidos
- **Apenas para desenvolvimento**: Esta versão é para testes e desenvolvimento

## 🔄 Migração Futura

Quando configurar o banco de dados:
1. Substituir `auth_service_memory.py` por `auth_service.py`
2. Substituir `auth_middleware_memory.py` por `auth_middleware.py`
3. Adicionar dependências do banco no controller

## 🎯 Funcionalidades

✅ Registro de usuários  
✅ Login com JWT  
✅ Middleware de autenticação  
✅ Validação de email  
✅ Criptografia de senhas  
✅ Endpoints protegidos  
✅ Documentação automática
