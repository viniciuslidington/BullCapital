from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from core.config import settings
from core.database import engine
from core.models import Base
from api.auth import router as auth_router
import logging
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação FastAPI.
    
    Função assíncrona que controla eventos de inicialização e finalização
    da aplicação. Durante a inicialização, cria as tabelas do banco de dados
    automaticamente usando SQLAlchemy.
    
    Args:
        app: Instância da aplicação FastAPI
        
    Yields:
        None: Controle retorna ao FastAPI durante a execução da aplicação
        
    Note:
        Em caso de falha na criação das tabelas, a aplicação continua
        executando mas registra o erro no log.
    """
    # Startup
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        logger.warning("Application will continue without database connection")
    
    yield
    
    # Shutdown
    logger.info("Application shutting down...")

app = FastAPI(
    title="Auth Service",
    description="Serviço de autenticação e gerenciamento de usuários",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])

@app.get("/")
def read_root():
    """
    Endpoint raiz da aplicação.
    
    Retorna uma mensagem simples confirmando que o serviço de autenticação
    está em execução. Útil para verificações básicas de saúde.
    
    Returns:
        dict: Mensagem de status do serviço
    """
    return {"message": "Auth Service is running"}

@app.get("/health")
def health_check():
    """
    Endpoint de verificação de saúde do serviço.
    
    Verifica o status geral da aplicação e a conectividade com o banco de dados.
    Retorna informações sobre o estado da aplicação e da conexão com o banco.
    
    Returns:
        dict: Status da aplicação e do banco de dados
        
    Note:
        Se houver problemas na conexão com o banco, o serviço ainda
        reportará como "healthy" mas indicará o problema no campo "database".
    """
    try:
        # Test database connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {"status": "healthy", "database": "disconnected", "error": str(e)}

