from typing import Any

from pydantic import BaseModel, model_validator


class BaseValidatedModel(BaseModel):
    @model_validator(mode="before")
    @classmethod
    def check_empty_fields(cls, data: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(data, dict):
            return data

        for field_name, value in data.items():
            if isinstance(value, str) and value.strip() == "":
                raise ValueError(f"{field_name} cannot be empty or contain only whitespace")
        return data
