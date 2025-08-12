###############################
# Frontend (Vite + React) Dev Dockerfile
# Objetivos:
# - Cache eficiente de dependências
# - Suporte a hot reload (npm run dev)
# - Usuário não-root
# - Sem Nginx (dev server do Vite)
# - Parametrização de porta e host
###############################

FROM node:20-alpine AS base

ENV PNPM_HOME="/pnpm" \
	NODE_ENV=development \
	CI=true
ENV PATH="$PNPM_HOME:$PATH"

WORKDIR /app

# Dependências do SO mínimas (se precisar bibliotecas adicionais, adicione aqui)
RUN apk add --no-cache bash git libc6-compat

# Copia somente arquivos de manifesto para camada de dependências
COPY package*.json ./
COPY tsconfig*.json ./
COPY vite.config.ts ./
COPY tailwind.config.ts ./
# components.json (se existir) - não falhar se ausente
RUN if [ -f components.json ]; then echo "components.json presente"; fi

# Instala dependências (usa npm ci para reprodutibilidade)
RUN npm ci --no-audit --no-fund

# Copia restante do código
COPY . .

# Cria usuário não-root para rodar o dev server
RUN addgroup -g 1001 nodeapp && \
	adduser -D -u 1001 -G nodeapp nodeapp && \
	chown -R nodeapp:nodeapp /app
USER nodeapp

# Porta padrão do Vite
EXPOSE 5173

# Argumentos/variáveis opcionais (podem ser sobrepostos via docker-compose)
ENV VITE_PORT=5173 \
	VITE_HOST=0.0.0.0

# Comando de desenvolvimento (hot reload)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]

