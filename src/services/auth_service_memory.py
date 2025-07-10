from typing import Dict, List, Optional
from models.schemas import UserCreateRequest, UserLoginRequest
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt

pwd_contexto = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configurações JWT
SECRET_KEY = "seu_secret_key_aqui"  # Mude para uma chave segura
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Armazenamento temporário em memória (substitui o banco de dados)
usuarios_db: List[Dict] = []
next_user_id = 1

class UserInMemory:
    def __init__(self, id: int, nome_completo: str, data_nascimento: str, email: str, senha: str):
        self.id = id
        self.nome_completo = nome_completo
        self.data_nascimento = data_nascimento
        self.email = email
        self.senha = senha

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

def criar_usuario(user_data: UserCreateRequest) -> UserInMemory:
    global next_user_id
    
    # Verificar se o email já existe
    for user in usuarios_db:
        if user["email"] == user_data.email:
            raise ValueError("Email já cadastrado")
    
    senha_hashed = gerar_hash_senha(user_data.senha)
    novo_usuario_data = {
        "id": next_user_id,
        "nome_completo": user_data.nome_completo,
        "data_nascimento": str(user_data.data_nascimento),
        "email": user_data.email,
        "senha": senha_hashed
    }
    
    usuarios_db.append(novo_usuario_data)
    novo_usuario = UserInMemory(**novo_usuario_data)
    next_user_id += 1
    
    return novo_usuario

def autenticar_usuario(login_data: UserLoginRequest) -> Optional[UserInMemory]:
    for user_data in usuarios_db:
        if user_data["email"] == login_data.email:
            if verificar_senha(login_data.senha, user_data["senha"]):
                return UserInMemory(**user_data)
    return None

def obter_usuario_por_email(email: str) -> Optional[UserInMemory]:
    for user_data in usuarios_db:
        if user_data["email"] == email:
            return UserInMemory(**user_data)
    return None

def listar_usuarios() -> List[Dict]:
    """Função para debug - listar todos os usuários cadastrados"""
    return [
        {
            "id": user["id"],
            "nome_completo": user["nome_completo"],
            "data_nascimento": user["data_nascimento"],
            "email": user["email"]
        }
        for user in usuarios_db
    ]
