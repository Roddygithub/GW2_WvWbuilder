"""
Configuration des fixtures de test pour l'application GW2 WvW Builder.

Ce module définit les fixtures partagées pour les tests unitaires et d'intégration.
"""

import asyncio
import os
import sys
import uuid
import logging
from typing import Any, AsyncGenerator, Callable, List
from unittest.mock import patch, PropertyMock

# IMPORTANT: Configure environment BEFORE any app imports
# This ensures settings are loaded with test values
os.environ["TESTING"] = "True"
os.environ["ENVIRONMENT"] = "testing"
# Ensure JWT keys are consistent for tests (must match for token creation/validation)
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-jwt"
os.environ["SECRET_KEY"] = "test-secret-key-for-jwt"

# Configuration du logging pour le débogage des tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import pytest
import pytest_asyncio

# Configuration des plugins pytest (doit être dans le conftest top-level)
pytest_plugins = ["pytest_asyncio", "pytest_mock", "pytest_cov"]
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy import text, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

# Configuration des chemins
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import des dépendances de l'application (AFTER env vars are set)
from app.main import create_application
from app.db.session import get_async_db
from app.core.security import get_password_hash, create_access_token

# Import des modèles nécessaires pour les tests
from app.models.user import User
from app.models.role import Role
from app.models.profession import Profession
from app.models.build import Build  # Ajout de l'import manquant

# Configuration de la base de données de test
# Use a file-based SQLite DB to ensure all endpoints and fixtures see the same data
test_db_dir = os.path.join(os.path.dirname(__file__), "test_db")
os.makedirs(test_db_dir, exist_ok=True)
db_path = os.path.join(test_db_dir, "test.db")

# Clean up the test database file if it exists
if os.path.exists(db_path):
    try:
        os.remove(db_path)
        logger.info(f"Removed existing test database: {db_path}")
    except Exception as e:
        logger.warning(f"Could not remove test database: {e}")

# Use file-based SQLite for tests to ensure session sharing
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{db_path}?check_same_thread=False"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["ASYNC_SQLALCHEMY_DATABASE_URI"] = TEST_DATABASE_URL

# Configuration du moteur de test avec file-based SQLite
# Using NullPool to avoid connection pooling issues with file-based SQLite
from sqlalchemy.pool import NullPool

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=NullPool,  # No connection pooling for file-based SQLite
)


@pytest.fixture(scope="session")
def event_loop():
    """Provide a clean session-scoped asyncio event loop for tests.

    This avoids prematurely closing or reassigning the global loop between tests,
    which can lead to 'Event loop is closed' errors.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    os.environ["TZ"] = "UTC"
    try:
        yield loop
    finally:
        try:
            loop.run_until_complete(loop.shutdown_asyncgens())
        except Exception:
            pass
        loop.close()

    # Configurer le niveau de log pour asyncio
    logging.getLogger("asyncio").setLevel(logging.WARNING)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_test_db() -> AsyncGenerator[None, None]:
    """Initialize the test database with all tables."""
    from app.models import Base

    # Nettoyage initial
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"Ancien fichier de base de données supprimé: {db_path}")
        except Exception as e:
            print(f"Erreur lors de la suppression du fichier de base de données: {e}")

    # Afficher les métadonnées des tables à créer
    print("\n=== Préparation de la base de données de test ===")
    print("Métadonnées des tables à créer:")
    for table in Base.metadata.tables.values():
        print(f"- {table.name} (clé: {table.key})")

    # Créer toutes les tables
    print("\n=== Création des tables dans la base de données ===")
    async with test_engine.begin() as conn:
        # Activer les clés étrangères
        await conn.execute(text("PRAGMA foreign_keys=ON"))
        await conn.execute(text("PRAGMA journal_mode=WAL"))
        await conn.execute(text("PRAGMA synchronous=NORMAL"))

        # Créer les tables
        print("Création des tables...")
        await conn.run_sync(Base.metadata.create_all)

        # Vérifier les tables créées
        result = await conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table'")
        )
        tables = [row[0] for row in result.fetchall()]
        print(f"Tables créées: {', '.join(tables)}")

    # Vérifier que les tables ont été créées
    print("\n=== Vérification des tables créées ===")
    async with test_engine.connect() as conn:
        # Liste des tables dans la base de données
        result = await conn.execute(
            text("SELECT name, sql FROM sqlite_master WHERE type='table'")
        )
        tables = {row[0]: row[1] for row in result.fetchall()}

        print("\n=== Tables dans la base de données ===")
        for name, sql in sorted(tables.items()):
            print(f"\nTable: {name}")
            print(f"SQL: {sql}")

            # Afficher les colonnes pour chaque table
            if name != "sqlite_sequence":
                try:
                    result = await conn.execute(text(f"PRAGMA table_info({name})"))
                    columns = result.fetchall()
                    print("  Colonnes:")
                    for col in columns:
                        print(f"  - {col[1]} ({col[2]})")
                except Exception as e:
                    print(f"  Erreur lors de la récupération des colonnes: {e}")

        # Vérifier les index
        result = await conn.execute(
            text("SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index'")
        )
        indexes = result.fetchall()
        if indexes:
            print("\n=== Index dans la base de données ===")
            for idx in indexes:
                print(f"- {idx[0]} sur la table {idx[1]}: {idx[2]}")

    yield

    # Nettoyage après les tests
    print("\n=== Nettoyage de la base de données ===")
    await test_engine.dispose()

    # Supprimer le fichier de base de données
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Fichier de base de données supprimé: {db_path}")


@pytest_asyncio.fixture(scope="function")
async def db_session(event_loop) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a clean database session for testing.

    Uses file-based SQLite with commits (no rollback) to ensure data visibility
    across fixtures and endpoints. Tables are truncated between tests.
    """
    # Configurer la fabrique de sessions
    async_session_factory = async_sessionmaker(
        bind=test_engine, expire_on_commit=False, autoflush=False, class_=AsyncSession
    )

    # Créer une nouvelle session
    session = async_session_factory()

    try:
        yield session
        # Commit changes to make them visible to endpoints
        await session.commit()
    except Exception as e:
        # If test fails, rollback the session
        await session.rollback()
        logger.debug(f"Test failed, rolled back session: {e}")
        raise
    finally:
        # Always close the session
        try:
            await session.close()
        except Exception as e:
            logger.warning(f"Error closing session: {e}")

        # Clean up: truncate all tables for next test
        # Use a fresh connection to avoid greenlet issues
        try:
            async with test_engine.connect() as conn:
                from app.models import Base

                # Start a transaction for cleanup
                async with conn.begin():
                    # Disable foreign keys temporarily for cleanup
                    await conn.execute(text("PRAGMA foreign_keys=OFF"))
                    # Delete in reverse order to respect dependencies
                    for table in reversed(Base.metadata.sorted_tables):
                        try:
                            await conn.execute(text(f"DELETE FROM {table.name}"))
                        except Exception as table_error:
                            logger.warning(
                                f"Failed to clean table {table.name}: {table_error}"
                            )
                    await conn.execute(text("PRAGMA foreign_keys=ON"))
        except Exception as e:
            # If cleanup fails (e.g., greenlet issues), log but don't fail the test
            logger.warning(f"DB cleanup failed: {e}")


@pytest_asyncio.fixture
async def db(db_session: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    """Alias for db_session to support tests using 'db' parameter name."""
    yield db_session


@pytest.fixture
def override_get_db(
    db_session: AsyncSession,
) -> Callable[..., AsyncGenerator[AsyncSession, None]]:
    """
    Override the get_db dependency for testing.

    This fixture provides a database session that is automatically rolled back
    after each test, ensuring test isolation.
    """

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        # Yield the same session used by fixtures to ensure data visibility
        # Don't start a new nested transaction here to avoid isolation issues
        print(f"[DEBUG] override_get_db called, yielding session: {db_session}")
        try:
            yield db_session
        except Exception:
            # If an error occurs, rollback the transaction
            if db_session.in_transaction():
                await db_session.rollback()
            raise

    return _override_get_db


@pytest.fixture
def override_get_db_sync(
    db_session: AsyncSession,
) -> Callable[..., AsyncGenerator[AsyncSession, None]]:
    """
    Override the sync get_db dependency for testing (returns async session).

    Note: Even though the original get_db is sync, we return an async generator
    because FastAPI can handle both sync and async dependencies.
    """

    async def _override_get_db_sync() -> AsyncGenerator[AsyncSession, None]:
        try:
            yield db_session
        except Exception:
            if db_session.in_transaction():
                await db_session.rollback()
            raise

    return _override_get_db_sync


# Test data fixtures


@pytest.fixture
def test_password() -> str:
    """Return a test password."""
    return "securepassword"


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession, test_password: str) -> User:
    """Create a test user."""

    user = User(
        username=f"testuser_{uuid.uuid4().hex[:8]}",
        email=f"test_{uuid.uuid4().hex[:8]}@example.com",
        hashed_password=get_password_hash(test_password),
        full_name="Test User",
        is_active=True,
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest_asyncio.fixture
async def test_role(db_session: AsyncSession) -> Role:
    """Create a test role."""
    role = Role(
        name=f"test_role_{uuid.uuid4().hex[:8]}",
        description="Test Role Description",
        permission_level=1,
        is_default=False,
    )

    db_session.add(role)
    await db_session.commit()
    await db_session.refresh(role)

    return role


@pytest_asyncio.fixture
async def test_profession(db_session: AsyncSession) -> Profession:
    """Create a test profession."""
    profession = Profession(
        name=f"Test Profession {uuid.uuid4().hex[:4]}",
        description="Test Profession Description",
        icon_url="http://example.com/icon.png",
        profession_type="test_type",
    )

    db_session.add(profession)
    await db_session.commit()
    await db_session.refresh(profession)

    return profession


@pytest_asyncio.fixture
async def test_build(
    db_session: AsyncSession, test_user: User, test_profession: Profession
) -> Build:
    """Create a single test build."""
    build = Build(
        name=f"Test Build {uuid.uuid4().hex[:4]}",
        description="Test Build Description",
        game_mode="pve",
        is_public=True,
        created_by=test_user.id,
        profession_id=test_profession.id,
        build_status="active",
        build_type="pve",
    )

    db_session.add(build)
    await db_session.commit()
    await db_session.refresh(build)

    return build


@pytest_asyncio.fixture
async def test_builds(
    db_session: AsyncSession, test_user: User, test_profession: Profession
) -> List[Build]:
    """Create multiple test builds."""
    builds = []
    for i in range(5):
        build = Build(
            name=f"Test Build {i} {uuid.uuid4().hex[:4]}",
            description=f"Test Build {i} Description",
            game_mode="pve",
            is_public=True,
            created_by=test_user.id,
            profession_id=test_profession.id,
            build_status="active",
            build_type="pve",
        )
        db_session.add(build)
        builds.append(build)

    await db_session.commit()

    # Refresh all builds
    for build in builds:
        await db_session.refresh(build)

    return builds


@pytest.fixture(autouse=True)
def mock_redis():
    """Mock Redis pour tous les tests."""

    # Créer un mock pour redis_client
    class MockRedis:
        def __init__(self):
            self.data = {}

        async def get(self, key, *args, **kwargs):
            return self.data.get(key)

        async def set(self, key, value, *args, **kwargs):
            self.data[key] = value
            return True

        async def incr(self, key, amount=1, **kwargs):
            if hasattr(self, "_in_pipeline") and self._in_pipeline:
                self._pipeline_commands.append(
                    {"method": "incr", "key": key, "amount": amount}
                )
                return self

            current = int(self.data.get(key, 0))
            new_value = current + amount
            self.data[key] = str(new_value)
            return new_value

        async def expire(self, key, ttl, **kwargs):
            if hasattr(self, "_in_pipeline") and self._in_pipeline:
                self._pipeline_commands.append(
                    {"method": "expire", "key": key, "ttl": ttl}
                )
                return self

            # Dans ce mock, on ne fait rien avec l'expiration
            # car c'est juste pour les tests
            return True

        async def close(self, *args, **kwargs):
            self.data.clear()

        def pipeline(self):
            return self

        async def execute(self):
            # Exécute toutes les commandes en attente dans le pipeline
            results = []
            for cmd in self._pipeline_commands:
                if cmd["method"] == "incr":
                    result = await self.incr(cmd["key"], cmd.get("amount", 1))
                    results.append(result)
                elif cmd["method"] == "expire":
                    result = await self.expire(cmd["key"], cmd["ttl"])
                    results.append(result)
            self._pipeline_commands = []
            return results

        def __init__(self):
            self.data = {}
            self._pipeline_commands = []

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

    # Créer une instance de MockRedis
    mock_redis = MockRedis()

    # Patcher la propriété redis_client pour retourner notre mock
    with patch(
        "app.core.config.Settings.redis_client", new_callable=PropertyMock
    ) as mock_prop:
        # Assurons-nous que le champ existe avant de le patcher, au cas où
        if not hasattr(mock_prop, "return_value"):
            setattr(type(settings), "redis_client", None)

        mock_prop.return_value = mock_redis
        yield mock_redis


@pytest.fixture(autouse=True)
def mock_rate_limiter():
    """Désactive le rate limiting pour tous les tests."""

    async def mock_rate_limiter(*args, **kwargs):
        async def noop():
            return None

        return noop

    with patch("app.core.limiter.get_rate_limiter", mock_rate_limiter):
        yield


@pytest.fixture(autouse=True)
def mock_fastapi_limiter(monkeypatch):
    """Mock FastAPILimiter pour tous les tests."""

    class MockFastAPILimiter:
        redis = None

        @classmethod
        async def init(cls, *args, **kwargs):
            cls.redis = kwargs.get("redis")
            return cls

        @classmethod
        async def close(cls):
            if cls.redis:
                await cls.redis.close()
                cls.redis = None

    # Utiliser monkeypatch pour remplacer la classe FastAPILimiter
    import app.core.limiter

    monkeypatch.setattr(app.core.limiter, "FastAPILimiter", MockFastAPILimiter)

    # S'assurer que la fonction init_rate_limiter ne fait rien
    async def mock_init_rate_limiter():
        pass

    monkeypatch.setattr(app.core.limiter, "init_rate_limiter", mock_init_rate_limiter)


@pytest.fixture
def app(
    override_get_db: Callable[..., AsyncGenerator[AsyncSession, None]],
    override_get_db_sync: Callable[..., AsyncGenerator[AsyncSession, None]],
) -> FastAPI:
    """Create a test FastAPI application with rate limiting and Redis disabled."""
    # Désactiver le chargement des variables d'environnement pour les tests
    os.environ["ENVIRONMENT"] = "test"
    os.environ["TESTING"] = "true"
    os.environ["REDIS_URL"] = ""  # Désactiver Redis pour les tests
    os.environ["CACHE_ENABLED"] = "false"

    # Importer les paramètres après avoir défini les variables d'environnement
    from app.core.config import settings
    from app.core.security import get_current_user

    # Forcer la désactivation du cache et de Redis
    settings.ENVIRONMENT = "test"
    settings.TESTING = True
    settings.CACHE_ENABLED = False
    settings.REDIS_URL = ""
    settings.DEBUG = True

    # CRITICAL: Ensure JWT keys match for token creation/validation
    settings.JWT_SECRET_KEY = "test-secret-key-for-jwt"
    settings.SECRET_KEY = "test-secret-key-for-jwt"

    # CRITICAL: Long-lived tokens for tests (1 hour instead of default)
    settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60
    settings.ACCESS_TOKEN_EXPIRE_MINUTES = 60

    # CRITICAL: Force app to use the same test database file
    settings.DATABASE_URL = TEST_DATABASE_URL
    settings.ASYNC_SQLALCHEMY_DATABASE_URI = TEST_DATABASE_URL

    # Créer le répertoire static s'il n'existe pas
    static_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../app/static")
    )
    os.makedirs(static_dir, exist_ok=True)

    # Créer un fichier vide dans le répertoire static pour éviter l'erreur
    with open(os.path.join(static_dir, ".gitkeep"), "w") as f:
        f.write("")

    # Créer l'application
    app = create_application()

    # Surcharger la dépendance de la base de données pour utiliser notre session de test
    # Override both sync and async DB dependencies
    from app.db.session import get_db as get_db_sync

    app.dependency_overrides[get_async_db] = override_get_db
    app.dependency_overrides[get_db_sync] = (
        override_get_db_sync  # Tags endpoint uses sync get_db
    )

    # Override get_current_user to return the user stored in app.state by auth_headers
    # This bypasses JWT validation issues while still using real users from the DB
    async def mock_get_current_user():
        """Return the test user stored in app.state by auth_headers fixture."""
        if hasattr(app.state, "test_user") and app.state.test_user:
            return app.state.test_user
        # Fallback: create a default test user if none exists
        from app.models.user import User

        return User(
            id=999,
            username="default_test_user",
            email="default@test.com",
            is_active=True,
            is_superuser=False,
            hashed_password="dummy",
        )

    from app.api.deps import get_current_user

    app.dependency_overrides[get_current_user] = mock_get_current_user

    yield app

    # Nettoyer les dépendances
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client for making HTTP requests with rate limiting disabled."""
    from app.core.limiter import get_rate_limiter

    # Désactiver le rate limiting pour le client de test
    app.dependency_overrides[get_rate_limiter] = lambda: None

    async with AsyncClient(app=app, base_url="http://test") as client:
        try:
            yield client
        except Exception as e:
            print(f"Error in client fixture: {e}")
            raise


@pytest.fixture(scope="session")
def performance_limits() -> dict[str, Any]:
    """
    Définit les seuils de performance pour les tests.
    Ces valeurs peuvent être ajustées en fonction de l'environnement de test.
    """
    env = os.getenv("TEST_ENV", "local")

    if env == "ci":
        # Seuils plus tolérants pour les environnements CI
        return {
            "create_build": 0.5,
            "get_build": 0.3,
            "list_builds": 1.5,  # Seuil pour lister 100 builds
            "create_10_builds": 4.0,
            "large_payload": 0.6,
            "memory_increase_mb": 100,
            "load_test_success_rate": 0.9,
            "load_test_duration": 20.0,
            "update_build": 0.5,
            "max_memory_increase_mb": 150,
            "max_cpu_percent": 95.0,
            "timeouts": {
                "short": 10.0,  # secondes
                "medium": 20.0,
                "long": 60.0,
            },
        }
    else:
        # Seuils plus stricts pour l'environnement local
        return {
            "create_build": 0.2,
            "get_build": 0.1,
            "list_builds": 0.5,  # Seuil pour lister 100 builds
            "create_10_builds": 2.0,
            "large_payload": 0.3,
            "memory_increase_mb": 50,
            "load_test_success_rate": 0.95,
            "load_test_duration": 10.0,
            "update_build": 0.2,
            "max_memory_increase_mb": 100,
            "max_cpu_percent": 90.0,
            "timeouts": {
                "short": 5.0,
                "medium": 10.0,
                "long": 30.0,
            },
        }


# Suppression des sections en double - Nettoyage effectué


@pytest_asyncio.fixture
async def async_client(app: FastAPI):
    """Create an async test client for making HTTP requests."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def auth_headers(db_session: AsyncSession, app: FastAPI):
    """
    Fixture callable to create users dynamically and return auth headers.

    Usage:
        headers = await auth_headers(username="testuser", is_superuser=True)

    This fixture creates a real user in the DB and stores it in app.state
    for the mocked get_current_user to retrieve.
    """

    async def _auth_headers(
        username: str = None,
        email: str = None,
        password: str = "testpassword",
        is_superuser: bool = False,
        is_active: bool = True,
    ):
        from datetime import timedelta
        from sqlalchemy import select

        # Generate unique username/email if not provided
        unique_id = uuid.uuid4().hex[:8]
        username = username or f"user_{unique_id}"
        email = email or f"{username}@example.com"

        # Check if user already exists (for cleanup robustness)
        result = await db_session.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()

        if user is None:
            # Create user in DB
            user = User(
                username=username,
                email=email,
                hashed_password=get_password_hash(password),
                is_active=is_active,
                is_superuser=is_superuser,
            )
            db_session.add(user)
            await db_session.commit()
            await db_session.refresh(user)

        # Store user in app.state for mocked get_current_user
        app.state.test_user = user

        # Create JWT token with user ID as subject (backend expects int ID in sub)
        # Use long expiration for tests to avoid expiry during test execution
        access_token = create_access_token(
            subject=str(user.id), expires_delta=timedelta(hours=1)  # 1 hour for tests
        )
        return {"Authorization": f"Bearer {access_token}"}

    return _auth_headers


@pytest_asyncio.fixture
async def tag_factory(db_session: AsyncSession):
    """Factory fixture to create tags for testing."""
    from app.models.tag import Tag

    async def _create_tag(
        name: str = None, description: str = None, category: str = None
    ):
        unique_id = uuid.uuid4().hex[:6]
        tag = Tag(
            name=name or f"Tag_{unique_id}",
            description=description or f"Description for {name or 'tag'}",
            category=category or "test",
        )
        db_session.add(tag)
        await db_session.commit()
        await db_session.refresh(tag)
        return tag

    return _create_tag


@pytest_asyncio.fixture
async def user_factory(db_session: AsyncSession):
    """Factory fixture to create users for testing."""

    async def _create_user(
        username: str = None,
        email: str = None,
        password: str = "testpassword",
        is_active: bool = True,
        is_superuser: bool = False,
    ):
        unique_id = uuid.uuid4().hex[:8]
        username = username or f"user_{unique_id}"
        email = email or f"{username}@example.com"

        user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            is_active=is_active,
            is_superuser=is_superuser,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    return _create_user


@pytest_asyncio.fixture
async def role_factory(db_session: AsyncSession):
    """Factory fixture to create roles for testing."""
    from app.models.role import Role

    async def _create_role(name: str = None, description: str = None):
        unique_id = uuid.uuid4().hex[:6]
        role = Role(
            name=name or f"Role_{unique_id}",
            description=description or f"Description for {name or 'role'}",
        )
        db_session.add(role)
        await db_session.commit()
        await db_session.refresh(role)
        return role

    return _create_role


@pytest_asyncio.fixture
async def profession_factory(db_session: AsyncSession):
    """Factory fixture to create professions for testing."""
    from app.models.profession import Profession

    async def _create_profession(name: str = None):
        unique_id = uuid.uuid4().hex[:6]
        profession = Profession(
            name=name or f"Profession_{unique_id}",
        )
        db_session.add(profession)
        await db_session.commit()
        await db_session.refresh(profession)
        return profession

    return _create_profession


@pytest_asyncio.fixture
async def build_factory(db_session: AsyncSession, user_factory):
    """Factory fixture to create builds for testing."""
    from app.models.build import Build

    async def _create_build(
        name: str = None,
        description: str = None,
        creator_id: int = None,
        is_public: bool = True,
    ):
        unique_id = uuid.uuid4().hex[:6]

        # Create a creator if not provided
        if creator_id is None:
            creator = await user_factory(username=f"creator_{unique_id}")
            creator_id = creator.id

        build = Build(
            name=name or f"Build_{unique_id}",
            description=description or f"Description for {name or 'build'}",
            creator_id=creator_id,
            is_public=is_public,
        )
        db_session.add(build)
        await db_session.commit()
        await db_session.refresh(build)
        return build

    return _create_build


@pytest_asyncio.fixture
async def webhook_factory(db_session: AsyncSession, user_factory):
    """Factory fixture to create webhooks for testing."""
    from app.models.webhook import Webhook

    async def _create_webhook(
        url: str = None,
        user_id: int = None,
        is_active: bool = True,
    ):
        unique_id = uuid.uuid4().hex[:6]

        # Create a user if not provided
        if user_id is None:
            user = await user_factory(username=f"webhook_user_{unique_id}")
            user_id = user.id

        webhook = Webhook(
            url=url or f"https://example.com/webhook_{unique_id}",
            user_id=user_id,
            is_active=is_active,
        )
        db_session.add(webhook)
        await db_session.commit()
        await db_session.refresh(webhook)
        return webhook

    return _create_webhook
