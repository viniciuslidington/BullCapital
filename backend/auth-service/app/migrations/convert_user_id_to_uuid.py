"""Reset destrutivo da tabela users para usar UUID como PK.

Uso (irá APAGAR usuários existentes):
  uv run app/migrations/convert_user_id_to_uuid.py

O modelo SQL já inclui campos de suporte ao Google OAuth.
"""
from sqlalchemy import text
import os, sys

# Garantir que possamos importar app.core.database tanto via execução direta quanto via -m
try:
    from app.core.database import engine  # caminho absoluto dentro do pacote 'app'
except ModuleNotFoundError:
    # Ajusta sys.path adicionando diretório pai de 'app'
    CURRENT_DIR = os.path.dirname(__file__)
    APP_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))  # .../auth-service/app
    PROJECT_ROOT = os.path.dirname(APP_DIR)  # .../auth-service
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    from app.core.database import engine

RESET_SQL = """
DROP TABLE IF EXISTS users CASCADE;
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);
"""

EXTENSIONS_SQL = [
    'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";',
    'CREATE EXTENSION IF NOT EXISTS pgcrypto;'
]

def run():
    print(f"📂 CWD: {os.getcwd()}")
    with engine.begin() as conn:
        print("🔧 Garantindo extensões UUID...")
        for stmt in EXTENSIONS_SQL:
            try:
                conn.execute(text(stmt))
            except Exception as e:
                print(f"   ⚠️  Falha (ignorada) ao criar extensão: {e}")
        print("🧨 Resetando tabela users ...")
        conn.execute(text(RESET_SQL))
    print("✅ Tabela users recriada com UUID (todos os dados antigos foram removidos).")

if __name__ == "__main__":
    run()
