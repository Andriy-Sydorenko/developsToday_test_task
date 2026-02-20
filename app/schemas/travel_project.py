import datetime

from pydantic import BaseModel, Field

from app.constants import MAX_PLACES_PER_PROJECT, MIN_PLACES_PER_PROJECT
from app.schemas.base import BaseValidatedModel
from app.schemas.project_place import ProjectPlaceImport, ProjectPlacePublic


class TravelProjectCreate(BaseValidatedModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    start_date: datetime.date | None = None
    places: list[ProjectPlaceImport] = Field(
        ...,
        min_length=MIN_PLACES_PER_PROJECT,
        max_length=MAX_PLACES_PER_PROJECT,
    )


class TravelProjectUpdate(BaseValidatedModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    start_date: datetime.date | None = None


class TravelProjectPublic(BaseModel):
    id: str
    user_id: str
    name: str
    description: str | None = None
    start_date: datetime.date | None = None
    is_completed: bool
    completed_at: datetime.datetime | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


class TravelProjectWithPlacesPublic(TravelProjectPublic):
    places: list[ProjectPlacePublic]
