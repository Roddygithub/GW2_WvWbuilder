"""Tests for users API endpoints."""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_password_hash
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate
from app.crud import user as crud_user
from app.db.session import get_async_db
from app.main import app
from tests.utils.utils import random_email, random_lower_string
from app.db.base import Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)


# Create tables
async def init_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Override get_async_db dependency
async def override_get_async_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_async_db] = override_get_async_db

# Initialize test client
client = TestClient(app)

# Initialize test database
import asyncio

asyncio.get_event_loop().run_until_complete(init_test_db())


@pytest_asyncio.fixture
async def test_user() -> User:
    """Create a test user."""
    email = random_email()
    password = random_lower_string()
    username = email.split("@")[0]

    user_in = UserCreate(email=email, password=password, username=username, full_name="Test User")
    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        username=username,
        full_name=user_in.full_name,
        is_active=True,
    )
    async with TestingSessionLocal() as db:
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user


@pytest_asyncio.fixture
async def test_superuser() -> User:
    """Create a test superuser."""
    email = "superuser@example.com"
    password = random_lower_string()

    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        username="superuser",
        full_name="Super User",
        is_superuser=True,
        is_active=True,
    )
    async with TestingSessionLocal() as db:
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user


def get_user_authentication_headers(client: TestClient, email: str, password: str) -> dict[str, str]:
    """Get authentication headers for a user."""
    login_data = {
        "username": email,
        "password": password,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    access_token = tokens["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


def test_create_user(client: TestClient) -> None:
    """Test creating a new user."""
    email = random_email()
    password = random_lower_string()
    username = email.split("@")[0]

    data = {
        "email": email,
        "password": password,
        "username": username,
        "full_name": "Test User",
    }

    r = client.post(
        f"{settings.API_V1_STR}/users/",
        json=data,
    )

    assert r.status_code == 200
    created_user = r.json()
    assert created_user["email"] == email
    assert created_user["username"] == username
    assert "id" in created_user
    assert "hashed_password" not in created_user


def test_read_user_me(client: TestClient, test_user: User) -> None:
    """Test reading the current user's profile."""
    headers = get_user_authentication_headers(client, test_user.email, test_user.hashed_password)

    r = client.get(
        f"{settings.API_V1_STR}/users/me",
        headers=headers,
    )

    assert r.status_code == 200
    current_user = r.json()
    assert current_user["email"] == test_user.email
    assert current_user["username"] == test_user.username
    assert "id" in current_user
    assert "hashed_password" not in current_user


def test_update_user_me(client: TestClient, test_user: User) -> None:
    """Test updating the current user's profile."""
    headers = get_user_authentication_headers(client, test_user.email, test_user.hashed_password)

    new_full_name = "Updated Name"
    data = {"full_name": new_full_name}

    r = client.put(
        f"{settings.API_V1_STR}/users/me",
        headers=headers,
        json=data,
    )

    assert r.status_code == 200
    updated_user = r.json()
    assert updated_user["full_name"] == new_full_name
    assert updated_user["email"] == test_user.email


def test_read_users(client: TestClient, test_superuser: User) -> None:
    """Test reading all users (admin only)."""
    headers = get_user_authentication_headers(client, test_superuser.email, test_superuser.hashed_password)

    r = client.get(
        f"{settings.API_V1_STR}/users/",
        headers=headers,
    )

    assert r.status_code == 200
    users = r.json()
    assert isinstance(users, list)
    assert len(users) > 0
    assert any(user["email"] == test_superuser.email for user in users)


def test_read_user_by_id(client: TestClient, test_superuser: User, test_user: User) -> None:
    """Test reading a user by ID (admin only)."""
    headers = get_user_authentication_headers(client, test_superuser.email, test_superuser.hashed_password)

    r = client.get(
        f"{settings.API_V1_STR}/users/{test_user.id}",
        headers=headers,
    )

    assert r.status_code == 200
    user = r.json()
    assert user["email"] == test_user.email
    assert user["username"] == test_user.username
    assert "id" in user
    assert "hashed_password" not in user


def test_update_user(client: TestClient, test_superuser: User, test_user: User) -> None:
    """Test updating a user (admin only)."""
    headers = get_user_authentication_headers(client, test_superuser.email, test_superuser.hashed_password)

    new_email = f"updated_{test_user.email}"
    data = {"email": new_email}

    r = client.put(
        f"{settings.API_V1_STR}/users/{test_user.id}",
        headers=headers,
        json=data,
    )

    assert r.status_code == 200
    updated_user = r.json()
    assert updated_user["email"] == new_email
    assert updated_user["username"] == test_user.username


def test_delete_user(client: TestClient, test_superuser: User, test_user: User) -> None:
    """Test deleting a user (admin only)."""
    headers = get_user_authentication_headers(client, test_superuser.email, test_superuser.hashed_password)

    # First, create a copy of the user to delete
    email = random_email()
    password = random_lower_string()
    username = email.split("@")[0]

    user_data = UserCreate(email=email, password=password, username=username, full_name="User to Delete")

    # Create the user in the database
    db = next(override_get_db())
    user_to_delete = crud_user.create(db, obj_in=user_data)

    # Now delete the user
    r = client.delete(
        f"{settings.API_V1_STR}/users/{user_to_delete.id}",
        headers=headers,
    )

    assert r.status_code == 200
    deleted_user = r.json()
    assert deleted_user["id"] == user_to_delete.id

    # Verify the user no longer exists
    db_user = crud_user.get(db, id=user_to_delete.id)
    assert db_user is None
