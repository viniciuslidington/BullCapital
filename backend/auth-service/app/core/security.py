from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from core.database import get_db
from core.models import User
from services.auth_service import auth_service

# Esquema de segurança HTTP Bearer para autenticação via token JWT
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependência para obter o usuário autenticado atual.
    
    Valida o token JWT fornecido no cabeçalho Authorization e retorna
    o usuário correspondente. Levanta exceção HTTP 401 se o token
    for inválido ou expirado.
    
    Args:
        credentials: Credenciais de autorização HTTP Bearer
        db: Sessão do banco de dados
        
    Returns:
        User: Objeto do usuário autenticado
        
    Raises:
        HTTPException: 401 se o token for inválido ou usuário não encontrado
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = auth_service.get_current_user(db, credentials.credentials)
    if user is None:
        raise credentials_exception
    
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
