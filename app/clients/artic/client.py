from __future__ import annotations

import asyncio
import time
from collections import OrderedDict
from typing import ClassVar

import httpx

from app.clients.artic.errors import (
    ArtInstituteBadResponseError,
    ArtInstituteClientError,
    ArtInstituteNotFoundError,
    ArtInstituteRateLimitError,
    ArtInstituteTimeoutError,
)
from app.clients.artic.models import ArticPlace, GetPlaceRequest, PlaceResponse
from app.config import settings


class ArtInstituteClient:
    _shared_client: ClassVar[httpx.AsyncClient | None] = None
    _shared_client_lock: ClassVar[asyncio.Lock] = asyncio.Lock()

    _cache: ClassVar[OrderedDict[int, tuple[float, ArticPlace]]] = OrderedDict()
    _cache_lock: ClassVar[asyncio.Lock] = asyncio.Lock()

    def __init__(
        self,
        *,
        http_client: httpx.AsyncClient | None = None,
        base_url: str | None = None,
        timeout_seconds: float | None = None,
    ) -> None:
        self._client_override = http_client
        self._base_url_override = base_url
        self._timeout_override = timeout_seconds

    async def close(self) -> None:
        # No-op by default: the client uses a shared AsyncClient.
        # If a custom client was injected, its lifecycle is managed by the caller.
        return

    async def get_place(self, external_id: int) -> ArticPlace:
        if settings.artic_cache_enabled:
            cached = await self._cache_get(external_id)
            if cached is not None:
                return cached

        request = GetPlaceRequest(external_id=external_id)
        response = await self._request("GET", request.path, params=request.query_params())
        try:
            payload = PlaceResponse.model_validate(response.json())
        except Exception as exc:
            raise ArtInstituteBadResponseError("Invalid response format from Art Institute API") from exc

        place = ArticPlace(id=payload.data.id, title=payload.data.title)
        if settings.artic_cache_enabled:
            await self._cache_set(external_id, place)
        return place

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
    ) -> httpx.Response:
        client = self._client_override or await self._get_shared_client(
            base_url=self._base_url_override,
            timeout_seconds=self._timeout_override,
        )
        try:
            response = await client.request(method, path, params=params)
        except httpx.TimeoutException as exc:
            raise ArtInstituteTimeoutError("Art Institute API timeout") from exc
        except httpx.HTTPError as exc:
            raise ArtInstituteClientError("Art Institute API request failed") from exc

        self._raise_for_status(response)
        return response

    @classmethod
    async def _get_shared_client(
        cls,
        *,
        base_url: str | None,
        timeout_seconds: float | None,
    ) -> httpx.AsyncClient:
        if cls._shared_client is not None:
            return cls._shared_client

        async with cls._shared_client_lock:
            if cls._shared_client is not None:
                return cls._shared_client

            cls._shared_client = httpx.AsyncClient(
                base_url=(base_url or settings.artic_api_base_url).rstrip("/"),
                timeout=httpx.Timeout(timeout_seconds or settings.artic_api_timeout_seconds),
            )
            return cls._shared_client

    @classmethod
    async def aclose_shared(cls) -> None:
        async with cls._shared_client_lock:
            if cls._shared_client is not None:
                await cls._shared_client.aclose()
                cls._shared_client = None

    @classmethod
    async def _cache_get(cls, external_id: int) -> ArticPlace | None:
        now = time.monotonic()
        async with cls._cache_lock:
            entry = cls._cache.get(external_id)
            if entry is None:
                return None
            expires_at, place = entry
            if expires_at <= now:
                cls._cache.pop(external_id, None)
                return None
            cls._cache.move_to_end(external_id)
            return place

    @classmethod
    async def _cache_set(cls, external_id: int, place: ArticPlace) -> None:
        ttl = max(0, int(settings.artic_cache_ttl_seconds))
        if ttl == 0:
            return
        max_entries = max(1, int(settings.artic_cache_max_entries))
        expires_at = time.monotonic() + ttl

        async with cls._cache_lock:
            cls._cache[external_id] = (expires_at, place)
            cls._cache.move_to_end(external_id)

            # First, remove expired entries.
            now = time.monotonic()
            expired_keys = [k for k, (exp, _) in cls._cache.items() if exp <= now]
            for k in expired_keys:
                cls._cache.pop(k, None)

            # Then enforce max size (simple LRU eviction).
            while len(cls._cache) > max_entries:
                cls._cache.popitem(last=False)

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        if response.status_code == 404:
            raise ArtInstituteNotFoundError("Place not found")

        if response.status_code == 429:
            raise ArtInstituteRateLimitError("Art Institute API rate limited")

        if response.status_code >= 500:
            raise ArtInstituteClientError("Art Institute API server error")

        if response.status_code != 200:
            raise ArtInstituteBadResponseError(f"Unexpected response status: {response.status_code}")
