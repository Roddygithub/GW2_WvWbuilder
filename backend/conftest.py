"""
Configuration des fixtures de test pour l'application GW2 WvW Builder.

Ce module définit les fixtures partagées pour les tests unitaires et d'intégration.
"""
import asyncio
import os
import sys
import uuid
from typing import Any, AsyncGenerator, Callable, Dict, Generator, List, Optional

import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import text, event
from sqlalchemy.ext.asyncio import (
    AsyncSession, 
    create_async_engine, 
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

# Configuration des chemins
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import des dépendances de l'application
from app.main import create_application
from app.core.security import create_access_token, get_password_hash
from app.models import Base
from app.models.user import User

# Configuration de l'environnement de test
os.environ["TESTING"] = "True"
os.environ["ENVIRONMENT"] = "testing"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"

# Désactiver le cache et Redis pour les tests
os.environ["CACHE_ENABLED"] = "False"
os.environ["REDIS_URL"] = ""

# Configuration du moteur de base de données de test
TEST_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    
    # Configurer le fuseau horaire pour la session de test
    os.environ['TZ'] = 'UTC'
    
    yield loop
    
    # Nettoyage après les tests
    if not loop.is_closed():
        pending = asyncio.all_tasks(loop=loop)
        for task in pending:
            task.cancel()
            try:
                loop.run_until_complete(task)
            except (asyncio.CancelledError, RuntimeError):
                pass
        
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

@pytest.fixture(scope="session")
async def engine():
    """Create database engine for tests."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
        connect_args={
            "check_same_thread": False,
            "timeout": 30,
            "uri": True
        },
        poolclass=StaticPool
    )
    
    # Créer toutes les tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("PRAGMA foreign_keys=ON"))
    
    yield engine
    
    # Nettoyage
    await engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def db_session(engine):
    """Create a fresh database session for each test with automatic rollback."""
    connection = await engine.connect()
    transaction = await connection.begin()
    
    # Créer une session liée à cette connexion
    TestingSessionLocal = async_sessionmaker(
        bind=connection,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False
    )
    session = TestingSessionLocal()
    
    # Activer les contraintes de clé étrangère pour SQLite
    await connection.execute(text("PRAGMA foreign_keys=ON"))
    
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
        if transaction.is_active:
            await transaction.rollback()
        await connection.close()

@pytest.fixture
def override_get_db(db_session: AsyncSession):
    """Override the get_db dependency for testing."""
    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        try:
            yield db_session
            await db_session.commit()
        except Exception as e:
            await db_session.rollback()
            raise e
        finally:
            await db_session.close()
    
    return _override_get_db

# Test data fixtures

@pytest.fixture
def test_password() -> str:
    """Return a test password."""
    return "securepassword123!"

@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession, test_password: str) -> User:
    """Create a test user."""
    user = User(
        username=f"testuser_{uuid.uuid4().hex[:8]}",
        email=f"test_{uuid.uuid4().hex[:8]}@example.com",
        hashed_password=get_password_hash(test_password),
        full_name="Test User",
        is_active=True,
        is_superuser=False
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return user

@pytest_asyncio.fixture
async def test_superuser(db_session: AsyncSession, test_password: str) -> User:
    """Create a test superuser."""
    user = User(
        username=f"admin_{uuid.uuid4().hex[:8]}",
        email=f"admin_{uuid.uuid4().hex[:8]}@example.com",
        hashed_password=get_password_hash(test_password),
        full_name="Admin User",
        is_active=True,
        is_superuser=True
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return user

@pytest.fixture
def access_token(test_user: User) -> str:
    """Create an access token for testing."""
    return create_access_token(subject=test_user.id)

@pytest.fixture
def authorized_client(client: TestClient, access_token: str) -> TestClient:
    """Return an authorized client with a valid token."""
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    return client

@pytest.fixture
def app(override_get_db) -> FastAPI:
    """Create a test FastAPI application."""
    from app.main import app
    from app.core.deps import get_db
    
    # Surcharger les dépendances
    app.dependency_overrides[get_db] = override_get_db
    
    # Désactiver le rate limiting pour les tests
    app.dependency_overrides.update({
        # Ajouter d'autres dépendances à surcharger ici
    })
    
    return app

@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)

@pytest_asyncio.fixture
async def async_client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for the FastAPI app."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
