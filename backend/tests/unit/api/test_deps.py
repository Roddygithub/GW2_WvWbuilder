"""Unit tests for API dependencies in app.api.deps and app.db.dependencies."""

import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db


@pytest.mark.asyncio
async def test_get_db_dependency_success():
    """
    Test that the get_db dependency yields a session and closes it.
    """
    # Mock the SessionLocal to track session creation and closing
    mock_session = AsyncMock(spec=AsyncSession)

    with patch("app.db.dependencies.SessionLocal", return_value=mock_session) as mock_session_local:
        # Simulate the dependency injection process
        async def run_dependency():
            gen = get_db()
            try:
                session = await gen.__anext__()
                assert session is mock_session
                # This part simulates the request handling
            except StopAsyncIteration:
                pass  # Generator finished

        await run_dependency()

        # Verify that a session was created and closed
        mock_session_local.assert_called_once()
        mock_session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_db_dependency_with_exception():
    """Test that the get_db dependency closes the session even if an error occurs."""
    mock_session = AsyncMock(spec=AsyncSession)
    with patch("app.db.dependencies.SessionLocal", return_value=mock_session):
        with pytest.raises(RuntimeError):
            async for session in get_db():
                raise RuntimeError("Simulating error during request")

        mock_session.close.assert_awaited_once()
