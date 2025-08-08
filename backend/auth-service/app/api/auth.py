from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from core.database import get_db
from core.security import require_auth
from core.config import settings
from schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse, UserUpdate, GoogleAuthRequest
from services.auth_service import auth_service
from schemas.user import LoginResponse
from services.google_oauth_service import google_oauth_service
from crud.user import get_users, get_user_by_id, update_user, delete_user

router = APIRouter()

@router.post("/register", response_model=UserResponse, summary="Registrar usuário")
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Registra um novo usuário no sistema.
    
    - **nome_completo**: Nome completo do usuário
    - **cpf**: CPF do usuário (será validado)
    - **data_nascimento**: Data de nascimento (YYYY-MM-DD)
    - **email**: Email único do usuário
    - **senha**: Senha que será hasheada antes de salvar
    """
    try:
        user = auth_service.register_user(db, user_data)
        return UserResponse(
            id=user.id,
            nome_completo=user.nome_completo,
            cpf=user.cpf,
            data_nascimento=user.data_nascimento,
            email=user.email,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
def login(
    request: UserLogin, # Expect email/password in the request body
    response: Response, # Inject Response object to set cookies
    db: Session = Depends(get_db) # Inject database session
):
    # 1. Authenticate the user using your existing service logic
    user = auth_service.authenticate_user(db, request)
    if not user:
        # Raise 401 if authentication fails
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
        )

    # 2. Create the JWT access token using your existing service logic
    access_token = auth_service.create_access_token(data={"sub": user.email})

    # 3. ✅ Set the JWT in a secure HTTP-only cookie
    response.set_cookie(
        key="access_token",           # Cookie name
        value=access_token,           # The JWT value
        httponly=True,                # Prevents XSS attacks (inaccessible to JS)
        secure=False,                 # Set to True in production (requires HTTPS)
        samesite="Lax",               # Helps mitigate CSRF (Lax is a good default)
        max_age=3600,                 # Cookie expiry in seconds (match token expiry)
        path="/"                      # Cookie is sent to all paths on the domain
    )

    # 4. ✅ Return a simple success message (token is in the cookie, not the body)
    return LoginResponse(
        message="Login realizado com sucesso",
        email=user.email # Include non-sensitive info if needed
    )

@router.get("/profile", response_model=UserResponse, summary="Obter perfil")
def get_user_profile(current_user = Depends(require_auth)):
    """
    Retorna o perfil do usuário autenticado.
    
    Endpoint protegido que requer token JWT válido no cabeçalho Authorization.
    Retorna os dados completos do usuário autenticado, incluindo timestamps
    de criação e atualização.
    
    Args:
        current_user: Usuário autenticado atual (injetado pela dependência)
        
    Returns:
        UserResponse: Dados completos do perfil do usuário
        
    Raises:
        HTTPException: 401 se o token for inválido ou expirado
        
    Example:
        ```
        GET /api/v1/auth/profile
        Authorization: Bearer <seu_token_jwt>
        ```
    """
    return UserResponse(
        id=current_user.id,
        nome_completo=current_user.nome_completo,
        data_nascimento=current_user.data_nascimento,
        email=current_user.email,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )

@router.put("/profile", response_model=UserResponse, summary="Atualizar perfil")
def update_user_profile(
    user_update: UserUpdate,
    current_user = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Atualiza o perfil do usuário autenticado.
    
    Permite atualização parcial dos dados do usuário. Apenas os campos
    fornecidos no corpo da requisição serão atualizados. Requer token
    JWT válido no cabeçalho Authorization.
    
    Args:
        user_update: Dados a serem atualizados (todos os campos são opcionais)
        current_user: Usuário autenticado atual (injetado pela dependência)
        db: Sessão do banco de dados
        
    Returns:
        UserResponse: Dados atualizados do usuário
        
    Raises:
        HTTPException: 401 se o token for inválido ou expirado
        HTTPException: 404 se o usuário não for encontrado
        
    Example:
        ```
        PUT /api/v1/auth/profile
        Authorization: Bearer <seu_token_jwt>
        {
            "nome_completo": "Novo Nome Completo"
        }
        ```
    """
    updated_user = update_user(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return UserResponse(
        id=updated_user.id,
        nome_completo=updated_user.nome_completo,
        data_nascimento=updated_user.data_nascimento,
        email=updated_user.email,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at
    )

@router.get("/users", response_model=List[UserResponse], summary="Listar usuários")
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)  # Protegido por autenticação
):
    """
    Lista usuários cadastrados com suporte a paginação.
    
    Endpoint protegido que requer autenticação. Permite listar usuários
    com controle de paginação através dos parâmetros skip e limit.
    
    Args:
        skip: Número de registros a pular (padrão: 0, mínimo: 0)
        limit: Número máximo de registros a retornar (padrão: 100, máximo: 100)
        db: Sessão do banco de dados
        current_user: Usuário autenticado atual (injetado pela dependência)
        
    Returns:
        List[UserResponse]: Lista de usuários encontrados
        
    Raises:
        HTTPException: 401 se o token for inválido ou expirado
        
    Example:
        ```
        GET /api/v1/auth/users?skip=0&limit=10
        Authorization: Bearer <seu_token_jwt>
        ```
    """
    users = get_users(db, skip=skip, limit=limit)
    return [
        UserResponse(
            id=user.id,
            nome_completo=user.nome_completo,
            data_nascimento=user.data_nascimento,
            email=user.email,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        for user in users
    ]

@router.get("/users/{user_id}", response_model=UserResponse, summary="Obter usuário por ID")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)  # Protegido por autenticação
):
    """
    Obtém dados de um usuário específico pelo seu ID.
    
    Endpoint protegido que requer autenticação. Busca e retorna
    os dados completos de um usuário específico.
    
    Args:
        user_id: ID único do usuário a ser buscado
        db: Sessão do banco de dados
        current_user: Usuário autenticado atual (injetado pela dependência)
        
    Returns:
        UserResponse: Dados completos do usuário encontrado
        
    Raises:
        HTTPException: 401 se o token for inválido ou expirado
        HTTPException: 404 se o usuário não for encontrado
        
    Example:
        ```
        GET /api/v1/auth/users/123
        Authorization: Bearer <seu_token_jwt>
        ```
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return UserResponse(
        id=user.id,
        nome_completo=user.nome_completo,
        data_nascimento=user.data_nascimento,
        email=user.email,
        created_at=user.created_at,
        updated_at=user.updated_at
    )

@router.delete("/users/{user_id}", summary="Deletar usuário")
def delete_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)  # Protegido por autenticação
):
    """
    Remove um usuário do sistema pelo seu ID.
    
    Endpoint protegido que requer autenticação. Remove permanentemente
    um usuário do banco de dados. Esta operação não pode ser desfeita.
    
    Args:
        user_id: ID único do usuário a ser removido
        db: Sessão do banco de dados
        current_user: Usuário autenticado atual (injetado pela dependência)
        
    Returns:
        dict: Mensagem de confirmação da exclusão
        
    Raises:
        HTTPException: 401 se o token for inválido ou expirado
        HTTPException: 404 se o usuário não for encontrado
        
    Example:
        ```
        DELETE /api/v1/auth/users/123
        Authorization: Bearer <seu_token_jwt>
        ```
    """
    if not delete_user(db, user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return {"message": "Usuário deletado com sucesso"}

@router.get("/google/auth-url", summary="Obter URL de autenticação do Google")
def get_google_auth_url():
    """
    Retorna a URL para iniciar o processo de autenticação com Google OAuth.
    
    Esta URL deve ser usada para redirecionar o usuário para a página de login do Google.
    Após o login, o usuário será redirecionado de volta com um código de autorização.
    
    Returns:
        dict: Contém a URL de autenticação do Google
        
    Example:
        ```
        GET /api/v1/auth/google/auth-url
        ```
        
        Response:
        ```json
        {
            "auth_url": "https://accounts.google.com/oauth/authorize?..."
        }
        ```
    """
    base_url = "https://accounts.google.com/o/oauth2/auth"
    params = {
        "response_type": "code",
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    
    # Constrói a URL com os parâmetros
    query_string = "&".join([f"{key}={value}" for key, value in params.items()])
    auth_url = f"{base_url}?{query_string}"
    
    return {"auth_url": auth_url}

@router.post("/google/callback", response_model=TokenResponse, summary="Callback do Google OAuth")
def google_oauth_callback(auth_request: GoogleAuthRequest, db: Session = Depends(get_db)):
    """
    Processa o callback do Google OAuth e autentica o usuário.
    
    Este endpoint é chamado após o usuário ser redirecionado do Google
    com um código de autorização. O código é trocado por um token de acesso
    e as informações do usuário são obtidas para criar/autenticar o usuário.
    
    Args:
        auth_request: Dados do callback contendo código e redirect_uri
        db: Sessão do banco de dados
        
    Returns:
        TokenResponse: Token JWT e dados do usuário autenticado
        
    Raises:
        HTTPException: 400 se houver erro na autenticação com Google
        HTTPException: 401 se a autenticação falhar
        
    Example:
        ```
        POST /api/v1/auth/google/callback
        {
            "code": "4/0AX4XfWi...",
            "redirect_uri": "http://localhost:8001/api/v1/auth/google/callback"
        }
        ```
    """
    try:
        # Autentica com Google OAuth
        user = google_oauth_service.authenticate_with_google(
            db, auth_request.code, auth_request.redirect_uri
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Falha na autenticação com Google",
            )
        
        # Cria token JWT para o usuário
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_service.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse(
                id=user.id,
                nome_completo=user.nome_completo,
                cpf=user.cpf,
                data_nascimento=user.data_nascimento,
                email=user.email,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro na autenticação com Google: {str(e)}"
        )
