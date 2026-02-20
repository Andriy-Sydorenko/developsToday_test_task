from __future__ import annotations

from pydantic import BaseModel, Field


class GetPlaceRequest(BaseModel):
    external_id: int
    fields: tuple[str, ...] = ("id", "title", "api_link")

    @property
    def path(self) -> str:
        return f"/places/{self.external_id}"

    def query_params(self) -> dict[str, str]:
        return {"fields": ",".join(self.fields)}


class ArticPlace(BaseModel):
    id: int
    title: str | None = None
    api_link: str | None = None


class ListPlacesRequest(BaseModel):
    limit: int = Field(default=12, ge=1, le=100)
    page: int = Field(default=1, ge=1)
    fields: tuple[str, ...] = ("id", "title", "api_link")

    @property
    def path(self) -> str:
        return "/places"

    def query_params(self) -> dict[str, str]:
        return {
            "limit": str(self.limit),
            "page": str(self.page),
            "fields": ",".join(self.fields),
        }


class SearchPlacesRequest(BaseModel):
    q: str
    limit: int = Field(default=12, ge=1, le=100)
    page: int = Field(default=1, ge=1)
    fields: tuple[str, ...] = ("id", "title", "api_link")

    @property
    def path(self) -> str:
        return "/places/search"

    def query_params(self) -> dict[str, str]:
        return {
            "q": self.q,
            "limit": str(self.limit),
            "page": str(self.page),
            "fields": ",".join(self.fields),
        }


class PlaceData(BaseModel):
    id: int
    title: str | None = None
    api_link: str | None = None


class PlaceResponse(BaseModel):
    data: PlaceData


class Pagination(BaseModel):
    total: int
    limit: int
    offset: int
    total_pages: int
    current_page: int
    next_url: str | None = None


class PlaceListItem(BaseModel):
    id: int
    title: str | None = None
    api_link: str | None = None


class PlaceSearchItem(PlaceListItem):
    score: float | None = Field(default=None, alias="_score")


class PlacesResponse(BaseModel):
    pagination: Pagination
    data: list[PlaceListItem]


class PlacesSearchResponse(BaseModel):
    pagination: Pagination
    data: list[PlaceSearchItem]
