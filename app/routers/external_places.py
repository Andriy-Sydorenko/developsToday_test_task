from typing import Annotated

from fastapi import APIRouter, Query

from app.clients.artic.client import ArtInstituteClient
from app.clients.artic.errors import (
    ArtInstituteBadResponseError,
    ArtInstituteClientError,
    ArtInstituteNotFoundError,
    ArtInstituteRateLimitError,
    ArtInstituteTimeoutError,
)
from app.clients.artic.schemas import PlaceResponse, PlacesResponse, PlacesSearchResponse


router = APIRouter(prefix="/external/places", tags=["external-places"])


@router.get("", response_model=PlacesResponse)
async def list_places(
    limit: Annotated[int, Query(ge=1, le=100)] = 12,
    page: Annotated[int, Query(ge=1)] = 1,
) -> PlacesResponse:
    client = ArtInstituteClient()
    try:
        return await client.list_places(limit=limit, page=page)
    except (ArtInstituteTimeoutError, ArtInstituteRateLimitError, ArtInstituteClientError):
        # Upstream is unavailable or unstable; this endpoint is a proxy.
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Third-party API error") from None
    except ArtInstituteBadResponseError as exc:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from None


@router.get("/search", response_model=PlacesSearchResponse)
async def search_places(
    q: str,
    limit: Annotated[int, Query(ge=1, le=100)] = 12,
    page: Annotated[int, Query(ge=1)] = 1,
) -> PlacesSearchResponse:
    client = ArtInstituteClient()
    try:
        return await client.search_places(q=q, limit=limit, page=page)
    except (ArtInstituteTimeoutError, ArtInstituteRateLimitError, ArtInstituteClientError):
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Third-party API error") from None
    except ArtInstituteBadResponseError as exc:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from None


@router.get("/{external_id}", response_model=PlaceResponse)
async def get_place(
    external_id: int,
) -> PlaceResponse:
    client = ArtInstituteClient()
    try:
        # Use underlying request/response model so response shape matches upstream `data: {id,title,api_link}`.
        from app.clients.artic.schemas import GetPlaceRequest

        request = GetPlaceRequest(external_id=external_id)
        response = await client._request("GET", request.path, params=request.query_params())
        return PlaceResponse.model_validate(response.json())
    except ArtInstituteNotFoundError:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found") from None
    except (ArtInstituteTimeoutError, ArtInstituteRateLimitError, ArtInstituteClientError):
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Third-party API error") from None
    except ArtInstituteBadResponseError as exc:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from None
