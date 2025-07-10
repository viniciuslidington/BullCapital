import psycopg2
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Dados de conexão
host = "127.0.0.1"  # Proxy local
port = "5432"
database = "postgres"
user = "bullcapital"
password = "bullcapital"

DATABASE_URL = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"

# Configurar o engine assíncrono
engine = create_async_engine(DATABASE_URL, echo=True)

# Criar uma fábrica de sessões
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Função para obter uma sessão de banco de dados
async def get_db():
    async with SessionLocal() as session:
        yield session

def get_db_sync():
    try:
        # Conecta ao banco
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        return conn
    except Exception as e:
        print("Erro na conexão com o banco de dados:", e)
        return None
