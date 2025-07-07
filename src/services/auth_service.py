from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.user import User
from passlib.context import CryptContext

pwd_contexto = CryptContext(schemes=["bcrypt"], deprecated="auto")

def gerar_hash_senha(senha):
    return pwd_contexto.hash(senha)

def verificar_senha(senha_plana, senha_hashed):
    return pwd_contexto.verify(senha_plana, senha_hashed)

async def criar_usuario(db: AsyncSession, nome_usuario: str, senha: str):
    senha_hashed = gerar_hash_senha(senha)
    novo_usuario = User(username=nome_usuario, password=senha_hashed)
    db.add(novo_usuario)
    await db.commit()
    await db.refresh(novo_usuario)
    return novo_usuario

async def autenticar_usuario(db: AsyncSession, nome_usuario: str, senha: str):
    resultado = await db.execute(select(User).where(User.username == nome_usuario))
    usuario = resultado.scalars().first()
    if usuario and verificar_senha(senha, usuario.password):
        return usuario
    return None
