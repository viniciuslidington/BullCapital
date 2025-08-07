"""
Script de migração para adicionar suporte ao Google OAuth.

Este script adiciona as colunas necessárias para suportar autenticação
via Google OAuth no modelo de usuário existente.

Execute este script após atualizar o modelo User para garantir que
o banco de dados esteja em sincronia com o novo schema.
"""

import sys
import os

# Adicionar o diretório pai (app) ao Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from core.database import engine

def run_migration():
    """
    Executa a migração para criar/atualizar a tabela users com suporte ao Google OAuth.
    
    Cria a tabela users se não existir, ou adiciona as colunas necessárias:
    - google_id: ID único do usuário no Google
    - is_google_user: Indica se o usuário foi criado via Google OAuth
    - profile_picture: URL da foto do perfil do Google
    
    Também torna opcionais as colunas cpf, data_nascimento e senha.
    """
    
    # SQL para criar a tabela users se não existir
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        nome_completo VARCHAR(255) NOT NULL,
        cpf VARCHAR(14),
        data_nascimento DATE,
        email VARCHAR(255) UNIQUE NOT NULL,
        senha VARCHAR(255),
        google_id VARCHAR UNIQUE,
        is_google_user BOOLEAN DEFAULT FALSE NOT NULL,
        profile_picture VARCHAR,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # SQL para adicionar colunas se a tabela já existir (migração)
    migration_commands = [
        # Adicionar google_id se não existir
        """
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS google_id VARCHAR UNIQUE
        """,
        
        # Adicionar is_google_user se não existir
        """
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS is_google_user BOOLEAN DEFAULT FALSE NOT NULL
        """,
        
        # Adicionar profile_picture se não existir
        """
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS profile_picture VARCHAR
        """,
        
        # Criar índices
        "CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id)",
        "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
        
        # Tornar colunas opcionais (usando comandos condicionais mais simples)
        """
        ALTER TABLE users 
        ALTER COLUMN cpf DROP NOT NULL
        """,
        
        """
        ALTER TABLE users 
        ALTER COLUMN data_nascimento DROP NOT NULL
        """,
        
        """
        ALTER TABLE users 
        ALTER COLUMN senha DROP NOT NULL
        """
    ]
    
    try:
        with engine.connect() as connection:
            print("🔄 Criando tabela users se não existir...")
            connection.execute(text(create_table_sql))
            connection.commit()
            print("✅ Tabela users verificada/criada!")
            
            print("🔄 Executando migração para Google OAuth...")
            # Executa cada comando separadamente
            for i, command in enumerate(migration_commands, 1):
                try:
                    print(f"   {i}/{len(migration_commands)} - Executando comando...")
                    connection.execute(text(command.strip()))
                    connection.commit()
                except Exception as cmd_error:
                    # Alguns comandos podem falhar se a coluna já não tiver NOT NULL
                    # ou se a coluna não existir, mas isso é esperado
                    print(f"   ⚠️  Comando {i} falhou (pode ser normal): {cmd_error}")
                    continue
            connection.commit()
            print("✅ Migração concluída com sucesso!")
            
            # Verificar estrutura da tabela
            result = connection.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                ORDER BY ordinal_position;
            """))
            
            print("\n📋 Estrutura da tabela users:")
            for row in result:
                nullable = "NULL" if row[2] == "YES" else "NOT NULL"
                print(f"   - {row[0]}: {row[1]} ({nullable})")
                
        print("✅ Migração executada com sucesso!")
        print("✅ Suporte ao Google OAuth adicionado ao banco de dados")
        
    except Exception as e:
        print(f"❌ Erro ao executar migração: {e}")
        raise

if __name__ == "__main__":
    run_migration()
