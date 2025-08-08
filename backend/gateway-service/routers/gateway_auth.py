
from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.encoders import jsonable_encoder
import httpx
from typing import List
from models.auth_models import UserCreate, UserLogin, UserResponse, TokenResponse, UserUpdate

router = APIRouter()


AUTH_SERVICE_URL = "http://auth-service:8003/api/v1/auth"

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def register_user(user: UserCreate):
    async with httpx.AsyncClient() as client:
        try:
            user_json = jsonable_encoder(user)
            response = await client.post(f"{AUTH_SERVICE_URL}/register", json=user_json)
            response.raise_for_status()
            return UserResponse(**response.json())
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK
)
async def login_user(user: UserLogin):
    async with httpx.AsyncClient() as client:
        try:
            user_json = jsonable_encoder(user)
            response = await client.post(f"{AUTH_SERVICE_URL}/login", json=user_json)
            response.raise_for_status()
            return TokenResponse(**response.json())
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)



@router.put(
    "/profile",
    response_model=UserResponse,
    summary="Atualizar perfil do usuário",
    description="Atualiza as informações do perfil do usuário autenticado."
)
async def update_profile(user: UserUpdate, request: Request):
    token = request.headers.get("Authorization")
    async with httpx.AsyncClient() as client:
        try:
            user_json = jsonable_encoder(user)
            response = await client.put(
                f"{AUTH_SERVICE_URL}/profile",
                json=user_json,
                headers={"Authorization": token} if token else {}
            )
            response.raise_for_status()
            return UserResponse(**response.json())
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)


@router.get(
    "/profile",
    response_model=UserResponse,
    summary="Obter perfil do usuário",
    description="Retorna as informações do perfil do usuário autenticado."
)
async def get_profile(request: Request):
    token = request.headers.get("Authorization")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/profile",
                headers={"Authorization": token} if token else {}
            )
            response.raise_for_status()
            return UserResponse(**response.json())
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)


@router.get(
    "/users",
    response_model=List[UserResponse],
    summary="Obter lista de usuários",
    description="Retorna uma lista de todos os usuários."
)
async def get_users_list(request: Request):
    token = request.headers.get("Authorization")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/users",
                headers={"Authorization": token} if token else {}
            )
            response.raise_for_status()
            return [UserResponse(**user) for user in response.json()]
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Obter usuário por ID",
    description="Retorna as informações de um usuário específico pelo ID."
)
async def get_user(user_id: int, request: Request):
    token = request.headers.get("Authorization")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/users/{user_id}",
                headers={"Authorization": token} if token else {}
            )
            response.raise_for_status()
            return UserResponse(**response.json())
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)


@router.delete(
    "/users/{user_id}",
    summary="Deletar usuário",
    description="Deleta um usuário específico pelo ID."
)
async def delete_user_endpoint(user_id: int, request: Request):
    token = request.headers.get("Authorization")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(
                f"{AUTH_SERVICE_URL}/users/{user_id}",
                headers={"Authorization": token} if token else {}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
