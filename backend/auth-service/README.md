# Auth Service

Serviço de autenticação e gerenciamento de usuários usando FastAPI, SQLAlchemy e PostgreSQL.

## Estrutura do Projeto

```
auth-service/
├── app/
│   ├── api/                    # Endpoints da API
│   │   ├── __init__.py
│   │   └── auth.py
│   ├── core/                   # Configurações centrais
│   │   ├── __init__.py
│   │   ├── config.py          # Configurações da aplicação
│   │   ├── database.py        # Configuração do banco
│   │   ├── models.py          # Modelos SQLAlchemy
│   │   └── security.py        # Middleware de autenticação
│   ├── schemas/                # Schemas Pydantic
│   │   ├── __init__.py
│   │   └── user.py
│   ├── crud/                   # Operações CRUD
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services/               # Lógica de negócio
│   │   ├── __init__.py
│   │   └── auth_service.py
│   ├── __init__.py
│   └── main.py                 # Aplicação principal
├── requirements.txt
├── Dockerfile
├── .env
└── README.md
```

## Funcionalidades

- ✅ Registro de usuários
- ✅ Autenticação via JWT
- ✅ Perfil do usuário (obter/atualizar)
- ✅ Listar usuários (paginado)
- ✅ Buscar usuário por ID
- ✅ Deletar usuário
- ✅ Middleware de autenticação
- ✅ Validação de dados com Pydantic
- ✅ Hash seguro de senhas com bcrypt
- ✅ Documentação automática com Swagger/OpenAPI

## Instalação e Execução

### 1. Configurar ambiente virtual

```bash
cd auth-service
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente

Copie o arquivo `.env` e configure suas variáveis:

```bash
cp .env .env.local
# Edite .env.local com suas configurações
```

### 4. Executar a aplicação

```bash
# Desenvolvimento
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Produção
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. Com Docker

```bash
# Build
docker build -t auth-service .

# Run
docker run -p 8000:8000 --env-file .env auth-service
```

## API Endpoints

### Autenticação

- `POST /api/v1/auth/register` - Registrar usuário
- `POST /api/v1/auth/login` - Fazer login
- `GET /api/v1/auth/profile` - Obter perfil (requer auth)
- `PUT /api/v1/auth/profile` - Atualizar perfil (requer auth)

### Usuários

- `GET /api/v1/auth/users` - Listar usuários (requer auth)
- `GET /api/v1/auth/users/{id}` - Obter usuário por ID (requer auth)
- `DELETE /api/v1/auth/users/{id}` - Deletar usuário (requer auth)

### Utilitários

- `GET /` - Status do serviço
- `GET /health` - Health check
- `GET /docs` - Documentação Swagger
- `GET /redoc` - Documentação ReDoc

## Exemplos de Uso

### Registrar usuário

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "nome_completo": "João Silva",
    "data_nascimento": "1990-01-01",
    "email": "joao@example.com",
    "senha": "senha123"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "joao@example.com",
    "senha": "senha123"
  }'
```

### Acessar perfil (com token)

```bash
curl -X GET "http://localhost:8000/api/v1/auth/profile" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

## Configurações

### Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `user` | Usuário do banco | postgres |
| `password` | Senha do banco | password |
| `host` | Host do banco | localhost |
| `port` | Porta do banco | 5432 |
| `dbname` | Nome do banco | bullcapital |
| `SECRET_KEY` | Chave secreta JWT | - |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiração do token | 30 |
| `DEBUG_SQL` | Debug SQL | false |

### Segurança

- Senhas são hasheadas com bcrypt
- Tokens JWT com expiração configurável
- CORS configurado para desenvolvimento
- Validação de entrada com Pydantic

## Desenvolvimento

A aplicação está estruturada seguindo os princípios de Clean Architecture:

- **API Layer**: Endpoints e validação de entrada
- **Service Layer**: Lógica de negócio
- **CRUD Layer**: Operações de banco de dados
- **Core Layer**: Configurações e modelos

## Melhorias Futuras

- [ ] Rate limiting
- [ ] Refresh tokens
- [ ] Roles e permissões
- [ ] Logs estruturados
- [ ] Testes automatizados
- [ ] Métricas e monitoring
- [ ] Cache com Redis
