"""Database session management."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from soulspot.config import Settings


class Database:
    """Database connection and session manager."""

    def __init__(self, settings: Settings) -> None:
        """Initialize database with settings."""
        self.settings = settings

        # Configure connection pool for PostgreSQL
        engine_kwargs: dict[str, Any] = {
            "echo": settings.database.echo,
            "pool_pre_ping": settings.database.pool_pre_ping,
        }

        # Only apply pool settings for PostgreSQL
        if "postgresql" in settings.database.url:
            engine_kwargs.update(
                {
                    "pool_size": settings.database.pool_size,
                    "max_overflow": settings.database.max_overflow,
                    "pool_timeout": settings.database.pool_timeout,
                    "pool_recycle": settings.database.pool_recycle,
                }
            )

        self._engine = create_async_engine(
            settings.database.url,
            **engine_kwargs,
        )
        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session."""
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    @asynccontextmanager
    async def session_scope(self) -> AsyncGenerator[AsyncSession, None]:
        """Provide a transactional scope for database operations."""
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def close(self) -> None:
        """Close database connection."""
        await self._engine.dispose()

    async def create_tables(self) -> None:
        """Create all tables (for testing only)."""
        from soulspot.infrastructure.persistence.models import Base

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self) -> None:
        """Drop all tables (for testing only)."""
        from soulspot.infrastructure.persistence.models import Base

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    def get_pool_stats(self) -> dict[str, Any]:
        """Get connection pool statistics for monitoring.

        Returns:
            Dictionary with pool statistics including size, checked out connections, etc.
            Returns empty dict for SQLite as it doesn't use connection pooling.
        """
        # Pool stats only available for databases that use connection pooling
        if "sqlite" in self.settings.database.url:
            return {
                "pool_type": "sqlite",
                "note": "SQLite does not use connection pooling",
            }

        pool = self._engine.pool
        # Note: Pool statistics methods may not be available on all pool types
        # Using getattr with defaults to handle this safely
        return {
            "pool_size": getattr(pool, "size", lambda: 0)(),
            "checked_out": getattr(pool, "checkedout", lambda: 0)(),
            "overflow": getattr(pool, "overflow", lambda: 0)(),
            "checked_in": getattr(pool, "checkedin", lambda: 0)(),
            "pool_timeout": self.settings.database.pool_timeout,
            "pool_recycle": self.settings.database.pool_recycle,
            "max_overflow": self.settings.database.max_overflow,
        }
