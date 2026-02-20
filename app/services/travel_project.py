from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.artic.client import ArtInstituteClient
from app.clients.artic.errors import (
    ArtInstituteBadResponseError,
    ArtInstituteClientError,
    ArtInstituteNotFoundError,
    ArtInstituteRateLimitError,
    ArtInstituteTimeoutError,
)
from app.constants import MAX_PLACES_PER_PROJECT
from app.models.project_place import ProjectPlace
from app.models.travel_project import TravelProject
from app.repositories.project_place import ProjectPlaceRepository
from app.repositories.travel_project import TravelProjectRepository
from app.schemas.project_place import ProjectPlaceImport, ProjectPlaceUpdate
from app.schemas.travel_project import TravelProjectCreate, TravelProjectUpdate


class TravelProjectService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.project_repo = TravelProjectRepository(db)
        self.place_repo = ProjectPlaceRepository(db)
        self.artic = ArtInstituteClient()

    async def list_projects(
        self,
        user_id: str,
        *,
        limit: int,
        offset: int,
        is_completed: bool | None = None,
        q: str | None = None,
    ) -> list[TravelProject]:
        return await self.project_repo.list_for_user(
            user_id,
            limit=limit,
            offset=offset,
            is_completed=is_completed,
            q=q,
        )

    async def get_project(self, user_id: str, project_id: str) -> TravelProject:
        project = await self.project_repo.get_for_user_by_id(user_id, project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        return project

    async def create_project(self, user_id: str, payload: TravelProjectCreate) -> TravelProject:
        external_ids = [p.external_id for p in payload.places]
        if len(set(external_ids)) != len(external_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate places in request",
            )

        if len(external_ids) > MAX_PLACES_PER_PROJECT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum {MAX_PLACES_PER_PROJECT} places per project",
            )

        project = TravelProject(
            user_id=UUID(user_id),
            name=payload.name,
            description=payload.description,
            start_date=payload.start_date,
        )
        await self.project_repo.create(project)

        for place_payload in payload.places:
            place_from_api = await self._get_place_or_http_error(place_payload.external_id)
            place = ProjectPlace(
                project_id=project.id,
                external_id=place_from_api.id,
                title=place_from_api.title,
                notes=place_payload.notes,
            )
            try:
                await self.place_repo.create(place)
            except IntegrityError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Place already added to project"
                ) from None

        await self._sync_project_completion(str(project.id))
        return project

    async def update_project(self, user_id: str, project_id: str, payload: TravelProjectUpdate) -> TravelProject:
        project = await self.get_project(user_id, project_id)
        data = payload.model_dump(exclude_unset=True)
        if not data:
            return project
        return await self.project_repo.update(project, data)

    async def delete_project(self, user_id: str, project_id: str) -> None:
        project = await self.get_project(user_id, project_id)
        if await self.place_repo.any_visited_for_project(project_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project cannot be deleted because it has visited places",
            )
        await self.project_repo.delete(project)

    async def list_places(
        self,
        user_id: str,
        project_id: str,
        *,
        limit: int,
        offset: int,
        visited: bool | None = None,
    ) -> list[ProjectPlace]:
        await self.get_project(user_id, project_id)
        return await self.place_repo.list_for_project(project_id, limit=limit, offset=offset, visited=visited)

    async def get_place(self, user_id: str, project_id: str, place_id: str) -> ProjectPlace:
        await self.get_project(user_id, project_id)
        place = await self.place_repo.get_for_project_by_id(project_id, place_id)
        if not place:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found")
        return place

    async def add_place(self, user_id: str, project_id: str, payload: ProjectPlaceImport) -> ProjectPlace:
        project = await self.get_project(user_id, project_id)

        current_count = await self.place_repo.count_for_project(project_id)
        if current_count >= MAX_PLACES_PER_PROJECT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum {MAX_PLACES_PER_PROJECT} places per project",
            )

        if await self.place_repo.exists_external_in_project(project_id, payload.external_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Place already added to project")

        place_from_api = await self._get_place_or_http_error(payload.external_id)
        place = ProjectPlace(
            project_id=project.id,
            external_id=place_from_api.id,
            title=place_from_api.title,
            notes=payload.notes,
        )
        created = await self.place_repo.create(place)
        await self._sync_project_completion(project_id)
        return created

    async def update_place(
        self, user_id: str, project_id: str, place_id: str, payload: ProjectPlaceUpdate
    ) -> ProjectPlace:
        place = await self.get_place(user_id, project_id, place_id)
        data = payload.model_dump(exclude_unset=True)
        if not data:
            return place

        if data.get("visited") is True and not place.visited:
            place.mark_visited()
            data.pop("visited", None)
        elif data.get("visited") is False and place.visited:
            place.mark_unvisited()
            data.pop("visited", None)

        updated = await self.place_repo.update(place, data)
        await self._sync_project_completion(project_id)
        return updated

    async def _sync_project_completion(self, project_id: str) -> None:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            return

        total = await self.place_repo.count_for_project(project_id)
        visited = await self.place_repo.count_visited_for_project(project_id)

        if total > 0 and visited == total and not project.is_completed:
            project.mark_completed()
            await self.project_repo.update(
                project,
                {"is_completed": project.is_completed, "completed_at": project.completed_at},
            )
            return

        if project.is_completed:
            project.mark_incomplete()
            await self.project_repo.update(
                project,
                {"is_completed": project.is_completed, "completed_at": project.completed_at},
            )

    async def _get_place_or_http_error(self, external_id: int):
        try:
            return await self.artic.get_place(external_id)
        except ArtInstituteNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Place not found in Art Institute API",
            ) from None
        except ArtInstituteRateLimitError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Third-party API rate limited",
            ) from None
        except ArtInstituteTimeoutError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Third-party API timeout",
            ) from None
        except ArtInstituteBadResponseError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(exc),
            ) from None
        except ArtInstituteClientError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Third-party API error",
            ) from None
