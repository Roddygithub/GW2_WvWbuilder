"""Unit tests for API dependencies in app.api.deps and app.db.dependencies."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_async_db as get_db


@pytest.mark.asyncio
async def test_get_db_dependency_success():
    """
    Test that the get_db dependency yields a session and closes it.
    """
    # Mock the AsyncSessionLocal context manager
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session_local = MagicMock()
    mock_session_local.return_value.__aenter__.return_value = mock_session
    mock_session_local.return_value.__aexit__.return_value = None

    with patch("app.db.dependencies.AsyncSessionLocal", mock_session_local):
        # Simulate the dependency injection process
        gen = get_db()
        session = await gen.__anext__()
        assert session is mock_session

        # Close the generator
        try:
            await gen.__anext__()
        except StopAsyncIteration:
            pass  # Expected

        # Verify that a session was created
        mock_session_local.assert_called_once()


@pytest.mark.asyncio
async def test_get_db_dependency_with_exception():
    """Test that the get_db dependency handles exceptions properly."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session_local = MagicMock()
    mock_session_local.return_value.__aenter__.return_value = mock_session
    mock_session_local.return_value.__aexit__.return_value = None

    with patch("app.db.dependencies.AsyncSessionLocal", mock_session_local):
        with pytest.raises(RuntimeError):
            gen = get_db()
            session = await gen.__anext__()
            # Simulate an error during request processing
            await gen.athrow(RuntimeError("Simulating error during request"))

        # Verify rollback was called
        mock_session.rollback.assert_awaited_once()
