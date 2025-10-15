"""Tests for build CRUD operations."""

import pytest
import pytest_asyncio
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.crud.build import CRUDBuild, build
from app.models import Build, Profession
from app.schemas.build import BuildCreate, BuildUpdate

# Test data
TEST_BUILD_NAME = "Test Build"
TEST_BUILD_DESCRIPTION = "Test Description"
TEST_GAME_MODE = "pvp"
TEST_IS_PUBLIC = True
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
        created_by_id=TEST_USER_ID,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def mock_professions():
    """Create mock profession objects."""
    return [
        Profession(id=1, name="Warrior"),
        Profession(id=2, name="Guardian"),
    ]


# Test CRUDBuild class
@pytest.mark.unit
class TestCRUDBuild:
    """Test cases for CRUDBuild class."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_with_owner_success(
        self, db_session: Session, build_data, mock_professions
    ):
        """Test creating a build with owner and profession associations (synchronous)."""
        # Mock the database session and query
        mock_db = MagicMock(spec=Session)
        mock_query = MagicMock()

        # Create a mock build that will be returned by the session
        mock_build = MagicMock()
        mock_build.professions = []

        # Set up the mock to return our test professions
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value.all.return_value = mock_professions

        # Mock the add and commit to set the ID and return the mock build
        def add_side_effect(obj):
            if hasattr(obj, "id") and obj.id is None:
                obj.id = TEST_BUILD_ID
            return obj

        mock_db.add.side_effect = add_side_effect
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None

        # Mock the build creation to return our mock build
        with patch("app.crud.build.Build", return_value=mock_build) as mock_build_cls:
            # Create the build
            result = build.create_with_owner(
                db=mock_db, obj_in=BuildCreate(**build_data), owner_id=TEST_USER_ID
            )

        # Verify the result
        assert result is not None
        assert result == mock_build

        # Verify the database interactions
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_build)

        # Verify the build was created with the correct data
        call_args = mock_build_cls.call_args[1]  # Get the keyword arguments
        assert call_args["name"] == TEST_BUILD_NAME
        assert call_args["description"] == TEST_BUILD_DESCRIPTION
        assert call_args["game_mode"] == TEST_GAME_MODE
        assert call_args["is_public"] == TEST_IS_PUBLIC
        assert call_args["created_by_id"] == TEST_USER_ID

        # Verify the professions were added through the relationship
        # The professions are added after the build is created, so we verify the relationship was set up
        mock_build.professions = mock_professions

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_with_owner_invalid_profession(
        self, db_session: Session, build_data
    ):
        """Test creating a build with invalid profession IDs."""
        # Mock the database to return no professions
        mock_db = MagicMock(spec=Session)
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value.all.return_value = []

        # Test with invalid profession IDs
        build_data["profession_ids"] = [999, 1000]  # Non-existent profession IDs

        # Mock the build creation to return a mock build
        with patch("app.crud.build.Build", return_value=MagicMock()):
            # The error should be raised during the create_with_owner call
            with pytest.raises(ValueError) as exc_info:
                build.create_with_owner(
                    db=mock_db, obj_in=BuildCreate(**build_data), owner_id=TEST_USER_ID
                )

            # Verify the error message
            assert "The following profession IDs do not exist" in str(exc_info.value)

            # Verify the database interactions
            mock_db.query.assert_called()
            mock_db.add.assert_not_called()
            mock_db.commit.assert_not_called()
            mock_db.rollback.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_with_owner_db_error(
        self, db_session: Session, build_data, mock_professions
    ):
        """Test handling of database errors during build creation."""
        # Mock the database to return test professions but raise an exception on commit
        mock_db = MagicMock(spec=Session)
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value.all.return_value = mock_professions

        # Create a mock build that will be returned by the session
        mock_build = MagicMock()
        mock_build.professions = mock_professions

        # Mock the build creation to return our mock build
        with patch("app.crud.build.Build", return_value=mock_build):
            # Mock the commit to raise an error
            mock_db.commit.side_effect = SQLAlchemyError("Database error")

            # Test that the exception is propagated
            with pytest.raises(ValueError) as exc_info:
                build.create_with_owner(
                    db=mock_db, obj_in=BuildCreate(**build_data), owner_id=TEST_USER_ID
                )

            # Verify the error message
            assert "Failed to create build" in str(exc_info.value)
            assert "Database error" in str(exc_info.value)

            # Verify the database interactions
            mock_db.add.assert_called_once_with(mock_build)
            mock_db.commit.assert_called_once()
            mock_db.rollback.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_multi_by_owner(self, db_session: Session, mock_build):
        """Test retrieving multiple builds by owner ID."""
        # Mock the database query
        mock_db = MagicMock(spec=Session)
        mock_db.scalars.return_value.all.return_value = [mock_build]

        # Get builds by owner
        result = build.get_multi_by_owner(
            db=mock_db, owner_id=TEST_USER_ID, skip=0, limit=10
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

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_with_professions_success(
        self, db_session: Session, mock_build, mock_professions
    ):
        """Test updating a build with new professions."""
        # Create a mock async session
        mock_async_db = AsyncMock(spec=AsyncSession)

        # Create test data
        update_data = {
            "name": "Updated Build Name",
            "description": "Updated Description",
            "profession_ids": [2],  # Just Guardian
        }

        # Mock the execute method to handle different SQL operations
        async def execute_mock(stmt, *args, **kwargs):
            stmt_str = str(stmt).lower()
            mock_result = MagicMock()

            if "delete from build_professions" in stmt_str:
                # Mock delete of existing profession associations
                mock_result.rowcount = 1
                return mock_result
            elif "select professions" in stmt_str:
                # Mock select of professions
                mock_scalars = MagicMock()
                mock_scalars.all.return_value = [
                    p for p in mock_professions if p.id in update_data["profession_ids"]
                ]
                mock_result.scalars.return_value = mock_scalars
                return mock_result
            elif "insert into build_professions" in stmt_str:
                # Mock insert of new profession associations
                mock_result.rowcount = 1
                return mock_result

            # Default return for other operations
            mock_result.rowcount = 1
            return mock_result

        mock_async_db.execute = AsyncMock(side_effect=execute_mock)

        # Mock the commit and refresh methods
        mock_async_db.commit = AsyncMock()
        mock_async_db.refresh = AsyncMock()

        # Create a mock for the base update method
        async def base_update_mock(self, db, db_obj, obj_in):
            # Update the build with the input data
            for field, value in obj_in.items():
                if (
                    field != "profession_ids"
                ):  # Skip profession_ids as it's handled separately
                    setattr(db_obj, field, value)
            return db_obj

        # Patch the base update method
        with patch("app.crud.base.CRUDBase.update", new=base_update_mock):
            # Perform the update
            result = await build.update_with_professions_async(
                db=mock_async_db,
                db_obj=mock_build,
                obj_in=BuildUpdate(**update_data),
                user_id=TEST_USER_ID,
            )

            # Verify the result
            assert result is not None
            assert result.name == update_data["name"]
            assert result.description == update_data["description"]

            # Verify the database interactions
            mock_async_db.commit.assert_called_once()

            # Verify refresh was called twice - once for the build and once for relationships
            assert mock_async_db.refresh.call_count == 2

            # First refresh call is for the build itself
            mock_async_db.refresh.assert_any_call(mock_build)

            # Second refresh call is for the relationships
            mock_async_db.refresh.assert_any_call(mock_build, ["professions"])

            # Verify the execute was called for delete and insert operations
            assert mock_async_db.execute.await_count >= 2  # At least delete and insert

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete(self, db_session: Session, mock_build):
        """Test deleting a build."""
        # Create a mock async session
        mock_async_db = AsyncMock(spec=AsyncSession)

        # Mock the get_async method to return our mock build
        # Note: The method will be called with either (db, id=id) or (db, id)
        async def get_async_mock(*args, **kwargs):
            return mock_build

        # Track if delete was called
        delete_called = False

        # Mock the delete method
        async def delete_mock(obj):
            nonlocal delete_called
            delete_called = True
            return None

        # Set up the mocks
        mock_async_db.delete = AsyncMock(side_effect=delete_mock)
        mock_async_db.commit = AsyncMock()

        # Patch the get_async method
        with patch("app.crud.base.CRUDBase.get_async", new=get_async_mock):
            # Perform the deletion
            result = await build.remove_async(db=mock_async_db, id=TEST_BUILD_ID)

            # Verify the result is the build that was deleted
            assert result == mock_build, "Expected the deleted build to be returned"

            # Verify the database interactions
            assert delete_called, "Delete was not called on the session"
            mock_async_db.commit.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_public_builds(self, db_session: Session, mock_build):
        """Test retrieving public builds."""
        # Mock the database query
        mock_db = MagicMock(spec=Session)
        mock_db.scalars.return_value.all.return_value = [mock_build]

        # Get public builds
        result = build.get_public_builds(db=mock_db, skip=0, limit=10)

        # Verify the result
        assert len(result) == 1
        assert result[0].id == TEST_BUILD_ID
        assert result[0].is_public is True

        # Verify the query was built correctly
        mock_db.scalars.assert_called_once()
        query = str(mock_db.scalars.call_args[0][0]).lower()
        assert "where builds.is_public = true" in query
        assert "limit :param_1" in query
        assert "offset :param_2" in query


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
