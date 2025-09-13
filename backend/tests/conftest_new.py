"""
Test configuration and fixtures for the GuildWars2_TeamBuilder test suite.
This file provides the test configuration, fixtures, and utilities needed for testing.
"""
import asyncio
import os
import pytest
from typing import AsyncGenerator, Dict, Any, List, Optional

from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.db.session import async_session, engine
from app.main import app
from app.models import User, Role, Profession, Build, Composition, CompositionTag
from app.schemas.user import UserCreate, UserUpdate
from app.crud.crud_user import user as crud_user
from app.core.security import get_password_hash, create_access_token

# Test database configuration
TEST_SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Override settings for tests
settings.TESTING = True
settings.DATABASE_URL = TEST_SQLALCHEMY_DATABASE_URL

# Create async engine and session for testing
async_engine = create_async_engine(
    TEST_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
)

# Create test client
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def db_engine():
    """Create and drop test database tables."""
    # Create all tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield async_engine
    
    # Clean up
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def app() -> FastAPI:
    """Create a test FastAPI application."""
    return app

@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create a test client for the FastAPI application."""
    return TestClient(app)

@pytest.fixture
async def async_client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for the FastAPI application."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a database session for testing."""
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()

# Test data fixtures
@pytest.fixture
async def test_role(db_session: AsyncSession) -> Role:
    """Create a test role."""
    role = Role(name="test_role", description="Test Role")
    db_session.add(role)
    await db_session.commit()
    await db_session.refresh(role)
    return role

@pytest.fixture
async def test_user(db_session: AsyncSession, test_role: Role) -> User:
    """Create a test user."""
    user_data = {
        "email": "test@example.com",
        "hashed_password": get_password_hash("testpassword"),
        "is_active": True,
        "is_superuser": False,
        "username": "testuser"
    }
    user = User(**user_data)
    user.roles.append(test_role)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
async def test_profession(db_session: AsyncSession) -> Profession:
    """Create a test profession."""
    profession = Profession(name="Warrior", description="A mighty warrior")
    db_session.add(profession)
    await db_session.commit()
    await db_session.refresh(profession)
    return profession

@pytest.fixture
async def test_build(db_session: AsyncSession, test_user: User, test_profession: Profession) -> Build:
    """Create a test build."""
    build = Build(
        name="Test Build",
        description="Test Build Description",
        created_by=test_user.id,
        profession_id=test_profession.id,
        is_public=True
    )
    db_session.add(build)
    await db_session.commit()
    await db_session.refresh(build)
    return build

@pytest.fixture
async def test_composition(db_session: AsyncSession, test_user: User) -> Composition:
    """Create a test composition."""
    composition = Composition(
        name="Test Composition",
        description="Test Composition Description",
        created_by=test_user.id,
        is_public=True,
        squad_size=5
    )
    db_session.add(composition)
    await db_session.commit()
    await db_session.refresh(composition)
    return composition

@pytest.fixture
async def test_composition_tag(db_session: AsyncSession, test_composition: Composition) -> CompositionTag:
    """Create a test composition tag."""
    tag = CompositionTag(name="test_tag", composition_id=test_composition.id)
    db_session.add(tag)
    await db_session.commit()
    await db_session.refresh(tag)
    return tag

@pytest.fixture
def user_authentication_headers(
    client: TestClient, test_user: User
) -> Dict[str, str]:
    """Get authentication headers for a test user."""
    access_token = create_access_token(subject=test_user.id)
    return {"Authorization": f"Bearer {access_token}"}

# Override the app's database dependency
def override_get_db():
    """Override the get_db dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Apply the override
app.dependency_overrides[get_db] = override_get_db
