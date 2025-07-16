from sqlalchemy.orm import Session
from typing import Optional, List
from core.models import User
from schemas.user import UserCreate, UserUpdate

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Busca um usuário específico pelo seu ID.
    
    Args:
        db: Sessão do banco de dados
        user_id: ID único do usuário
        
    Returns:
        User ou None: Objeto do usuário se encontrado, None caso contrário
    """
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_cpf(db: Session, cpf: str) -> Optional[User]:
    """
    Busca um usuário específico pelo seu CPF.
    
    Args:
        db: Sessão do banco de dados
        cpf: CPF do usuário (apenas números)
        
    Returns:
        User ou None: Objeto do usuário se encontrado, None caso contrário
    """
    return db.query(User).filter(User.cpf == cpf).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Busca um usuário específico pelo seu email.
    
    Args:
        db: Sessão do banco de dados
        email: Email do usuário
        
    Returns:
        User ou None: Objeto do usuário se encontrado, None caso contrário
    """
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """
    Lista usuários com paginação.
    
    Args:
        db: Sessão do banco de dados
        skip: Número de registros a pular (para paginação)
        limit: Número máximo de registros a retornar
        
    Returns:
        List[User]: Lista de usuários encontrados
    """
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate, hashed_password: str) -> User:
    """
    Cria um novo usuário no banco de dados.
    
    Args:
        db: Sessão do banco de dados
        user: Dados do usuário a ser criado
        hashed_password: Senha já hasheada
        
    Returns:
        User: Objeto do usuário criado com ID atribuído
        
    Raises:
        SQLAlchemyError: Se houver erro na operação do banco de dados
    """
    db_user = User(
        nome_completo=user.nome_completo,
        cpf=user.cpf,
        data_nascimento=user.data_nascimento,
        email=user.email,
        senha=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """
    Atualiza dados de um usuário existente.
    
    Realiza atualização parcial dos dados do usuário, modificando
    apenas os campos fornecidos no objeto user_update.
    
    Args:
        db: Sessão do banco de dados
        user_id: ID do usuário a ser atualizado
        user_update: Dados a serem atualizados (campos opcionais)
        
    Returns:
        User ou None: Objeto do usuário atualizado se encontrado, None caso contrário
        
    Raises:
        SQLAlchemyError: Se houver erro na operação do banco de dados
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    """
    Remove um usuário do banco de dados.
    
    Args:
        db: Sessão do banco de dados
        user_id: ID do usuário a ser removido
        
    Returns:
        bool: True se o usuário foi removido com sucesso, False se não encontrado
        
    Raises:
        SQLAlchemyError: Se houver erro na operação do banco de dados
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True
