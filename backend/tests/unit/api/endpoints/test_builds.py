"""Tests for build endpoints."""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import AsyncMock, patch, MagicMock
import pytest

from app.main import app as original_app
from app.core.config import settings
from app import schemas
from app.crud import build_crud, user_crud
from app.api.deps import get_current_user, get_db
from app.models import User, Build

# Create a test app with overridden dependencies
def create_test_app():
    test_app = FastAPI()
    test_app.include_router(original_app.router)
    
    # Override the get_current_user dependency for testing
    async def override_get_current_user():
        return test_user
    
    # Apply the overrides
    test_app.dependency_overrides[get_current_user] = override_get_current_user
    
    return test_app

# Create test client with the test app
test_app = create_test_app()
client = TestClient(test_app)

# Test authentication headers
AUTH_HEADERS = {"Authorization": "Bearer x"}  # 'x' is a special test token

# Test data
test_user = User(
    id=1,
    email="test@example.com",
    hashed_password="hashed_password",
    is_active=True,
    is_superuser=False,
)

test_build = Build(
    id=1,
    name="Test Build",
    description="Test Description",
    game_mode="wvw",
    team_size=5,
    is_public=True,
    created_by_id=1,
    config={
        "weapons": ["Greatsword", "Axe", "Mace"],
        "traits": ["Strength", "Discipline", "Berserker"],
        "skills": ["Blood Reckoning", "Head Butt"]
    }
)


@pytest.fixture
def mock_current_user():
    """Mock the current user."""
    return test_user


@pytest.fixture
def mock_db_session():
    """Mock the database session and CRUD operations."""
    with patch('app.api.deps.SessionLocal') as mock_session_local, \
         patch('app.crud.build_crud') as mock_build_crud, \
         patch('app.crud.user_crud') as mock_user_crud:
        
        # Configure the mock session
        mock_session = AsyncMock()
        mock_session_local.return_value = mock_session
        
        # Configure the user CRUD mock
        mock_user_crud.get.return_value = test_user
        
        # Configure the build CRUD mock to return coroutines
        mock_build_crud.get = AsyncMock(return_value=test_build)
        mock_build_crud.get_multi_by_owner = AsyncMock(return_value=[test_build])
        mock_build_crud.create_with_owner = AsyncMock(return_value=test_build)
        mock_build_crud.update = AsyncMock(return_value=test_build)
        mock_build_crud.remove = AsyncMock(return_value=test_build)
        
        # Configure the mock session for async operations
        mock_session.execute.return_value = mock_session
        mock_session.scalars.return_value = mock_session
        mock_session.first = AsyncMock(return_value=None)
        mock_session.add = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        mock_session.close = AsyncMock()
        
        # For the test that checks for duplicate names
        mock_build_crud.get_by_name = AsyncMock(return_value=test_build)
        
        yield mock_session


@pytest.mark.asyncio
async def test_create_build(mock_db_session, mock_current_user):
    """Test creating a new build."""
    # Mock the CRUD operations
    mock_db_session.execute.return_value.scalars.return_value.first.return_value = None
    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.return_value = None
    
    # Test data
    build_data = {
        "name": "New Build",
        "description": "New Description",
        "game_mode": "wvw",
        "team_size": 5,
        "is_public": True,
        "config": {
            "weapons": ["Axe", "Shield"],
            "traits": ["Radiance", "Honor", "Firebrand"],
            "skills": ["Mantra of Potence", "Mantra of Solace"]
        },
        "profession_ids": [1, 2]
    }
    
    # Make the request with a valid test token
    response = client.post(
        f"{settings.API_V1_STR}/builds/",
        json=build_data,
        headers={"Authorization": "Bearer x"}  # 'x' is a special test token
    )
    
    # Assertions
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == build_data["name"]
    assert data["game_mode"] == build_data["game_mode"]
    assert data["team_size"] == build_data["team_size"]


@pytest.mark.asyncio
async def test_read_builds(mock_db_session, mock_current_user):
    """Test reading a list of builds."""
    # Mock the CRUD operations
    mock_build = MagicMock()
    mock_build.owner_id = test_user.id
    mock_db_session.execute.return_value.scalars.return_value.all.return_value = [test_build]
    
    # Make the request with test authentication
    response = client.get(
        f"{settings.API_V1_STR}/builds/",
        headers=AUTH_HEADERS
    )
    
    # Assertions
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == test_build.name


@pytest.mark.asyncio
async def test_read_build(mock_db_session, mock_current_user):
    """Test reading a single build."""
    # Mock the CRUD operations
    mock_db_session.execute.return_value.scalars.return_value.first.return_value = test_build
    
    # Make the request with test authentication
    response = client.get(
        f"{settings.API_V1_STR}/builds/1",
        headers=AUTH_HEADERS
    )
    
    # Assertions
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_build.id
    assert data["name"] == test_build.name


@pytest.mark.asyncio
async def test_update_build(mock_db_session, mock_current_user):
    """Test updating a build."""
    # Mock the CRUD operations
    mock_db = AsyncMock()
    mock_db.execute.return_value.scalars.return_value.first.return_value = test_build
    
    # Test data
    update_data = {"name": "Updated Build Name"}
    
    # Make the request with test authentication
    response = client.put(
        f"{settings.API_V1_STR}/builds/1",
        json=update_data,
        headers=AUTH_HEADERS
    )
    
    # Assertions
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]


@pytest.mark.asyncio
async def test_delete_build(mock_db_session, mock_current_user):
    """Test deleting a build."""
    # Mock the CRUD operations
    mock_db_session.execute.return_value.scalars.return_value.first.return_value = test_build
    
    # Make the request with test authentication
    response = client.delete(
        f"{settings.API_V1_STR}/builds/1",
        headers=AUTH_HEADERS
    )
    
    # Assertions
    assert response.status_code == status.HTTP_204_NO_CONTENT


# Error case tests

@pytest.mark.asyncio
async def test_create_build_duplicate_name(mock_db_session, mock_current_user):
    """Test creating a build with a duplicate name."""
    # Mock the CRUD operations to return an existing build
    mock_db_session.execute.return_value.scalars.return_value.first.return_value = test_build
    
    # Test data with duplicate name
    build_data = {
        "name": test_build.name,
        "description": "Duplicate build",
        "game_mode": "wvw",
        "team_size": 5,
        "is_public": True,
        "config": {
            "weapons": ["Sword", "Focus"],
            "traits": ["Zeal", "Radiance", "Dragonhunter"],
            "skills": ["Procession of Blades", "Sword of Justice"]
        },
        "profession_ids": [1, 3]
    }
    
    # Make the request with a valid test token
    response = client.post(
        f"{settings.API_V1_STR}/builds/",
        json=build_data,
        headers={"Authorization": "Bearer x"}  # 'x' is a special test token
    )
    
    # Assertions
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_read_nonexistent_build(mock_db_session, mock_current_user):
    """Test reading a build that doesn't exist."""
    # Mock the CRUD operations to return None
    mock_db_session.execute.return_value.scalars.return_value.first.return_value = None
    
    # Make the request with a valid test token
    response = client.get(
        f"{settings.API_V1_STR}/builds/999",
        headers={"Authorization": "Bearer x"}  # 'x' is a special test token
    )
    
    # Assertions
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Build not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_nonexistent_build(mock_db_session, mock_current_user):
    """Test updating a build that doesn't exist."""
    # Mock the CRUD operations to return None
    mock_db_session.execute.return_value.scalars.return_value.first.return_value = None
    
    # Test data
    update_data = {"name": "Nonexistent Build"}
    
    # Make the request with a valid test token
    response = client.put(
        f"{settings.API_V1_STR}/builds/999",
        json=update_data,
        headers={"Authorization": "Bearer x"}  # 'x' is a special test token
    )
    
    # Assertions
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Build not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_nonexistent_build(mock_db_session, mock_current_user):
    """Test deleting a build that doesn't exist."""
    # Mock the CRUD operations to return None
    mock_db_session.execute.return_value.scalars.return_value.first.return_value = None
    
    # Make the request with a valid test token
    response = client.delete(
        f"{settings.API_V1_STR}/builds/999",
        headers={"Authorization": "Bearer x"}  # 'x' is a special test token
    )
    
    # Assertions
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Build not found" in response.json()["detail"]
