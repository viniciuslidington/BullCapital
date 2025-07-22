from fastapi import FastAPI
import uvicorn
from routers import gateway_market_data

app = FastAPI(title="API Gateway Service")

app.get("/")
async def read_root():
    return {"message": "Welcome to the API Gateway Service"}

# Inclui o router de Market Data do Gateway
# O prefixo '/market-data' é a URL que os CLIENTES EXTERNOS verão
app.include_router(gateway_market_data.router, prefix="/market-data", tags=["Market Data Gateway"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)