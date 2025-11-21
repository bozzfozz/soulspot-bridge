"""Pagination schemas for API responses."""

from typing import TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Query parameters for pagination."""

    page: int = Field(default=1, ge=1, description="Page number (starts at 1)")
    page_size: int = Field(
        default=20, ge=1, le=100, description="Number of items per page"
    )

    # Hey future me, this calculates SQL OFFSET from page number. Page 1 = skip 0, page 2 = skip 20, etc.
    # The math is (page - 1) * page_size. This is OFFSET-based pagination which has problems at scale -
    # if data changes between page fetches, you can skip rows or see duplicates! For large datasets or
    # real-time data, use cursor-based pagination instead. But for small/medium datasets, OFFSET is simple.
    @property
    def skip(self) -> int:
        """Calculate number of records to skip."""
        return (self.page - 1) * self.page_size

    # Yo, this is just a convenience alias - limit = page_size. SQL queries use LIMIT, so this makes
    # the code read nicer: `query.offset(params.skip).limit(params.limit)` instead of mixing skip/page_size.
    # It's the same number, just better naming for database queries!
    @property
    def limit(self) -> int:
        """Get the limit (same as page_size)."""
        return self.page_size


class PaginatedResponse[T](BaseModel):
    """Generic paginated response model."""

    items: list[T] = Field(description="List of items for current page")
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Number of items per page")
    pages: int = Field(description="Total number of pages")

    # Hey, this is the factory method for creating paginated responses. The pages calculation uses ceiling
    # division: (total + page_size - 1) // page_size. Why the weird math? To round UP without float division.
    # Example: 25 items, 10 per page = 3 pages (not 2.5!). The page_size > 0 check prevents division by zero
    # (returns 0 pages if page_size is somehow 0, which shouldn't happen due to validation but defensive code!).
    # This is used like: PaginatedResponse.create(items, total, page, page_size) in your endpoints.
    @classmethod
    def create(
        cls, items: list[T], total: int, page: int, page_size: int
    ) -> "PaginatedResponse[T]":
        """Create a paginated response."""
        pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )
