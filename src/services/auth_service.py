from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.user import User
from models.schemas import UserCreateRequest, UserLoginRequest
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from typing import Optional

pwd_contexto = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configurações JWT
SECRET_KEY = "seu_secret_key_aqui"  # Mude para uma chave segura
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def gerar_hash_senha(senha: str) -> str:
    return pwd_contexto.hash(senha)

def verificar_senha(senha_plana: str, senha_hashed: str) -> bool:
    return pwd_contexto.verify(senha_plana, senha_hashed)

def criar_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def criar_usuario(db: AsyncSession, user_data: UserCreateRequest) -> User:
    # Verificar se o email já existe
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise ValueError("Email já cadastrado")
    
    senha_hashed = gerar_hash_senha(user_data.senha)
    novo_usuario = User(
        nome_completo=user_data.nome_completo,
        data_nascimento=user_data.data_nascimento,
        email=user_data.email,
        senha=senha_hashed
    )
    db.add(novo_usuario)
    await db.commit()
    await db.refresh(novo_usuario)
    return novo_usuario

async def autenticar_usuario(db: AsyncSession, login_data: UserLoginRequest) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == login_data.email))
    usuario = result.scalars().first()
    if usuario and verificar_senha(login_data.senha, usuario.senha):
        return usuario
    return None

async def obter_usuario_por_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()
