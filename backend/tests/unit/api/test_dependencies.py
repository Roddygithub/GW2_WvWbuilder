"""Unit tests for API dependencies."""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from typing_extensions import AsyncGenerator
from fastapi import FastAPI, HTTPException, status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.api import deps
from app.models.user import User


async def redis_client():
    """
    Fournit un client Redis pour les tests et vide la base de données Redis après chaque test.
    """
    if not settings.CACHE_ENABLED:
        pytest.skip("Cache is not enabled in settings")
        return

    client = settings.redis_client
    await client.flushdb()
    yield client
    await client.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    """
    Crée la base de données de test une fois par session et la supprime à la fin.
    """
    database_url = settings.get_async_test_database_url()
    engine = create_async_engine(
        database_url,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False} if "sqlite" in database_url else {},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_session(setup_test_database) -> AsyncGenerator[AsyncSession, None]:
    """
    Fournit une session de base de données transactionnelle pour chaque test.
    Les modifications sont annulées (rollback) après chaque test pour garantir l'isolation.
    """
    database_url = settings.get_async_test_database_url()
    engine = create_async_engine(
        database_url,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False} if "sqlite" in database_url else {},
    )
    TestingSessionLocal = async_sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with TestingSessionLocal() as session:
        await session.begin_nested()
        yield session
        await session.rollback()
        await session.close()


# Fixture pour le client de test HTTP
@pytest_asyncio.fixture(scope="function")
async def app() -> FastAPI:
    """Create a FastAPI app for testing with overridden dependencies."""
    from app.main import create_application

    _app = create_application()
    # Charger la configuration de test
    _app.dependency_overrides[get_db] = get_async_db
    yield _app


@pytest_asyncio.fixture(scope="function")
async def async_client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for making HTTP requests."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_user() -> User:
    """Returns a mock active user."""
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        is_active=True,
        is_superuser=False,
    )


@pytest.fixture
def mock_inactive_user() -> User:
    """Returns a mock inactive user."""
    return User(
        id=2,
        username="inactive",
        email="inactive@example.com",
        is_active=False,
        is_superuser=False,
    )


@pytest.fixture
def mock_superuser() -> User:
    """Returns a mock active superuser."""
    return User(
        id=3,
        username="super",
        email="super@example.com",
        is_active=True,
        is_superuser=True,
    )


@pytest.mark.asyncio
async def test_get_async_db():
    """Test that the get_async_db dependency yields a session and closes it."""
    # Créer un mock pour la session et ses méthodes asynchrones
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.close = AsyncMock()

    # Créer un mock pour le context manager qui sera retourné par AsyncSessionLocal()
    mock_session_context = AsyncMock()
    mock_session_context.__aenter__.return_value = mock_session

    # Configurer le mock pour AsyncSessionLocal
    with patch("app.db.session.AsyncSessionLocal", return_value=mock_session_context):
        # Appeler la fonction à tester
        db_gen = deps.get_async_db()

        # Récupérer la session du générateur
        session = await anext(db_gen)

        # Vérifier que la session est bien celle retournée par notre mock
        assert session is mock_session

        # Simuler la fin du générateur
        with pytest.raises(StopAsyncIteration):
            await anext(db_gen)

    # Vérifier que les méthodes ont été appelées comme prévu
    mock_session.commit.assert_awaited_once()
    mock_session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_async_db_with_exception():
    """Test that get_async_db properly handles exceptions and closes the session."""
    # Créer un mock pour la session
    mock_session = AsyncMock(spec=AsyncSession)

    # Créer un mock pour le context manager
    mock_session_context = AsyncMock()
    mock_session_context.__aenter__.return_value = mock_session

    # Configurer le mock pour AsyncSessionLocal
    with patch("app.db.session.AsyncSessionLocal", return_value=mock_session_context):
        # Appeler la fonction à tester
        db_gen = deps.get_async_db()

        # Vérifier que la session est bien retournée
        session = await anext(db_gen)
        assert session is mock_session

        # Simuler une erreur
        with pytest.raises(ValueError, match="Simulated error"):
            try:
                # Simuler une erreur pendant l'utilisation de la session
                raise ValueError("Simulated error")
            finally:
                # S'assurer que le générateur est correctement fermé
                await db_gen.aclose()

        # Vérifier que le context manager a été utilisé correctement
        mock_session_context.__aenter__.assert_awaited_once()
        mock_session_context.__aexit__.assert_awaited_once()


async def test_get_current_user_dependency(mock_user: User):
    """Test the get_current_user dependency successfully retrieves a user."""
    mock_db = AsyncMock()
    mock_request = AsyncMock()
    with patch(
        "app.api.deps.security.get_current_user",
        new_callable=AsyncMock,
        return_value={"sub": str(mock_user.id)},
    ):
        with patch(
            "app.api.deps.crud.user.get", new_callable=AsyncMock, return_value=mock_user
        ):
            user = await get_current_user(request=mock_request, db=mock_db)
        assert user == mock_user


async def test_get_current_active_user_success(mock_user: User):
    """Test that an active user passes the get_current_active_user dependency."""
    user = await get_current_active_user(current_user=mock_user)
    assert user == mock_user


async def test_get_current_active_user_inactive(mock_inactive_user: User):
    """Test that an inactive user is rejected by get_current_active_user."""
    with pytest.raises(HTTPException) as exc_info:
        await get_current_active_user(current_user=mock_inactive_user)
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Inactive user" in exc_info.value.detail


async def test_get_current_active_superuser_success(mock_superuser: User):
    """Test that a superuser passes the get_current_active_superuser dependency."""
    user = await get_current_active_superuser(current_user=mock_superuser)
    assert user == mock_superuser


async def test_get_current_active_superuser_not_superuser(mock_user: User):
    """Test that a non-superuser is rejected by get_current_active_superuser."""
    with pytest.raises(HTTPException) as exc_info:
        await get_current_active_superuser(current_user=mock_user)
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "The user doesn't have enough privileges" in exc_info.value.detail
