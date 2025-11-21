"""Unit tests for NotificationService."""

import logging
from unittest.mock import MagicMock, patch

import pytest

from soulspot.application.services.notification_service import NotificationService


class TestNotificationService:
    """Test suite for NotificationService."""

    @pytest.fixture
    def service(self) -> NotificationService:
        """Create a NotificationService instance for testing."""
        return NotificationService()

    @pytest.fixture
    def mock_logger(self) -> MagicMock:
        """Create a mock logger for testing."""
        return MagicMock(spec=logging.Logger)

    async def test_send_new_release_notification_success(
        self, service: NotificationService, mock_logger: MagicMock
    ):
        """Test sending new release notification."""
        with patch(
            "soulspot.application.services.notification_service.logger", mock_logger
        ):
            result = await service.send_new_release_notification(
                artist_name="The Beatles",
                album_name="Abbey Road",
                release_date="1969-09-26",
            )

            assert result is True
            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args[0][0]
            assert "[NOTIFICATION]" in call_args
            assert "The Beatles" in call_args
            assert "Abbey Road" in call_args
            assert "1969-09-26" in call_args

    async def test_send_missing_album_notification_success(
        self, service: NotificationService, mock_logger: MagicMock
    ):
        """Test sending missing album notification."""
        with patch(
            "soulspot.application.services.notification_service.logger", mock_logger
        ):
            result = await service.send_missing_album_notification(
                artist_name="Pink Floyd", missing_count=3, total_count=15
            )

            assert result is True
            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args[0][0]
            assert "[NOTIFICATION]" in call_args
            assert "Pink Floyd" in call_args
            assert "3 of 15 albums missing" in call_args
            assert "80.0% complete" in call_args

    async def test_send_missing_album_notification_zero_total(
        self, service: NotificationService, mock_logger: MagicMock
    ):
        """Test missing album notification with zero total count."""
        with patch(
            "soulspot.application.services.notification_service.logger", mock_logger
        ):
            result = await service.send_missing_album_notification(
                artist_name="New Artist", missing_count=0, total_count=0
            )

            assert result is True
            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args[0][0]
            assert "0.0% complete" in call_args

    async def test_send_quality_upgrade_notification_success(
        self, service: NotificationService, mock_logger: MagicMock
    ):
        """Test sending quality upgrade notification."""
        with patch(
            "soulspot.application.services.notification_service.logger", mock_logger
        ):
            result = await service.send_quality_upgrade_notification(
                track_title="Bohemian Rhapsody",
                current_quality="MP3 320kbps",
                target_quality="FLAC Lossless",
            )

            assert result is True
            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args[0][0]
            assert "[NOTIFICATION]" in call_args
            assert "Bohemian Rhapsody" in call_args
            assert "MP3 320kbps → FLAC Lossless" in call_args

    async def test_send_automation_notification_minimal_context(
        self, service: NotificationService, mock_logger: MagicMock
    ):
        """Test automation notification with minimal context."""
        with patch(
            "soulspot.application.services.notification_service.logger", mock_logger
        ):
            result = await service.send_automation_notification(
                trigger="new_release", context={}
            )

            assert result is True
            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args[0][0]
            assert "[NOTIFICATION]" in call_args
            assert "new_release" in call_args

    async def test_send_automation_notification_with_artist_id(
        self, service: NotificationService, mock_logger: MagicMock
    ):
        """Test automation notification with artist ID in context."""
        with patch(
            "soulspot.application.services.notification_service.logger", mock_logger
        ):
            result = await service.send_automation_notification(
                trigger="new_release", context={"artist_id": "spotify:artist:123"}
            )

            assert result is True
            call_args = mock_logger.info.call_args[0][0]
            assert "Artist: spotify:artist:123" in call_args

    async def test_send_automation_notification_with_album_info(
        self, service: NotificationService, mock_logger: MagicMock
    ):
        """Test automation notification with album info in context."""
        with patch(
            "soulspot.application.services.notification_service.logger", mock_logger
        ):
            result = await service.send_automation_notification(
                trigger="missing_album",
                context={"album_info": {"name": "Dark Side of the Moon"}},
            )

            assert result is True
            call_args = mock_logger.info.call_args[0][0]
            assert "Album: Dark Side of the Moon" in call_args

    async def test_send_automation_notification_with_album_info_no_name(
        self, service: NotificationService, mock_logger: MagicMock
    ):
        """Test automation notification with album info but no name."""
        with patch(
            "soulspot.application.services.notification_service.logger", mock_logger
        ):
            result = await service.send_automation_notification(
                trigger="missing_album", context={"album_info": {}}
            )

            assert result is True
            call_args = mock_logger.info.call_args[0][0]
            assert "Album: Unknown" in call_args

    async def test_send_automation_notification_with_track_title(
        self, service: NotificationService, mock_logger: MagicMock
    ):
        """Test automation notification with track title in context."""
        with patch(
            "soulspot.application.services.notification_service.logger", mock_logger
        ):
            result = await service.send_automation_notification(
                trigger="quality_upgrade", context={"track_title": "Stairway to Heaven"}
            )

            assert result is True
            call_args = mock_logger.info.call_args[0][0]
            assert "Track: Stairway to Heaven" in call_args

    async def test_send_automation_notification_with_all_context(
        self, service: NotificationService, mock_logger: MagicMock
    ):
        """Test automation notification with all context fields."""
        with patch(
            "soulspot.application.services.notification_service.logger", mock_logger
        ):
            result = await service.send_automation_notification(
                trigger="new_release",
                context={
                    "artist_id": "spotify:artist:456",
                    "album_info": {"name": "Led Zeppelin IV"},
                    "track_title": "Black Dog",
                },
            )

            assert result is True
            call_args = mock_logger.info.call_args[0][0]
            assert "Artist: spotify:artist:456" in call_args
            assert "Album: Led Zeppelin IV" in call_args
            assert "Track: Black Dog" in call_args

    async def test_send_download_started_notification_success(
        self, service: NotificationService, mock_logger: MagicMock
    ):
        """Test sending download started notification."""
        with patch(
            "soulspot.application.services.notification_service.logger", mock_logger
        ):
            result = await service.send_download_started_notification(
                item_name="Hotel California - Eagles", quality_profile="FLAC Lossless"
            )

            assert result is True
            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args[0][0]
            assert "[NOTIFICATION]" in call_args
            assert "Download started" in call_args
            assert "Hotel California - Eagles" in call_args
            assert "FLAC Lossless" in call_args

    async def test_send_download_completed_notification_success(
        self, service: NotificationService, mock_logger: MagicMock
    ):
        """Test sending download completed notification with success."""
        with patch(
            "soulspot.application.services.notification_service.logger", mock_logger
        ):
            result = await service.send_download_completed_notification(
                item_name="Comfortably Numb - Pink Floyd", success=True
            )

            assert result is True
            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args[0][0]
            assert "[NOTIFICATION]" in call_args
            assert "completed successfully" in call_args
            assert "Comfortably Numb - Pink Floyd" in call_args

    async def test_send_download_completed_notification_failure(
        self, service: NotificationService, mock_logger: MagicMock
    ):
        """Test sending download completed notification with failure."""
        with patch(
            "soulspot.application.services.notification_service.logger", mock_logger
        ):
            result = await service.send_download_completed_notification(
                item_name="Wish You Were Here - Pink Floyd", success=False
            )

            assert result is True
            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args[0][0]
            assert "[NOTIFICATION]" in call_args
            assert "failed" in call_args
            assert "Wish You Were Here - Pink Floyd" in call_args

    async def test_notification_service_initialization(self):
        """Test NotificationService initialization."""
        service = NotificationService()
        assert service is not None
        assert isinstance(service, NotificationService)
