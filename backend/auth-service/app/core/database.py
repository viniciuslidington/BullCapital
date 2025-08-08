"""
Módulo de configuração e gerenciamento do banco de dados.

Este módulo configura a conexão com o banco de dados PostgreSQL usando SQLAlchemy,
incluindo configurações de pool de conexões, timeouts e gerenciamento de sessões.

Componentes principais:
- Engine do SQLAlchemy com pool de conexões otimizado
- SessionLocal para criação de sessões de banco
- Base declarativa para modelos ORM
- Função de dependência get_db para FastAPI
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from core.config import settings
import logging

logger = logging.getLogger(__name__)

# Create engine with connection pooling and error handling
"""
Engine do SQLAlchemy configurado com pool de conexões e tratamento de erros.

Configurações do pool:
- pool_pre_ping: Verifica conexões antes de usar (detecta conexões mortas)
- pool_recycle: Recicla conexões a cada 5 minutos
- pool_size: Mantém 5 conexões ativas no pool
- max_overflow: Permite até 10 conexões adicionais quando o pool está cheio
- echo: Ativa log de queries SQL se DEBUG_SQL estiver True
"""
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,    # Recycle connections every 5 minutes
    pool_size=5,         # Number of connections to maintain
    max_overflow=10,     # Additional connections when pool is full
    echo=settings.DEBUG_SQL
)

# Create SessionLocal class
"""
Classe de sessão local configurada para não fazer autocommit nem autoflush.
Esta configuração garante controle manual sobre transações.
"""
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for declarative models
"""
Classe base para todos os modelos SQLAlchemy.
Todos os modelos de dados devem herdar desta classe.
"""
Base = declarative_base()

# Dependency to get DB session
def get_db():
    """
    Dependência do FastAPI para obter uma sessão do banco de dados.
    
    Esta função cria uma nova sessão do banco de dados para cada requisição,
    garantindo o isolamento de transações e o fechamento adequado das conexões.
    Em caso de erro, faz rollback automático da transação.
    
    Yields:
        Session: Sessão ativa do SQLAlchemy
        
    Raises:
        Exception: Re-propaga exceções após fazer rollback da transação
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

# Test the connection (only in debug mode)
if settings.DEBUG_SQL:
    try:
        with engine.connect() as connection:
            logger.info("Database connection successful!")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
