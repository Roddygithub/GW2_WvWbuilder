"""Tests for build CRUD operations."""
import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.crud.build import CRUDBuild, build
from app.models import Build, Profession, User, Role, UserRole
from app.schemas.build import BuildCreate, BuildUpdate
from app.core.exceptions import (
    NotFoundException,
    ValidationException,
    DatabaseException
)

# Test data
TEST_BUILD_NAME = "Test Build"
TEST_BUILD_DESCRIPTION = "Test Description"
TEST_GAME_MODE = "pvp"
TEST_IS_PUBLIC = True
TEST_IS_VERIFIED = False
TEST_PROFESSION_IDS = [1, 2]
TEST_USER_ID = 1
TEST_BUILD_ID = 1

# Fixtures
@pytest.fixture
def build_data():
    """Return test build data."""
    return {
        "name": TEST_BUILD_NAME,
        "description": TEST_BUILD_DESCRIPTION,
        "game_mode": TEST_GAME_MODE,
        "is_public": TEST_IS_PUBLIC,
        "is_verified": TEST_IS_VERIFIED,
        "profession_ids": TEST_PROFESSION_IDS,
    }

@pytest.fixture
def mock_build():
    """Create a mock build object."""
    return Build(
        id=TEST_BUILD_ID,
        name=TEST_BUILD_NAME,
        description=TEST_BUILD_DESCRIPTION,
        game_mode=TEST_GAME_MODE,
        is_public=TEST_IS_PUBLIC,
        is_verified=TEST_IS_VERIFIED,
        created_by_id=TEST_USER_ID,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

@pytest.fixture
def mock_professions():
    """Create mock profession objects."""
    return [
        Profession(id=1, name="Warrior", icon="warrior.png"),
        Profession(id=2, name="Guardian", icon="guardian.png"),
    ]

# Test CRUDBuild class
class TestCRUDBuild:
    """Test cases for CRUDBuild class."""

    @pytest.mark.asyncio
    async def test_create_with_owner_success(self, db: Session, build_data, mock_professions):
        """Test creating a build with owner and profession associations (synchronous)."""
        # Mock the database session and query
        mock_db = MagicMock(spec=Session)
        mock_query = MagicMock()
        
        # Set up the mock to return our test professions
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value.all.return_value = mock_professions
        
        # Create the build
        result = build.create_with_owner(
            db=mock_db,
            obj_in=BuildCreate(**build_data),
            owner_id=TEST_USER_ID
        )
        
        # Verify the result
        assert result is not None
        assert result.name == TEST_BUILD_NAME
        assert result.description == TEST_BUILD_DESCRIPTION
        assert result.game_mode == TEST_GAME_MODE
        assert result.is_public == TEST_IS_PUBLIC
        assert result.created_by_id == TEST_USER_ID
        
        # Verify the database interactions
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        
        # Verify profession associations were added
        assert len(result.professions) == len(TEST_PROFESSION_IDS)
        assert all(isinstance(p, Profession) for p in result.professions)

    @pytest.mark.asyncio
    async def test_create_with_owner_invalid_profession(self, db: Session, build_data):
        """Test creating a build with invalid profession IDs."""
        # Mock the database to return no professions
        mock_db = MagicMock(spec=Session)
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value.all.return_value = []
        
        # Test with invalid profession IDs
        build_data["profession_ids"] = [999, 1000]  # Non-existent profession IDs
        
        with pytest.raises(ValidationException) as exc_info:
            build.create_with_owner(
                db=mock_db,
                obj_in=BuildCreate(**build_data),
                owner_id=TEST_USER_ID
            )
        
        assert "One or more profession IDs are invalid" in str(exc_info.value)
        mock_db.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_with_owner_db_error(self, db: Session, build_data, mock_professions):
        """Test handling of database errors during build creation."""
        # Mock the database to raise an exception on commit
        mock_db = MagicMock(spec=Session)
        mock_db.commit.side_effect = SQLAlchemyError("Database error")
        mock_db.query.return_value.filter.return_value.all.return_value = mock_professions
        
        with pytest.raises(DatabaseException) as exc_info:
            build.create_with_owner(
                db=mock_db,
                obj_in=BuildCreate(**build_data),
                owner_id=TEST_USER_ID
            )
        
        assert "Error creating build" in str(exc_info.value)
        mock_db.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_multi_by_owner(self, db: Session, mock_build):
        """Test retrieving multiple builds by owner ID."""
        # Mock the database query
        mock_db = MagicMock(spec=Session)
        mock_db.scalars.return_value.all.return_value = [mock_build]
        
        # Get builds by owner
        result = build.get_multi_by_owner(
            db=mock_db,
            owner_id=TEST_USER_ID,
            skip=0,
            limit=10
        )
        
        # Verify the result
        assert len(result) == 1
        assert result[0].id == TEST_BUILD_ID
        assert result[0].created_by_id == TEST_USER_ID
        
        # Verify the query was built correctly
        mock_db.scalars.assert_called_once()
        query = mock_db.scalars.call_args[0][0]
        assert str(query).find("WHERE builds.created_by_id") > 0
        assert str(query).find("LIMIT :param_1") > 0
        assert str(query).find("OFFSET :param_2") > 0

    @pytest.mark.asyncio
    async def test_update_with_professions_success(self, db: Session, mock_build, mock_professions):
        """Test updating a build with new profession associations."""
        # Mock the database session and queries
        mock_db = MagicMock(spec=Session)
        
        # Mock build query
        mock_build_query = MagicMock()
        mock_build_query.filter.return_value.first.return_value = mock_build
        
        # Mock profession query
        mock_profession_query = MagicMock()
        mock_profession_query.filter.return_value.all.return_value = mock_professions
        
        # Configure the mock_db to return different queries based on the model
        def query_side_effect(model, *args, **kwargs):
            if model == Build:
                return mock_build_query
            elif model == Profession:
                return mock_profession_query
            return MagicMock()
        
        mock_db.query.side_effect = query_side_effect
        
        # Update data
        update_data = {
            "name": "Updated Build Name",
            "description": "Updated Description",
            "profession_ids": [2, 3]  # Change one profession
        }
        
        # Perform the update
        result = await build.update_with_professions_async(
            db=mock_db,
            db_obj=mock_build,
            obj_in=BuildUpdate(**update_data)
        )
        
        # Verify the result
        assert result is not None
        assert result.name == update_data["name"]
        assert result.description == update_data["description"]
        assert len(result.professions) == len(update_data["profession_ids"])
        
        # Verify the database interactions
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_build)

    @pytest.mark.asyncio
    async def test_delete(self, db: Session, mock_build):
        """Test deleting a build."""
        # Mock the database session
        mock_db = MagicMock(spec=Session)
        
        # Perform the deletion
        result = build.remove(db=mock_db, id=TEST_BUILD_ID)
        
        # Verify the result
        assert result == 1  # Number of rows affected
        
        # Verify the database interactions
        mock_db.query.assert_called_once_with(Build)
        mock_db.query.return_value.filter.return_value.delete.assert_called_once()
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_public_builds(self, db: Session, mock_build):
        """Test retrieving public builds."""
        # Mock the database query
        mock_db = MagicMock(spec=Session)
        mock_db.scalars.return_value.all.return_value = [mock_build]
        
        # Get public builds
        result = build.get_public_builds(
            db=mock_db,
            skip=0,
            limit=10
        )
        
        # Verify the result
        assert len(result) == 1
        assert result[0].is_public is True
        
        # Verify the query was built correctly
        mock_db.scalars.assert_called_once()
        query = mock_db.scalars.call_args[0][0]
        assert str(query).find("WHERE builds.is_public = 1") > 0

# Test the build instance
class TestBuildInstance:
    """Test cases for the build instance."""
    
    @pytest.mark.asyncio
    async def test_build_instance_creation(self):
        """Test that the build instance is created correctly."""
        assert isinstance(build, CRUDBuild)
        assert build.model == Build

    @pytest.mark.asyncio
    async def test_build_instance_methods(self):
        """Test that the build instance has the expected methods."""
        assert hasattr(build, "create_with_owner")
        assert hasattr(build, "get_multi_by_owner")
        assert hasattr(build, "get_public_builds")
        assert hasattr(build, "update_with_professions_async")
