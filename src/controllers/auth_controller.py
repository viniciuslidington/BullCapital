from fastapi import APIRouter, Depends, HTTPException, status
from models.schemas import UserCreateRequest, UserLoginRequest, UserResponse
from services.auth_service_memory import criar_usuario, autenticar_usuario, criar_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, listar_usuarios
from middlewares.auth_middleware_memory import require_auth
from datetime import timedelta

router = APIRouter()

@router.post("/registrar", response_model=UserResponse)
def registrar_usuario(user_data: UserCreateRequest):
    try:
        usuario = criar_usuario(user_data)
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

@router.post("/login")
def login(login_data: UserLoginRequest):
    usuario = autenticar_usuario(login_data)
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
        "user": UserResponse(
            id=usuario.id,
            nome_completo=usuario.nome_completo,
            data_nascimento=usuario.data_nascimento,
            email=usuario.email
        )
    }

@router.get("/perfil", response_model=UserResponse)
def obter_perfil(current_user = Depends(require_auth)):
    """Endpoint protegido que requer autenticação"""
    return UserResponse(
        id=current_user.id,
        nome_completo=current_user.nome_completo,
        data_nascimento=current_user.data_nascimento,
        email=current_user.email
    )

@router.get("/usuarios")
def listar_usuarios_endpoint():
    """Endpoint para debug - listar todos os usuários cadastrados"""
    return {
        "usuarios": listar_usuarios(),
        "total": len(listar_usuarios())
    }
