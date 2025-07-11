from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.v1 import v1_router

app = FastAPI(
    title="BullCapital API",
    description="API para obter dados financeiros processados da B3",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Habilita CORS para o frontend acessar a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include da API versionada
app.include_router(v1_router)

@app.get("/", tags=["Root"])
def read_root():
    """
    Endpoint raiz para verificar se a API está funcionando.
    """
    return {
        "message": "Bem-vindo à API BullCapital!",
        "version": "1.0.0",
        "docs": "/docs",
        "api_v1": "/api/v1"
    }

@app.get("/health", tags=["System"])
def health_check():
    """
    Health check endpoint para monitoramento da aplicação.
    """
    return {
        "status": "healthy",
        "service": "bullcapital-api",
        "version": "1.0.0"
    }
