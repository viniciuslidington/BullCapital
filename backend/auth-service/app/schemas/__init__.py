"""
Módulo Schemas - Modelos de validação e serialização.

Este módulo contém todos os schemas Pydantic utilizados para validação
de dados de entrada e serialização de respostas da API:

- Schemas para operações com usuários (criação, atualização, resposta)
- Schemas para autenticação (login, token)
- Validação automática de tipos e formatos

Exporta todos os schemas principais para uso nas rotas da API.
"""

from .user import UserCreate, UserLogin, UserResponse, UserUpdate, TokenResponse

__all__ = ["UserCreate", "UserLogin", "UserResponse", "UserUpdate", "TokenResponse"]
