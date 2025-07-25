from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from core.database import get_db
from core.security import require_auth
from core.config import settings
from schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse, UserUpdate
from services.auth_service import auth_service
from crud.user import get_users, get_user_by_id, update_user, delete_user

router = APIRouter()


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = auth_service.register_user(db, user)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User registration failed")
    return {"access_token": db_user.access_token, "token_type": "bearer"}

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK
)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = auth_service.login_user(db, user)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"access_token": db_user.access_token, "token_type": "bearer"}


@router.put("/profile"
            , response_model=UserResponse,
    summary="Atualizar perfil do usuário",
    description="Atualiza as informações do perfil do usuário autenticado."
)
def update_profile(user: UserUpdate, db: Session = Depends(get_db), current_user: UserResponse = Depends(require_auth)):
    db_user = update_user(db, current_user.id, user)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User update failed")
    return db_user

@router.get("/profile",
            response_model=UserResponse,
    summary="Obter perfil do usuário",
    description="Retorna as informações do perfil do usuário autenticado."
)
def get_profile(db: Session = Depends(get_db), current_user: UserResponse = Depends(require_auth)):
    db_user = get_user_by_id(db, current_user.id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

@router.get(
    "/users",
    response_model=List[UserResponse],
    summary="Obter lista de usuários",
    description="Retorna uma lista de todos os usuários."
)
def get_users_list(db: Session = Depends(get_db), current_user: UserResponse = Depends(require_auth)):
    db_users = get_users(db)
    return db_users

@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Obter usuário por ID",
    description="Retorna as informações de um usuário específico pelo ID."
)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: UserResponse = Depends(require_auth)):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

@router.delete(
    "/users/{user_id}",
    summary="Deletar usuário",
    description="Deleta um usuário específico pelo ID."
)
def delete_user_endpoint(user_id: int, db: Session = Depends(get_db), current_user: UserResponse = Depends(require_auth)):
    db_user = delete_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"detail": "User deleted successfully"}
