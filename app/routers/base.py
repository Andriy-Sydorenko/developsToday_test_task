from fastapi import APIRouter

from app.routers.auth import router as auth_router


base_api_router = APIRouter(prefix="/api/v1")

base_api_router.include_router(auth_router)
