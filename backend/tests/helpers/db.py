"""Database test helpers."""

from typing import Any, AsyncGenerator, Type, TypeVar

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base

T = TypeVar("T", bound=Base)


async def init_test_db() -> AsyncGenerator[AsyncSession, None]:
    """Initialize a test database session.

    Yields:
        AsyncSession: Database session for testing
    """
    # Create async engine and session factory
    engine = create_async_engine(settings.ASYNC_SQLALCHEMY_DATABASE_URI, echo=False, future=True)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    # Create and yield a session
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
    """Get a test database session.

    Yields:
        AsyncSession: Database session for testing
    """
    async for session in init_test_db():
        yield session


async def clear_tables(session: AsyncSession) -> None:
    """Clear all data from the database tables.

    Args:
        session: Database session
    """
    # Get all tables in reverse order to handle dependencies
    tables = reversed(Base.metadata.sorted_tables)

    # Delete all data from tables
    for table in tables:
        await session.execute(f"DELETE FROM {table.name}")

    await session.commit()


async def create_test_instance(session: AsyncSession, model: Type[T], **data: Any) -> T:
    """Create a test instance of a model.

    Args:
        session: Database session
        model: SQLAlchemy model class
        **data: Data to create the instance with

    Returns:
        The created model instance
    """
    instance = model(**data)
    session.add(instance)
    await session.commit()
    await session.refresh(instance)
    return instance


async def get_test_instance(session: AsyncSession, model: Type[T], **filters: Any) -> T:
    """Get a test instance by filters.

    Args:
        session: Database session
        model: SQLAlchemy model class
        **filters: Filters to apply

    Returns:
        The first matching instance or None
    """
    from sqlalchemy import select

    stmt = select(model).filter_by(**filters)
    result = await session.execute(stmt)
    return result.scalars().first()


def assert_models_equal(model1: Any, model2: Any, exclude: list = None) -> None:
    """Assert that two model instances are equal.

    Args:
        model1: First model instance
        model2: Second model instance
        exclude: List of attributes to exclude from comparison
    """
    exclude = exclude or []

    # Get all column names
    columns = [c.key for c in inspect(model1).mapper.column_attrs if c.key not in exclude]

    # Compare each column
    for column in columns:
        assert getattr(model1, column) == getattr(model2, column), (
            f"{column} does not match: " f"{getattr(model1, column)} != {getattr(model2, column)}"
        )
