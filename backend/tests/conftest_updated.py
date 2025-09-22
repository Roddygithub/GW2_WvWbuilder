"""
Updated test configuration and fixtures for the GuildWars2_TeamBuilder test suite.
This file provides a comprehensive test setup with improved organization and utilities.
"""

import asyncio
import pytest
from typing import AsyncGenerator, Dict, Any, List, Optional, Callable

from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_async_db
from app.main import app as fastapi_app
from app.models import User, Role, Profession, Build, Composition
from app.core.security import get_password_hash

# Test database configuration
TEST_SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:?cache=shared"

# Override settings for tests
settings.TESTING = True
settings.DATABASE_URL = "sqlite:///:memory:"
settings.ASYNC_SQLALCHEMY_DATABASE_URI = TEST_SQLALCHEMY_DATABASE_URL

# Create async engine and session for testing
async_engine = create_async_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
)

# Create sync engine for migrations and setup
sync_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SyncTestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=sync_engine
)

# Create all tables
Base.metadata.create_all(bind=sync_engine)


# Event loop fixture
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


# Database setup and teardown
@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Set up the test database with all tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield  # Test functions run here

    # Teardown
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await async_engine.dispose()


# Database session fixture
@pytest.fixture(scope="function")
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Create a new database session with automatic rollback after each test."""
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()


# Test client fixtures
@pytest.fixture(scope="module")
def app() -> FastAPI:
    """Create a test FastAPI application with overridden dependencies."""
    # Create test database tables
    Base.metadata.create_all(bind=sync_engine)

    # Override the database dependency
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with TestingSessionLocal() as session:
            yield session

    fastapi_app.dependency_overrides[get_async_db] = override_get_db

    return fastapi_app


@pytest.fixture(scope="module")
def client(app: FastAPI) -> TestClient:
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture(scope="module")
async def async_client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for the FastAPI application."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# Test data factories
@pytest.fixture(scope="function")
async def role_factory(db: AsyncSession) -> Callable[..., Role]:
    """Factory for creating test roles."""

    async def _role_factory(
        name: str = "test_role",
        description: str = "Test Role",
        permission_level: int = 1,
        is_default: bool = False,
    ) -> Role:
        role = Role(
            name=name,
            description=description,
            permission_level=permission_level,
            is_default=is_default,
        )
        db.add(role)
        await db.commit()
        await db.refresh(role)
        return role

    return _role_factory


@pytest.fixture(scope="function")
async def user_factory(db: AsyncSession, role_factory) -> Callable[..., User]:
    """Factory for creating test users."""

    async def _user_factory(
        username: str = "testuser",
        email: str = "test@example.com",
        password: str = "testpassword",
        is_active: bool = True,
        is_superuser: bool = False,
        roles: Optional[List[Role]] = None,
    ) -> User:
        if roles is None:
            # Create a default role if none provided
            role = await role_factory()
            roles = [role]

        hashed_password = get_password_hash(password)
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_active=is_active,
            is_superuser=is_superuser,
            roles=roles,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    return _user_factory


@pytest.fixture(scope="function")
async def profession_factory(db: AsyncSession) -> Callable[..., Profession]:
    """Factory for creating test professions."""

    async def _profession_factory(
        name: str = "Test Profession",
        description: str = "A test profession",
        icon: str = "test_icon.png",
    ) -> Profession:
        profession = Profession(
            name=name,
            description=description,
            icon=icon,
        )
        db.add(profession)
        await db.commit()
        await db.refresh(profession)
        return profession

    return _profession_factory


@pytest.fixture(scope="function")
async def build_factory(
    db: AsyncSession, user_factory, profession_factory
) -> Callable[..., Build]:
    """Factory for creating test builds."""

    async def _build_factory(
        name: str = "Test Build",
        description: str = "A test build",
        game_mode: str = "pve",
        is_public: bool = True,
        user: Optional[User] = None,
        profession: Optional[Profession] = None,
    ) -> Build:
        if user is None:
            user = await user_factory()

        if profession is None:
            profession = await profession_factory()

        build = Build(
            name=name,
            description=description,
            game_mode=game_mode,
            is_public=is_public,
            user_id=user.id,
            profession_id=profession.id,
        )

        db.add(build)
        await db.commit()
        await db.refresh(build)
        return build

    return _build_factory


# Authentication helpers
@pytest.fixture(scope="function")
async def auth_headers(
    client: TestClient,
    user_factory,
) -> Callable[..., Dict[str, str]]:
    """Factory for creating authentication headers."""

    async def _auth_headers(
        username: str = "testuser",
        password: str = "testpassword",
        is_superuser: bool = False,
    ) -> Dict[str, str]:
        # Create a test user
        user = await user_factory(
            username=username,
            email=f"{username}@example.com",
            password=password,
            is_superuser=is_superuser,
        )

        # Get access token
        response = client.post(
            f"{settings.API_V1_STR}/auth/login/access-token",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == status.HTTP_200_OK
        token = response.json()["access_token"]

        return {"Authorization": f"Bearer {token}"}

    return _auth_headers


# Test data setup
@pytest.fixture(scope="function")
async def test_data(
    db: AsyncSession,
    user_factory,
    role_factory,
    profession_factory,
    build_factory,
) -> Dict[str, Any]:
    """Set up test data for integration tests."""
    # Create roles
    admin_role = await role_factory(
        name="admin",
        description="Administrator",
        permission_level=10,
        is_default=False,
    )

    user_role = await role_factory(
        name="user",
        description="Regular User",
        permission_level=1,
        is_default=True,
    )

    # Create users
    admin_user = await user_factory(
        username="admin",
        email="admin@example.com",
        password="admin123",
        is_superuser=True,
        roles=[admin_role],
    )

    test_user = await user_factory(
        username="testuser",
        email="test@example.com",
        password="test123",
        is_superuser=False,
        roles=[user_role],
    )

    # Create professions
    guardian = await profession_factory(
        name="Guardian",
        description="A versatile profession that can fill multiple roles.",
        icon="guardian.png",
    )

    warrior = await profession_factory(
        name="Warrior",
        description="A heavy armor profession that excels at melee combat.",
        icon="warrior.png",
    )

    # Create builds
    guardian_build = await build_factory(
        name="Power Dragonhunter",
        description="High DPS Dragonhunter build for PvE.",
        game_mode="pve",
        is_public=True,
        user=test_user,
        profession=guardian,
    )

    warrior_build = await build_factory(
        name="Berserker Banner Slave",
        description="Support Warrior with banners for PvE.",
        game_mode="pve",
        is_public=True,
        user=admin_user,
        profession=warrior,
    )

    # Create compositions
    raid_comp = Composition(
        name="Power Quickness Firebrand",
        description="Support Firebrand with Quickness for raids.",
        squad_size=10,
        is_public=True,
        user_id=admin_user.id,
        builds=[guardian_build],
    )

    wvw_comp = Composition(
        name="WvW Zerg Frontline",
        description="Frontline composition for WvW zergs.",
        squad_size=50,
        is_public=True,
        user_id=test_user.id,
        builds=[guardian_build, warrior_build],
    )

    db.add_all([raid_comp, wvw_comp])
    await db.commit()

    return {
        "users": {"admin": admin_user, "test": test_user},
        "roles": {"admin": admin_role, "user": user_role},
        "professions": {"guardian": guardian, "warrior": warrior},
        "builds": {"guardian": guardian_build, "warrior": warrior_build},
        "compositions": {"raid": raid_comp, "wvw": wvw_comp},
    }
