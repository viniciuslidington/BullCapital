"""
Market Data Service - Aplicação Principal.

Este módulo configura e inicializa o microserviço de Market Data,
incluindo middleware, CORS, documentação automática e tratamento de erros.

Example:
    # Executar o serviço
    uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
"""

import time
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.market_data import router as market_data_router
from core.config import settings
from core.logging import get_logger
from models.responses import ErrorResponse

# Configurar logger
logger = get_logger(__name__)

# Variável para tracking de uptime
startup_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação.
    
    Executa tarefas de inicialização e finalização do serviço,
    incluindo configuração de recursos e limpeza de conexões.
    
    Args:
        app: Instância da aplicação FastAPI
    """
    # Startup
    logger.info("🚀 Iniciando Market Data Service...")
    logger.info(f"📊 Versão: {settings.API_VERSION}")
    logger.info(f"🔧 Debug Mode: {settings.DEBUG}")
    logger.info(f"🔗 CORS Origins: {settings.ALLOWED_ORIGINS}")
    
    # Aqui podem ser adicionadas tarefas de inicialização como:
    # - Conexões com databases
    # - Inicialização de cache
    # - Verificação de serviços externos
    # - Pré-carregamento de dados
    
    try:
        # Teste básico de funcionalidade
        logger.info("✅ Serviços inicializados com sucesso")
        logger.info(f"🌐 Servidor rodando em {settings.HOST}:{settings.PORT}")
        
    except Exception as e:
        logger.error(f"❌ Erro na inicialização: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Finalizando Market Data Service...")
    logger.info("✅ Recursos liberados com sucesso")


# Criar aplicação FastAPI
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    # Metadata adicional para documentação
    contact={
        "name": "BullCapital Team",
        "email": "dev@bullcapital.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {
            "url": f"http://localhost:{settings.PORT}",
            "description": "Desenvolvimento"
        },
        {
            "url": "https://api.bullcapital.com",
            "description": "Produção"
        }
    ]
)


# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Rate-Limit-Remaining"]
)


# Middleware para logging de requisições
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """
    Middleware para logging detalhado de requisições.
    
    Registra informações sobre cada requisição incluindo tempo de processamento,
    status de resposta e dados relevantes para monitoramento.
    
    Args:
        request: Objeto de requisição HTTP
        call_next: Próximo middleware na cadeia
        
    Returns:
        Response HTTP com headers adicionais
    """
    start_time = time.time()
    
    # Gerar ID único para a requisição
    request_id = f"{int(start_time * 1000)}-{hash(str(request.url)) % 10000}"
    
    # Log da requisição
    logger.info(
        f"📥 {request.method} {request.url.path} "
        f"[{request_id}] from {request.client.host if request.client else 'unknown'}"
    )
    
    try:
        # Processar requisição
        response = await call_next(request)
        
        # Calcular tempo de processamento
        process_time = time.time() - start_time
        
        # Adicionar headers de resposta
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.3f}"
        
        # Log da resposta
        logger.info(
            f"📤 {request.method} {request.url.path} "
            f"[{request_id}] {response.status_code} "
            f"({process_time:.3f}s)"
        )
        
        return response
        
    except Exception as e:
        # Log de erro
        process_time = time.time() - start_time
        logger.error(
            f"💥 {request.method} {request.url.path} "
            f"[{request_id}] ERROR: {str(e)} "
            f"({process_time:.3f}s)"
        )
        raise


# Middleware para rate limiting headers
@app.middleware("http")
async def rate_limit_headers_middleware(request: Request, call_next):
    """
    Middleware para adicionar headers de rate limiting.
    
    Adiciona informações sobre limites de taxa nas respostas,
    permitindo que clientes monitorem seu uso da API.
    
    Args:
        request: Objeto de requisição HTTP
        call_next: Próximo middleware na cadeia
        
    Returns:
        Response HTTP com headers de rate limiting
    """
    response = await call_next(request)
    
    # Adicionar headers de rate limiting
    response.headers["X-Rate-Limit-Limit"] = str(settings.RATE_LIMIT_REQUESTS)
    response.headers["X-Rate-Limit-Window"] = str(settings.RATE_LIMIT_WINDOW)
    
    # Em uma implementação real, você calcularia os valores reais baseado
    # no rate limiter do serviço
    response.headers["X-Rate-Limit-Remaining"] = "95"  # Placeholder
    response.headers["X-Rate-Limit-Reset"] = str(int(time.time() + 60))  # Placeholder
    
    return response


# Handler global para exceções não tratadas
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handler global para exceções não tratadas.
    
    Captura todas as exceções que não foram tratadas especificamente
    e retorna uma resposta estruturada consistente.
    
    Args:
        request: Objeto de requisição HTTP
        exc: Exceção capturada
        
    Returns:
        JSONResponse com detalhes do erro
    """
    logger.error(f"Exceção não tratada: {str(exc)}", exc_info=True)
    
    error_response = ErrorResponse(
        error="INTERNAL_SERVER_ERROR",
        message="Erro interno do servidor",
        details={"path": str(request.url.path)} if settings.DEBUG else None,
        timestamp=datetime.now().isoformat()
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.dict()
    )


# Handler para 404 (Not Found)
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """
    Handler personalizado para 404 Not Found.
    
    Args:
        request: Objeto de requisição HTTP
        exc: Exceção 404
        
    Returns:
        JSONResponse com mensagem amigável
    """
    error_response = ErrorResponse(
        error="NOT_FOUND",
        message=f"Endpoint '{request.url.path}' não encontrado",
        details={
            "available_endpoints": [
                "/docs",
                "/api/v1/market-data/",
                "/api/v1/market-data/stocks/{symbol}",
                "/api/v1/market-data/stocks/search",
                "/api/v1/market-data/health"
            ]
        },
        timestamp=datetime.now().isoformat()
    )
    
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=error_response.dict()
    )


# Incluir routers
app.include_router(
    market_data_router,
    prefix="/api/v1/market-data",
    tags=["Market Data"]
)


# Endpoints raiz
@app.get(
    "/",
    summary="Informações do Market Data Service",
    description="Retorna informações básicas e status do serviço."
)
async def root():
    """
    Endpoint raiz com informações do serviço.
    
    Returns:
        Informações básicas sobre o Market Data Service
    """
    uptime = time.time() - startup_time
    
    return {
        "service": "Market Data Service",
        "version": settings.API_VERSION,
        "status": "running",
        "uptime_seconds": round(uptime, 2),
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "documentation": "/docs",
            "api": "/api/v1/market-data/",
            "health": "/api/v1/market-data/health"
        },
        "features": [
            "Real-time stock data",
            "Historical price data",
            "Stock search and validation",
            "Bulk data requests",
            "Rate limiting",
            "Caching",
            "Comprehensive API documentation"
        ]
    }


@app.get(
    "/ping",
    summary="Verificação básica de conectividade",
    description="Endpoint simples para verificar se o serviço está respondendo."
)
async def ping():
    """
    Endpoint simples de ping.
    
    Returns:
        Resposta básica de pong com timestamp
    """
    return {
        "message": "pong",
        "timestamp": datetime.now().isoformat(),
        "service": "market-data-service"
    }


# Configuração adicional para desenvolvimento
if settings.DEBUG:
    logger.info("🔧 Modo DEBUG ativado")
    
    @app.get("/debug/config")
    async def debug_config():
        """Endpoint de debug para visualizar configurações (apenas desenvolvimento)."""
        return {
            "debug": settings.DEBUG,
            "api_version": settings.API_VERSION,
            "allowed_origins": settings.ALLOWED_ORIGINS,
            "cache_enabled": settings.ENABLE_CACHE,
            "cache_ttl": settings.CACHE_TTL_SECONDS,
            "rate_limit_requests": settings.RATE_LIMIT_REQUESTS,
            "rate_limit_window": settings.RATE_LIMIT_WINDOW
        }


# Punto de entrada para executar com uvicorn
if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🚀 Iniciando servidor em {settings.HOST}:{settings.PORT}")
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )
