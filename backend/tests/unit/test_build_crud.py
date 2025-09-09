import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.crud.build import CRUDBuild
from app.models import Build, Profession, build_profession
from app.schemas.build import BuildCreate, BuildUpdate
from app.core.config import settings


@pytest.fixture
def mock_db_session():
    """Create a mock SQLAlchemy session."""
    # Create a mock session
    session = MagicMock(spec=Session)
    
    # Create a mock query object
    mock_query = MagicMock()
    
    # Set up the query chain
    session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    
    # Set up the scalars chain
    mock_result = MagicMock()
    session.scalars.return_value = mock_result
    
    # Set up the all() return value
    mock_result.all.return_value = []
    
    return session, mock_query, mock_result

def test_create_with_owner_success(mock_db_session):
    session, mock_query, _ = mock_db_session
    """Test successful build creation with owner and profession associations."""
    # Setup
    crud = CRUDBuild(Build)
    owner_id = 1
    profession_ids = [1, 2, 3]
    build_data = {
        "name": "Test Build",
        "description": "A test build",
        "game_mode": "wvw",
        "team_size": 5,
        "is_public": True,
        "config": {"test": "config"},
        "constraints": {"test": "constraints"},
        "profession_ids": profession_ids
    }
    build_in = BuildCreate(**build_data)
    
    # Mock database operations - create a mock profession for each ID
    mock_professions = []
    for prof_id in profession_ids:
        mock_prof = MagicMock(spec=Profession)
        mock_prof.id = prof_id
        mock_professions.append(mock_prof)
    
    # Mock the query to return our mock professions
    mock_query.all.return_value = mock_professions
    
    # Create a mock for the build object that will be returned
    mock_build = MagicMock(spec=Build)
    mock_build.id = 1
    mock_build.professions = mock_professions
    
    # Execute
    result = crud.create_with_owner(session, obj_in=build_in, owner_id=owner_id)
    
    # Assert
    assert result is not None
    assert result.id == 1
    assert len(result.professions) == 3
    session.add.assert_called_once()
    session.commit.assert_called_once()
    session.refresh.assert_called_once()


def test_create_with_owner_missing_professions(mock_db_session):
    session, mock_query, _ = mock_db_session
    """Test build creation when referenced professions don't exist."""
    # Setup
    crud = CRUDBuild(Build)
    owner_id = 1
    build_data = {
        "name": "Test Build",
        "game_mode": "wvw",
        "team_size": 5,
        "is_public": True,
        "config": {},
        "constraints": {},
        "profession_ids": [999]  # Non-existent profession
    }
    build_in = BuildCreate(**build_data)
    
    # Mock database to return no professions
    mock_query.all.return_value = []
    
    # Execute & Assert
    with pytest.raises(ValueError) as exc_info:
        crud.create_with_owner(session, obj_in=build_in, owner_id=owner_id)
    
    assert "do not exist" in str(exc_info.value)
    session.rollback.assert_called_once()


def test_create_with_owner_database_error(mock_db_session):
    session, mock_query, _ = mock_db_session
    """Test error handling during build creation."""
    # Setup
    crud = CRUDBuild(Build)
    owner_id = 1
    build_data = {
        "name": "Test Build",
        "game_mode": "wvw",
        "team_size": 5,
        "is_public": True,
        "config": {},
        "constraints": {},
        "profession_ids": [1, 2, 3]
    }
    build_in = BuildCreate(**build_data)
    
    # Mock database operations
    mock_profession = MagicMock(spec=Profession)
    mock_profession.id = 1
    mock_query.all.return_value = [mock_profession] * 3
    
    # Force a database error
    session.commit.side_effect = SQLAlchemyError("Database error")
    
    # Execute & Assert
    with pytest.raises(ValueError) as exc_info:
        crud.create_with_owner(session, obj_in=build_in, owner_id=owner_id)
    
    assert "Failed to create build" in str(exc_info.value)
    session.rollback.assert_called_once()


def test_get_multi_by_owner(mock_db_session):
    """Test retrieving multiple builds by owner ID."""
    session, _, mock_result = mock_db_session
    
    # Setup
    crud = CRUDBuild(Build)
    owner_id = 1
    mock_builds = [MagicMock(spec=Build), MagicMock(spec=Build)]
    mock_result.all.return_value = mock_builds
    
    # Execute
    result = crud.get_multi_by_owner(session, owner_id=owner_id)
    
    # Assert
    assert len(result) == 2
    session.scalars.assert_called_once()


def test_get_public_builds(mock_db_session):
    """Test retrieving public builds."""
    session, _, mock_result = mock_db_session
    
    # Setup
    crud = CRUDBuild(Build)
    mock_builds = [MagicMock(spec=Build, is_public=True), MagicMock(spec=Build, is_public=True)]
    mock_result.all.return_value = mock_builds
    
    # Execute
    result = crud.get_public_builds(session)
    
    # Assert
    assert len(result) == 2
    session.scalars.assert_called_once()


# Add more test cases for other CRUD operations as needed
