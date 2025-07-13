"""
Módulo CRUD - Operações de banco de dados.

Este módulo contém todas as operações CRUD (Create, Read, Update, Delete)
para as entidades do sistema. Implementa a camada de acesso a dados,
separando a lógica de negócio das operações de banco de dados.

Funcionalidades:
- Operações de busca (por ID, email, listagem paginada)
- Criação de novos registros
- Atualização de dados existentes
- Remoção de registros

Exporta todas as funções CRUD para uso nos serviços e rotas.
"""

from .user import (
    get_user_by_id,
    get_user_by_email,
    get_users,
    create_user,
    update_user,
    delete_user
)

__all__ = [
    "get_user_by_id",
    "get_user_by_email", 
    "get_users",
    "create_user",
    "update_user",
    "delete_user"
]
