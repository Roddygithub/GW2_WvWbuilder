"""Tests for database base module."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

# Import the module/class to test
from app.database.base import SessionLocal, get_db

# Test cases
def test_session_local_initialization():
    """Test that SessionLocal is properly initialized."""
    from sqlalchemy.orm import sessionmaker
    
    # Check that SessionLocal is a sessionmaker instance
    assert SessionLocal is not None
    assert isinstance(SessionLocal, sessionmaker)
    
    # Check session configuration
    assert SessionLocal.kw['autocommit'] is False
    assert SessionLocal.kw['autoflush'] is False

def test_get_db():
    """Test that get_db yields a database session and closes it properly."""
    # Mock the SessionLocal
    mock_session = MagicMock()
    with patch('app.database.base.SessionLocal', return_value=mock_session):
        # Get the generator
        db_gen = get_db()
        
        # Get the session
        db = next(db_gen)
        
        # Check the session was created
        assert db is mock_session
        
        # Check that the session is closed when done
        try:
            next(db_gen)
        except StopIteration:
            pass
            
        # Verify close was called
        db.close.assert_called_once()
