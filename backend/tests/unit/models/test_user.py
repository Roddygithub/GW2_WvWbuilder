"""
Unit tests for the User model.
"""

import pytest
import uuid
from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Role, UserRole
from app.core.security import get_password_hash, verify_password

# Configure logging
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestUserModel:
    """Test cases for the User model."""

    @pytest.mark.asyncio
    async def test_create_user(self, db_session: AsyncSession, test_password: str) -> None:
        """Test creating a basic user."""
        try:
            # Create a test user
            user = User(
                username=f"testuser_{uuid.uuid4().hex[:8]}",
                email=f"test_{uuid.uuid4().hex[:8]}@example.com",
                hashed_password=get_password_hash(test_password),
                full_name="Test User",
                is_active=True,
                is_superuser=False,
            )

            # Add to session and commit
            db_session.add(user)
            await db_session.commit()
            await db_session.refresh(user)  # Refresh to get any database defaults

            # Verify user attributes
            assert user.id is not None
            assert user.username.startswith("testuser_")
            assert "@example.com" in user.email
            assert user.full_name == "Test User"
            assert user.is_active is True
            assert user.is_superuser is False
            assert isinstance(user.created_at, datetime)
            assert user.updated_at is None

            # Verify password hashing
            assert verify_password(test_password, user.hashed_password)
        except Exception as e:
            await db_session.rollback()
            logger.error(f"Error in test_create_user: {e}")
            raise
        assert verify_password(test_password, user.hashed_password)
        assert not verify_password("wrong_password", user.hashed_password)

    @pytest.mark.asyncio
    async def test_user_relationships(self, db_session: AsyncSession, test_user: User, test_role: Role) -> None:
        """Test user relationships with roles."""
        try:
            # Ajouter le rôle à l'utilisateur via la relation
            test_user.role_associations = [UserRole(role=test_role)]
            await db_session.commit()
            await db_session.refresh(test_user)

            # Récupérer l'utilisateur avec ses rôles
            result = await db_session.execute(
                select(User)
                .where(User.id == test_user.id)
                .options(selectinload(User.role_associations).selectinload(UserRole.role))
            )
            user = result.scalars().first()

            # Vérifier que l'utilisateur a bien le rôle
            assert user is not None
            assert len(user.role_associations) == 1
            assert user.role_associations[0].role_id == test_role.id

        except Exception as e:
            await db_session.rollback()
            logger.error(f"Error in test_user_relationships: {e}")
            raise
        finally:
            # Nettoyage
            try:
                if (
                    "test_user" in locals()
                    and hasattr(test_user, "id")
                    and "test_role" in locals()
                    and hasattr(test_role, "id")
                ):
                    await db_session.execute(
                        text("DELETE FROM user_roles WHERE user_id = :user_id AND role_id = :role_id"),
                        {"user_id": test_user.id, "role_id": test_role.id},
                    )
                    await db_session.commit()
            except Exception as e:
                await db_session.rollback()
                logger.error(f"Error during cleanup in test_user_relationships: {e}")

    async def test_user_update(self, db_session, test_user):
        """Test updating user attributes."""
        # Update user
        new_email = f"updated_{test_user.email}"
        new_full_name = "Updated User"
        test_user.email = new_email
        test_user.full_name = new_full_name

        await db_session.commit()
        await db_session.refresh(test_user)

        # Verify updates
        assert test_user.email == new_email
        assert test_user.full_name == new_full_name
        assert test_user.updated_at is not None

    @pytest.mark.asyncio
    async def test_user_authentication(self, db_session: AsyncSession, test_user: User, test_password: str) -> None:
        """Test user authentication methods."""
        try:
            # Test password verification
            assert verify_password(test_password, test_user.hashed_password)
            assert not verify_password("wrongpassword", test_user.hashed_password)

            # Test is_active flag
            assert test_user.is_active is True

            # Test deactivation
            test_user.is_active = False
            await db_session.commit()
            await db_session.refresh(test_user)
            assert test_user.is_active is False

        except Exception as e:
            await db_session.rollback()
            logger.error(f"Error in test_user_authentication: {e}")
            raise

    @pytest.mark.asyncio
    async def test_user_validation(self, db_session: AsyncSession, test_user: User) -> None:
        """Test user model validation and constraints."""
        # Test 1: Vérifier que les champs requis sont bien obligatoires
        invalid_user = User()  # Manque tous les champs requis
        db_session.add(invalid_user)

        try:
            with pytest.raises(IntegrityError):
                await db_session.commit()
        finally:
            await db_session.rollback()

        # Test 2: Vérifier la contrainte d'unicité sur le nom d'utilisateur
        duplicate_username = User(
            username=test_user.username,  # Même nom d'utilisateur
            email=f"new_{uuid.uuid4().hex[:8]}@example.com",
            hashed_password=get_password_hash("testpassword"),
            full_name="Duplicate Username",
            is_active=True,
        )
        db_session.add(duplicate_username)

        try:
            with pytest.raises(IntegrityError):
                await db_session.commit()
        finally:
            await db_session.rollback()

        # Test 3: Vérifier la contrainte d'unicité sur l'email
        duplicate_email = User(
            username=f"newuser_{uuid.uuid4().hex[:8]}",
            email=test_user.email,  # Même email
            hashed_password=get_password_hash("testpassword"),
            full_name="Duplicate Email",
            is_active=True,
        )
        db_session.add(duplicate_email)

        try:
            with pytest.raises(IntegrityError):
                await db_session.commit()
        finally:
            await db_session.rollback()

    @pytest.mark.asyncio
    async def test_user_timestamps(self, db_session: AsyncSession) -> None:
        """Test user model timestamps."""
        try:
            # Create a user
            user = User(
                username=f"timestamp_{uuid.uuid4().hex[:8]}",
                email=f"timestamp_{uuid.uuid4().hex[:8]}@example.com",
                hashed_password=get_password_hash("testpassword"),
                full_name="Timestamp User",
            )

            db_session.add(user)
            await db_session.commit()
            await db_session.refresh(user)

            # Check created_at is set
            assert user.created_at is not None
            assert user.updated_at is None

            # Get the current timestamp
            before_update = datetime.utcnow()

            # Update the user
            user.full_name = "Updated Timestamp User"
            await db_session.commit()
            await db_session.refresh(user)

            # Check updated_at is set and is not before created_at
            assert user.updated_at is not None
            assert user.updated_at >= user.created_at, "updated_at should be greater than or equal to created_at"

            # Log timestamps for debugging
            logger.info(f"created_at: {user.created_at}, updated_at: {user.updated_at}, before_update: {before_update}")

        except Exception as e:
            await db_session.rollback()
            logger.error(f"Error in test_user_timestamps: {e}")
            raise

    @pytest.mark.asyncio
    async def test_user_password_hashing(self, db_session: AsyncSession) -> None:
        """Test password hashing and verification."""
        try:
            password = "testpassword123"
            hashed = get_password_hash(password)

            # Test password verification
            assert verify_password(password, hashed) is True
            assert verify_password("wrongpassword", hashed) is False

            # Test password hashing changes
            hashed2 = get_password_hash(password)
            assert hashed != hashed2  # Should be different due to salt

        except Exception as e:
            logger.error(f"Error in test_user_password_hashing: {e}")
            raise
