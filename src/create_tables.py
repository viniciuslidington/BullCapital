from models.user import Base
from models.database import engine

async def criar_tabelas():
    """Cria todas as tabelas no banco de dados"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    import asyncio
    asyncio.run(criar_tabelas())
    print("Tabelas criadas com sucesso!")
