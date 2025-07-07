from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://usuario:senha@localhost:5432/nome_do_banco"

# Configurar o engine assíncrono
engine = create_async_engine(DATABASE_URL, echo=True)

# Criar uma fábrica de sessões
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Função para obter uma sessão de banco de dados
async def get_db():
    async with SessionLocal() as session:
        yield session
