import datetime

from pydantic import BaseModel

from app.schemas.base import BaseValidatedModel


class ProjectPlaceImport(BaseValidatedModel):
    # Art Institute "places" IDs can be negative (see /api/v1/places list response).
    external_id: int
    notes: str | None = None


class ProjectPlaceUpdate(BaseValidatedModel):
    notes: str | None = None
    visited: bool | None = None


class ProjectPlacePublic(BaseModel):
    id: str
    project_id: str
    external_id: int
    title: str | None = None
    notes: str | None = None
    visited: bool
    visited_at: datetime.datetime | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True
