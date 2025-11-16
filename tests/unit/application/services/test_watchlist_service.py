"""Unit tests for watchlist service."""

from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from soulspot.application.services.watchlist_service import WatchlistService
from soulspot.domain.entities import ArtistWatchlist, WatchlistStatus
from soulspot.domain.value_objects import ArtistId, WatchlistId


class TestWatchlistService:
    """Test WatchlistService."""

    @pytest.mark.asyncio
    async def test_create_watchlist(self) -> None:
        """Test creating a new watchlist."""
        session = AsyncMock(spec=AsyncSession)
        service = WatchlistService(session)

        artist_id = ArtistId.generate()
        watchlist = await service.create_watchlist(
            artist_id=artist_id,
            check_frequency_hours=24,
            auto_download=True,
            quality_profile="high",
        )

        assert watchlist.artist_id == artist_id
        assert watchlist.check_frequency_hours == 24
        assert watchlist.auto_download is True
        assert watchlist.quality_profile == "high"
        assert watchlist.status == WatchlistStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_get_watchlist(self) -> None:
        """Test getting a watchlist by ID."""
        session = AsyncMock(spec=AsyncSession)
        service = WatchlistService(session)

        watchlist_id = WatchlistId.generate()
        artist_id = ArtistId.generate()

        mock_watchlist = ArtistWatchlist(
            id=watchlist_id,
            artist_id=artist_id,
            status=WatchlistStatus.ACTIVE,
            check_frequency_hours=24,
            auto_download=True,
            quality_profile="high",
            last_checked_at=None,
            last_release_date=None,
            total_releases_found=0,
            total_downloads_triggered=0,
        )

        service.repository.get_by_id = AsyncMock(return_value=mock_watchlist)

        result = await service.get_watchlist(watchlist_id)
        assert result == mock_watchlist
        service.repository.get_by_id.assert_called_once_with(watchlist_id)

    @pytest.mark.asyncio
    async def test_list_all_watchlists(self) -> None:
        """Test listing all watchlists."""
        session = AsyncMock(spec=AsyncSession)
        service = WatchlistService(session)

        mock_watchlists = [
            ArtistWatchlist(
                id=WatchlistId.generate(),
                artist_id=ArtistId.generate(),
                status=WatchlistStatus.ACTIVE,
                check_frequency_hours=24,
                auto_download=True,
                quality_profile="high",
                last_checked_at=None,
                last_release_date=None,
                total_releases_found=0,
                total_downloads_triggered=0,
            )
            for _ in range(3)
        ]

        service.repository.list_all = AsyncMock(return_value=mock_watchlists)

        result = await service.list_all(limit=100, offset=0)
        assert len(result) == 3
        service.repository.list_all.assert_called_once_with(100, 0)

    @pytest.mark.asyncio
    async def test_delete_watchlist(self) -> None:
        """Test deleting a watchlist."""
        session = AsyncMock(spec=AsyncSession)
        service = WatchlistService(session)

        watchlist_id = WatchlistId.generate()
        service.repository.delete = AsyncMock()

        await service.delete_watchlist(watchlist_id)
        service.repository.delete.assert_called_once_with(watchlist_id)

    @pytest.mark.asyncio
    async def test_pause_watchlist(self) -> None:
        """Test pausing a watchlist."""
        session = AsyncMock(spec=AsyncSession)
        service = WatchlistService(session)

        watchlist_id = WatchlistId.generate()
        artist_id = ArtistId.generate()

        mock_watchlist = ArtistWatchlist(
            id=watchlist_id,
            artist_id=artist_id,
            status=WatchlistStatus.ACTIVE,
            check_frequency_hours=24,
            auto_download=True,
            quality_profile="high",
            last_checked_at=None,
            last_release_date=None,
            total_releases_found=0,
            total_downloads_triggered=0,
        )

        service.repository.get_by_id = AsyncMock(return_value=mock_watchlist)
        service.repository.update = AsyncMock()

        await service.pause_watchlist(watchlist_id)

        assert mock_watchlist.status == WatchlistStatus.PAUSED
        service.repository.update.assert_called_once_with(mock_watchlist)

    @pytest.mark.asyncio
    async def test_resume_watchlist(self) -> None:
        """Test resuming a paused watchlist."""
        session = AsyncMock(spec=AsyncSession)
        service = WatchlistService(session)

        watchlist_id = WatchlistId.generate()
        artist_id = ArtistId.generate()

        mock_watchlist = ArtistWatchlist(
            id=watchlist_id,
            artist_id=artist_id,
            status=WatchlistStatus.PAUSED,
            check_frequency_hours=24,
            auto_download=True,
            quality_profile="high",
            last_checked_at=None,
            last_release_date=None,
            total_releases_found=0,
            total_downloads_triggered=0,
        )

        service.repository.get_by_id = AsyncMock(return_value=mock_watchlist)
        service.repository.update = AsyncMock()

        await service.resume_watchlist(watchlist_id)

        assert mock_watchlist.status == WatchlistStatus.ACTIVE
        service.repository.update.assert_called_once_with(mock_watchlist)
