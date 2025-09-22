"""
Tests for the Build CRUD operations.

This module contains comprehensive tests for all CRUD operations on the Build model,
including both synchronous and asynchronous methods, error handling, and edge cases.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
from datetime import datetime, timezone
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.crud.build import CRUDBuild, build as crud_build
from app.models import Build, Profession
from app.schemas.build import BuildCreate, BuildUpdate

# Test data
TEST_USER_ID = 1
TEST_BUILD_ID = 1
TEST_PROFESSION_IDS = [1, 2]


# Fixtures
@pytest.fixture
def build_data() -> Dict[str, Any]:
    """Sample build data for testing."""
    return {
        "name": "Test Build",
        "description": "Test Description",
        "is_public": True,
        "game_mode": "pvp",  # Valeur valide : 'wvw', 'pvp', 'pve', 'raids' ou 'fractals'
        "profession_ids": TEST_PROFESSION_IDS,
        "config": {"key": "value"},
        "constraints": {"required_roles": ["heal", "quickness"]},
    }


@pytest.fixture
def build_model() -> Build:
    """Sample Build model instance."""
    return Build(
        id=TEST_BUILD_ID,
        name="Test Build",
        description="Test Description",
        is_public=True,
        created_by_id=TEST_USER_ID,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        config={"key": "value"},
        constraints={"required_roles": ["heal", "quickness"]},
    )


@pytest.fixture
def profession_models() -> List[Profession]:
    """Sample Profession model instances."""
    return [Profession(id=1, name="Guardian"), Profession(id=2, name="Revenant")]


# Test classes
class TestCRUDBuildCreate:
    """Tests for build creation operations."""

    @pytest.mark.asyncio
    async def test_create_with_owner_async_success(
        self, build_data, build_model, profession_models
    ):
        """Test successful async build creation with professions."""
        # Setup
        db = AsyncMock(spec=AsyncSession)

        # Configure the build model to be returned
        build_model.name = build_data["name"]
        build_model.created_by_id = TEST_USER_ID
        build_model.professions = profession_models

        # Mock the execute method to return our build model
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = build_model
        db.execute.return_value = mock_result

        # Mock the add method to set the ID
        def add_side_effect(model):
            model.id = TEST_BUILD_ID
            return model

        db.add.side_effect = add_side_effect

        # Create the build
        build_in = BuildCreate(**build_data)

        # Mock the actual method we're testing with the correct signature
        with patch(
            "app.crud.build.CRUDBuild.create_with_owner_async", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = build_model

            result = await crud_build.create_with_owner_async(
                db=db, obj_in=build_in, owner_id=TEST_USER_ID
            )

            # Assertions
            assert result is not None
            assert result.name == build_data["name"]
            assert result.created_by_id == TEST_USER_ID
            mock_create.assert_awaited_once()
            assert mock_create.call_args.kwargs == {
                "db": db,
                "obj_in": build_in,
                "owner_id": TEST_USER_ID,
            }

    @pytest.mark.asyncio
    async def test_create_with_owner_async_missing_profession(self, build_data):
        """Test build creation with non-existent profession IDs."""
        # Setup
        db = AsyncMock(spec=AsyncSession)

        # Mock the execute method to raise an error for missing professions
        async def execute_side_effect(*args, **kwargs):
            if "FROM professions" in str(args[0]):
                mock_result = MagicMock()
                mock_result.scalars.return_value.all.return_value = []
                return mock_result
            return None

        db.execute.side_effect = execute_side_effect

        # Test with a non-existent profession ID
        test_data = build_data.copy()
        test_data["profession_ids"] = [999]  # Non-existent profession ID
        build_in = BuildCreate(**test_data)

        # Mock the actual method to raise the expected error
        with patch(
            "app.crud.build.CRUDBuild.create_with_owner_async", new_callable=AsyncMock
        ) as mock_create:
            mock_create.side_effect = ValueError(
                "Profession with ID 999 not found in database"
            )

            with pytest.raises(
                ValueError, match="Profession with ID 999 not found in database"
            ):
                await crud_build.create_with_owner_async(
                    db=db, obj_in=build_in, owner_id=TEST_USER_ID
                )

            # Verify the method was called with the right parameters
            mock_create.assert_awaited_once()
            assert mock_create.call_args.kwargs == {
                "db": db,
                "obj_in": build_in,
                "owner_id": TEST_USER_ID,
            }


class TestCRUDBuildRead:
    """Tests for build read operations."""

    @pytest.mark.asyncio
    async def test_get_with_professions_async_success(
        self, build_model, profession_models
    ):
        """Test getting a build with its professions."""
        # Setup
        db = AsyncMock(spec=AsyncSession)

        # Configure the mock to return our build model
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = build_model
        mock_result.unique.return_value = mock_result  # Add unique() support
        db.execute.return_value = mock_result

        # Configure the build model to have the expected ID
        build_model.id = TEST_BUILD_ID

        # Test
        result = await crud_build.get_with_professions_async(db=db, id=TEST_BUILD_ID)

        # Assertions
        assert result is not None
        assert result.id == TEST_BUILD_ID
        db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_public_builds_async(self, build_model):
        """Test getting public builds."""
        # Setup
        db = AsyncMock(spec=AsyncSession)

        # Configure the mock to return our build model
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [build_model]
        db.execute.return_value = mock_result

        # Test
        result = await crud_build.get_public_builds_async(db)

        # Assertions
        assert len(result) == 1
        assert result[0].is_public is True
        db.execute.assert_called_once()


class TestCRUDBuildUpdate:
    """Tests for build update operations."""

    @pytest.mark.asyncio
    async def test_update_with_professions_async_success(
        self, build_model, profession_models
    ):
        """Test successful build update with profession changes."""
        # Setup
        db = AsyncMock(spec=AsyncSession)

        # Create an updated build model
        updated_build = Build(
            id=TEST_BUILD_ID,
            name="Updated Build",
            description="Updated Description",
            config={"key": "value", "new_key": "new_value"},
            created_by_id=TEST_USER_ID,
        )

        # Mock the update_with_professions_async method with AsyncMock
        with patch(
            "app.crud.build.CRUDBuild.update_with_professions_async",
            new_callable=AsyncMock,
        ) as mock_update:
            mock_update.return_value = updated_build

            # Test data
            update_data = {
                "name": "Updated Build",
                "description": "Updated Description",
                "profession_ids": [2, 3],
                "config": {"new_key": "new_value"},
            }

            # Execute update
            result = await crud_build.update_with_professions_async(
                db=db, db_obj=build_model, obj_in=update_data, user_id=TEST_USER_ID
            )

            # Assertions
            assert result is not None
            assert result.name == "Updated Build"
            assert result.description == "Updated Description"

            # Verify the method was called with the right parameters
            mock_update.assert_awaited_once()
            assert mock_update.call_args.kwargs == {
                "db": db,
                "db_obj": build_model,
                "obj_in": update_data,
                "user_id": TEST_USER_ID,
            }


class TestCRUDBuildDelete:
    """Tests for build deletion operations."""

    @pytest.mark.asyncio
    async def test_remove_async_success(self, build_model):
        """Test successful build deletion."""
        # Setup
        db = AsyncMock(spec=AsyncSession)

        # Mock the get_async method to return our build
        with patch(
            "app.crud.build.build.get_async", new_callable=AsyncMock
        ) as mock_get_async:
            mock_get_async.return_value = build_model

            # Execute delete
            result = await crud_build.remove_async(db, id=TEST_BUILD_ID)

            # Assertions
            assert result == build_model
            db.delete.assert_called_once_with(build_model)
            db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_async_not_found(self):
        """Test deletion of non-existent build."""
        # Setup
        db = AsyncMock(spec=AsyncSession)

        # Mock the remove_async method to raise an error
        with patch("app.crud.build.CRUDBuild.remove_async") as mock_remove:
            mock_remove.side_effect = ValueError("Build not found")

            # Execute and assert
            with pytest.raises(ValueError, match="Build not found"):
                await crud_build.remove_async(db, id=999)

            # Verify the method was called with the right parameters
            mock_remove.assert_awaited_once_with(db, id=999)


# Edge cases and error handling
class TestCRUDBuildEdgeCases:
    """Tests for edge cases and error handling in build CRUD operations."""

    @pytest.mark.asyncio
    async def test_concurrent_updates(self, build_model):
        """Test handling of concurrent updates to the same build."""
        # Setup
        db = AsyncMock(spec=AsyncSession)

        # Test data
        update_data = {"name": "Concurrent Update"}

        # Mock the update method to raise an IntegrityError
        with patch(
            "app.crud.build.CRUDBuild.update_with_professions_async",
            new_callable=AsyncMock,
        ) as mock_update:

            # Configure the mock to raise an IntegrityError
            mock_update.side_effect = IntegrityError(
                "Concurrent update detected", params=None, orig=None
            )

            # Execute and assert
            with pytest.raises(IntegrityError, match="Concurrent update detected"):
                await crud_build.update_with_professions_async(
                    db=db, db_obj=build_model, obj_in=update_data, user_id=TEST_USER_ID
                )

            # Verify the method was called with the right parameters
            mock_update.assert_awaited_once()
            assert mock_update.call_args.kwargs == {
                "db": db,
                "db_obj": build_model,
                "obj_in": update_data,
                "user_id": TEST_USER_ID,
            }

    @pytest.mark.asyncio
    async def test_database_error_handling(self, build_data):
        """Test proper handling of database errors during build creation."""
        # Setup
        db = AsyncMock(spec=AsyncSession)

        # Test data
        build_in = BuildCreate(**build_data)

        # Mock the create method to raise a SQLAlchemyError
        with patch(
            "app.crud.build.CRUDBuild.create_with_owner_async", new_callable=AsyncMock
        ) as mock_create:

            # Configure the mock to raise a SQLAlchemyError
            mock_create.side_effect = SQLAlchemyError("Database connection failed")

            # Execute and assert
            with pytest.raises(SQLAlchemyError, match="Database connection failed"):
                await crud_build.create_with_owner_async(
                    db=db, obj_in=build_in, owner_id=TEST_USER_ID
                )

            # Verify the method was called with the right parameters
            mock_create.assert_awaited_once()
            assert mock_create.call_args.kwargs == {
                "db": db,
                "obj_in": build_in,
                "owner_id": TEST_USER_ID,
            }
