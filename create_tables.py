#!/usr/bin/env python3
"""
Script para criar as tabelas no banco de dados
"""

import sys
import os

# Adicionar o diretório src ao Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.database import create_tables

if __name__ == "__main__":
    print("Criando tabelas no banco de dados...")
    try:
        create_tables()
        print("✅ Tabelas criadas com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        sys.exit(1)
