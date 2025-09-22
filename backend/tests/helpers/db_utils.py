"""Database utilities for testing."""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base, async_session_maker, engine
from app.db.session import get_db

T = TypeVar("T", bound=Base)


@asynccontextmanager
async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
    """Get a test database session with automatic rollback.

    Yields:
        An AsyncSession instance
    """
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create a new session
    async with async_session_maker() as session:
        # Begin a nested transaction (using SAVEPOINT)
        await session.begin_nested()

        # Override the get_db dependency
        async def override_get_db():
            try:
                yield session
            finally:
                pass  # Don't close the session here

        # Apply the override
        from app.main import app as fastapi_app

        fastapi_app.dependency_overrides[get_db] = override_get_db

        try:
            yield session
        finally:
            # Rollback the transaction
            await session.rollback()
            # Remove the override
            fastapi_app.dependency_overrides = {}

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_model_count(session: AsyncSession, model: Type[T], **filters: Any) -> int:
    """Get the count of model instances matching the filters.

    Args:
        session: Database session
        model: SQLAlchemy model class
        **filters: Filters to apply

    Returns:
        Number of matching instances
    """
    stmt = select(model).filter_by(**filters)
    result = await session.execute(stmt)
    return len(result.scalars().all())


async def get_model_by_id(
    session: AsyncSession, model: Type[T], id: Any, raise_if_not_found: bool = True
) -> Optional[T]:
    """Get a model instance by ID.

    Args:
        session: Database session
        model: SQLAlchemy model class
        id: Primary key value
        raise_if_not_found: Whether to raise an exception if not found

    Returns:
        The model instance, or None if not found and raise_if_not_found is False

    Raises:
        ValueError: If the instance is not found and raise_if_not_found is True
    """
    instance = await session.get(model, id)
    if instance is None and raise_if_not_found:
        raise ValueError(f"{model.__name__} with id {id} not found")
    return instance


async def create_model(session: AsyncSession, model: Type[T], **data: Any) -> T:
    """Create a model instance.

    Args:
        session: Database session
        model: SQLAlchemy model class
        **data: Model attributes

    Returns:
        The created model instance
    """
    instance = model(**data)
    session.add(instance)
    await session.commit()
    await session.refresh(instance)
    return instance


async def update_model(session: AsyncSession, instance: T, **data: Any) -> T:
    """Update a model instance.

    Args:
        session: Database session
        instance: Model instance to update
        **data: Attributes to update

    Returns:
        The updated model instance
    """
    for key, value in data.items():
        setattr(instance, key, value)

    session.add(instance)
    await session.commit()
    await session.refresh(instance)

    return instance


async def delete_model(session: AsyncSession, instance: T) -> None:
    """Delete a model instance.

    Args:
        session: Database session
        instance: Model instance to delete
    """
    await session.delete(instance)
    await session.commit()


async def get_or_create_model(
    session: AsyncSession,
    model: Type[T],
    defaults: Optional[dict] = None,
    **kwargs: Any,
) -> tuple[T, bool]:
    """Get or create a model instance.

    Args:
        session: Database session
        model: SQLAlchemy model class
        defaults: Default values for creation
        **kwargs: Lookup parameters

    Returns:
        A tuple of (instance, created)
    """
    stmt = select(model).filter_by(**kwargs)
    result = await session.execute(stmt)
    instance = result.scalar_one_or_none()

    if instance:
        return instance, False

    data = {**kwargs, **(defaults or {})}
    instance = model(**data)
    session.add(instance)
    await session.commit()
    await session.refresh(instance)

    return instance, True


async def refresh_model(
    session: AsyncSession, instance: T, attribute_names: Optional[list[str]] = None
) -> None:
    """Refresh model attributes from the database.

    Args:
        session: Database session
        instance: Model instance to refresh
        attribute_names: Optional list of attribute names to refresh
    """
    await session.refresh(instance, attribute_names=attribute_names)


async def execute_raw_sql(
    session: AsyncSession, sql: str, params: Optional[dict] = None
) -> Any:
    """Execute raw SQL.

    Args:
        session: Database session
        sql: SQL query
        params: Query parameters

    Returns:
        The result of the query
    """
    result = await session.execute(sql, params or {})
    return result


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


async def assert_model_exists(
    session: AsyncSession, model: Type[T], **filters: Any
) -> T:
    """Assert that a model instance exists.

    Args:
        session: Database session
        model: SQLAlchemy model class
        **filters: Filters to apply

    Returns:
        The found model instance

    Raises:
        AssertionError: If the instance does not exist
    """
    stmt = select(model).filter_by(**filters)
    result = await session.execute(stmt)
    instance = result.scalar_one_or_none()

    assert instance is not None, f"No {model.__name__} found with filters: {filters}"
    return instance


async def assert_model_not_exists(
    session: AsyncSession, model: Type[T], **filters: Any
) -> None:
    """Assert that a model instance does not exist.

    Args:
        session: Database session
        model: SQLAlchemy model class
        **filters: Filters to apply

    Raises:
        AssertionError: If the instance exists
    """
    stmt = select(model).filter_by(**filters)
    result = await session.execute(stmt)
    instance = result.scalar_one_or_none()

    assert instance is None, f"{model.__name__} found with filters: {filters}"
