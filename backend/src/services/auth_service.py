from sqlalchemy.orm import Session
from models.user import User
from models.schemas import UserCreateRequest, UserLoginRequest
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

pwd_contexto = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configurações JWT
SECRET_KEY = os.getenv("SECRET_KEY", "seu_secret_key_aqui_muito_seguro_e_unico")
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

def criar_usuario(db: Session, user_data: UserCreateRequest) -> User:
    # Verificar se o email já existe
    existing_user = db.query(User).filter(User.email == user_data.email).first()
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
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario

def autenticar_usuario(db: Session, login_data: UserLoginRequest) -> Optional[User]:
    usuario = db.query(User).filter(User.email == login_data.email).first()
    if usuario and verificar_senha(login_data.senha, usuario.senha):
        return usuario
    return None

def obter_usuario_por_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def listar_usuarios(db: Session) -> list[User]:
    return db.query(User).all()
