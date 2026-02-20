import datetime

from pydantic import BaseModel, Field

from app.schemas.base import BaseValidatedModel


class ProjectPlaceImport(BaseValidatedModel):
    external_id: int = Field(..., ge=1)
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
