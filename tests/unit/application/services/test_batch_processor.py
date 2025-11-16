"""Unit tests for batch processing functionality."""

import asyncio

import pytest

from soulspot.application.services.batch_processor import BatchProcessor, BatchResult


class TestBatchResult:
    """Test batch result tracking."""

    def test_initial_result(self) -> None:
        """Test initial batch result is empty."""
        result: BatchResult[str] = BatchResult()

        assert result.total_items == 0
        assert result.success_count == 0
        assert result.failure_count == 0
        assert result.success_rate == 0.0

    def test_result_with_successes(self) -> None:
        """Test batch result with successful items."""
        result: BatchResult[str] = BatchResult()
        result.successful = ["item1", "item2", "item3"]

        assert result.total_items == 3
        assert result.success_count == 3
        assert result.failure_count == 0
        assert result.success_rate == 100.0

    def test_result_with_failures(self) -> None:
        """Test batch result with failed items."""
        result: BatchResult[str] = BatchResult()
        result.failed = [("item1", Exception("error1")), ("item2", Exception("error2"))]

        assert result.total_items == 2
        assert result.success_count == 0
        assert result.failure_count == 2
        assert result.success_rate == 0.0

    def test_result_with_mixed(self) -> None:
        """Test batch result with both successes and failures."""
        result: BatchResult[str] = BatchResult()
        result.successful = ["item1", "item2"]
        result.failed = [("item3", Exception("error"))]

        assert result.total_items == 3
        assert result.success_count == 2
        assert result.failure_count == 1
        assert result.success_rate == pytest.approx(66.67, rel=0.01)


class TestBatchProcessor:
    """Test batch processor functionality."""

    @pytest.mark.asyncio
    async def test_basic_batch_processing(self) -> None:
        """Test basic batch processing."""
        processed_items: list[list[int]] = []

        async def processor(items: list[int]) -> list[int]:
            processed_items.append(items)
            return items

        batch_processor: BatchProcessor[int, int] = BatchProcessor(
            batch_size=3,
            processor_func=processor,
            auto_flush=False,
        )

        await batch_processor.add(1)
        await batch_processor.add(2)
        await batch_processor.add(3)

        result = await batch_processor.flush()

        assert len(processed_items) == 1
        assert processed_items[0] == [1, 2, 3]
        assert result.success_count == 3

    @pytest.mark.asyncio
    async def test_auto_flush(self) -> None:
        """Test automatic flushing when batch size is reached."""
        processed_items: list[list[int]] = []

        async def processor(items: list[int]) -> list[int]:
            processed_items.append(items)
            return items

        batch_processor: BatchProcessor[int, int] = BatchProcessor(
            batch_size=3,
            processor_func=processor,
            auto_flush=True,
        )

        await batch_processor.add(1)
        await batch_processor.add(2)
        result = await batch_processor.add(3)  # Should trigger auto-flush

        assert result is not None
        assert len(processed_items) == 1
        assert processed_items[0] == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_multiple_batches(self) -> None:
        """Test processing multiple batches."""
        processed_items: list[list[int]] = []

        async def processor(items: list[int]) -> list[int]:
            processed_items.append(items)
            return items

        batch_processor: BatchProcessor[int, int] = BatchProcessor(
            batch_size=2,
            processor_func=processor,
            auto_flush=True,
        )

        for i in range(5):
            await batch_processor.add(i)

        # Flush remaining - item 4 should still be pending since batch size wasn't reached
        final_result = await batch_processor.flush()

        # Should have auto-flushed 2 full batches: [0,1], [2,3]
        # And manually flushed the remaining: [4]
        assert len(processed_items) == 3
        assert final_result.success_count == 1  # 1 item in final flush

    @pytest.mark.asyncio
    async def test_add_batch(self) -> None:
        """Test adding multiple items at once."""
        processed_items: list[list[int]] = []

        async def processor(items: list[int]) -> list[int]:
            processed_items.append(items)
            return items

        batch_processor: BatchProcessor[int, int] = BatchProcessor(
            batch_size=3,
            processor_func=processor,
            auto_flush=True,
        )

        results = await batch_processor.add_batch([1, 2, 3, 4, 5, 6, 7])

        # Should have processed 2 full batches
        assert len(results) == 2
        assert len(processed_items) == 2

        # Flush remaining item
        final_result = await batch_processor.flush()
        assert final_result.success_count == 1

    @pytest.mark.asyncio
    async def test_pending_count(self) -> None:
        """Test tracking pending items count."""
        async def processor(items: list[int]) -> list[int]:
            return items

        batch_processor: BatchProcessor[int, int] = BatchProcessor(
            batch_size=5,
            processor_func=processor,
            auto_flush=False,
        )

        assert batch_processor.get_pending_count() == 0

        await batch_processor.add(1)
        await batch_processor.add(2)
        await batch_processor.add(3)

        assert batch_processor.get_pending_count() == 3

        await batch_processor.flush()

        assert batch_processor.get_pending_count() == 0

    @pytest.mark.asyncio
    async def test_empty_flush(self) -> None:
        """Test flushing when no items are pending."""
        async def processor(items: list[int]) -> list[int]:
            return items

        batch_processor: BatchProcessor[int, int] = BatchProcessor(
            batch_size=3,
            processor_func=processor,
        )

        result = await batch_processor.flush()

        assert result.total_items == 0
        assert result.success_count == 0

    @pytest.mark.asyncio
    async def test_close(self) -> None:
        """Test closing processor and flushing remaining items."""
        processed_items: list[list[int]] = []

        async def processor(items: list[int]) -> list[int]:
            processed_items.append(items)
            return items

        batch_processor: BatchProcessor[int, int] = BatchProcessor(
            batch_size=10,
            processor_func=processor,
            auto_flush=False,
        )

        await batch_processor.add(1)
        await batch_processor.add(2)

        result = await batch_processor.close()

        assert len(processed_items) == 1
        assert processed_items[0] == [1, 2]
        assert result.success_count == 2

    @pytest.mark.asyncio
    async def test_processor_error_handling(self) -> None:
        """Test error handling when processor fails."""
        call_count = 0
        
        async def failing_processor(items: list[int]) -> list[int]:
            nonlocal call_count
            call_count += 1
            raise ValueError("Processing failed")

        batch_processor: BatchProcessor[int, int] = BatchProcessor(
            batch_size=3,
            processor_func=failing_processor,
            auto_flush=False,  # Disable auto-flush to control when processing happens
        )

        await batch_processor.add(1)
        await batch_processor.add(2)
        await batch_processor.add(3)

        result = await batch_processor.flush()

        # Processor should have been called once
        assert call_count == 1
        # All items should be marked as failed
        assert result.success_count == 0
        assert result.failure_count == 3
        assert result.success_rate == 0.0

    @pytest.mark.asyncio
    async def test_no_processor_func(self) -> None:
        """Test error when no processor function is configured."""
        batch_processor: BatchProcessor[int, int] = BatchProcessor(
            batch_size=3,
            processor_func=None,
        )

        await batch_processor.add(1)

        with pytest.raises(ValueError, match="No processor function configured"):
            await batch_processor.flush()

    @pytest.mark.asyncio
    async def test_max_wait_time(self) -> None:
        """Test flush based on max wait time."""
        processed_items: list[list[int]] = []

        async def processor(items: list[int]) -> list[int]:
            processed_items.append(items)
            return items

        batch_processor: BatchProcessor[int, int] = BatchProcessor(
            batch_size=10,
            processor_func=processor,
            max_wait_time=0.1,  # Very short wait time for testing
            auto_flush=False,
        )

        await batch_processor.add(1)
        await batch_processor.add(2)

        # Wait for max wait time to expire
        await asyncio.sleep(0.15)

        result = await batch_processor.flush_if_needed()

        assert result is not None
        assert result.success_count == 2
        assert len(processed_items) == 1

    @pytest.mark.asyncio
    async def test_flush_if_needed_no_flush(self) -> None:
        """Test flush_if_needed returns None when not needed."""
        async def processor(items: list[int]) -> list[int]:
            return items

        batch_processor: BatchProcessor[int, int] = BatchProcessor(
            batch_size=10,
            processor_func=processor,
            max_wait_time=10.0,
            auto_flush=False,
        )

        await batch_processor.add(1)

        result = await batch_processor.flush_if_needed()

        assert result is None
