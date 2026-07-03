"""Database connection and session management."""

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

async_session_factory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session and ensure it is closed afterwards."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables (development only)."""
    from app.models.base import Base  # noqa: F401
    import app.models.component_check  # noqa: F401
    import app.models.component_template  # noqa: F401
    import app.models.evaluation_standard  # noqa: F401
    import app.models.evaluation_standard_knowledge  # noqa: F401
    import app.models.report_signature  # noqa: F401
    import app.models.report_template  # noqa: F401
    import app.models.structural_test_result  # noqa: F401
    import app.models.survey  # noqa: F401
    import app.models.test_image  # noqa: F401
    import app.models.user  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
