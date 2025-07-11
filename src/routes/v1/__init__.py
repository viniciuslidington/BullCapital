from fastapi import APIRouter
from .auth import router as auth_router
from .market_data import router as market_data_router

# API V1 Router
v1_router = APIRouter(prefix="/api/v1")

# Incluir todas as rotas da v1
v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
v1_router.include_router(market_data_router, prefix="/market", tags=["Market Data"])
