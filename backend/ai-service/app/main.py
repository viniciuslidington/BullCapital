"""
Ponto de entrada principal para o serviço de autenticação.

Este módulo inicia o servidor FastAPI usando Uvicorn quando executado diretamente.
Configurado para escutar em todas as interfaces de rede na porta 8000 com
recarregamento automático habilitado para desenvolvimento.
"""

import uvicorn

if __name__ == "__main__":
    """
    Inicia o servidor de desenvolvimento do FastAPI.
    
    Configurações:
    - Host: 0.0.0.0 (aceita conexões de qualquer IP)
    - Porta: 8000
    - Reload: True (reinicia automaticamente quando arquivos são modificados)
    """
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )