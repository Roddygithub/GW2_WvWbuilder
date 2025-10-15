"""Tests for service layer functions."""

import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

# Application imports
from app.crud import user_crud
from app.schemas.user import UserCreate, UserUpdate

pytestmark = pytest.mark.asyncio


class TestUserService:
    """Tests for user-related service functions."""

    async def test_create_user(self, db: AsyncSession):
        """Test creating a new user."""
        # Test data - use unique values for each test run
        unique_id = str(uuid.uuid4())[:8]
        password = "testpassword123"
        user_data = {
            "email": f"newuser_{unique_id}@example.com",
            "username": f"newuser_{unique_id}",
            "password": password,
            "full_name": f"New User {unique_id}",
        }

        # Call the service function
        user = await user_crud.create(db, obj_in=UserCreate(**user_data))

        # Check the results
        assert user is not None
        assert user.email == user_data["email"]
        assert user.username == user_data["username"]
        assert user.hashed_password is not None
        assert user.hashed_password != password  # Should be hashed
        assert user.is_active is True
        assert user.is_superuser is False

    async def test_authenticate_user(self, db: AsyncSession):
        """Test authenticating a user with correct password."""
        # Create a test user in the database with unique data
        unique_id = str(uuid.uuid4())[:8]
        password = "testpassword123"
        hashed_password = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # hash of 'testpassword123'
        user_data = {
            "email": f"auth_test_{unique_id}@example.com",
            "username": f"authtestuser_{unique_id}",
            "hashed_password": hashed_password,
            "full_name": f"Auth Test User {unique_id}",
            "is_active": True,
        }

        # Create user directly with hashed password to avoid re-hashing
        user = await user_crud.create(
            db,
            obj_in=UserCreate(
                email=user_data["email"],
                username=user_data["username"],
                password=password,  # Will be hashed by create_async
                full_name=user_data["full_name"],
            ),
        )

        # Test with correct password
        authenticated_user = await user_crud.authenticate(
            db, email=user.email, password=password
        )
        assert authenticated_user is not None
        assert authenticated_user.email == user.email

        # Test with incorrect password
        authenticated_user = await user_crud.authenticate(
            db, email=user.email, password="wrong_password"
        )
        assert authenticated_user is None

        # Test with non-existent user
        authenticated_user = await user_crud.authenticate(
            db, email="nonexistent@example.com", password=password
        )
        assert authenticated_user is None

        # Test with inactive user
        user.is_active = False
        db.add(user)
        await db.commit()
        await db.refresh(user)

        authenticated_user = await user_crud.authenticate(
            db, email=user.email, password=password
        )
        assert authenticated_user is None

    async def test_update_user(self, db: AsyncSession):
        """Test updating a user's information."""
        # Create a test user first
        user_data = {
            "email": f"update_test_{uuid.uuid4().hex[:8]}@example.com",
            "username": f"updatetestuser_{uuid.uuid4().hex[:4]}",
            "password": "testpassword123",
            "full_name": "Update Test User",
        }
        user = await user_crud.create(db, obj_in=UserCreate(**user_data))

        # Test update data
        update_data = {
            "is_active": False,
            "email": f"updated_{uuid.uuid4().hex[:8]}@example.com",
        }

        # Call the update method
        updated_user = await user_crud.update(
            db, db_obj=user, obj_in=UserUpdate(**update_data)
        )

        # Check the results
        assert updated_user is not None
        assert updated_user.is_active == update_data["is_active"]
        assert updated_user.email == update_data["email"]

    async def test_delete_user(self, db: AsyncSession):
        """Test deleting a user."""
        # Create a test user first
        user_data = {
            "email": f"delete_test_{uuid.uuid4().hex[:8]}@example.com",
            "username": f"deletetestuser_{uuid.uuid4().hex[:4]}",
            "password": "testpassword123",
            "full_name": "Delete Test User",
        }
        user = await user_crud.create(db, obj_in=UserCreate(**user_data))

        # Store the user ID before deletion
        user_id = user.id

        # Call the delete method
        deleted_user = await user_crud.remove(db, id=user_id)

        # Check the results
        assert deleted_user is not None
        assert deleted_user.id == user_id

        # Verify the user no longer exists in the database
        deleted_user = await user_crud.get(db, id=user_id)
        assert deleted_user is None
