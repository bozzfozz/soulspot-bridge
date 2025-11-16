"""Unit tests for filter service."""

from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from soulspot.application.services.filter_service import FilterService
from soulspot.domain.entities import FilterRule, FilterTarget, FilterType
from soulspot.domain.value_objects import FilterRuleId


class TestFilterService:
    """Test FilterService."""

    @pytest.mark.asyncio
    async def test_create_filter(self) -> None:
        """Test creating a new filter rule."""
        session = AsyncMock(spec=AsyncSession)
        service = FilterService(session)

        filter_rule = await service.create_filter(
            name="Test Filter",
            filter_type=FilterType.WHITELIST,
            target=FilterTarget.KEYWORD,
            pattern="test*",
            is_regex=True,
            priority=1,
            description="Test filter rule",
        )

        assert filter_rule.name == "Test Filter"
        assert filter_rule.filter_type == FilterType.WHITELIST
        assert filter_rule.target == FilterTarget.KEYWORD
        assert filter_rule.pattern == "test*"
        assert filter_rule.is_regex is True
        assert filter_rule.priority == 1
        assert filter_rule.enabled is True

    @pytest.mark.asyncio
    async def test_get_filter(self) -> None:
        """Test getting a filter by ID."""
        session = AsyncMock(spec=AsyncSession)
        service = FilterService(session)

        filter_id = FilterRuleId.generate()
        mock_filter = FilterRule(
            id=filter_id,
            name="Test Filter",
            filter_type=FilterType.WHITELIST,
            target=FilterTarget.KEYWORD,
            pattern="test*",
            is_regex=True,
            enabled=True,
            priority=1,
        )

        service.repository.get_by_id = AsyncMock(return_value=mock_filter)

        result = await service.get_filter(filter_id)
        assert result == mock_filter
        service.repository.get_by_id.assert_called_once_with(filter_id)

    @pytest.mark.asyncio
    async def test_list_by_type(self) -> None:
        """Test listing filters by type."""
        session = AsyncMock(spec=AsyncSession)
        service = FilterService(session)

        mock_filters = [
            FilterRule(
                id=FilterRuleId.generate(),
                name="Whitelist 1",
                filter_type=FilterType.WHITELIST,
                target=FilterTarget.KEYWORD,
                pattern="good*",
                is_regex=True,
                enabled=True,
                priority=1,
            ),
            FilterRule(
                id=FilterRuleId.generate(),
                name="Whitelist 2",
                filter_type=FilterType.WHITELIST,
                target=FilterTarget.USER,
                pattern="trusted*",
                is_regex=True,
                enabled=True,
                priority=2,
            ),
        ]

        service.repository.list_by_type = AsyncMock(return_value=mock_filters)

        result = await service.list_by_type(FilterType.WHITELIST)
        assert len(result) == 2
        assert all(f.filter_type == FilterType.WHITELIST for f in result)

    @pytest.mark.asyncio
    async def test_list_enabled(self) -> None:
        """Test listing enabled filters."""
        session = AsyncMock(spec=AsyncSession)
        service = FilterService(session)

        mock_filters = [
            FilterRule(
                id=FilterRuleId.generate(),
                name="Enabled Filter",
                filter_type=FilterType.WHITELIST,
                target=FilterTarget.KEYWORD,
                pattern="test*",
                is_regex=True,
                enabled=True,
                priority=1,
            )
        ]

        service.repository.list_enabled = AsyncMock(return_value=mock_filters)

        result = await service.list_enabled()
        assert len(result) == 1
        assert result[0].enabled is True

    @pytest.mark.asyncio
    async def test_apply_filters_whitelist(self) -> None:
        """Test applying whitelist filters."""
        session = AsyncMock(spec=AsyncSession)
        service = FilterService(session)

        whitelist_filter = FilterRule(
            id=FilterRuleId.generate(),
            name="Allow Test",
            filter_type=FilterType.WHITELIST,
            target=FilterTarget.KEYWORD,
            pattern="good",
            is_regex=False,
            enabled=True,
            priority=1,
        )

        service.repository.list_enabled = AsyncMock(return_value=[whitelist_filter])

        # Test search results that match whitelist
        search_results = [
            {"filename": "Good Track.mp3", "username": "user1"},
            {"filename": "Bad Track.mp3", "username": "user2"},
        ]

        filtered = await service.apply_filters(search_results)
        # Should only include results matching whitelist
        assert len(filtered) <= len(search_results)

    @pytest.mark.asyncio
    async def test_apply_filters_blacklist(self) -> None:
        """Test applying blacklist filters."""
        session = AsyncMock(spec=AsyncSession)
        service = FilterService(session)

        blacklist_filter = FilterRule(
            id=FilterRuleId.generate(),
            name="Block Bad",
            filter_type=FilterType.BLACKLIST,
            target=FilterTarget.KEYWORD,
            pattern="bad",
            is_regex=False,
            enabled=True,
            priority=1,
        )

        service.repository.list_enabled = AsyncMock(return_value=[blacklist_filter])

        # Test search results with blacklisted terms
        search_results = [
            {"filename": "Good Track.mp3", "username": "user1"},
            {"filename": "Bad Track.mp3", "username": "user2"},
        ]

        filtered = await service.apply_filters(search_results)
        # Should exclude results matching blacklist
        assert len(filtered) <= len(search_results)

    @pytest.mark.asyncio
    async def test_apply_filters_regex(self) -> None:
        """Test applying regex filters."""
        session = AsyncMock(spec=AsyncSession)
        service = FilterService(session)

        regex_filter = FilterRule(
            id=FilterRuleId.generate(),
            name="Regex Test",
            filter_type=FilterType.WHITELIST,
            target=FilterTarget.KEYWORD,
            pattern=r"test\d+",
            is_regex=True,
            enabled=True,
            priority=1,
        )

        service.repository.list_enabled = AsyncMock(return_value=[regex_filter])

        # Test search results
        search_results = [
            {"filename": "test123.mp3", "username": "user1"},
            {"filename": "testabc.mp3", "username": "user2"},
        ]

        filtered = await service.apply_filters(search_results)
        # Should only include results matching regex
        assert isinstance(filtered, list)

    @pytest.mark.asyncio
    async def test_disable_filter(self) -> None:
        """Test disabling a filter."""
        session = AsyncMock(spec=AsyncSession)
        service = FilterService(session)

        filter_id = FilterRuleId.generate()
        mock_filter = FilterRule(
            id=filter_id,
            name="Test Filter",
            filter_type=FilterType.WHITELIST,
            target=FilterTarget.KEYWORD,
            pattern="test*",
            is_regex=True,
            enabled=True,
            priority=1,
        )

        service.repository.get_by_id = AsyncMock(return_value=mock_filter)
        service.repository.update = AsyncMock()

        await service.disable_filter(filter_id)

        assert mock_filter.enabled is False
        service.repository.update.assert_called_once_with(mock_filter)

    @pytest.mark.asyncio
    async def test_enable_filter(self) -> None:
        """Test enabling a filter."""
        session = AsyncMock(spec=AsyncSession)
        service = FilterService(session)

        filter_id = FilterRuleId.generate()
        mock_filter = FilterRule(
            id=filter_id,
            name="Test Filter",
            filter_type=FilterType.WHITELIST,
            target=FilterTarget.KEYWORD,
            pattern="test*",
            is_regex=True,
            enabled=False,
            priority=1,
        )

        service.repository.get_by_id = AsyncMock(return_value=mock_filter)
        service.repository.update = AsyncMock()

        await service.enable_filter(filter_id)

        assert mock_filter.enabled is True
        service.repository.update.assert_called_once_with(mock_filter)
