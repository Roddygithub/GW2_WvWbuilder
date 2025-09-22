"""
Unit tests for the Composition model.
"""

import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.models import Composition, User, Build, CompositionTag


class TestCompositionModel:
    """Test cases for the Composition model."""

    async def test_create_composition(self, db):
        """Test creating a basic composition."""
        # Create a user
        user = User(
            username="comp_creator",
            email="creator@example.com",
            hashed_password="hashed_password",
        )
        db.add(user)
        await db.flush()

        # Create a build
        build = Build(
            name="Test Build", game_mode="wvw", created_by_id=user.id, config={}
        )
        db.add(build)
        await db.flush()

        # Create a composition
        composition = Composition(
            name="Test Composition",
            description="A test composition",
            is_public=True,
            created_by=user.id,
            build_id=build.id,
            squad_size=10,
            config={"roles": ["healer", "dps"]},
        )
        db.add(composition)
        await db.commit()
        await db.refresh(composition)

        assert composition.id is not None
        assert composition.name == "Test Composition"
        assert composition.description == "A test composition"
        assert composition.is_public is True
        assert composition.created_by == user.id
        assert composition.build_id == build.id
        assert composition.squad_size == 10
        assert composition.config == {"roles": ["healer", "dps"]}
        assert isinstance(composition.created_at, datetime)
        assert composition.updated_at is None

    async def test_composition_relationships(self, db):
        """Test composition relationships with users, build, and tags."""
        # Create a user
        user = User(
            username="comp_creator",
            email="creator@example.com",
            hashed_password="hashed_password",
        )
        db.add(user)
        await db.flush()

        # Create a build
        build = Build(
            name="Test Build", game_mode="wvw", created_by_id=user.id, config={}
        )
        db.add(build)
        await db.flush()

        # Create a composition
        composition = Composition(
            name="Test Composition",
            created_by=user.id,
            build_id=build.id,
            squad_size=10,
        )

        # Add tags
        tag1 = CompositionTag(name="wvw", composition=composition)
        tag2 = CompositionTag(name="zerg", composition=composition)
        db.add_all([composition, tag1, tag2])

        # Add members (users in the composition)
        member1 = User(
            username="member1",
            email="member1@example.com",
            hashed_password="hashed_password",
        )
        member2 = User(
            username="member2",
            email="member2@example.com",
            hashed_password="hashed_password",
        )
        composition.members.extend([member1, member2])

        await db.commit()
        await db.refresh(composition)

        # Test relationships
        assert composition.creator == user
        assert composition.build == build
        assert len(composition.tags) == 2
        assert {t.name for t in composition.tags} == {"wvw", "zerg"}
        assert len(composition.members) == 2
        assert {m.username for m in composition.members} == {"member1", "member2"}

        # Test backrefs
        assert composition in build.compositions
        for tag in composition.tags:
            assert tag.composition == composition

    async def test_composition_validation(self, db):
        """Test composition validation and constraints."""
        # Test required fields
        composition = Composition()
        db.add(composition)

        with pytest.raises(IntegrityError):
            await db.commit()

        await db.rollback()

        # Test squad_size validation
        user = User(
            username="test", email="test@example.com", hashed_password="hashed_password"
        )
        db.add(user)
        await db.flush()

        build = Build(
            name="Test Build", game_mode="wvw", created_by_id=user.id, config={}
        )
        db.add(build)
        await db.flush()

        composition = Composition(
            name="Invalid Squad Size",
            created_by=user.id,
            build_id=build.id,
            squad_size=0,  # Must be at least 1
        )
        db.add(composition)

        with pytest.raises(IntegrityError):
            await db.commit()

    async def test_composition_default_values(self, db):
        """Test that default values are set correctly."""
        user = User(
            username="test", email="test@example.com", hashed_password="hashed_password"
        )
        db.add(user)
        await db.flush()

        build = Build(
            name="Test Build", game_mode="wvw", created_by_id=user.id, config={}
        )
        db.add(build)
        await db.flush()

        composition = Composition(
            name="Default Values Test", created_by=user.id, build_id=build.id
        )
        db.add(composition)
        await db.commit()
        await db.refresh(composition)

        assert composition.is_public is True
        assert composition.squad_size == 5
        assert composition.config == {}
        assert composition.description is None
        assert isinstance(composition.created_at, datetime)
        assert composition.updated_at is None

    async def test_composition_update_timestamps(self, db):
        """Test that updated_at is updated on changes."""
        user = User(
            username="test", email="test@example.com", hashed_password="hashed_password"
        )
        db.add(user)
        await db.flush()

        build = Build(
            name="Test Build", game_mode="wvw", created_by_id=user.id, config={}
        )
        db.add(build)
        await db.flush()

        composition = Composition(
            name="Timestamp Test", created_by=user.id, build_id=build.id
        )
        db.add(composition)
        await db.commit()

        original_created_at = composition.created_at

        # Make a change and commit
        composition.description = "Updated description"
        await db.commit()
        await db.refresh(composition)

        assert composition.updated_at is not None
        assert composition.updated_at > original_created_at
