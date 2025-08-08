from fastapi import FastAPI
import uvicorn
from routers import gateway_market_data, gateway_auth, gateway_ai
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="API Gateway Service")

app.get("/")
async def read_root():
    return {"message": "Welcome to the API Gateway Service"}

# Inclui o router de Market Data do Gateway
# O prefixo '/market-data' é a URL que os CLIENTES EXTERNOS verão
app.include_router(gateway_market_data.router, prefix="/market-data", tags=["Market Data Gateway"])
app.include_router(gateway_auth.router, prefix="/auth", tags=["Auth Gateway"])
app.include_router(gateway_ai.router, prefix="/ai", tags=["AI Gateway"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Rate-Limit-Remaining"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)