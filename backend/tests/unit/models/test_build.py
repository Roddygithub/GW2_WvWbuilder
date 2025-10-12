"""
Unit tests for the Build model.
"""

import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.models import Build, User, Profession, Composition


class TestBuildModel:
    """Test cases for the Build model."""

    async def test_create_build(self, db):
        """Test creating a basic build."""
        # Create a user
        user = User(
            username="build_creator",
            email="creator@example.com",
            hashed_password="hashed_password",
        )
        db.add(user)
        await db.flush()

        # Create a build
        build = Build(
            name="Test Build",
            description="A test build",
            game_mode="wvw",
            team_size=5,
            is_public=True,
            created_by_id=user.id,
            config={"traits": [1, 2, 3], "skills": [4, 5, 6]},
            constraints={"required_professions": ["Guardian", "Warrior"]},
        )
        db.add(build)
        await db.commit()
        await db.refresh(build)

        assert build.id is not None
        assert build.name == "Test Build"
        assert build.description == "A test build"
        assert build.game_mode == "wvw"
        assert build.team_size == 5
        assert build.is_public is True
        assert build.created_by_id == user.id
        assert build.config == {"traits": [1, 2, 3], "skills": [4, 5, 6]}
        assert build.constraints == {"required_professions": ["Guardian", "Warrior"]}
        assert isinstance(build.created_at, datetime)
        assert build.updated_at is None

    async def test_build_relationships(self, db):
        """Test build relationships with user, professions, and compositions."""
        # Create a user
        user = User(
            username="build_creator",
            email="creator@example.com",
            hashed_password="hashed_password",
        )
        db.add(user)
        await db.flush()

        # Create professions
        guardian = Profession(name="Guardian", game_modes=["wvw"])
        warrior = Profession(name="Warrior", game_modes=["wvw"])
        db.add_all([guardian, warrior])
        await db.flush()

        # Create a build with professions
        build = Build(name="Test Build", game_mode="wvw", created_by_id=user.id, config={})
        build.professions.extend([guardian, warrior])
        db.add(build)

        # Create a composition that uses this build
        composition = Composition(
            name="Test Composition",
            description="A test composition",
            is_public=True,
            created_by=user.id,
            build_id=build.id,
        )
        db.add(composition)
        await db.commit()
        await db.refresh(build)

        # Test relationships
        assert len(build.professions) == 2
        assert {p.name for p in build.professions} == {"Guardian", "Warrior"}

        # Test backrefs
        assert build.created_by == user
        assert build in user.builds

        # Test composition relationship
        assert build.compositions[0].name == "Test Composition"

    async def test_build_validation(self, db):
        """Test build validation and constraints."""
        # Test required fields
        build = Build()
        db.add(build)

        with pytest.raises(IntegrityError):
            await db.commit()

        await db.rollback()

        # Test game_mode validation
        user = User(username="test", email="test@example.com", hashed_password="pwd")
        db.add(user)
        await db.flush()

        build = Build(
            name="Invalid Game Mode",
            game_mode="invalid_mode",
            created_by_id=user.id,
            config={},
        )
        db.add(build)

        with pytest.raises(IntegrityError):
            await db.commit()

        await db.rollback()

        # Test team_size validation
        build = Build(
            name="Invalid Team Size",
            game_mode="wvw",
            team_size=0,  # Must be at least 1
            created_by_id=user.id,
            config={},
        )
        db.add(build)

        with pytest.raises(IntegrityError):
            await db.commit()

    async def test_build_default_values(self, db):
        """Test that default values are set correctly."""
        user = User(username="test", email="test@example.com", hashed_password="pwd")
        db.add(user)
        await db.flush()

        build = Build(
            name="Default Values Test",
            game_mode="wvw",
            created_by_id=user.id,
            config={},
        )
        db.add(build)
        await db.commit()
        await db.refresh(build)

        assert build.is_public is False
        assert build.team_size == 5
        assert build.config == {}
        assert build.constraints == {}
        assert isinstance(build.created_at, datetime)
        assert build.updated_at is None

    async def test_build_update_timestamps(self, db):
        """Test that updated_at is updated on changes."""
        user = User(username="test", email="test@example.com", hashed_password="pwd")
        db.add(user)
        await db.flush()

        build = Build(name="Timestamp Test", game_mode="wvw", created_by_id=user.id, config={})
        db.add(build)
        await db.commit()

        original_created_at = build.created_at

        # Make a change and commit
        build.description = "Updated description"
        await db.commit()
        await db.refresh(build)

        assert build.updated_at is not None
        assert build.updated_at > original_created_at
