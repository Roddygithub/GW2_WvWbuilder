"""Tests for the User model."""
import pytest
from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models import User, Role, Build, Composition, Comment, Rating, Favorite, UserActivity
from app.schemas.user import UserCreate, UserUpdate, UserInDB
from app.core.security import get_password_hash, verify_password

# Use function scope for tests
pytestmark = pytest.mark.asyncio

@pytest.fixture
async def test_role(async_db: AsyncSession):
    """Create a test role."""
    role = Role(name="test_role", description="Test Role", permission_level=1)
    async_db.add(role)
    return role

@pytest.fixture
async def test_user(async_db: AsyncSession, test_role):
    """Create a test user with a role."""
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
        username="testuser",
        roles=[test_role]
    )
    async_db.add(user)
    return user

async def test_create_user(async_db: AsyncSession):
    """Test creating a user."""
    # Create a test user
    user = User(
        email="test2@example.com",
        hashed_password="hashed_password",
        username="testuser2"
    )
    
    # Add to session
    async_db.add(user)
    
    # Flush to get the ID without committing
    await async_db.flush()
    
    # Assertions
    assert user.id is not None
    assert user.email == "test2@example.com"
    assert user.is_active is True
    assert user.created_at is not None
    assert user.updated_at is not None
    assert user.last_login is None
    assert user.is_superuser is False
    assert user.is_superuser is False
    assert user.username == "testuser2"

async def test_user_roles_relationship(test_user: User):
    """Test user roles relationship."""
    # Assertions
    assert len(test_user.roles) == 1
    assert test_user.roles[0].name == "test_role"

async def test_user_representation(test_user: User):
    """Test user string representation."""
    assert str(test_user) == f"<User {test_user.username}>"
    assert repr(test_user) == f"<User {test_user.username}>"

async def test_user_equality(test_user: User):
    """Test user equality comparison."""
    # Ensure test_user has an ID
    test_user.id = 1
    
    # Create another user with the same ID but different attributes
    other_user = User(
        id=test_user.id,  # Same ID
        username="different_username",
        email="different@example.com",
        hashed_password="different_hash"
    )
    
    # Users with the same ID should be considered equal
    assert test_user == other_user
    assert hash(test_user) == hash(other_user)
    
    # Different user should not be equal
    different_user = User(
        id=test_user.id + 1,  # Different ID
        username="different_user",
        email="another@example.com",
        hashed_password="hash"
    )
    assert test_user != different_user
    assert test_user != "not_a_user"  # Should not raise TypeError

async def test_user_relationships(test_user: User, async_db: AsyncSession):
    """Test user relationships are properly set up."""
    # Test roles relationship
    assert len(test_user.roles) == 1
    assert test_user.roles[0].name == "test_role"
    
    # Test builds relationship
    build = Build(
        name="Test Build",
        description="Test Description",
        game_mode="pve",
        user_id=test_user.id
    )
    async_db.add(build)
    await async_db.flush()
    
    # Test composition relationship
    composition = Composition(
        name="Test Composition",
        description="Test Description",
        game_mode="pve",
        created_by=test_user.id
    )
    async_db.add(composition)
    await async_db.flush()
    
    # Test comments relationship
    comment = Comment(
        content="Test comment",
        user_id=test_user.id,
        build_id=build.id
    )
    async_db.add(comment)
    await async_db.flush()
    
    # Test ratings relationship
    rating = Rating(
        value=5,
        user_id=test_user.id,
        build_id=build.id
    )
    async_db.add(rating)
    await async_db.flush()
    
    # Test favorites relationship
    favorite = Favorite(
        user_id=test_user.id,
        build_id=build.id
    )
    async_db.add(favorite)
    await async_db.flush()
    
    # Test activity relationship
    activity = UserActivity(
        user_id=test_user.id,
        action="test_action",
        details={"test": "data"}
    )
    async_db.add(activity)
    await async_db.flush()
    
    # Refresh user to load relationships
    await async_db.refresh(test_user, ['builds', 'compositions', 'comments', 'ratings', 'favorites', 'activities'])
    
    # Assert relationships
    assert len(test_user.builds) == 1
    assert test_user.builds[0].name == "Test Build"
    assert len(test_user.compositions) == 1
    assert test_user.compositions[0].name == "Test Composition"
    assert len(test_user.comments) == 1
    assert test_user.comments[0].content == "Test comment"
    assert len(test_user.ratings) == 1
    assert test_user.ratings[0].value == 5
    assert len(test_user.favorites) == 1
    assert test_user.favorites[0].build_id == build.id
    assert len(test_user.activities) == 1
    assert test_user.activities[0].action == "test_action"
    assert hasattr(test_user, 'compositions')
    assert isinstance(test_user.compositions, list)
