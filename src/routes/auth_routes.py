from fastapi import APIRouter
from controllers.auth_controller import router as auth_router

router = APIRouter()
router.include_router(auth_router, prefix="/auth", tags=["Autenticação"])
