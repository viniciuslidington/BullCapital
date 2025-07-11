from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.database import get_db
from models.schemas import UserCreateRequest, UserLoginRequest, UserResponse
from services.auth_service import (
    criar_usuario,
    autenticar_usuario,
    criar_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    listar_usuarios,
)
from middlewares.auth_middleware import require_auth
from datetime import timedelta

router = APIRouter()


@router.post("/registrar", response_model=UserResponse)
def registrar_usuario(user_data: UserCreateRequest, db: Session = Depends(get_db)):
    try:
        usuario = criar_usuario(db, user_data)
        return UserResponse(
            id=usuario.id,
            nome_completo=usuario.nome_completo,
            data_nascimento=usuario.data_nascimento,
            email=usuario.email,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login")
def login(login_data: UserLoginRequest, db: Session = Depends(get_db)):
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
        "user": UserResponse(
            id=usuario.id,
            nome_completo=usuario.nome_completo,
            data_nascimento=usuario.data_nascimento,
            email=usuario.email,
        ),
    }


@router.get("/perfil", response_model=UserResponse)
def obter_perfil(current_user=Depends(require_auth)):
    """Endpoint protegido que requer autenticação"""
    return UserResponse(
        id=current_user.id,
        nome_completo=current_user.nome_completo,
        data_nascimento=current_user.data_nascimento,
        email=current_user.email,
    )


@router.get("/usuarios")
def listar_usuarios_endpoint(db: Session = Depends(get_db)):
    """Endpoint para debug - listar todos os usuários cadastrados"""
    usuarios = listar_usuarios(db)
    return {
        "usuarios": [
            {
                "id": user.id,
                "nome_completo": user.nome_completo,
                "email": user.email,
                "data_nascimento": user.data_nascimento.isoformat(),
            }
            for user in usuarios
        ],
        "total": len(usuarios),
    }
