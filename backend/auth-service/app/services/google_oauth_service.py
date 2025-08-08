"""
Serviço para autenticação via Google OAuth 2.0.

Este módulo implementa toda a lógica necessária para autenticação
com Google OAuth, incluindo troca de códigos por tokens, validação
de tokens e obtenção de informações do usuário.
"""

import requests
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from core.config import settings
from core.models import User
from schemas.user import GoogleUserInfo


class GoogleOAuthService:
    """
    Serviço para autenticação via Google OAuth 2.0.
    
    Fornece métodos para trocar códigos de autorização por tokens,
    validar tokens JWT do Google e obter informações do usuário.
    """

    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.token_url = "https://oauth2.googleapis.com/token"
        self.userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"

    def exchange_code_for_token(self, code: str, redirect_uri: str) -> Optional[Dict[str, Any]]:
        """
        Troca o código de autorização por um token de acesso.
        
        Args:
            code: Código de autorização retornado pelo Google
            redirect_uri: URI de redirecionamento usada na autenticação
            
        Returns:
            Dict contendo access_token e id_token, ou None se houver erro
        """
        try:
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
            }
            
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()
            
            return response.json()
        except requests.RequestException as e:
            print(f"Erro ao trocar código por token: {e}")
            return None

    def get_user_info(self, access_token: str) -> Optional[GoogleUserInfo]:
        """
        Obtém informações do usuário usando o token de acesso.
        
        Args:
            access_token: Token de acesso do Google
            
        Returns:
            GoogleUserInfo com dados do usuário, ou None se houver erro
        """
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(self.userinfo_url, headers=headers)
            response.raise_for_status()
            
            user_data = response.json()
            return GoogleUserInfo(
                id=user_data["id"],
                email=user_data["email"],
                name=user_data["name"],
                picture=user_data.get("picture"),
                verified_email=user_data.get("verified_email", False)
            )
        except requests.RequestException as e:
            print(f"Erro ao obter informações do usuário: {e}")
            return None

    def verify_id_token(self, id_token_str: str) -> Optional[Dict[str, Any]]:
        """
        Verifica e decodifica o ID token JWT do Google.
        
        Args:
            id_token_str: ID token JWT retornado pelo Google
            
        Returns:
            Dict com claims do token, ou None se inválido
        """
        try:
            request = google_requests.Request()
            id_info = id_token.verify_oauth2_token(
                id_token_str, request, self.client_id
            )
            
            if id_info["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
                raise ValueError("Token inválido")
                
            return id_info
        except ValueError as e:
            print(f"Erro ao verificar ID token: {e}")
            return None

    def create_or_get_user(self, db: Session, google_user: GoogleUserInfo) -> Optional[User]:
        """
        Cria um novo usuário ou retorna um existente baseado no Google ID.
        
        Args:
            db: Sessão do banco de dados
            google_user: Informações do usuário do Google
            
        Returns:
            Usuário criado ou encontrado, ou None se houver erro
        """
        try:
            # Verifica se usuário já existe pelo Google ID
            existing_user = db.query(User).filter(User.google_id == google_user.id).first()
            if existing_user:
                return existing_user
            
            # Verifica se usuário já existe pelo email
            existing_user_by_email = db.query(User).filter(User.email == google_user.email).first()
            if existing_user_by_email:
                # Atualiza usuário existente com dados do Google
                existing_user_by_email.google_id = google_user.id
                existing_user_by_email.is_google_user = True
                existing_user_by_email.profile_picture = google_user.picture
                db.commit()
                db.refresh(existing_user_by_email)
                return existing_user_by_email
            
            # Cria novo usuário
            new_user = User(
                nome_completo=google_user.name,
                email=google_user.email,
                google_id=google_user.id,
                is_google_user=True,
                profile_picture=google_user.picture,
                senha=None,  # Usuários do Google não precisam de senha
                cpf=None,    # CPF será solicitado posteriormente se necessário
                data_nascimento=None  # Data nascimento será solicitada posteriormente se necessário
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            return new_user
        except Exception as e:
            print(f"Erro ao criar/obter usuário: {e}")
            db.rollback()
            return None

    def authenticate_with_google(self, db: Session, code: str, redirect_uri: str) -> Optional[User]:
        """
        Processo completo de autenticação com Google OAuth.
        
        Args:
            db: Sessão do banco de dados
            code: Código de autorização do Google
            redirect_uri: URI de redirecionamento
            
        Returns:
            Usuário autenticado, ou None se houver erro
        """
        # Troca código por tokens
        token_data = self.exchange_code_for_token(code, redirect_uri)
        if not token_data:
            return None
        
        # Obtém informações do usuário
        user_info = self.get_user_info(token_data["access_token"])
        if not user_info:
            return None
        
        # Verifica se o email foi verificado pelo Google
        if not user_info.verified_email:
            print("Email não verificado pelo Google")
            return None
        
        # Cria ou obtém usuário
        user = self.create_or_get_user(db, user_info)
        return user


# Instância global do serviço
google_oauth_service = GoogleOAuthService()
