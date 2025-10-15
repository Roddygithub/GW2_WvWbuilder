"""Configuration pour les tests d'intégration."""

import os
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from fastapi import FastAPI
from typing import AsyncGenerator
import asyncio

# Configuration des variables d'environnement pour les tests
os.environ["TESTING"] = "True"
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_async_db
from app.main import create_application
from app.models.user import User
from app.models.role import Role
from app.core.security import get_password_hash

# Création du moteur de test
engine = create_async_engine(
    settings.ASYNC_SQLALCHEMY_DATABASE_URI,
    echo=True,
    future=True,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Session de test asynchrone
TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


# Surcharge de la dépendance de la base de données
async def override_get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Configuration de l'application de test
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
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


@pytest_asyncio.fixture(scope="session")
async def app() -> FastAPI:
    """Create a test application with overridden dependencies."""
    # Créer l'application de test
    app = create_application()

    # Surcharger les dépendances
    app.dependency_overrides[get_async_db] = override_get_async_db

    # Créer un utilisateur de test
    async with TestingSessionLocal() as session:
        # Créer un rôle de test s'il n'existe pas
        role = await session.execute("SELECT * FROM role WHERE name = 'user'")
        role = role.scalar_one_or_none()

        if not role:
            role = Role(name="user", description="Test User Role")
            session.add(role)
            await session.commit()
            await session.refresh(role)

        # Créer un utilisateur de test
        user = await session.execute(
            "SELECT * FROM user WHERE email = 'test@example.com'"
        )
        user = user.scalar_one_or_none()

        if not user:
            user = User(
                email="test@example.com",
                hashed_password=get_password_hash("testpassword"),
                full_name="Test User",
                is_active=True,
                role_id=role.id,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)

    yield app


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
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
    """Create a test client for the API with authentication."""
    from fastapi.testclient import TestClient
    from jose import jwt
    from datetime import datetime, timedelta

    # Créer un token JWT pour les tests
    to_encode = {
        "sub": "1",
        "exp": datetime.utcnow() + timedelta(minutes=30),
    }  # ID de l'utilisateur de test
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    # Créer le client de test avec le token d'authentification
    client = TestClient(app)
    client.headers.update({"Authorization": f"Bearer {token}"})

    return client
