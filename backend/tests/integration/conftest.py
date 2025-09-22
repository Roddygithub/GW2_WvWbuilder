"""Configuration pour les tests d'intégration."""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.core.config import settings
from app.db.session import get_db
from app.main import app
from fastapi.testclient import TestClient
from fastapi import FastAPI
from typing import AsyncGenerator
import asyncio

# Base de données de test SQLite en mémoire
DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Création du moteur de test
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Session de test
TestingSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
)

# Surcharge de la dépendance de la base de données
async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Configuration de l'application de test
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def async_db_engine():
    """Create engine and databases."""
    # Créer toutes les tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Nettoyage après les tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture
def app() -> FastAPI:
    """Return app with test dependencies."""
    app.dependency_overrides[get_db] = override_get_db
    return app

@pytest.fixture
async def db_session(async_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a new database session for testing."""
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create a test client for the API."""
    return TestClient(app)
