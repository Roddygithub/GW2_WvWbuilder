"""
Configuration et fixtures pour les tests unitaires.

Ce module définit les configurations et les fixtures partagées pour les tests unitaires.
"""

import asyncio
import logging
import sqlite3
import uuid
import os
import sys
from typing import AsyncGenerator, Callable

import pytest
import pytest_asyncio
from fastapi import Depends, HTTPException, FastAPI, status
from fastapi.security import OAuth2PasswordBearer
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import select, text, event

# Ajouter le répertoire parent au chemin Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.main import app, create_application
from app.api.deps import get_async_db
from app.models import User, Base, Profession, Role, Permission
from app.core.config import settings
from app.core.security import get_password_hash, create_access_token

# Configuration du logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Désactiver les logs de certains modules trop verbeux
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)

# OAuth2 scheme pour les tests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Configuration de la base de données de test
TEST_ASYNC_DATABASE_URL = "sqlite+aiosqlite:///:memory:?cache=shared"

# Création du moteur de base de données de test
logger.info(f"Configuration de la base de données de test avec l'URL : {TEST_ASYNC_DATABASE_URL}")

test_engine = create_async_engine(
    TEST_ASYNC_DATABASE_URL,
    echo=settings.SQL_ECHO,
    future=True,
    connect_args={"check_same_thread": False, "timeout": 30, "uri": True, "isolation_level": "IMMEDIATE"},
    poolclass=StaticPool,
    pool_pre_ping=True,
)

# Configuration de la session de test
TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine, expire_on_commit=False, class_=AsyncSession, twophase=False
)


# Configuration des événements SQLAlchemy
@event.listens_for(test_engine.sync_engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    """Active les clés étrangères pour SQLite"""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


logger.info("Moteur de test configuré avec succès")

# Note: pytest_plugins a été déplacé vers tests/conftest.py (top-level)
# pour éviter les warnings pytest


# Configuration des marqueurs pytest
def pytest_configure(config):
    config.addinivalue_line("markers", "asyncio: marque les tests asynchrones")
    config.addinivalue_line("markers", "integration: marque les tests d'intégration")
    config.addinivalue_line("markers", "unit: marque les tests unitaires")
    config.addinivalue_line("markers", "db: marque les tests qui utilisent la base de données")


# Marqueurs pour les tests
@pytest.mark.asyncio
def asyncio_marker(f):
    """Marqueur pour les tests asynchrones"""
    return pytest.mark.asyncio(f)


@pytest.mark.integration
def integration_marker(f):
    """Marqueur pour les tests d'intégration"""
    return pytest.mark.integration(f)


@pytest.mark.unit
def unit_marker(f):
    """Marqueur pour les tests unitaires"""
    return pytest.mark.unit(f)


@pytest.mark.db
def db_marker(f):
    """Marqueur pour les tests qui utilisent la base de données"""
    return pytest.mark.db(f)


@pytest_asyncio.fixture(scope="function")
async def override_get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_async_db)):
    """
    Surcharge de la dépendance get_current_user pour les tests.

    Args:
        token: JWT token d'authentification
        db: Session de base de données

    Returns:
        User: L'utilisateur authentifié

    Raises:
        HTTPException: Si les identifiants sont invalides
    """
    from app.core.security import verify_token
    from app.crud.crud_user import get_user_by_email

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        if token.startswith("test_token:"):
            # Mode de test avec token simple
            user_id = int(token.split(":")[1])
            result = await db.execute(select(User).filter(User.id == user_id))
            user = result.scalars().first()
        else:
            # Mode normal avec JWT
            token_data = verify_token(token, credentials_exception)
            user = await get_user_by_email(db, email=token_data.email)

        if not user:
            raise credentials_exception

        return user
    except Exception as e:
        logger.error(f"Erreur lors de la validation du token: {str(e)}")
        raise credentials_exception


# Application des surcharges de dépendances
# Note: Les surcharges sont appliquées dans les fixtures, pas au niveau du module


@pytest_asyncio.fixture(scope="function")
async def client():
    """
    Client de test HTTP pour les requêtes asynchrones.

    Returns:
        AsyncClient: Un client HTTP asynchrone configuré pour les tests
    """
    # S'assurer que les dépendances sont bien surchargées
    override_dependencies()

    async with AsyncClient(app=app, base_url="http://testserver") as client:
        try:
            # Configuration des en-têtes par défaut
            client.headers.update(
                {
                    "User-Agent": "GW2_WvWbuilder-test-client/1.0.0",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                }
            )

            yield client

        except Exception as e:
            logger.error(f"Erreur dans le client de test : {e}")
            raise
        finally:
            # Nettoyage des ressources
            await client.aclose()


@pytest.fixture(scope="session")
def event_loop():
    """
    Crée une instance de la boucle d'événements par défaut pour chaque cas de test.

    Cette fixture garantit que chaque test obtient une nouvelle boucle d'événements
    et qu'elle est correctement fermée à la fin du test.
    """
    # Détruire toute boucle d'événements existante
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            logger.warning("Une boucle d'événements est déjà en cours d'exécution")
            yield loop
            return
        if not loop.is_closed():
            loop.close()
    except RuntimeError:
        pass

    # Créer une nouvelle boucle d'événements
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()

    # Configurer la boucle
    loop.set_debug(True)
    asyncio.set_event_loop(loop)

    try:
        yield loop
    finally:
        # Nettoyage des ressources
        try:
            # Annuler toutes les tâches en attente
            pending = asyncio.all_tasks(loop)
            if pending:
                logger.warning(f"Annulation de {len(pending)} tâches en cours...")
                for task in pending:
                    task.cancel()

                # Exécuter la boucle jusqu'à ce que toutes les tâches soient terminées
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))

                # Vérifier les exceptions dans les tâches annulées
                for task in pending:
                    if task.done() and not task.cancelled():
                        try:
                            task.result()
                        except Exception as e:
                            logger.error(f"La tâche {task} a généré une exception : {e}")
        finally:
            # Fermer la boucle
            if not loop.is_closed():
                loop.run_until_complete(loop.shutdown_asyncgens())
                loop.close()
            asyncio.set_event_loop(None)


@pytest_asyncio.fixture(scope="function")
async def init_test_db(request) -> AsyncGenerator[None, None]:
    """
    Initialize the test database with all tables and clean up after tests.

    This fixture is automatically used for each test function and ensures
    a clean database state before and after each test.

    Note: Not autouse to avoid conflicts with tests that have their own DB setup.
    """
    # Skip for tests in models directory that have their own engine fixture
    if "models" in str(request.fspath):
        yield
        return
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Create default roles and permissions
    async with TestingSessionLocal() as session:
        # Create test permissions
        permissions = [
            Permission(name="read", description="Read access"),
            Permission(name="write", description="Write access"),
            Permission(name="admin", description="Admin access"),
        ]
        session.add_all(permissions)

        # Create test roles
        roles = [
            Role(name="user", description="Regular user"),
            Role(name="moderator", description="Moderator"),
            Role(name="admin", description="Administrator"),
        ]
        session.add_all(roles)

        # Add permissions to roles
        for role in roles:
            if role.name == "admin":
                role.permissions.extend(permissions)
            elif role.name == "moderator":
                role.permissions.extend([p for p in permissions if p.name != "admin"])
            else:  # user
                role.permissions.append(permissions[0])  # read only

        await session.commit()

    # Yield control back to the test function
    yield

    # Clean up after the test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("[DEBUG] All tables dropped successfully")

    # Vérifier les modèles chargés
    async with test_engine.connect() as conn:
        # Afficher toutes les tables
        result = await conn.execute(text("SELECT name, sql FROM sqlite_master WHERE type='table'"))
        tables = result.fetchall()
        print("\n[DEBUG] ==== Tables dans la base de données ====")
        for name, sql in tables:
            print(f"\nTable: {name}")
            print(f"SQL: {sql}")

            # Afficher les index pour cette table
            index_result = await conn.execute(
                text("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name=:name"), {"name": name}
            )
            indexes = index_result.fetchall()
            if indexes:
                print("  Index:")
                for idx_name, idx_sql in indexes:
                    print(f"    - {idx_name}: {idx_sql}")

        print("\n[DEBUG] ==== Contenu des tables ====")
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        table_names = [row[0] for row in result.fetchall()]

        for table_name in table_names:
            if table_name.startswith("sqlite_"):
                continue

            try:
                result = await conn.execute(text(f"SELECT * FROM {table_name} LIMIT 5"))
                rows = result.fetchall()
                print(f"\nContenu de la table '{table_name}' (max 5 lignes):")
                if rows:
                    # Afficher les noms des colonnes
                    print("  ", ", ".join(str(col) for col in result.keys()))
                    # Afficher les données
                    for row in rows:
                        print("  ", ", ".join(str(val) for val in row))
                else:
                    print("  (vide)")
            except Exception as e:
                print(f"  Erreur lors de la lecture de la table {table_name}: {str(e)}")

        print("\n[DEBUG] ===============================================\n")

    print("[DEBUG] ===== Test database initialized =====\n")

    # Verify tables were created
    async with test_engine.connect() as conn:
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = result.fetchall()
        print(f"Tables created: {tables}")


@pytest.fixture
def override_get_db(init_test_db) -> Callable[..., AsyncGenerator[AsyncSession, None]]:
    """Override the get_db dependency for testing."""

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with TestingSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                print(f"Error in _override_get_db: {e}")
                raise
            finally:
                await session.close()

    return _override_get_db


@pytest.fixture
async def db_session(init_test_db) -> AsyncGenerator[AsyncSession, None]:
    """Create a clean database session for testing."""
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            print(f"Error in db_session: {e}")
            raise
        finally:
            await session.close()


@pytest.fixture
def test_password():
    """Retourne un mot de passe de test sécurisé."""
    return "TestPass123!"


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession, test_role: Role):
    """
    Crée un utilisateur de test avec des données aléatoires.

    Args:
        db_session: Session de base de données
        test_role: Rôle à attribuer à l'utilisateur

    Returns:
        User: Un utilisateur de test avec un mot de passe en clair dans l'attribut 'plain_password'
    """

    test_password = "TestPass123!"
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"

    user = User(
        email=email,
        hashed_password=get_password_hash(test_password),
        is_active=True,
        is_verified=True,
        first_name="Test",
        last_name="User",
        roles=[test_role],
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Ajouter le mot de passe en clair pour les tests
    user.plain_password = test_password

    return user


@pytest_asyncio.fixture(scope="function")
async def auth_headers(test_user: User, client: AsyncClient):
    """
    Crée un en-tête d'authentification pour un utilisateur de test.

    Args:
        test_user: Utilisateur de test
        client: Client de test HTTP

    Returns:
        dict: En-têtes d'authentification
    """

    access_token = create_access_token(data={"sub": test_user.email}, expires_delta=timedelta(minutes=15))

    return {"Authorization": f"Bearer {access_token}"}


@pytest_asyncio.fixture(scope="function")
async def admin_auth_headers(admin_user: User, client: AsyncClient):
    """
    Crée un en-tête d'authentification pour un administrateur.

    Args:
        admin_user: Utilisateur administrateur
        client: Client de test HTTP

    Returns:
        dict: En-têtes d'authentification
    """

    access_token = create_access_token(data={"sub": admin_user.email}, expires_delta=timedelta(minutes=15))

    return {"Authorization": f"Bearer {access_token}"}


@pytest_asyncio.fixture(scope="function")
async def admin_user(db_session: AsyncSession):
    """
    Crée un utilisateur administrateur pour les tests.

    Args:
        db_session: Session de base de données

    Returns:
        User: Un utilisateur administrateur
    """

    # Créer un rôle administrateur s'il n'existe pas
    admin_role = await db_session.execute(select(Role).where(Role.name == "admin"))
    admin_role = admin_role.scalar_one_or_none()

    if not admin_role:
        admin_role = Role(name="admin", description="Administrateur", is_active=True, is_default=False)
        db_session.add(admin_role)
        await db_session.commit()

    # Créer l'utilisateur administrateur
    admin_user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("AdminPass123!"),
        is_active=True,
        is_verified=True,
        first_name="Admin",
        last_name="User",
        roles=[admin_role],
    )

    db_session.add(admin_user)
    await db_session.commit()
    await db_session.refresh(admin_user)

    # Ajouter le mot de passe en clair pour les tests
    admin_user.plain_password = "AdminPass123!"

    return admin_user


@pytest_asyncio.fixture(scope="function")
async def test_role(db_session: AsyncSession):
    """
    Crée un rôle de test.

    Returns:
        Role: Un rôle de test avec un nom unique
    """
    role = Role(
        name=f"test_role_{uuid.uuid4().hex[:8]}",
        description="Test Role",
        is_active=True,
        is_default=False,
    )

    db_session.add(role)
    await db_session.commit()
    await db_session.refresh(role)

    return role


@pytest_asyncio.fixture(scope="function")
async def test_profession(db_session: AsyncSession):
    """
    Crée une profession de test.

    Returns:
        Profession: Une profession de test avec un nom unique
    """
    profession = Profession(name=f"Test Profession {uuid.uuid4().hex[:4]}", icon="test_icon.png", is_active=True)

    db_session.add(profession)
    await db_session.commit()
    await db_session.refresh(profession)

    return profession


# Application fixtures


@pytest.fixture
def app(override_get_db: Callable[..., AsyncGenerator[AsyncSession, None]]) -> FastAPI:
    """Create a test FastAPI application."""
    # Disable environment variable loading for tests
    import os

    os.environ["ENVIRONMENT"] = "test"

    app = create_application()

    # Override the database dependency
    app.dependency_overrides[get_async_db] = override_get_db

    return app


@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client for making HTTP requests."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        try:
            yield client
        except Exception as e:
            print(f"Error in client fixture: {e}")
            raise
