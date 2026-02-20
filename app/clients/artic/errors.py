from __future__ import annotations


class ArtInstituteClientError(Exception):
    """Base error for Art Institute client."""


class ArtInstituteTimeoutError(ArtInstituteClientError):
    pass


class ArtInstituteNotFoundError(ArtInstituteClientError):
    pass


class ArtInstituteRateLimitError(ArtInstituteClientError):
    pass


class ArtInstituteBadResponseError(ArtInstituteClientError):
    pass
