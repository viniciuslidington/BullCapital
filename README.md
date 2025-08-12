# Bull Capital

Plataforma de análise e acompanhamento do mercado financeiro com foco em investidores brasileiros. Integra dados de mercado, autenticação segura, agente de IA e um gateway unificado para consumo via frontend moderno (Vite + React + Tailwind).

## ✨ Visão Geral

| Componente | Porta | Descrição |
|-----------|-------|-----------|
| Gateway API | 8000 | Orquestra chamadas para os microserviços (facade) |
| Auth Service | 8003 | Autenticação, usuários, sessões e OAuth Google |
| Market Data Service | 8002 | Dados de mercado: cotações, históricos, rankings, busca |
| AI Service | 8001 | Agente de análise financeira e chat contextual |
| Frontend (Vite) | 5173 | Interface web SPA |
| Postgres Auth | 5432 | Banco de autenticação |
| Postgres AI | 5433 | Banco de conversas/IA |

## 🏛 Contexto Acadêmico e Motivação
Este repositório está associado a um esforço acadêmico do Centro de Informática (CIn/UFPE) voltado à democratização do acesso à análise do mercado de capitais brasileiro, com foco especial em investidores pessoa física do Nordeste. Entre 2021 e 2025, o número de investidores nordestinos cresceu mais de 36%, passando de aproximadamente 310 mil para 658 mil e alcançando cerca de 716 mil ao final de 2024 (dados B3). Ainda assim, barreiras de jargão técnico (P/L, ROE, WACC) e assimetria informacional limitam a autonomia decisória de iniciantes.

O BullCapital surge como uma plataforma que:
- Converte dados públicos dispersos (CVM, B3 e fontes abertas) em análises compreensíveis.
- Usa agentes de IA, processamento de linguagem natural e modelos fundamentalistas para responder perguntas abertas.
- Explicita premissas e limitações, evitando promessas de “automatização mágica” de investimentos.

### Objetivo Central
Reduzir barreiras cognitivas e linguísticas para que investidores iniciantes e intermediários compreendam não só o número final, mas também o raciocínio por trás das métricas de análise.

### Abordagem Metodológica
Foi construído um núcleo funcional mínimo (MVP incremental) com:
- Ciclos curtos de validação com usuários.
- Definição de fluxo conversacional e governança de dados.
- Transparência e rastreabilidade dos cálculos (valuation, múltiplos, fluxo de caixa, dividendos etc.).

### Escopo Evolutivo (MVP → Expansão)
1. MVP 1: Chat + indicadores fundamentais básicos (P/L, Dividend Yield, ROE) a partir de dados públicos.
2. MVP 2: Comparação de 2–5 ações, resumos automáticos de releases e notificações de eventos (dividendos / splits).
3. MVP 3: Gráficos interativos, personalização por perfil de risco e histórico de consultas.
4. MVP 4: Simulações de cenários (payout, margens), exportação PDF, RAG avançado direto na API da B3, comparações setoriais ampliadas.

### Diferencial
Foco em UX pedagógica: cada métrica acompanhada de contexto, definição e limitações – transformando dados em aprendizado progressivo.

### Equipe / Autores (Resumo Biográfico)
Projeto desenvolvido por estudantes e colaboradores do CIn-UFPE: Luiz Miguel G. R. Andrade, Marcelo Corrêa A. P. Melo, Gabriel W. A. Matias, Carlos Eduardo F. Teixeira, João Henrique Ebbers, Vinicius A. S. Lidington Lins – com experiências distribuídas em engenharia de software, dados, valuation, UX e liderança de times acadêmicos e iniciativas de impacto social.

> Para o texto completo do relatório (incluindo biografias ampliadas, fundamentação e referências B3), consulte a seção “Relatório Acadêmico” ou arquivo complementar quando disponibilizado.

## 🧱 Arquitetura (alto nível)
```
frontend (SPA) --> gateway-service --> { auth-service, market-data-service, ai-service }
                                         |            |                |
                                         |            |                +--> Postgres (ai)
                                         |            +--> Yahoo / fontes externas
                                         +--> Postgres (auth)
```

## 🔐 Variáveis de Ambiente (.env)
Para acessar todos os recursos (login, Google OAuth, agente IA) é necessário obter o arquivo `.env` completo.

Solicite o `.env` pelo e‑mail: vasll@cin.ufpe.br
Assunto sugerido: "Solicitação .env BullCapital".

Após receber, coloque-o na raiz do projeto (ao lado de `docker-compose.yml`).

Exemplo reduzido (NÃO usar em produção):
```
OPENAI_API_KEY=sk-...
AUTH_SECRET_KEY=gerar_nova_key
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=http://localhost:8003/api/v1/auth/google/callback
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:5173","http://localhost:8000"]
# Databases
AUTH_DB_USER=auth_user
AUTH_DB_PASSWORD=auth_password_2025
AI_DB_USER=ai_user
AI_DB_PASSWORD=ai_password_2025
```

## 🚀 Como Rodar (Super Simples)
Pré‑requisitos: Docker + Docker Compose V2 e arquivo `.env` na raiz (solicite por e‑mail conforme seção anterior).

1. Clonar
```
git clone https://github.com/viniciuslidington/BullCapital.git
cd BullCapital
```
2. Adicionar o `.env` na raiz.
3. Rodar tudo (build + subir em background):
```
docker compose up -d --build
```
4. Acessar:
  - Frontend: http://localhost:5173
  - Gateway: http://localhost:8000/

Logs rápidos (exemplo):
```
docker compose logs -f gateway-service
```
Parar:
```
docker compose down
```
Parar e limpar bancos (⚠️ apaga dados):
```
docker compose down -v
```

Opcional (subir sem IA inicialmente):
```
docker compose up -d --build auth-postgres auth-service market-data-service gateway-service frontend
```
Depois subir IA:
```
docker compose up -d ai-postgres ai-service
```

Rebuild de um serviço específico (ex: gateway):
```
docker compose up -d --build gateway-service
```

## 🔍 Health Endpoints
| Serviço | Endpoint |
|---------|----------|
| Gateway | http://localhost:8000/health |
| Auth | http://localhost:8003/health |
| Market Data | http://localhost:8002/health |
| AI | http://localhost:8001/health |

## 🧪 Testes Rápidos via curl
```
# Root gateway
curl http://localhost:8000/
# Busca mercado via gateway
curl "http://localhost:8000/market-data/search?query=PETR&limit=5"
# Health auth
curl http://localhost:8003/health
```

## 🗃️ Estrutura Simplificada
```
backend/
  auth-service/
  gateway-service/
  market-data-service/
  ai-service/
frontend/
  src/
```

## 🛡️ Segurança / Boas Práticas
- Nunca commitar `.env` reais (já ignorado em `.gitignore`).
- Rotacionar `AUTH_SECRET_KEY` se houver exposição.
- Usar chaves diferentes para ambiente de produção.
- Limitar CORS em produção (evitar `*`).

## 🧠 AI Service (resumo)
- Chat contextual com histórico persistente.
- Geração de título automático para conversas.
- Persistência em Postgres separado.

## 📈 Market Data (resumo)
- Multi endpoints: histórico, categorias, recomendações, performance, busca.
- Integração com dados de múltiplos mercados.

## 🔑 Auth Service (resumo)
- Registro/login tradicional.
- OAuth Google.
- Cookies HTTP-only (se configurado no backend) + JWT.

## 🌉 Gateway Service
- Simplifica consumo no frontend.
- Camada de agregação e roteamento.

## 💻 Frontend
- Vite + React + TypeScript + Tailwind.
- Hooks para cada domínio (auth, market, ai, etc.).

## 🧩 Roadmap (ideias)
- Rate limiting central no gateway.
- Observabilidade (Prometheus + Grafana).
- Cache Redis para market-data.
- Deploy com CI/CD e imagens multi-stage otimizadas.

## 🤝 Contribuição
1. Abra uma issue com descrição clara.
2. Crie branch: `feat/...`, `fix/...` ou `chore/...`.
3. PR descritivo citando contexto e testes.

## 🗑️ Limpeza de Volumes (se necessário)
```
docker volume ls | grep bullcapital
# remover específicos
docker volume rm bullcapital_ai_pgdata
```

## ❓ Suporte / Contato
Envie dúvidas ou solicitação de `.env` para: vasll@cin.ufpe.br

---
Feito com foco em modularidade e extensibilidade.
