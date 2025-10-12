"""
Additional tests for Build CRUD operations.

This module contains tests for additional CRUD methods in the Build module
that are not covered in the main test file.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.build import build as crud_build
from app.models import Build, Profession

# Test data
TEST_USER_ID = 1


# Fixtures
@pytest.fixture
def build_model():
    """Sample Build model instance."""
    return Build(
        id=1,
        name="Test Build",
        description="Test Description",
        is_public=True,
        game_mode="pvp",
        owner_id=TEST_USER_ID,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def profession_models():
    """Sample Profession model instances."""
    return [
        Profession(id=1, name="Warrior", icon="warrior.png"),
        Profession(id=2, name="Guardian", icon="guardian.png"),
    ]


# Tests for additional CRUD methods
class TestCRUDBuildAdditionalMethods:
    """Tests for additional CRUD methods in the Build module."""

    @pytest.mark.asyncio
    async def test_get_multi_by_owner_async(self, build_model):
        """Test getting multiple builds by owner ID."""
        # Setup
        db = AsyncMock(spec=AsyncSession)
        owner_id = 1
        skip = 0
        limit = 10

        # Mock the execute method to return a list of builds
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [build_model]
        db.execute.return_value = mock_result

        # Execute
        result = await crud_build.get_multi_by_owner_async(db, owner_id=owner_id, skip=skip, limit=limit)

        # Assert
        assert len(result) == 1
        assert result[0].id == build_model.id
        db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_public_builds_async(self, build_model):
        """Test getting public builds."""
        # Setup
        db = AsyncMock(spec=AsyncSession)
        skip = 0
        limit = 10

        # Mock the execute method to return a list of builds
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [build_model]
        db.execute.return_value = mock_result

        # Execute
        result = await crud_build.get_public_builds_async(db, skip=skip, limit=limit)

        # Assert
        assert len(result) == 1
        assert result[0].id == build_model.id
        db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_with_professions_async(self, build_model, profession_models):
        """Test getting a build with its professions."""
        # Setup
        db = AsyncMock(spec=AsyncSession)
        build_id = 1

        # Mock the get_async method
        with patch("app.crud.build.CRUDBuild.get_async") as mock_get:
            mock_get.return_value = build_model

            # Mock the execute method for professions
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = profession_models
            db.execute.return_value = mock_result

            # Execute
            result = await crud_build.get_with_professions_async(db, id=build_id)

            # Assert
            assert result == build_model
            assert len(result.professions) == len(profession_models)
            mock_get.assert_called_once_with(db, id=build_id)
            db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_profession_async(self, build_model, profession_models):
        """Test adding a profession to a build."""
        # Setup
        db = AsyncMock(spec=AsyncSession)
        build_id = 1
        profession_id = 1

        # Mock the get_async method for build
        with patch("app.crud.build.CRUDBuild.get_async") as mock_get_build:
            mock_get_build.return_value = build_model

            # Mock the get method for profession
            with patch("app.crud.build.CRUDProfession.get") as mock_get_profession:
                mock_get_profession.return_value = profession_models[0]

                # Execute
                result = await crud_build.add_profession_async(db, build_id=build_id, profession_id=profession_id)

                # Assert
                assert result is True
                db.add.assert_called_once()
                db.commit.assert_awaited_once()
                db.refresh.assert_awaited_once_with(build_model)

    @pytest.mark.asyncio
    async def test_remove_profession_async(self, build_model, profession_models):
        """Test removing a profession from a build."""
        # Setup
        db = AsyncMock(spec=AsyncSession)
        build_id = 1
        profession_id = 1

        # Mock the get_async method for build
        with patch("app.crud.build.CRUDBuild.get_async") as mock_get_build:
            mock_get_build.return_value = build_model

            # Mock the get method for profession
            with patch("app.crud.build.CRUDProfession.get") as mock_get_profession:
                mock_get_profession.return_value = profession_models[0]

                # Execute
                result = await crud_build.remove_profession_async(db, build_id=build_id, profession_id=profession_id)

                # Assert
                assert result is True
                db.execute.assert_called_once()
                db.commit.assert_awaited_once()
                db.refresh.assert_awaited_once_with(build_model)

    @pytest.mark.asyncio
    async def test_add_profession_nonexistent_build(self):
        """Test adding a profession to a non-existent build."""
        # Setup
        db = AsyncMock(spec=AsyncSession)
        build_id = 999
        profession_id = 1

        # Mock the get_async method to return None (build not found)
        with patch("app.crud.build.CRUDBuild.get_async") as mock_get_build:
            mock_get_build.return_value = None

            # Execute and assert
            result = await crud_build.add_profession_async(db, build_id=build_id, profession_id=profession_id)
            assert result is False

    @pytest.mark.asyncio
    async def test_remove_profession_nonexistent_build(self):
        """Test removing a profession from a non-existent build."""
        # Setup
        db = AsyncMock(spec=AsyncSession)
        build_id = 999
        profession_id = 1

        # Mock the get_async method to return None (build not found)
        with patch("app.crud.build.CRUDBuild.get_async") as mock_get_build:
            mock_get_build.return_value = None

            # Execute and assert
            result = await crud_build.remove_profession_async(db, build_id=build_id, profession_id=profession_id)
            assert result is False
