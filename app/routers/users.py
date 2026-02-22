from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.user import UserPasswordUpdate, UserPublic, UserUpdate
from app.security import get_current_user_id
from app.services.user import UserService


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserPublic)
async def me(
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserPublic:
    user = await UserService(db).get_by_id(user_id)
    return UserPublic.model_validate(user)


@router.patch("/me", response_model=UserPublic)
async def update_me(
    payload: UserUpdate,
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserPublic:
    user = await UserService(db).update_name(user_id, payload.name)
    return UserPublic.model_validate(user)


@router.patch("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def update_my_password(
    payload: UserPasswordUpdate,
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    await UserService(db).update_password(
        user_id,
        payload.current_password.get_secret_value(),
        payload.new_password.get_secret_value(),
    )
