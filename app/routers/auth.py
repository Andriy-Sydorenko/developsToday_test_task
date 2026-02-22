from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.constants import JWT_TOKEN_COOKIE_KEY
from app.database import get_db
from app.schemas.auth import (
    AuthUserResponse,
    LoginRequest,
    RegisterRequest,
)
from app.security import create_access_token
from app.services.user import UserService


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthUserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    register_data: RegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AuthUserResponse:
    user_service = UserService(db)
    user = await user_service.register(
        register_data.email,
        register_data.password.get_secret_value(),
        register_data.name,
    )
    return AuthUserResponse.model_validate(user)


@router.post("/login", response_model=AuthUserResponse)
async def login(
    login_data: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    response: Response,
) -> AuthUserResponse:
    user_service = UserService(db)
    user = await user_service.authenticate(login_data.email, login_data.password.get_secret_value())
    token = create_access_token(str(user.id))
    response.set_cookie(
        key=JWT_TOKEN_COOKIE_KEY,
        value=token,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        path="/",
        max_age=settings.jwt_access_token_expire_minutes * 60,
    )
    return AuthUserResponse.model_validate(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    response.delete_cookie(
        key=JWT_TOKEN_COOKIE_KEY,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        path="/",
    )
