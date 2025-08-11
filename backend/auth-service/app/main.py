"""
Ponto de entrada principal para o serviço de autenticação.

Este módulo inicia o servidor FastAPI usando Uvicorn quando executado diretamente.
Configurado para escutar em todas as interfaces de rede na porta 8003 com
recarregamento automático habilitado para desenvolvimento.
"""

import uvicorn

if __name__ == "__main__":
    """
    Inicia o servidor de desenvolvimento do FastAPI.
    
    Configurações:
    - Host: 0.0.0.0 (aceita conexões de qualquer IP)
    - Porta: 8003
    - Reload: True (reinicia automaticamente quando arquivos são modificados)
    """
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8003,
        reload=True
    )