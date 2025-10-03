"""
Unit tests for the User model.
"""

import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from app.models import User, Role
from app.core.security import get_password_hash, verify_password


class TestUserModel:
    """Test cases for the User model."""

    async def test_create_user(self, db):
        """Test creating a basic user."""
        # Create a test user
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            full_name="Test User",
        )

        # Add to session and commit
        db.add(user)
        await db.commit()
        await db.refresh(user)  # Refresh to get any database defaults

        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert user.is_superuser is False
        assert isinstance(user.created_at, datetime)
        assert user.updated_at is None

    async def test_user_relationships(self, db):
        """Test user relationships with roles and compositions."""
        # Create a role
        role = Role(name="test_role", description="Test Role")
        db.add(role)
        await db.flush()  # Flush to get the role ID

        # Create a user with the role
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
        )
        user.roles.append(role)
        db.add(user)
        await db.commit()

        # Test the relationship
        assert len(user.roles) == 1
        assert user.roles[0].name == "test_role"

        # Test the backref
        result = await db.execute(select(Role).where(Role.id == role.id))
        role_from_db = result.scalars().first()
        assert len(role_from_db.users) == 1
        assert role_from_db.users[0].username == "testuser"

    async def test_user_unique_constraints(self, db):
        """Test that username and email must be unique."""
        # Create first user
        user1 = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
        )
        db.add(user1)
        await db.commit()

        # Try to create a user with the same username
        user2 = User(
            username="testuser",  # Duplicate username
            email="another@example.com",
            hashed_password="hashed_password",
        )
        db.add(user2)

        with pytest.raises(IntegrityError):
            await db.commit()

        await db.rollback()

        # Try to create a user with the same email
        user3 = User(
            username="anotheruser",
            email="test@example.com",  # Duplicate email
            hashed_password="hashed_password",
        )
        db.add(user3)

        with pytest.raises(IntegrityError):
            await db.commit()

    async def test_user_password_hashing(self, db):
        """Test password hashing and verification."""
        password = "securepassword123"
        hashed_password = get_password_hash(password)

        # Create a user with the hashed password
        user = User(
            username="testuser_pw",
            email="test_pw@example.com",
            hashed_password=hashed_password,
        )

        # Add to session and commit
        db.add(user)
        await db.commit()
        await db.refresh(user)

        # Test password verification
        assert verify_password(password, user.hashed_password) is True
        assert verify_password("wrongpassword", user.hashed_password) is False

    async def test_user_timestamps(self, db):
        """Test that created_at and updated_at timestamps work correctly."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
        )
        db.add(user)
        await db.commit()

        # Check created_at is set
        assert user.created_at is not None
        assert user.updated_at is None

        # Update the user and check updated_at
        original_created_at = user.created_at
        user.full_name = "Updated Name"
        await db.commit()

        assert user.updated_at is not None
        assert user.updated_at > user.created_at
        assert user.updated_at > original_created_at
