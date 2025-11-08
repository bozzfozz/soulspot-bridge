"""Application use cases - Business logic orchestration."""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

# Type variables for generic use case pattern
TRequest = TypeVar("TRequest")
TResponse = TypeVar("TResponse")


class UseCase(ABC, Generic[TRequest, TResponse]):
    """Base class for all use cases following command pattern."""

    @abstractmethod
    async def execute(self, request: TRequest) -> TResponse:
        """Execute the use case with the given request."""
        pass


# Import concrete use cases
from soulspot.application.use_cases.enrich_metadata import EnrichMetadataUseCase
from soulspot.application.use_cases.import_spotify_playlist import ImportSpotifyPlaylistUseCase
from soulspot.application.use_cases.search_and_download import SearchAndDownloadTrackUseCase

__all__ = [
    "UseCase",
    "ImportSpotifyPlaylistUseCase",
    "SearchAndDownloadTrackUseCase",
    "EnrichMetadataUseCase",
]
