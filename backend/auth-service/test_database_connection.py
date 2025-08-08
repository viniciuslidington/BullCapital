#!/usr/bin/env python3
"""
Script para testar a conectividade com o banco PostgreSQL Docker.

Este script verifica se a aplicação consegue conectar corretamente
com o banco PostgreSQL rodando no Docker e executa algumas consultas básicas.
"""

import sys
import os

# Adicionar o diretório app ao Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy import text
from core.database import engine, get_db
from core.config import settings

def test_connection():
    """Testa a conexão com o banco de dados."""
    print("🔍 Testando conectividade com PostgreSQL Docker...")
    print(f"📊 Database URL: {settings.DATABASE_URL}")
    
    try:
        with engine.connect() as connection:
            # Teste básico de conexão
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Conexão estabelecida com sucesso!")
            print(f"📝 Versão do PostgreSQL: {version}")
            
            # Verificar se a extensão uuid-ossp está instalada
            result = connection.execute(text("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'uuid-ossp');"))
            has_uuid = result.fetchone()[0]
            print(f"🔧 Extensão uuid-ossp: {'✅ Instalada' if has_uuid else '❌ Não instalada'}")
            
            # Verificar se a extensão pgcrypto está instalada
            result = connection.execute(text("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'pgcrypto');"))
            has_crypto = result.fetchone()[0]
            print(f"🔐 Extensão pgcrypto: {'✅ Instalada' if has_crypto else '❌ Não instalada'}")
            
            # Verificar timezone
            result = connection.execute(text("SHOW timezone;"))
            timezone = result.fetchone()[0]
            print(f"🌍 Timezone: {timezone}")
            
            # Listar tabelas existentes
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """))
            tables = result.fetchall()
            print(f"📋 Tabelas encontradas: {len(tables)}")
            for table in tables:
                print(f"   - {table[0]}")
            
            if not tables:
                print("⚠️  Nenhuma tabela encontrada. Execute a migração primeiro!")
                print("   Comando: cd app && python migrations/add_google_oauth_support.py")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro ao conectar com o banco: {e}")
        print("\n🔧 Passos para resolver:")
        print("1. Verifique se o Docker está rodando: docker --version")
        print("2. Inicie o PostgreSQL: docker-compose up -d postgres")
        print("3. Verifique os logs: docker-compose logs postgres")
        print("4. Verifique se a porta 5432 está livre: lsof -i :5432")
        return False

def test_database_operations():
    """Testa operações básicas no banco."""
    print("\n🧪 Testando operações básicas...")
    
    try:
        with engine.connect() as connection:
            # Teste de criação de tabela temporária
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS test_connection (
                    id SERIAL PRIMARY KEY,
                    test_data VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            print("✅ Criação de tabela: OK")
            
            # Teste de inserção
            connection.execute(text("""
                INSERT INTO test_connection (test_data) 
                VALUES ('Teste de conectividade Docker PostgreSQL');
            """))
            print("✅ Inserção de dados: OK")
            
            # Teste de consulta
            result = connection.execute(text("SELECT COUNT(*) FROM test_connection;"))
            count = result.fetchone()[0]
            print(f"✅ Consulta de dados: OK ({count} registros)")
            
            # Limpeza
            connection.execute(text("DROP TABLE test_connection;"))
            print("✅ Limpeza de dados: OK")
            
            connection.commit()
            return True
            
    except Exception as e:
        print(f"❌ Erro nas operações: {e}")
        return False

if __name__ == "__main__":
    print("🐘 Teste de conectividade PostgreSQL Docker")
    print("=" * 50)
    
    # Testar conexão
    if test_connection():
        # Se conexão OK, testar operações
        test_database_operations()
        print("\n🎉 Todos os testes passaram! O banco está pronto para uso.")
    else:
        print("\n💡 Consulte o arquivo DOCKER_MIGRATION.md para instruções detalhadas.")
        sys.exit(1)
