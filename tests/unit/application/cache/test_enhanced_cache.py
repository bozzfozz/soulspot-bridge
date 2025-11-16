"""Unit tests for enhanced cache functionality."""

import asyncio

import pytest

from soulspot.application.cache.enhanced_cache import (
    CacheMetrics,
    CacheWarmer,
    LRUCache,
    LRUCacheEntry,
)


class TestCacheMetrics:
    """Test cache metrics tracking."""

    def test_initial_metrics(self) -> None:
        """Test initial metrics are zero."""
        metrics = CacheMetrics()
        assert metrics.hits == 0
        assert metrics.misses == 0
        assert metrics.evictions == 0
        assert metrics.writes == 0
        assert metrics.hit_rate == 0.0

    def test_hit_rate_calculation(self) -> None:
        """Test hit rate calculation."""
        metrics = CacheMetrics()
        metrics.hits = 80
        metrics.misses = 20
        assert metrics.hit_rate == 80.0

    def test_hit_rate_with_no_requests(self) -> None:
        """Test hit rate returns 0 when no requests."""
        metrics = CacheMetrics()
        assert metrics.hit_rate == 0.0

    def test_reset_metrics(self) -> None:
        """Test resetting metrics."""
        metrics = CacheMetrics()
        metrics.hits = 100
        metrics.misses = 50
        metrics.evictions = 10
        metrics.writes = 75

        metrics.reset()

        assert metrics.hits == 0
        assert metrics.misses == 0
        assert metrics.evictions == 0
        assert metrics.writes == 0


class TestLRUCacheEntry:
    """Test LRU cache entry behavior."""

    def test_entry_not_expired_initially(self) -> None:
        """Test entry is not expired initially."""
        import time
        entry = LRUCacheEntry(value="test", created_at=time.time(), ttl_seconds=3600)
        assert not entry.is_expired()

    def test_entry_expiration(self) -> None:
        """Test entry expiration after TTL."""
        import time
        entry = LRUCacheEntry(
            value="test",
            created_at=time.time() - 3700,
            ttl_seconds=3600,
        )
        assert entry.is_expired()

    def test_entry_touch(self) -> None:
        """Test entry touch updates access metadata."""
        import time
        entry = LRUCacheEntry(value="test", created_at=time.time(), ttl_seconds=3600)
        initial_count = entry.access_count

        entry.touch()

        assert entry.access_count == initial_count + 1
        assert entry.last_accessed > 0


class TestLRUCache:
    """Test LRU cache functionality."""

    @pytest.mark.asyncio
    async def test_cache_basic_operations(self) -> None:
        """Test basic cache set/get operations."""
        cache: LRUCache[str, str] = LRUCache(max_size=10)

        await cache.set("key1", "value1")
        result = await cache.get("key1")

        assert result == "value1"

    @pytest.mark.asyncio
    async def test_cache_miss(self) -> None:
        """Test cache miss returns None."""
        cache: LRUCache[str, str] = LRUCache(max_size=10)
        result = await cache.get("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_cache_expiration(self) -> None:
        """Test cache entry expiration."""
        cache: LRUCache[str, str] = LRUCache(max_size=10)

        await cache.set("key1", "value1", ttl_seconds=0)
        await asyncio.sleep(0.1)
        result = await cache.get("key1")

        assert result is None

    @pytest.mark.asyncio
    async def test_lru_eviction(self) -> None:
        """Test LRU eviction when max size is reached."""
        cache: LRUCache[str, str] = LRUCache(max_size=3)

        # Fill cache to max
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.set("key3", "value3")

        # Access key1 to make it recently used
        await cache.get("key1")

        # Add new key, should evict key2 (least recently used)
        await cache.set("key4", "value4")

        # key1 should still exist
        assert await cache.get("key1") == "value1"
        # key2 should be evicted
        assert await cache.get("key2") is None
        # key3 and key4 should exist
        assert await cache.get("key3") == "value3"
        assert await cache.get("key4") == "value4"

    @pytest.mark.asyncio
    async def test_cache_delete(self) -> None:
        """Test cache entry deletion."""
        cache: LRUCache[str, str] = LRUCache(max_size=10)

        await cache.set("key1", "value1")
        deleted = await cache.delete("key1")

        assert deleted is True
        assert await cache.get("key1") is None

    @pytest.mark.asyncio
    async def test_cache_clear(self) -> None:
        """Test clearing entire cache."""
        cache: LRUCache[str, str] = LRUCache(max_size=10)

        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.clear()

        assert await cache.get("key1") is None
        assert await cache.get("key2") is None

    @pytest.mark.asyncio
    async def test_cache_exists(self) -> None:
        """Test cache key existence check."""
        cache: LRUCache[str, str] = LRUCache(max_size=10)

        await cache.set("key1", "value1")

        assert await cache.exists("key1") is True
        assert await cache.exists("nonexistent") is False

    @pytest.mark.asyncio
    async def test_cleanup_expired(self) -> None:
        """Test cleanup of expired entries."""
        cache: LRUCache[str, str] = LRUCache(max_size=10)

        await cache.set("key1", "value1", ttl_seconds=0)
        await cache.set("key2", "value2", ttl_seconds=3600)
        await asyncio.sleep(0.1)

        removed = await cache.cleanup_expired()

        assert removed == 1
        assert await cache.get("key1") is None
        assert await cache.get("key2") == "value2"

    @pytest.mark.asyncio
    async def test_cache_metrics(self) -> None:
        """Test cache metrics tracking."""
        cache: LRUCache[str, str] = LRUCache(max_size=3)

        # Perform operations
        await cache.set("key1", "value1")  # write
        await cache.get("key1")  # hit
        await cache.get("nonexistent")  # miss
        await cache.set("key2", "value2")  # write
        await cache.set("key3", "value3")  # write
        await cache.set("key4", "value4")  # write + eviction

        metrics = cache.get_metrics()

        assert metrics.hits == 1
        assert metrics.misses == 1
        assert metrics.writes == 4
        assert metrics.evictions == 1
        assert metrics.hit_rate == 50.0

    @pytest.mark.asyncio
    async def test_cache_stats(self) -> None:
        """Test cache statistics."""
        cache: LRUCache[str, str] = LRUCache(max_size=10)

        await cache.set("key1", "value1")
        await cache.set("key2", "value2")

        stats = cache.get_stats()

        assert stats["total_entries"] == 2
        assert stats["active_entries"] == 2
        assert stats["max_size"] == 10
        assert stats["utilization_percent"] == 20.0
        assert "metrics" in stats

    @pytest.mark.asyncio
    async def test_batch_set(self) -> None:
        """Test batch set operation."""
        cache: LRUCache[str, str] = LRUCache(max_size=10)

        items = {"key1": "value1", "key2": "value2", "key3": "value3"}
        await cache.set_batch(items, ttl_seconds=3600)

        assert await cache.get("key1") == "value1"
        assert await cache.get("key2") == "value2"
        assert await cache.get("key3") == "value3"

    @pytest.mark.asyncio
    async def test_batch_set_with_eviction(self) -> None:
        """Test batch set with LRU eviction."""
        cache: LRUCache[str, str] = LRUCache(max_size=3)

        # Fill cache
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")

        # Batch set more items than remaining space
        items = {"key3": "value3", "key4": "value4"}
        await cache.set_batch(items)

        # Check that eviction occurred
        stats = cache.get_stats()
        assert stats["total_entries"] == 3


class TestCacheWarmer:
    """Test cache warming functionality."""

    @pytest.mark.asyncio
    async def test_warm_from_dict(self) -> None:
        """Test warming cache from dictionary."""
        cache: LRUCache[str, str] = LRUCache(max_size=10)
        warmer = CacheWarmer(cache)

        items = {"key1": "value1", "key2": "value2"}
        count = await warmer.warm_from_dict(items)

        assert count == 2
        assert await cache.get("key1") == "value1"
        assert await cache.get("key2") == "value2"

    @pytest.mark.asyncio
    async def test_warm_from_loader(self) -> None:
        """Test warming cache from loader function."""
        cache: LRUCache[str, str] = LRUCache(max_size=10)
        warmer = CacheWarmer(cache)

        async def loader(key: str) -> str | None:
            if key == "skip":
                return None
            return f"value_{key}"

        keys = ["key1", "key2", "skip", "key3"]
        count = await warmer.warm_from_loader(keys, loader)

        assert count == 3
        assert await cache.get("key1") == "value_key1"
        assert await cache.get("key2") == "value_key2"
        assert await cache.get("skip") is None
        assert await cache.get("key3") == "value_key3"
