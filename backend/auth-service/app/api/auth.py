from fastapi import APIRouter, Depends, HTTPException, status, Query, Response, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from core.database import get_db
from core.security import require_auth
from core.config import settings
from schemas.user import UserCreate, UserLogin, UserResponse, UserUpdate
from services.auth_service import auth_service
from schemas.user import LoginResponse
from services.google_oauth_service import google_oauth_service
from crud.user import get_users, get_user_by_id, update_user, delete_user

router = APIRouter()

def set_auth_cookie(response: Response, access_token: str, auth_method: str = "default"):
    """
    Helper function para definir cookie de autenticação com configurações padronizadas.
    
    Args:
        response: Objeto Response do FastAPI
        access_token: Token JWT para ser armazenado no cookie
        auth_method: Método de autenticação usado (para debugging)
        
    Returns:
        dict: Informações sobre o cookie definido
    """
    cookie_max_age = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=cookie_max_age,  # em segundos
        httponly=True,  # Previne acesso via JavaScript (proteção XSS)
        secure=settings.ENVIRONMENT == "production",  # HTTPS apenas em produção
        samesite="lax",  # Proteção CSRF básica
        domain=settings.COOKIE_DOMAIN if settings.ENVIRONMENT == "production" else None,
        path="/",  # Cookie disponível em toda a aplicação
    )
    
    # Headers para debugging e monitoramento
    response.headers["X-Auth-Status"] = "authenticated"
    response.headers["X-Auth-Method"] = auth_method
    
    # Retorna informações sobre o cookie para incluir na resposta
    return {
        "cookie_name": "access_token",
        "cookie_max_age": cookie_max_age,
        "cookie_expires_in": f"{settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes",
        "cookie_secure": settings.ENVIRONMENT == "production",
        "cookie_httponly": True,
        "cookie_samesite": "lax",
        "cookie_path": "/",
        "auth_method": auth_method
    }

def clear_auth_cookie(response: Response):
    """
    Helper function para remover cookie de autenticação.
    
    Args:
        response: Objeto Response do FastAPI
        
    Returns:
        dict: Informações sobre a remoção do cookie
    """
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        domain="settings.COOKIE_DOMAIN if settings.ENVIRONMENT == "production" else None",
        path="/",  # Mesmo path usado ao criar
    )
    
    # Headers para confirmar logout
    response.headers["X-Auth-Status"] = "logged_out"
    
    return {
        "cookie_name": "access_token",
        "cookie_action": "deleted",
        "cookie_path": "/",
        "auth_status": "logged_out"
    }

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
@router.post("/login", summary="Fazer login")
def login_user(login_data: UserLogin, response: Response, db: Session = Depends(get_db)):
    """
    Autentica um usuário e define um cookie seguro com JWT.
    
    Verifica as credenciais fornecidas (email e senha) e, se válidas,
    define um cookie seguro com o token JWT que será usado para
    acessar endpoints protegidos.
    
    Args:
        login_data: Dados de login contendo email e senha
        response: Objeto Response para definir cookies
        db: Sessão do banco de dados
    
    Returns:
        dict: Mensagem de sucesso e dados do usuário (sem token)
        
    Raises:
        HTTPException: 401 se as credenciais forem inválidas
        
    Example:
        ```
        POST /api/v1/auth/login
        {
            "email": "usuario@exemplo.com",
            "senha": "minhasenha123"
        }
        ```
    """
    user = auth_service.authenticate_user(db, login_data)
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

    # Define cookie seguro usando função helper
    cookie_info = set_auth_cookie(response, access_token, "email_password")
    
    return {
        "message": "Login realizado com sucesso",
        "user": UserResponse(
            id=user.id,
            nome_completo=user.nome_completo,
            data_nascimento=user.data_nascimento,
            email=user.email,
            created_at=user.created_at,
            updated_at=user.updated_at
        ),
        "cookie": cookie_info,
        "session": {
            "expires_in_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        }
    }
\

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
        updated_at=current_user.updated_at,
        profile_picture=current_user.profile_picture,
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

@router.get("/google/callback", summary="Callback do Google OAuth")
def google_oauth_callback(
    response: Response,
    code: str = Query(..., description="Código de autorização do Google"),
    state: str = Query(None, description="Parâmetro de estado (opcional)"),
    db: Session = Depends(get_db)
):
    """
    Processa o callback do Google OAuth e define cookie seguro.
    
    Este endpoint é chamado após o usuário ser redirecionado do Google
    com um código de autorização. O código é trocado por um token de acesso
    e as informações do usuário são obtidas para criar/autenticar o usuário.
    Um cookie seguro é definido com o JWT.
    
    Args:
        code: Código de autorização retornado pelo Google
        state: Parâmetro de estado opcional
        response: Objeto Response para definir cookies
        db: Sessão do banco de dados
        
    Returns:
        dict: Mensagem de sucesso e dados do usuário
        
    Raises:
        HTTPException: 400 se houver erro na autenticação com Google
        HTTPException: 401 se a autenticação falhar
        
    Example:
        ```
        GET /api/v1/auth/google/callback?code=4/0AX4XfWi...&state=xyz
        ```
    """
    try:
        # Autentica com Google OAuth
        user = google_oauth_service.authenticate_with_google(
            db, code, settings.GOOGLE_REDIRECT_URI
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

        # Cria a resposta de redirecionamento para o seu frontend
        redirect_url = f"{settings.FRONTEND_URL}"
        redirect_response = RedirectResponse(
            url=redirect_url, 
            status_code=status.HTTP_302_FOUND
        )

        # Define cookie seguro usando função helper
        set_auth_cookie(response = redirect_response, access_token=access_token, auth_method="google_oauth")

        
        
        return redirect_response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro na autenticação com Google: {str(e)}"
        )

@router.post("/logout", summary="Fazer logout")
def logout(response: Response):
    """
    Remove o cookie de autenticação fazendo logout do usuário.
    
    Remove o cookie 'access_token' de forma segura, efetivamente
    fazendo logout do usuário. Após chamar este endpoint, o usuário
    precisará fazer login novamente para acessar endpoints protegidos.
    
    Args:
        response: Objeto Response para manipular cookies
        
    Returns:
        dict: Mensagem de confirmação do logout
        
    Example:
        ```
        POST /api/v1/auth/logout
        ```
    """
    # Remove cookie usando função helper
    cookie_info = clear_auth_cookie(response)
    
    return {
        "message": "Logout realizado com sucesso",
        "cookie": cookie_info
    }

@router.get("/cookie-status", summary="Verificar status do cookie de autenticação")
def check_cookie_status(request: Request):
    """
    Verifica se existe um cookie de autenticação válido.
    
    Este endpoint permite verificar se o cookie de autenticação está
    presente na requisição, sem validar o token JWT. Útil para
    verificações rápidas no frontend.
    
    Args:
        request: Objeto Request para acessar cookies
        
    Returns:
        dict: Status do cookie e informações de debug
        
    Example:
        ```
        GET /api/v1/auth/cookie-status
        ```
    """
    cookie_value = request.cookies.get("access_token")
    
    return {
        "cookie_present": cookie_value is not None,
        "cookie_name": "access_token",
        "cookie_length": len(cookie_value) if cookie_value else 0,
        "cookie_preview": f"{cookie_value[:20]}..." if cookie_value and len(cookie_value) > 20 else cookie_value,
        "all_cookies": list(request.cookies.keys()),
        "user_agent": request.headers.get("user-agent", "Unknown")
    }
