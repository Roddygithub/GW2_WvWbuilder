"""Test user operations with async database."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate, UserUpdate
from app.crud.user import user as crud_user
from app.core.security import verify_password

# Test data
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword"
TEST_USERNAME = "testuser"
TEST_FULL_NAME = "Test User"


@pytest.mark.asyncio
async def test_create_user(db: AsyncSession):
    """Test creating a new user."""
    # Arrange
    user_in = UserCreate(
        email=TEST_EMAIL,
        username=TEST_USERNAME,
        password=TEST_PASSWORD,
        full_name=TEST_FULL_NAME,
    )

    # Act
    user = await crud_user.create_async(db, obj_in=user_in)

    try:
        # Assert
        assert user is not None
        assert user.email == TEST_EMAIL
        assert user.username == TEST_USERNAME
        assert user.full_name == TEST_FULL_NAME
        assert user.is_active is True
        assert user.is_superuser is False
        assert hasattr(user, "hashed_password")
        assert verify_password(TEST_PASSWORD, user.hashed_password)

        # Verify the user can be retrieved
        db_user = await crud_user.get_async(db, id=user.id)
        assert db_user is not None
        assert db_user.email == user.email
        assert db_user.username == user.username
    finally:
        # Cleanup
        await db.delete(user)
        await db.commit()


@pytest.mark.asyncio
async def test_authenticate_user(db: AsyncSession):
    """Test user authentication."""
    # Arrange
    user_in = UserCreate(
        email=TEST_EMAIL,
        username=TEST_USERNAME,
        password=TEST_PASSWORD,
        full_name=TEST_FULL_NAME,
    )
    user = await crud_user.create_async(db, obj_in=user_in)

    try:
        # Act - Correct credentials
        authenticated_user = await crud_user.authenticate_async(
            db, email=TEST_EMAIL, password=TEST_PASSWORD
        )

        # Assert
        assert authenticated_user is not None
        assert authenticated_user.email == TEST_EMAIL

        # Act - Wrong password
        wrong_auth = await crud_user.authenticate_async(
            db, email=TEST_EMAIL, password="wrongpassword"
        )
        assert wrong_auth is None

        # Act - Wrong email
        wrong_email = await crud_user.authenticate_async(
            db, email="wrong@example.com", password=TEST_PASSWORD
        )
        assert wrong_email is None
    finally:
        # Cleanup
        await db.delete(user)
        await db.commit()


@pytest.mark.asyncio
async def test_update_user(db: AsyncSession):
    """Test updating a user."""
    # Arrange
    user_in = UserCreate(
        email=TEST_EMAIL,
        username=TEST_USERNAME,
        password=TEST_PASSWORD,
        full_name=TEST_FULL_NAME,
    )
    user = await crud_user.create_async(db, obj_in=user_in)

    try:
        # Act
        updated_data = UserUpdate(
            full_name="Updated Name",
            email="updated@example.com",
            username="updateduser",
        )
        updated_user = await crud_user.update_async(
            db, db_obj=user, obj_in=updated_data
        )

        # Assert
        assert updated_user is not None
        assert updated_user.id == user.id
        assert updated_user.email == "updated@example.com"
        assert updated_user.username == "updateduser"
        assert updated_user.full_name == "Updated Name"

        # Verify the update is persisted
        db_user = await crud_user.get_async(db, id=user.id)
        assert db_user is not None
        assert db_user.email == "updated@example.com"
    finally:
        # Cleanup
        await db.delete(user)
        await db.commit()


@pytest.mark.asyncio
async def test_remove_user(db: AsyncSession):
    """Test removing a user."""
    # Arrange
    user_in = UserCreate(
        email=TEST_EMAIL,
        username=TEST_USERNAME,
        password=TEST_PASSWORD,
        full_name=TEST_FULL_NAME,
    )
    user = await crud_user.create_async(db, obj_in=user_in)

    # Act
    removed_user = await crud_user.remove_async(db, id=user.id)

    # Assert
    assert removed_user is not None
    assert removed_user.id == user.id

    # Verify the user is removed
    db_user = await crud_user.get_async(db, id=user.id)
    assert db_user is None
