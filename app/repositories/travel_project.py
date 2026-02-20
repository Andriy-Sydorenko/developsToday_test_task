from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.travel_project import TravelProject


class TravelProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @staticmethod
    def _as_uuid(value: str | UUID) -> UUID:
        return value if isinstance(value, UUID) else UUID(value)

    async def get_by_id(self, project_id: str | UUID) -> TravelProject | None:
        result = await self.session.execute(
            select(TravelProject).where(TravelProject.id == self._as_uuid(project_id)),
        )
        return result.scalars().first()

    async def get_for_user_by_id(self, user_id: str, project_id: str) -> TravelProject | None:
        result = await self.session.execute(
            select(TravelProject).where(
                TravelProject.user_id == UUID(user_id),
                TravelProject.id == self._as_uuid(project_id),
            ),
        )
        return result.scalars().first()

    async def list_for_user(
        self,
        user_id: str,
        *,
        limit: int,
        offset: int,
        is_completed: bool | None = None,
        q: str | None = None,
    ) -> list[TravelProject]:
        query = select(TravelProject).where(TravelProject.user_id == UUID(user_id))
        if is_completed is not None:
            query = query.where(TravelProject.is_completed.is_(is_completed))
        if q:
            query = query.where(TravelProject.name.ilike(f"%{q}%"))

        query = query.order_by(TravelProject.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, project: TravelProject) -> TravelProject:
        self.session.add(project)
        await self.session.flush()
        await self.session.refresh(project)
        return project

    async def update(self, project: TravelProject, data: dict) -> TravelProject:
        for key, value in data.items():
            setattr(project, key, value)
        await self.session.flush()
        await self.session.refresh(project)
        return project

    async def delete(self, project: TravelProject) -> None:
        await self.session.delete(project)

    async def delete_by_id(self, project_id: str) -> None:
        await self.session.execute(delete(TravelProject).where(TravelProject.id == self._as_uuid(project_id)))
