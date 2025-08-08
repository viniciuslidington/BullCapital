from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Optional

from core.database import get_db
from core.models import User
from core.config import settings
from crud.user import get_user_by_email

# Esquema de segurança HTTP Bearer para compatibilidade com tokens
security = HTTPBearer(auto_error=False)

def get_token_from_cookie_or_header(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """
    Extrai token do cookie ou header Authorization.
    Prioriza cookie para maior segurança.
    """
    # Primeiro tenta obter do cookie
    token = request.cookies.get("access_token")
    
    # Se não tem cookie, tenta do header Authorization
    if not token and credentials:
        token = credentials.credentials
    
    return token

def get_current_user_from_token(token: str, db: Session) -> Optional[User]:
    """
    Valida token JWT e retorna o usuário correspondente.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None
    
    user = get_user_by_email(db, email)
    return user

def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> User:
    """
    Dependência para obter o usuário autenticado atual.
    
    Suporta autenticação via cookie (preferencial) ou header Authorization.
    Valida o token JWT e retorna o usuário correspondente.
    
    Args:
        request: Objeto Request do FastAPI para acessar cookies
        db: Sessão do banco de dados
        credentials: Credenciais de autorização HTTP Bearer (opcional)
        
    Returns:
        User: Objeto do usuário autenticado
        
    Raises:
        HTTPException: 401 se não houver token ou for inválido
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token de acesso requerido",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Obtém token do cookie ou header
    token = get_token_from_cookie_or_header(request, credentials)
    
    if not token:
        raise credentials_exception
    
    # Valida token e obtém usuário
    user = get_current_user_from_token(token, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def require_auth(current_user: User = Depends(get_current_user)) -> User:
    """
    Middleware para verificar se o usuário está autenticado.
    
    Esta função pode ser usada como dependência em rotas que
    requerem autenticação. Simplesmente retorna o usuário
    autenticado obtido através de get_current_user.
    
    Args:
        current_user: Usuário autenticado atual
        
    Returns:
        User: Objeto do usuário autenticado
    """
    return current_user
