from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project_place import ProjectPlace


class ProjectPlaceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, place_id: str) -> ProjectPlace | None:
        result = await self.session.execute(select(ProjectPlace).where(ProjectPlace.id == UUID(place_id)))
        return result.scalars().first()

    async def get_for_project_by_id(self, project_id: str, place_id: str) -> ProjectPlace | None:
        result = await self.session.execute(
            select(ProjectPlace).where(
                ProjectPlace.project_id == UUID(project_id),
                ProjectPlace.id == UUID(place_id),
            ),
        )
        return result.scalars().first()

    async def list_for_project(
        self,
        project_id: str,
        *,
        limit: int,
        offset: int,
        visited: bool | None = None,
    ) -> list[ProjectPlace]:
        query = select(ProjectPlace).where(ProjectPlace.project_id == UUID(project_id))
        if visited is not None:
            query = query.where(ProjectPlace.visited.is_(visited))
        query = query.order_by(ProjectPlace.created_at.asc()).limit(limit).offset(offset)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_for_project(self, project_id: str) -> int:
        result = await self.session.execute(
            select(func.count(ProjectPlace.id)).where(ProjectPlace.project_id == UUID(project_id)),
        )
        return int(result.scalar_one())

    async def count_visited_for_project(self, project_id: str) -> int:
        result = await self.session.execute(
            select(func.count(ProjectPlace.id)).where(
                ProjectPlace.project_id == UUID(project_id),
                ProjectPlace.visited.is_(True),
            ),
        )
        return int(result.scalar_one())

    async def any_visited_for_project(self, project_id: str) -> bool:
        result = await self.session.execute(
            select(func.count(ProjectPlace.id)).where(
                ProjectPlace.project_id == UUID(project_id),
                ProjectPlace.visited.is_(True),
            ),
        )
        return int(result.scalar_one()) > 0

    async def exists_external_in_project(self, project_id: str, external_id: int) -> bool:
        result = await self.session.execute(
            select(func.count(ProjectPlace.id)).where(
                ProjectPlace.project_id == UUID(project_id),
                ProjectPlace.external_id == external_id,
            ),
        )
        return int(result.scalar_one()) > 0

    async def create(self, place: ProjectPlace) -> ProjectPlace:
        self.session.add(place)
        await self.session.flush()
        await self.session.refresh(place)
        return place

    async def update(self, place: ProjectPlace, data: dict) -> ProjectPlace:
        for key, value in data.items():
            setattr(place, key, value)
        await self.session.flush()
        await self.session.refresh(place)
        return place

    async def delete(self, place: ProjectPlace) -> None:
        await self.session.delete(place)
