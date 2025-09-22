import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user import CRUDUser
from app.models import User
from app.schemas.user import UserCreate, UserUpdate

# Create an instance of CRUDUser for testing
user_crud = CRUDUser(User)


# Fixtures
@pytest.fixture
def mock_user():
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
        role_id=1,
    )


@pytest.fixture
def mock_user_create():
    return UserCreate(
        username="newuser", email="new@example.com", password="password123", role_id=1
    )


@pytest.fixture
def mock_user_update():
    return UserUpdate(email="updated@example.com", is_active=False)


# Helper function to create a mock result
def create_mock_result(return_value, is_list=False):
    mock_result = MagicMock()
    if is_list:
        mock_result.scalars.return_value.all.return_value = return_value
    else:
        mock_result.scalars.return_value.first.return_value = return_value
    return mock_result


# Tests
class TestCRUDUser:
    @pytest.mark.asyncio
    async def test_create_user_success(self, mock_user, mock_user_create):
        """Test creating a user with valid data"""
        db = AsyncMock(spec=AsyncSession)
        db.scalar.return_value = mock_user

        result = await user_crud.create_async(db, obj_in=mock_user_create)

        assert result.username == mock_user_create.username
        assert result.email == mock_user_create.email
        assert result.is_active is True
        db.add.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_by_id(self, mock_user):
        """Test retrieving a user by ID"""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = create_mock_result(mock_user)

        result = await user_crud.get_async(db, 1)

        assert result.id == 1
        assert result.username == "testuser"
        db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_by_email(self, mock_user):
        """Test retrieving a user by email"""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = create_mock_result(mock_user)

        result = await user_crud.get_by_email_async(db, email="test@example.com")

        assert result.email == "test@example.com"
        db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user(self, mock_user, mock_user_update):
        """Test updating a user"""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = create_mock_result(mock_user)

        result = await user_crud.update_async(
            db, db_obj=mock_user, obj_in=mock_user_update
        )

        assert result.email == "updated@example.com"
        assert result.is_active is False
        db.add.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_user(self, mock_user):
        """Test removing a user"""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = create_mock_result(mock_user)

        result = await user_crud.remove_async(db, id=1)

        assert result.username == "testuser"
        db.delete.assert_called_once_with(mock_user)
        db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_authenticate_user(self, mock_user):
        """Test user authentication"""
        db = AsyncMock(spec=AsyncSession)
        db.execute.return_value = create_mock_result(mock_user)

        with patch("app.crud.user.verify_password", return_value=True):
            result = await user_crud.authenticate_async(
                db, username="testuser", password="password123"
            )

            assert result.username == "testuser"
            assert result.email == "test@example.com"
            db.execute.assert_called_once()
