import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, timezone
from app.crud.build import CRUDBuild
from app.models.base_models import Build

def test_get_multi_by_owner():
    """Test retrieving multiple builds by owner ID."""
    # Create mock session and scalars result
    session = MagicMock()
    mock_scalars = MagicMock()
    
    # Set up the mock session to return our mock scalars
    session.scalars.return_value = mock_scalars
    
    # Set up the result
    owner_id = 1
    mock_builds = [
        MagicMock(
            spec=Build,
            id=1,
            name="Build 1",
            game_mode="wvw",
            team_size=5,
            is_public=True,
            created_by_id=owner_id,
            config={"key": "value"},
            constraints={"max_players": 5},
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ),
        MagicMock(
            spec=Build,
            id=2,
            name="Build 2",
            game_mode="wvw",
            team_size=5,
            is_public=False,
            created_by_id=owner_id,
            config={"key": "value"},
            constraints={"max_players": 5},
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
    ]
    mock_scalars.all.return_value = mock_builds
    
    # Initialize CRUD
    crud = CRUDBuild(Build)
    
    # Test with default pagination
    result = crud.get_multi_by_owner(session, owner_id=owner_id)
    
    # Assertions
    assert len(result) == 2
    # Check that the returned objects have the expected attributes
    assert hasattr(result[0], 'id')
    assert hasattr(result[0], 'name')
    assert hasattr(result[0], 'game_mode')
    assert hasattr(result[1], 'id')
    assert hasattr(result[1], 'name')
    assert hasattr(result[1], 'game_mode')
    
    # Verify the query was constructed correctly
    session.scalars.assert_called_once()
    # Get the select statement that was passed to scalars()
    stmt = session.scalars.call_args[0][0]
    # Verify the where clause - using 'builds' as that's the actual table name
    assert str(stmt.whereclause) == "builds.created_by_id = :created_by_id_1"
    # Verify the offset and limit
    # SQLAlchemy stores offset and limit as callables in this context
    assert stmt._offset == 0  # Default offset
    assert stmt._limit == 100  # Default limit
    
    # Test with custom pagination
    session.scalars.reset_mock()
    
    skip = 10
    limit = 20
    result = crud.get_multi_by_owner(session, owner_id=owner_id, skip=skip, limit=limit)
    
    # Verify the query was constructed with custom pagination
    session.scalars.assert_called_once()
    stmt = session.scalars.call_args[0][0]
    assert stmt._offset == skip
    assert stmt._limit == limit
