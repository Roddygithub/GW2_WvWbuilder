"""Tests for database session management."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# Import the module/class to test
from app.db.session import get_async_db, ASYNC_DATABASE_URL, AsyncSessionLocal

# Test cases
@pytest.mark.asyncio
async def test_async_session_initialization():
    """Test that async session can be initialized."""
    # Create a test async engine
    test_engine = create_async_engine(
        ASYNC_DATABASE_URL,
        echo=False
    )
    
    # Test getting a session using the actual AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        assert isinstance(session, AsyncSession)
        assert session.is_active

@pytest.mark.asyncio
async def test_get_async_db():
    """Test the get_async_db dependency."""
    # Create a mock session
    mock_session = AsyncMock(spec=AsyncSession)
    
    # Create a mock context manager that returns our mock session
    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_session
    
    # Patch the AsyncSessionLocal to return our mock context
    with patch('app.db.session.AsyncSessionLocal', return_value=mock_context) as mock_session_maker:
        # Call the get_async_db generator
        gen = get_async_db()
        db = await gen.__anext__()
        
        # Verify the session was created and yielded
        assert db is mock_session
        
        # Test that the session is properly closed
        with pytest.raises(StopAsyncIteration):
            await gen.__anext__()
        
        # Verify session was committed and closed
        mock_session.commit.assert_awaited_once()
        mock_session.close.assert_awaited_once()
