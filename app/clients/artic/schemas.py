from __future__ import annotations

from pydantic import BaseModel


class GetPlaceRequest(BaseModel):
    external_id: int
    fields: tuple[str, ...] = ("id", "title")

    @property
    def path(self) -> str:
        return f"/places/{self.external_id}"

    def query_params(self) -> dict[str, str]:
        return {"fields": ",".join(self.fields)}


class ArticPlace(BaseModel):
    id: int
    title: str | None = None


class PlaceData(BaseModel):
    id: int
    title: str | None = None


class PlaceResponse(BaseModel):
    data: PlaceData
