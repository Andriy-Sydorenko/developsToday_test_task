import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, SecretStr

from app.constants import PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH
from app.schemas.base import BaseValidatedModel


class UserPublic(BaseModel):
    id: UUID
    email: EmailStr
    name: str | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseValidatedModel):
    name: str = Field(..., min_length=3)


class UserPasswordUpdate(BaseValidatedModel):
    current_password: SecretStr = Field(..., min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)
    new_password: SecretStr = Field(..., min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)
