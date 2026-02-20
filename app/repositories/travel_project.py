from uuid import UUID

from sqlalchemy import Select, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.travel_project import TravelProject


class TravelProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _base_query(self) -> Select:
        return select(TravelProject)

    async def get_by_id(self, project_id: str) -> TravelProject | None:
        result = await self.session.execute(self._base_query().where(TravelProject.id == UUID(project_id)))
        return result.scalars().first()

    async def get_for_user_by_id(self, user_id: str, project_id: str) -> TravelProject | None:
        result = await self.session.execute(
            self._base_query().where(
                TravelProject.user_id == UUID(user_id),
                TravelProject.id == UUID(project_id),
            ),
        )
        return result.scalars().first()

    async def list_for_user(self, user_id: str) -> list[TravelProject]:
        result = await self.session.execute(
            self._base_query().where(TravelProject.user_id == UUID(user_id)).order_by(TravelProject.created_at.desc()),
        )
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
        await self.session.execute(delete(TravelProject).where(TravelProject.id == UUID(project_id)))
