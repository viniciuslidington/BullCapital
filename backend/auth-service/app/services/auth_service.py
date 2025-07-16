from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import jwt

from core.config import settings
from core.models import User
from schemas.user import UserCreate, UserLogin
from crud.user import get_user_by_email, get_user_by_cpf, create_user

# Contexto para hash de senhas usando bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """
    Serviço de autenticação responsável por todas as operações relacionadas
    à segurança e gerenciamento de usuários.
    
    Esta classe centraliza as funcionalidades de:
    - Hash e verificação de senhas
    - Criação e verificação de tokens JWT
    - Registro e autenticação de usuários
    - Validação de tokens e recuperação de usuários
    """
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Gera um hash seguro da senha usando bcrypt.
        
        Args:
            password: Senha em texto plano
            
        Returns:
            str: Hash da senha pronto para armazenamento no banco
        """
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verifica se a senha fornecida confere com o hash armazenado.
        
        Args:
            plain_password: Senha em texto plano fornecida pelo usuário
            hashed_password: Hash da senha armazenado no banco de dados
            
        Returns:
            bool: True se a senha estiver correta, False caso contrário
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Cria um token JWT para autenticação do usuário.
        
        Args:
            data: Dados a serem incluídos no payload do token
            expires_delta: Tempo customizado de expiração (opcional)
            
        Returns:
            str: Token JWT assinado
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """
        Verifica e decodifica um token JWT.
        
        Args:
            token: Token JWT a ser verificado
            
        Returns:
            dict ou None: Payload do token se válido, None se inválido ou expirado
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None
    
    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> User:
        """
        Registra um novo usuário no sistema.
        
        Verifica se o email e CPF já estão em uso, cria o hash da senha
        e salva o novo usuário no banco de dados.
        
        Args:
            db: Sessão do banco de dados
            user_data: Dados do usuário a ser registrado
            
        Returns:
            User: Objeto do usuário criado
            
        Raises:
            ValueError: Se o email ou CPF já estiverem cadastrados
        """
        # Verificar se email já existe
        existing_user_email = get_user_by_email(db, user_data.email)
        if existing_user_email:
            raise ValueError("Email já cadastrado")
        
        # Verificar se CPF já existe
        existing_user_cpf = get_user_by_cpf(db, user_data.cpf)
        if existing_user_cpf:
            raise ValueError("CPF já cadastrado")
        
        # Hash da senha
        hashed_password = AuthService.hash_password(user_data.senha)
        
        # Criar usuário
        return create_user(db, user_data, hashed_password)
    
    @staticmethod
    def authenticate_user(db: Session, login_data: UserLogin) -> Optional[User]:
        """
        Autentica um usuário verificando email e senha.
        
        Args:
            db: Sessão do banco de dados
            login_data: Dados de login (email e senha)
            
        Returns:
            User ou None: Objeto do usuário se autenticação bem-sucedida, None caso contrário
        """
        user = get_user_by_email(db, login_data.email)
        if user and AuthService.verify_password(login_data.senha, user.senha):
            return user
        return None
    
    @staticmethod
    def get_current_user(db: Session, token: str) -> Optional[User]:
        """
        Obtém o usuário atual baseado em um token JWT.
        
        Decodifica o token, extrai o email do usuário e busca
        o usuário correspondente no banco de dados.
        
        Args:
            db: Sessão do banco de dados
            token: Token JWT do usuário
            
        Returns:
            User ou None: Objeto do usuário se token válido, None caso contrário
        """
        payload = AuthService.verify_token(token)
        if not payload:
            return None
        
        email = payload.get("sub")
        if not email:
            return None
        
        return get_user_by_email(db, email)

# Instância global do serviço de autenticação
auth_service = AuthService()
