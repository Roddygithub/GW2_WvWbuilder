"""
Configuration des fixtures de test pour la base de données.

Ce module définit les fixtures nécessaires pour les tests unitaires et d'intégration.
"""

import asyncio
import os
import sys
from typing import AsyncGenerator, Generator, Callable, Any

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.pool import StaticPool

# Ajouter le répertoire racine au chemin Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.base import Base
from app.db.session import get_async_db
from app.main import create_application

# URL de la base de données de test
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Configuration du moteur de base de données de test
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=True,
    future=True,
    connect_args={"check_same_thread": False, "timeout": 30, "uri": True},
    poolclass=StaticPool,
)

# Création d'une session de test
TestingSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def init_test_db() -> None:
    """Initialize the test database with all tables."""
    # Création des tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture
def override_get_db(init_test_db) -> Callable[..., AsyncGenerator[AsyncSession, None]]:
    """Override the get_db dependency for testing."""

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with TestingSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    return _override_get_db


@pytest.fixture
def app(override_get_db: Callable[..., AsyncGenerator[AsyncSession, None]]) -> FastAPI:
    """Create a test FastAPI application."""
    app = create_application()
    app.dependency_overrides[get_async_db] = override_get_db
    return app


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client for making HTTP requests."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def db_session(init_test_db) -> AsyncGenerator[AsyncSession, None]:
    """Create a clean database session for testing."""
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Fixtures pour les données de test
@pytest.fixture
def test_password() -> str:
    return "securepassword"


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession, test_password: str) -> dict[str, Any]:
    """Create a test user."""
    from app.models.user import User

    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=test_password,  # Dans un vrai test, utilisez get_password_hash
        full_name="Test User",
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "hashed_password": user.hashed_password,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
    }
