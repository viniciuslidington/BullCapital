from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.database import get_db
from models.schemas import UserCreateRequest, UserLoginRequest, UserResponse
from services.auth_service import criar_usuario, autenticar_usuario, criar_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, listar_usuarios
from middlewares.auth_middleware import require_auth
from datetime import timedelta

router = APIRouter()

@router.post("/register", response_model=UserResponse, summary="Registrar usuário")
def register_user(user_data: UserCreateRequest, db: Session = Depends(get_db)):
    """
    Registra um novo usuário no sistema.
    
    - **nome_completo**: Nome completo do usuário
    - **data_nascimento**: Data de nascimento (YYYY-MM-DD)
    - **email**: Email único do usuário
    - **senha**: Senha que será hasheada antes de salvar
    """
    try:
        usuario = criar_usuario(db, user_data)
        return UserResponse(
            id=usuario.id,
            nome_completo=usuario.nome_completo,
            data_nascimento=usuario.data_nascimento,
            email=usuario.email
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", summary="Fazer login")
def login_user(login_data: UserLoginRequest, db: Session = Depends(get_db)):
    """
    Autentica um usuário e retorna um token JWT.
    
    - **email**: Email do usuário
    - **senha**: Senha do usuário
    
    Retorna um token JWT válido por 30 minutos.
    """
    usuario = autenticar_usuario(db, login_data)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = criar_access_token(
        data={"sub": usuario.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # em segundos
        "user": UserResponse(
            id=usuario.id,
            nome_completo=usuario.nome_completo,
            data_nascimento=usuario.data_nascimento,
            email=usuario.email
        )
    }

@router.get("/profile", response_model=UserResponse, summary="Obter perfil")
def get_user_profile(current_user = Depends(require_auth)):
    """
    Endpoint protegido que retorna o perfil do usuário autenticado.
    
    Requer token JWT válido no header Authorization: Bearer <token>
    """
    return UserResponse(
        id=current_user.id,
        nome_completo=current_user.nome_completo,
        data_nascimento=current_user.data_nascimento,
        email=current_user.email
    )

@router.get("/users", summary="Listar usuários (Debug)")
def list_users(db: Session = Depends(get_db)):
    """
    Endpoint para debug - lista todos os usuários cadastrados.
    
    **Nota**: Em produção, este endpoint deve ser protegido ou removido.
    """
    usuarios = listar_usuarios(db)
    return {
        "users": [
            {
                "id": user.id,
                "nome_completo": user.nome_completo,
                "email": user.email,
                "data_nascimento": user.data_nascimento.isoformat()
            } 
            for user in usuarios
        ],
        "total": len(usuarios)
    }
