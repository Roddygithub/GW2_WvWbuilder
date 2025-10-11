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

# Configuration du logging pour le débogage des tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy import text, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

# Configuration des chemins
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import des dépendances de l'application
from app.main import create_application
from app.db.session import get_async_db
from app.core.security import get_password_hash

# Import des modèles nécessaires pour les tests
from app.models.user import User
from app.models.role import Role
from app.models.profession import Profession
from app.models.build import Build  # Ajout de l'import manquant

# Configuration de l'environnement de test
os.environ["TESTING"] = "True"
os.environ["ENVIRONMENT"] = "testing"

# Configuration de la base de données de test
test_db_dir = os.path.join(os.path.dirname(__file__), "test_db")
os.makedirs(test_db_dir, exist_ok=True)
db_path = os.path.join(test_db_dir, "test.db")

# Nettoyage du fichier de base de données s'il existe
if os.path.exists(db_path):
    try:
        os.remove(db_path)
    except Exception as e:
        print(f"Erreur lors de la suppression du fichier de base de données: {e}")

# Configuration du moteur de base de données de test
from tests.test_config import test_settings

# Configuration de la base de données en mémoire pour les tests
TEST_DATABASE_URL = test_settings.ASYNC_SQLALCHEMY_DATABASE_URI

# Configuration du moteur de test avec StaticPool pour SQLite en mémoire
# Note: StaticPool n'utilise pas de pool de connexions, donc les paramètres de pool ne sont pas nécessaires
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=test_settings.SQL_ECHO,
    future=True,
    connect_args={
        "check_same_thread": False,
        "timeout": test_settings.POOL_TIMEOUT,
        "uri": True,
        "isolation_level": "IMMEDIATE",
    },
    poolclass=StaticPool,
    pool_pre_ping=True,
)


@pytest.fixture(scope="session")
def event_loop():
    """
    Create an instance of the default event loop for each test case.

    This fixture ensures that each test gets a fresh event loop and properly closes it
    when the test is done.
    """
    # Détruire toute boucle d'événements existante
    try:
        loop = asyncio.get_event_loop()
        if not loop.is_closed():
            loop.close()
    except RuntimeError:
        pass

    # Créer une nouvelle boucle d'événements pour la session de test
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)

    # Configurer le fuseau horaire pour la session de test
    os.environ["TZ"] = "UTC"

    try:
        yield loop
    finally:
        # Nettoyer la boucle d'événements
        if not loop.is_closed():
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
        asyncio.set_event_loop(None)

    # Configurer le niveau de log pour asyncio
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    try:
        yield loop
    finally:
        # Nettoyage après les tests
        if not loop.is_closed():
            # Annuler toutes les tâches en cours
            pending = asyncio.all_tasks(loop=loop)
            for task in pending:
                task.cancel()

            # Exécuter les tâches annulées
            if pending:
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))

            # Fermer la boucle d'événements
            loop.run_until_complete(loop.shutdown_asyncgens())

            # Fermer les connexions de la base de données
            if "test_engine" in globals():
                loop.run_until_complete(test_engine.dispose())

            loop.close()

        # Réinitialiser la boucle d'événements par défaut
        asyncio.set_event_loop(None)

        # Nettoyer les fichiers temporaires
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except Exception as e:
                print(f"Erreur lors du nettoyage du fichier de base de données: {e}")


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
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result.fetchall()]
        print(f"Tables créées: {', '.join(tables)}")

    # Vérifier que les tables ont été créées
    print("\n=== Vérification des tables créées ===")
    async with test_engine.connect() as conn:
        # Liste des tables dans la base de données
        result = await conn.execute(text("SELECT name, sql FROM sqlite_master WHERE type='table'"))
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
        result = await conn.execute(text("SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index'"))
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
    Create a clean database session for testing with automatic rollback.

    This fixture provides a new database session for each test function and ensures
    that all changes are rolled back after the test completes.
    """
    # Créer une nouvelle connexion
    connection = await test_engine.connect()

    # Démarrer une nouvelle transaction
    transaction = await connection.begin()

    # Configurer la fabrique de sessions
    async_session_factory = async_sessionmaker(
        bind=connection, expire_on_commit=False, autoflush=False, class_=AsyncSession
    )

    # Créer une nouvelle session
    session = async_session_factory()

    # Démarrer un point de sauvegarde imbriqué
    await session.begin_nested()

    # Configurer le point de sauvegarde pour les commits
    @event.listens_for(session.sync_session, "after_transaction_end")
    def restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:
            session.expire_all()
            session.begin_nested()

    try:
        yield session

        # Toujours effectuer un rollback à la fin du test
        await session.rollback()
    finally:
        # Fermer la session et la connexion
        # Close the session and connection
        await session.close()
        if transaction.is_active:
            await transaction.rollback()
        await connection.close()


@pytest.fixture
def override_get_db(db_session: AsyncSession) -> Callable[..., AsyncGenerator[AsyncSession, None]]:
    """
    Override the get_db dependency for testing.

    This fixture provides a database session that is automatically rolled back
    after each test, ensuring test isolation.
    """

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        # Start a new transaction for each request
        await db_session.begin_nested()

        try:
            yield db_session

            # After the request, rollback to undo any changes
            await db_session.rollback()

        except Exception:
            # If an error occurs, rollback the transaction
            if db_session.in_transaction():
                await db_session.rollback()
            raise

    return _override_get_db


# Test data fixtures


@pytest.fixture
def test_password() -> str:
    """Return a test password."""
    return "securepassword"


@pytest.fixture
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


@pytest.fixture
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


@pytest.fixture
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


@pytest.fixture
async def test_build(db_session: AsyncSession, test_user: User, test_profession: Profession) -> Build:
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


@pytest.fixture
async def test_builds(db_session: AsyncSession, test_user: User, test_profession: Profession) -> List[Build]:
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
                self._pipeline_commands.append({"method": "incr", "key": key, "amount": amount})
                return self

            current = int(self.data.get(key, 0))
            new_value = current + amount
            self.data[key] = str(new_value)
            return new_value

        async def expire(self, key, ttl, **kwargs):
            if hasattr(self, "_in_pipeline") and self._in_pipeline:
                self._pipeline_commands.append({"method": "expire", "key": key, "ttl": ttl})
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
    with patch("app.core.config.Settings.redis_client", new_callable=PropertyMock) as mock_prop:
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
def app(override_get_db: Callable[..., AsyncGenerator[AsyncSession, None]]) -> FastAPI:
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

    # Créer le répertoire static s'il n'existe pas
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../app/static"))
    os.makedirs(static_dir, exist_ok=True)

    # Créer un fichier vide dans le répertoire static pour éviter l'erreur
    with open(os.path.join(static_dir, ".gitkeep"), "w") as f:
        f.write("")

    # Créer l'application
    app = create_application()

    # Surcharger la dépendance de la base de données pour utiliser notre session de test
    app.dependency_overrides[get_async_db] = override_get_db

    # Désactiver la vérification du token pour les tests
    async def mock_verify_token():
        return {"sub": "test_user_id", "email": "test@example.com"}

    async def mock_get_current_user():
        return User(id=1, email="test@example.com", username="testuser", is_superuser=False, is_active=True)

    # Appliquer les surcharges
    app.dependency_overrides[get_current_user] = mock_get_current_user

    yield app

    # Nettoyer les dépendances
    app.dependency_overrides.clear()


@pytest.fixture
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


@pytest.fixture
async def async_client(app: FastAPI):
    """Create an async test client for making HTTP requests."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
