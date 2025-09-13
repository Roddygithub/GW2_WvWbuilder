"""Tests for user CRUD operations."""
import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, NoResultFound

from app.crud.user import CRUDUser, user
from app.models import User, Role, UserRole
from app.schemas.user import UserCreate, UserUpdate, UserInDB
from app.core.security import get_password_hash
from app.core.exceptions import (
    NotFoundException,
    ValidationException,
    DatabaseException,
    UnauthorizedException
)

# Test data
TEST_EMAIL = "test@example.com"
TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpassword123"
TEST_FULL_NAME = "Test User"
TEST_IS_ACTIVE = True
TEST_IS_SUPERUSER = False
TEST_USER_ID = 1
TEST_ROLE_ID = 1

# Fixtures
@pytest.fixture
def user_data():
    """Return test user data."""
    return {
        "email": TEST_EMAIL,
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD,
        "full_name": TEST_FULL_NAME,
        "is_active": TEST_IS_ACTIVE,
        "is_superuser": TEST_IS_SUPERUSER,
    }

@pytest.fixture
def mock_user():
    """Create a mock user object."""
    return User(
        id=TEST_USER_ID,
        email=TEST_EMAIL,
        username=TEST_USERNAME,
        hashed_password=get_password_hash(TEST_PASSWORD),
        full_name=TEST_FULL_NAME,
        is_active=TEST_IS_ACTIVE,
        is_superuser=TEST_IS_SUPERUSER,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

@pytest.fixture
def mock_role():
    """Create a mock role object."""
    return Role(
        id=TEST_ROLE_ID,
        name="user",
        description="Regular user role",
        permission_level=1,
        is_default=True,
    )

# Test CRUDUser class
class TestCRUDUser:
    """Test cases for CRUDUser class."""

    @pytest.mark.asyncio
    async def test_create_user_success(self, db: Session, user_data, mock_role):
        """Test creating a user with valid data."""
        # Mock the database session and queries
        mock_db = MagicMock(spec=Session)
        
        # Mock role query
        mock_role_query = MagicMock()
        mock_role_query.filter.return_value.first.return_value = mock_role
        
        # Configure the mock_db to return different queries based on the model
        def query_side_effect(model, *args, **kwargs):
            if model == Role:
                return mock_role_query
            return MagicMock()
        
        mock_db.query.side_effect = query_side_effect
        
        # Create the user
        result = user.create(
            db=mock_db,
            obj_in=UserCreate(**user_data)
        )
        
        # Verify the result
        assert result is not None
        assert result.email == TEST_EMAIL
        assert result.username == TEST_USERNAME
        assert result.full_name == TEST_FULL_NAME
        assert result.is_active is True
        assert result.is_superuser is False
        
        # Verify the password was hashed
        assert result.hashed_password != TEST_PASSWORD
        assert "pbkdf2_sha256" in result.hashed_password
        
        # Verify the database interactions
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        
        # Verify default role was assigned
        assert len(result.roles) == 1
        assert result.roles[0].id == TEST_ROLE_ID

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, db: Session, user_data, mock_user):
        """Test creating a user with a duplicate email."""
        # Mock the database to simulate a duplicate email error
        mock_db = MagicMock(spec=Session)
        mock_db.commit.side_effect = IntegrityError(
            statement="", 
            params={}, 
            orig=Exception("duplicate key value violates unique constraint \"ix_users_email\"")
        )
        
        with pytest.raises(ValidationException) as exc_info:
            user.create(
                db=mock_db,
                obj_in=UserCreate(**user_data)
            )
        
        assert "Email already registered" in str(exc_info.value)
        mock_db.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_authenticate_success(self, db: Session, mock_user):
        """Test authenticating a user with correct credentials."""
        # Mock the database query
        mock_db = MagicMock(spec=Session)
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_user
        mock_db.query.return_value = mock_query
        
        # Test authentication
        result = user.authenticate(
            db=mock_db,
            email=TEST_EMAIL,
            password=TEST_PASSWORD
        )
        
        # Verify the result
        assert result is not None
        assert result.email == TEST_EMAIL
        
        # Verify the query was built correctly
        mock_query.filter.assert_called_once()
        filter_arg = mock_query.filter.call_args[0][0]
        assert str(filter_arg).find("users.email") > 0

    @pytest.mark.asyncio
    async def test_authenticate_wrong_password(self, db: Session, mock_user):
        """Test authenticating with wrong password."""
        # Mock the database query
        mock_db = MagicMock(spec=Session)
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_user
        mock_db.query.return_value = mock_query
        
        # Test authentication with wrong password
        result = user.authenticate(
            db=mock_db,
            email=TEST_EMAIL,
            password="wrongpassword"
        )
        
        # Verify authentication failed
        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_inactive_user(self, db: Session, mock_user):
        """Test authenticating an inactive user."""
        # Create an inactive user
        mock_user.is_active = False
        
        # Mock the database query
        mock_db = MagicMock(spec=Session)
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_user
        mock_db.query.return_value = mock_query
        
        # Test authentication
        result = user.authenticate(
            db=mock_db,
            email=TEST_EMAIL,
            password=TEST_PASSWORD
        )
        
        # Verify authentication failed for inactive user
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_email(self, db: Session, mock_user):
        """Test retrieving a user by email."""
        # Mock the database query
        mock_db = MagicMock(spec=Session)
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_user
        mock_db.query.return_value = mock_query
        
        # Get user by email
        result = user.get_by_email(mock_db, email=TEST_EMAIL)
        
        # Verify the result
        assert result is not None
        assert result.email == TEST_EMAIL
        
        # Verify the query was built correctly
        mock_query.filter.assert_called_once()
        filter_arg = mock_query.filter.call_args[0][0]
        assert str(filter_arg).find("users.email") > 0

    @pytest.mark.asyncio
    async def test_update_user(self, db: Session, mock_user):
        """Test updating a user's information."""
        # Mock the database query
        mock_db = MagicMock(spec=Session)
        
        # Update data
        update_data = {
            "email": "updated@example.com",
            "username": "updateduser",
            "full_name": "Updated User",
            "is_active": False,
        }
        
        # Perform the update
        result = user.update(
            db=mock_db,
            db_obj=mock_user,
            obj_in=UserUpdate(**update_data)
        )
        
        # Verify the result
        assert result is not None
        assert result.email == update_data["email"]
        assert result.username == update_data["username"]
        assert result.full_name == update_data["full_name"]
        assert result.is_active == update_data["is_active"]
        
        # Verify the database interactions
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_password(self, db: Session, mock_user):
        """Test updating a user's password."""
        # Mock the database
        mock_db = MagicMock(spec=Session)
        
        # New password
        new_password = "newsecurepassword123"
        
        # Update the password
        result = user.update_password(
            db=mock_db,
            db_user=mock_user,
            new_password=new_password
        )
        
        # Verify the result
        assert result is not None
        assert result.hashed_password != new_password  # Should be hashed
        assert result.hashed_password != mock_user.hashed_password  # Should be different from old hash
        
        # Verify the database interactions
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_user(self, db: Session, mock_user):
        """Test deleting a user."""
        # Mock the database session
        mock_db = MagicMock(spec=Session)
        
        # Mock the query to return our test user
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_user
        mock_db.query.return_value = mock_query
        
        # Delete the user
        result = user.remove(db=mock_db, id=TEST_USER_ID)
        
        # Verify the result
        assert result == 1  # Number of rows affected
        
        # Verify the database interactions
        mock_db.query.assert_called_once_with(User)
        mock_db.query.return_value.filter.return_value.delete.assert_called_once()
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_nonexistent_user(self, db: Session):
        """Test deleting a non-existent user."""
        # Mock the database session
        mock_db = MagicMock(spec=Session)
        
        # Mock the query to return None (user not found)
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        # Try to delete a non-existent user
        with pytest.raises(NotFoundException) as exc_info:
            user.remove(db=mock_db, id=999)  # Non-existent user ID
        
        # Verify the exception
        assert "User not found" in str(exc_info.value)
        mock_db.rollback.assert_called_once()

# Test the user instance
class TestUserInstance:
    """Test cases for the user instance."""
    
    @pytest.mark.asyncio
    async def test_user_instance_creation(self):
        """Test that the user instance is created correctly."""
        from app.crud.user import user
        assert isinstance(user, CRUDUser)
        assert user.model == User

    @pytest.mark.asyncio
    async def test_user_instance_methods(self):
        """Test that the user instance has the expected methods."""
        from app.crud.user import user
        assert hasattr(user, "create")
        assert hasattr(user, "authenticate")
        assert hasattr(user, "get_by_email")
        assert hasattr(user, "update")
        assert hasattr(user, "update_password")
        assert hasattr(user, "remove")
