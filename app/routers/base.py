from fastapi import APIRouter

from app.routers.auth import router as auth_router
from app.routers.external_places import router as external_places_router
from app.routers.projects import router as projects_router
from app.routers.users import router as users_router


base_api_router = APIRouter(prefix="/api/v1")

base_api_router.include_router(auth_router)
base_api_router.include_router(projects_router)
base_api_router.include_router(external_places_router)
base_api_router.include_router(users_router)
