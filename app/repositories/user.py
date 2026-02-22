from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @staticmethod
    def _as_uuid(value: str | UUID) -> UUID:
        return value if isinstance(value, UUID) else UUID(value)

    async def get_by_id(self, user_id: str | UUID) -> User | None:
        result = await self.session.execute(select(User).where(User.id == self._as_uuid(user_id)))
        return result.scalars().first()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def update(self, user: User, data: dict) -> User:
        for key, value in data.items():
            setattr(user, key, value)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def delete_user(self, user: User) -> None:
        await self.session.delete(user)
