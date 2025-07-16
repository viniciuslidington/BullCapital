"""
Módulo API - Rotas e endpoints da aplicação.

Este módulo contém todas as definições de rotas e endpoints da API REST,
organizados por funcionalidade:

- Rotas de autenticação (registro, login, perfil)
- Rotas de gerenciamento de usuários
- Middleware de segurança e validação

Exporta:
- auth_router: Router com todas as rotas de autenticação
"""

from .auth import router as auth_router

__all__ = ["auth_router"]
