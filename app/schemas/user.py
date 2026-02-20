import datetime

from pydantic import BaseModel, EmailStr, Field

from app.schemas.base import BaseValidatedModel


class UserPublic(BaseModel):
    id: str
    email: EmailStr
    name: str | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseValidatedModel):
    name: str = Field(..., min_length=3)
