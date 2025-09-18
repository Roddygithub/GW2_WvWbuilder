"""Test configuration overrides for the application."""
import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.base import Base
from app.db.session import AsyncSessionLocal, async_session
from app.main import app
from tests.test_config import test_settings


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def async_engine():
    """Create an async SQLAlchemy engine for testing."""
    engine = create_async_engine(
        test_settings.TEST_DATABASE_URL,
        echo=True,
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(async_engine):
    """Create a database session for testing with automatic rollback."""
    connection = await async_engine.connect()
    transaction = await connection.begin()
    
    # Create a new session
    TestingSessionLocal = sessionmaker(
        bind=connection,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    session = TestingSessionLocal()
    
    # Override the dependency
    async def override_get_db():
        try:
            yield session
        finally:
            pass  # Don't close the session here, we'll handle it in the fixture
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        yield session
    finally:
        await session.close()
        await transaction.rollback()
        await connection.close()
        app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def client(db_session):
    """Create a test client for the FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
async def async_client(db_session):
    """Create an async test client for the FastAPI application."""
    from httpx import AsyncClient
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="function")
async def test_user(db_session):
    """Create a test user."""
    from app.crud.crud_user import user as crud_user
    from app.schemas.user import UserCreate
    
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="testpassword",
        full_name="Test User",
    )
    
    user = await crud_user.create(db_session, obj_in=user_data)
    return user


@pytest.fixture(scope="function")
async def test_profession(db_session):
    """Create a test profession."""
    from app.crud.crud_profession import profession as crud_profession
    from app.schemas.profession import ProfessionCreate
    
    profession_data = ProfessionCreate(
        name="Test Profession",
        description="A test profession",
    )
    
    profession = await crud_profession.create(db_session, obj_in=profession_data)
    return profession


@pytest.fixture(scope="function")
async def test_build(db_session, test_user, test_profession):
    """Create a test build."""
    from app.crud.crud_build import build as crud_build
    from app.schemas.build import BuildCreate
    
    build_data = BuildCreate(
        name="Test Build",
        description="A test build",
        game_mode="wvw",
        team_size=5,
        is_public=True,
        profession_ids=[test_profession.id],
        config={"traits": [1, 2, 3]},
        constraints={"min_healers": 1},
    )
    
    build = await crud_build.create_with_owner(
        db=db_session,
        obj_in=build_data,
        owner_id=test_user.id,
    )
    
    return build
