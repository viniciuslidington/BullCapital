# BullCapital Backend - Integração com PostgreSQL

## 🎉 Status: ✅ CONFIGURADO COM SUCESSO!

Sua aplicação foi configurada para usar PostgreSQL! As tabelas foram criadas e a aplicação está funcionando.

## 📋 O que foi implementado:

### 1. **Configuração do Banco de Dados**
- ✅ Conexão com PostgreSQL via SQLAlchemy
- ✅ Sessões síncronas configuradas
- ✅ Tabela `users` criada com sucesso

### 2. **Sistema de Autenticação**
- ✅ Registro de usuários com hash de senha (bcrypt)
- ✅ Login com JWT tokens
- ✅ Middleware de autenticação
- ✅ Endpoint protegido de perfil

### 3. **API Endpoints Disponíveis**

#### **Autenticação (`/api/auth`)**
- `POST /api/auth/registrar` - Registrar novo usuário
- `POST /api/auth/login` - Fazer login
- `GET /api/auth/perfil` - Obter perfil (protegido)
- `GET /api/auth/usuarios` - Listar usuários (debug)

#### **Dados B3 (`/b3`)**
- `GET /b3/dados` - Obter dados de ações da B3

#### **Sistema**
- `GET /` - Mensagem de boas-vindas
- `GET /health` - Health check
- `GET /docs` - Documentação Swagger

## 🚀 Como Executar

### 1. **Configurar Variáveis de Ambiente**
```bash
cp .env.example .env
# Edite o .env com suas credenciais do PostgreSQL
```

### 2. **Instalar Dependências**
```bash
uv sync
```

### 3. **Criar Tabelas no Banco**
```bash
uv run create_tables.py
```

### 4. **Executar a Aplicação**
```bash
uv run src/main.py
```

A aplicação estará disponível em: http://localhost:8000

## 📚 Documentação da API

Acesse: http://localhost:8000/docs

## 🧪 Testando a API

### Registrar um usuário:
```bash
curl -X POST "http://localhost:8000/api/auth/registrar" \
  -H "Content-Type: application/json" \
  -d '{
    "nome_completo": "João Silva",
    "data_nascimento": "1990-01-01",
    "email": "joao@email.com",
    "senha": "minhasenha123"
  }'
```

### Fazer login:
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "joao@email.com",
    "senha": "minhasenha123"
  }'
```

### Acessar perfil (com token):
```bash
curl -X GET "http://localhost:8000/api/auth/perfil" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

## 🔧 Estrutura Atualizada

```
src/
├── main.py                    # Ponto de entrada da aplicação
├── models/
│   ├── database.py           # Configuração do SQLAlchemy
│   ├── user.py              # Modelo User
│   └── schemas.py           # Schemas Pydantic
├── services/
│   └── auth_service.py      # Lógica de autenticação
├── middlewares/
│   └── auth_middleware.py   # Middleware JWT
├── controllers/
│   └── auth_controller.py   # Controllers de autenticação
└── routes/
    ├── auth_routes.py       # Rotas de autenticação
    └── b3_data.py          # Rotas de dados B3
```

## 🛡️ Segurança

- ✅ Senhas hasheadas com bcrypt
- ✅ JWT tokens para autenticação
- ✅ Middleware de proteção de rotas
- ✅ Validação de dados com Pydantic

## 💾 Banco de Dados

**Tabela `users`:**
- `id` (PRIMARY KEY, SERIAL)
- `nome_completo` (VARCHAR, NOT NULL)
- `data_nascimento` (DATE, NOT NULL)
- `email` (VARCHAR, UNIQUE, NOT NULL)
- `senha` (VARCHAR, NOT NULL) - Hasheada com bcrypt

## 🔍 Logs

A aplicação mostra logs de:
- ✅ Conexão com banco de dados
- ✅ Criação de tabelas
- ✅ Queries SQL (modo debug)
- ✅ Requests HTTP

---

**🎯 Sua aplicação está pronta para uso com PostgreSQL!**
