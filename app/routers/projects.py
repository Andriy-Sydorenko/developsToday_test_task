from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.project_place import ProjectPlaceImport, ProjectPlacePublic, ProjectPlaceUpdate
from app.schemas.travel_project import (
    TravelProjectCreate,
    TravelProjectPublic,
    TravelProjectUpdate,
    TravelProjectWithPlacesPublic,
)
from app.security import get_current_user_id
from app.services.travel_project import TravelProjectService


router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=TravelProjectWithPlacesPublic, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: TravelProjectCreate,
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TravelProjectWithPlacesPublic:
    service = TravelProjectService(db)
    project = await service.create_project(user_id, payload)
    places = await service.list_places(user_id, str(project.id))

    return TravelProjectWithPlacesPublic.model_validate(
        {
            **TravelProjectPublic.model_validate(project).model_dump(),
            "places": [ProjectPlacePublic.model_validate(p).model_dump() for p in places],
        },
    )


@router.get("", response_model=list[TravelProjectPublic])
async def list_projects(
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[TravelProjectPublic]:
    service = TravelProjectService(db)
    projects = await service.list_projects(user_id)
    return [TravelProjectPublic.model_validate(p) for p in projects]


@router.get("/{project_id}", response_model=TravelProjectWithPlacesPublic)
async def get_project(
    project_id: str,
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TravelProjectWithPlacesPublic:
    service = TravelProjectService(db)
    project = await service.get_project(user_id, project_id)
    places = await service.list_places(user_id, project_id)

    return TravelProjectWithPlacesPublic.model_validate(
        {
            **TravelProjectPublic.model_validate(project).model_dump(),
            "places": [ProjectPlacePublic.model_validate(p).model_dump() for p in places],
        },
    )


@router.patch("/{project_id}", response_model=TravelProjectPublic)
async def update_project(
    project_id: str,
    payload: TravelProjectUpdate,
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TravelProjectPublic:
    service = TravelProjectService(db)
    project = await service.update_project(user_id, project_id, payload)
    return TravelProjectPublic.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    await TravelProjectService(db).delete_project(user_id, project_id)


@router.get("/{project_id}/places", response_model=list[ProjectPlacePublic])
async def list_places(
    project_id: str,
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[ProjectPlacePublic]:
    service = TravelProjectService(db)
    places = await service.list_places(user_id, project_id)
    return [ProjectPlacePublic.model_validate(p) for p in places]


@router.post("/{project_id}/places", response_model=ProjectPlacePublic, status_code=status.HTTP_201_CREATED)
async def add_place(
    project_id: str,
    payload: ProjectPlaceImport,
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProjectPlacePublic:
    place = await TravelProjectService(db).add_place(user_id, project_id, payload)
    return ProjectPlacePublic.model_validate(place)


@router.get("/{project_id}/places/{place_id}", response_model=ProjectPlacePublic)
async def get_place(
    project_id: str,
    place_id: str,
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProjectPlacePublic:
    place = await TravelProjectService(db).get_place(user_id, project_id, place_id)
    return ProjectPlacePublic.model_validate(place)


@router.patch("/{project_id}/places/{place_id}", response_model=ProjectPlacePublic)
async def update_place(
    project_id: str,
    place_id: str,
    payload: ProjectPlaceUpdate,
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProjectPlacePublic:
    place = await TravelProjectService(db).update_place(user_id, project_id, place_id, payload)
    return ProjectPlacePublic.model_validate(place)
