from __future__ import annotations

from dataclasses import dataclass

import httpx
from fastapi import HTTPException, status

from app.config import settings


@dataclass(frozen=True, slots=True)
class ArticArtwork:
    id: int
    title: str | None


class ArtInstituteClient:
    def __init__(self) -> None:
        self._base_url = settings.artic_api_base_url.rstrip("/")
        self._timeout = httpx.Timeout(settings.artic_api_timeout_seconds)

    async def get_artwork(self, external_id: int) -> ArticArtwork:
        url = f"{self._base_url}/artworks/{external_id}"
        params = {"fields": "id,title"}

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            try:
                response = await client.get(url, params=params)
            except httpx.TimeoutException:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Third-party API timeout",
                ) from None
            except httpx.HTTPError:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Third-party API error",
                ) from None

        if response.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Place not found in Art Institute API")

        if response.status_code >= 500:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Third-party API error",
            )

        if response.status_code != status.HTTP_200_OK:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Unexpected third-party API response",
            )

        payload = response.json()
        data = payload.get("data") or {}
        return ArticArtwork(id=int(data["id"]), title=data.get("title"))
