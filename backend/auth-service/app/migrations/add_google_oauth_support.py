"""
Script de migração para adicionar suporte ao Google OAuth.

Este script adiciona as colunas necessárias para suportar autenticação
via Google OAuth no modelo de usuário existente.

Execute este script após atualizar o modelo User para garantir que
o banco de dados esteja em sincronia com o novo schema.
"""

from sqlalchemy import text
from core.database import engine

def run_migration():
    """
    Executa a migração para adicionar suporte ao Google OAuth.
    
    Adiciona as seguintes colunas à tabela users:
    - google_id: ID único do usuário no Google
    - is_google_user: Indica se o usuário foi criado via Google OAuth
    - profile_picture: URL da foto do perfil do Google
    
    Também torna opcionais as colunas cpf, data_nascimento e senha.
    """
    
    migration_sql = """
    -- Adicionar novas colunas para Google OAuth
    ALTER TABLE users 
    ADD COLUMN IF NOT EXISTS google_id VARCHAR UNIQUE,
    ADD COLUMN IF NOT EXISTS is_google_user BOOLEAN DEFAULT FALSE NOT NULL,
    ADD COLUMN IF NOT EXISTS profile_picture VARCHAR;
    
    -- Criar índice para google_id
    CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);
    
    -- Tornar colunas opcionais (remover NOT NULL)
    ALTER TABLE users 
    ALTER COLUMN cpf DROP NOT NULL,
    ALTER COLUMN data_nascimento DROP NOT NULL,
    ALTER COLUMN senha DROP NOT NULL;
    """
    
    try:
        with engine.connect() as connection:
            # Executa cada statement separadamente
            statements = migration_sql.strip().split(';')
            for statement in statements:
                if statement.strip():
                    connection.execute(text(statement.strip()))
            connection.commit()
            
        print("✅ Migração executada com sucesso!")
        print("✅ Suporte ao Google OAuth adicionado ao banco de dados")
        
    except Exception as e:
        print(f"❌ Erro ao executar migração: {e}")
        raise

if __name__ == "__main__":
    run_migration()
