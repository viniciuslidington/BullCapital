from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models.database import get_db
from services.auth_service import criar_usuario, autenticar_usuario

router = APIRouter()

@router.post("/register")
async def register(nome_usuario: str, senha: str, db: AsyncSession = Depends(get_db)):
    usuario = await criar_usuario(db, nome_usuario, senha)
    return {"id": usuario.id, "username": usuario.username}

@router.post("/login")
async def login(nome_usuario: str, senha: str, db: AsyncSession = Depends(get_db)):
    usuario = await autenticar_usuario(db, nome_usuario, senha)
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuário ou senha inválidos")
    return {"id": usuario.id, "username": usuario.username}
