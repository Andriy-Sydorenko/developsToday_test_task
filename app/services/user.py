from fastapi import HTTPException, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user import UserRepository
from app.security import hash_password, verify_password


class UserService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)

    async def get_by_id(self, user_id: str) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    async def register(self, email: EmailStr, password: str, name: str | None = None) -> User:
        existing = await self.user_repo.get_by_email(str(email))
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

        new_user = User(email=str(email), name=name, password_hash=hash_password(password))
        return await self.user_repo.create(new_user)

    async def authenticate(self, email: EmailStr, password: str) -> User:
        user = await self.user_repo.get_by_email(str(email))
        if not user or not verify_password(user.password_hash, password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
        return user
