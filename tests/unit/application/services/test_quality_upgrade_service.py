"""Unit tests for quality upgrade service."""

from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from soulspot.application.services.quality_upgrade_service import QualityUpgradeService


class TestQualityUpgradeService:
    """Test QualityUpgradeService."""

    def test_calculate_improvement_score(self) -> None:
        """Test calculating improvement score."""
        session = AsyncMock(spec=AsyncSession)
        service = QualityUpgradeService(session)

        # Test bitrate improvement only (same format)
        score = service.calculate_improvement_score(
            current_bitrate=192,
            current_format="mp3",
            target_bitrate=320,
            target_format="mp3",
        )

        # Should be primarily based on bitrate improvement
        assert 0.0 <= score <= 1.0
        assert score > 0.0  # Some improvement

        # Test format improvement (lossy to lossless)
        score_lossless = service.calculate_improvement_score(
            current_bitrate=320,
            current_format="mp3",
            target_bitrate=1411,
            target_format="flac",
        )

        # Lossless should score higher
        assert score_lossless > score

    @pytest.mark.asyncio
    async def test_identify_upgrade_candidates(self) -> None:
        """Test identifying upgrade opportunities."""
        session = AsyncMock(spec=AsyncSession)
        service = QualityUpgradeService(session)

        # Mock the database query response - scalars() returns a synchronous object
        class MockScalarsResult:
            def all(self):
                return []

        mock_result = AsyncMock()
        mock_result.scalars = lambda: MockScalarsResult()

        session.execute.return_value = mock_result

        # Should complete without error
        candidates = await service.identify_upgrade_candidates(
            quality_profile="high", min_improvement_score=0.3, limit=100
        )

        assert isinstance(candidates, list)

    def test_quality_profile_constants(self) -> None:
        """Test quality profile constant definitions."""
        # Test that quality profiles are defined
        profiles = QualityUpgradeService.QUALITY_PROFILES

        assert "low" in profiles
        assert "medium" in profiles
        assert "high" in profiles
        assert "lossless" in profiles

        # Test profile bitrate thresholds
        assert profiles["low"]["min_bitrate"] == 128
        assert profiles["medium"]["min_bitrate"] == 192
        assert profiles["high"]["min_bitrate"] == 320
        assert profiles["lossless"]["min_bitrate"] == 1411

    def test_improvement_score_calculation_edge_cases(self) -> None:
        """Test improvement score edge cases."""
        session = AsyncMock(spec=AsyncSession)
        service = QualityUpgradeService(session)

        # Test same quality (no improvement)
        score = service.calculate_improvement_score(
            current_bitrate=320,
            current_format="mp3",
            target_bitrate=320,
            target_format="mp3",
        )
        assert score == 0.0

        # Test large bitrate jump
        score = service.calculate_improvement_score(
            current_bitrate=128,
            current_format="mp3",
            target_bitrate=1411,
            target_format="flac",
        )
        assert score > 0.5  # Significant improvement

    def test_format_quality_mapping(self) -> None:
        """Test that format quality mapping works correctly."""
        session = AsyncMock(spec=AsyncSession)
        service = QualityUpgradeService(session)

        # FLAC to FLAC should be no format improvement
        score1 = service.calculate_improvement_score(
            current_bitrate=1411,
            current_format="flac",
            target_bitrate=1411,
            target_format="flac",
        )

        # MP3 to FLAC should be format improvement
        score2 = service.calculate_improvement_score(
            current_bitrate=320,
            current_format="mp3",
            target_bitrate=1411,
            target_format="flac",
        )

        assert score2 > score1
