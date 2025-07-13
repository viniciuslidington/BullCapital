"""
Módulo Services - Lógica de negócio da aplicação.

Este módulo contém todos os serviços que implementam a lógica de negócio
da aplicação, servindo como camada intermediária entre as rotas da API
e as operações CRUD:

- Serviços de autenticação e segurança
- Validações de regras de negócio
- Processamento de dados complexos
- Integração entre diferentes componentes

Exporta:
- AuthService: Classe com métodos estáticos para autenticação
- auth_service: Instância global do serviço de autenticação
"""

from .auth_service import auth_service, AuthService

__all__ = ["auth_service", "AuthService"]
