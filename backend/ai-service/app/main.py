"""Ponto de entrada principal para o AI Service.

Expõe o objeto ``app`` importando de ``app.api_server`` para que o comando
``uvicorn app.main:app`` (usado no docker-compose) funcione corretamente.

Se executado diretamente (python -m app.main), inicia o servidor de
desenvolvimento com reload.
"""

from app.api_server import app  # noqa: F401 (re-export)
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.api_server:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
