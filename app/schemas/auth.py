from pydantic import BaseModel, EmailStr, Field, SecretStr

from app.constants import PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH
from app.schemas.base import BaseValidatedModel


class RegisterRequest(BaseValidatedModel):
    email: EmailStr
    password: SecretStr = Field(..., min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)
    name: str | None = Field(default=None, min_length=3)


class LoginRequest(BaseValidatedModel):
    email: EmailStr
    password: SecretStr = Field(..., min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)


class AuthUserResponse(BaseModel):
    email: EmailStr
    name: str | None = None

    class Config:
        from_attributes = True
