
from fastapi import APIRouter, HTTPException, status, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse
import httpx
from typing import List
from uuid import UUID
from models.auth_models import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
    LoginSuccessResponse,
)

router = APIRouter()


AUTH_SERVICE_URL = "http://auth-service:8003/api/v1/auth"

def _forward_cookies(request: Request) -> dict:
    """Extrai cookies da requisição do cliente para repassar ao auth-service."""
    return {k: v for k, v in request.cookies.items()}

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
    response_model=LoginSuccessResponse,
    status_code=status.HTTP_200_OK
)
async def login_user(user: UserLogin, request: Request):
    """Proxy de login: repassa credenciais e devolve estrutura completa (message, user, cookie, session).
    O cookie HTTP-only será setado pelo browser a partir dos headers do auth-service; não interceptamos aqui."""
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            user_json = jsonable_encoder(user)
            response = await client.post(f"{AUTH_SERVICE_URL}/login", json=user_json)
            response.raise_for_status()
            data = response.json()
            return LoginSuccessResponse(**data)
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)



@router.put(
    "/profile",
    response_model=UserResponse,
    summary="Atualizar perfil do usuário",
    description="Atualiza as informações do perfil do usuário autenticado."
)
async def update_profile(user: UserUpdate, request: Request):
    async with httpx.AsyncClient() as client:
        try:
            user_json = jsonable_encoder(user, exclude_unset=True)
            response = await client.put(
                f"{AUTH_SERVICE_URL}/profile",
                json=user_json,
                cookies=_forward_cookies(request),
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
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/profile",
                cookies=_forward_cookies(request),
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
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/users",
                cookies=_forward_cookies(request),
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
async def get_user(user_id: UUID, request: Request):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/users/{user_id}",
                cookies=_forward_cookies(request),
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
async def delete_user_endpoint(user_id: UUID, request: Request):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(
                f"{AUTH_SERVICE_URL}/users/{user_id}",
                cookies=_forward_cookies(request),
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

@router.post(
    "/logout",
    summary="Fazer logout",
)
async def logout(request: Request):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/logout",
                cookies=_forward_cookies(request),
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

@router.get(
    "/cookie-status",
    summary="Verificar status do cookie de autenticação",
)
async def cookie_status(request: Request):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/cookie-status",
                cookies=_forward_cookies(request),
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

@router.get("/google/auth-url", summary="Obter URL de autenticação Google")
async def google_auth_url():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{AUTH_SERVICE_URL}/google/auth-url")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

@router.get("/google/callback", summary="Callback Google OAuth")
async def google_callback(request: Request, code: str, state: str | None = None):
    async with httpx.AsyncClient(follow_redirects=False) as client:
        try:
            params = {"code": code}
            if state:
                params["state"] = state
            response = await client.get(
                f"{AUTH_SERVICE_URL}/google/callback",
                params=params,
                cookies=_forward_cookies(request),
            )
            # Se auth-service retornar redirect
            if response.is_redirect:
                location = response.headers.get("Location", "/")
                return RedirectResponse(url=location, status_code=response.status_code)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        
