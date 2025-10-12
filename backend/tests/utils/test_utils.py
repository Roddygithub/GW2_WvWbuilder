"""Test utilities and helpers for the test suite."""

from typing import Any, Dict, Optional, Type, TypeVar
from unittest.mock import MagicMock, AsyncMock

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

T = TypeVar("T")


def create_mock_result(return_value: Any, is_list: bool = False, scalar: bool = False) -> MagicMock:
    """Create a mock SQLAlchemy result object.

    Args:
        return_value: The value to return.
        is_list: If True, mock a list result.
        scalar: If True, mock a scalar result.

    Returns:
        A MagicMock configured as a SQLAlchemy result.
    """
    mock_result = MagicMock()

    if scalar:
        mock_result.scalar.return_value = return_value
    elif is_list:
        mock_result.scalars.return_value.all.return_value = return_value
    else:
        mock_result.scalars.return_value.first.return_value = return_value

    return mock_result


async def create_test_instance(session: AsyncSession, model: Type[T], **data: Any) -> T:
    """Create a test instance of a model.

    Args:
        session: The database session.
        model: The SQLAlchemy model class.
        **data: The data to create the instance with.

    Returns:
        The created model instance.
    """
    instance = model(**data)
    session.add(instance)
    await session.commit()
    await session.refresh(instance)
    return instance


async def get_test_instance(session: AsyncSession, model: Type[T], **filters: Any) -> Optional[T]:
    """Get a test instance by filters.

    Args:
        session: The database session.
        model: The SQLAlchemy model class.
        **filters: The filters to apply.

    Returns:
        The first matching instance or None.
    """
    stmt = select(model).filter_by(**filters)
    result = await session.execute(stmt)
    return result.scalars().first()


def assert_dict_contains_subset(actual: Dict[str, Any], expected: Dict[str, Any], path: str = "") -> None:
    """Assert that a dictionary contains a subset of key-value pairs.

    Args:
        actual: The actual dictionary to check.
        expected: The expected key-value pairs.
        path: The current path in the dictionary (used for error messages).

    Raises:
        AssertionError: If the actual dictionary does not contain all expected key-value pairs.
    """
    for key, expected_value in expected.items():
        full_path = f"{path}.{key}" if path else key
        assert key in actual, f"Key '{full_path}' not found in actual dictionary"

        actual_value = actual[key]

        if isinstance(expected_value, dict):
            assert isinstance(
                actual_value, dict
            ), f"Expected '{full_path}' to be a dictionary, got {type(actual_value).__name__}"
            assert_dict_contains_subset(actual_value, expected_value, full_path)
        else:
            assert actual_value == expected_value, (
                f"Value mismatch for '{full_path}': " f"expected {expected_value!r}, got {actual_value!r}"
            )


class AsyncContextManagerMock(AsyncMock):
    """Async context manager mock for testing async context managers."""

    async def __aenter__(self):
        return self.aenter

    async def __aexit__(self, *args):
        pass
