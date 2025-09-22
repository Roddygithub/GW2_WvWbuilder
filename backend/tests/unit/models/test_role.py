"""
Unit tests for the Role model.
"""

import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.models import Role, User


class TestRoleModel:
    """Test cases for the Role model."""

    async def test_create_role(self, db):
        """Test creating a basic role."""
        role = Role(
            name="test_role",
            description="Test Role Description",
            permission_level=1,
            is_default=False,
        )
        db.add(role)
        await db.commit()

        assert role.id is not None
        assert role.name == "test_role"
        assert role.description == "Test Role Description"
        assert role.permission_level == 1
        assert role.is_default is False
        assert isinstance(role.created_at, datetime)
        assert role.updated_at is None

    async def test_role_relationships(self, db):
        """Test role relationships with users."""
        # Create a role
        role = Role(name="test_role", description="Test Role")

        # Create a user
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
        )

        # Add user to role
        role.users.append(user)

        db.add(role)
        await db.commit()

        # Test the relationship
        assert len(role.users) == 1
        assert role.users[0].username == "testuser"

        # Test the backref
        assert len(user.roles) == 1
        assert user.roles[0].name == "test_role"

    async def test_role_unique_constraint(self, db):
        """Test that role names must be unique."""
        # Create first role
        role1 = Role(name="test_role", description="Test Role")
        db.add(role1)
        await db.commit()

        # Try to create a role with the same name
        role2 = Role(name="test_role", description="Duplicate Role")
        db.add(role2)

        with pytest.raises(IntegrityError):
            await db.commit()

        await db.rollback()

    async def test_role_timestamps(self, db):
        """Test that created_at and updated_at timestamps work correctly."""
        role = Role(name="test_role", description="Test Role")
        db.add(role)
        await db.commit()

        # Check created_at is set
        assert role.created_at is not None
        assert role.updated_at is None

        # Update the role and check updated_at
        original_created_at = role.created_at
        role.description = "Updated Description"
        await db.commit()

        assert role.updated_at is not None
        assert role.updated_at > role.created_at
        assert role.updated_at > original_created_at

    async def test_role_default_values(self, db):
        """Test that default values are set correctly."""
        role = Role(name="test_role")
        db.add(role)
        await db.commit()

        assert role.permission_level == 0
        assert role.is_default is False
        assert role.description is None
