"""
Test configuration and fixtures for the GW2 WvW Builder backend.

This module contains pytest fixtures and configuration for integration tests
that require a database or other external services.

Fixtures are organized into sections:
1. Basic configuration
2. Database setup and teardown
3. HTTP test clients
4. Authentication and test data
"""

# Standard library imports
import asyncio
import logging
import uuid
from typing import AsyncGenerator, Dict, Generator, AsyncIterator

# Third-party imports
import pytest
from dotenv import load_dotenv, find_dotenv
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
)
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load test environment variables - prioritize .env.test if it exists
env_file = find_dotenv(".env.test")
if env_file:
    load_dotenv(env_file)
else:
    load_dotenv()

# Generate a unique test database name to prevent conflicts
TEST_DB_NAME = f"test_db_{uuid.uuid4().hex}"

# Application imports
from app.core.config import settings
from app.core.security import get_password_hash, create_access_token
from app.db.base import Base
from app.main import app

# Import all models to ensure they're registered with SQLAlchemy
# This must be at module level
from app.models import *  # noqa: F403, F401

# Explicitly import the models to ensure they're loaded
from app.models import User, Role

# ============================================
# 1. Configuration de base
# ============================================

# ============================================
# 1. Test Configuration
# ============================================

# Test database configuration
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:?cache=shared"

# Configure test settings
settings.TESTING = True
settings.DATABASE_URL = "sqlite:///:memory:?cache=shared"  # For synchronous operations
settings.SQLALCHEMY_DATABASE_URI = settings.DATABASE_URL  # SQLAlchemy compatibility
settings.ASYNC_SQLALCHEMY_DATABASE_URI = TEST_DATABASE_URL  # For async operations

# Table creation order to respect foreign key constraints
# Test tables should be created first to avoid conflicts with application tables
TABLE_CREATION_ORDER = [
    # Test tables
    "test_model",
    "test_uuid_model",
    "test_timestamped_model",
    "test_uuid_timestamped_model",
    # Application tables
    "roles",
    "users",
    "user_roles",
    "professions",
    "elite_specializations",
    "builds",
    "compositions",
    "composition_members",
    "composition_tags",
    "build_professions",
]

# ============================================
# 2. Configuration de la base de données
# ============================================

# ============================================
# 2. Database Configuration and Setup
# ============================================


<<<<<<< HEAD
# Session de base de données de test
@pytest.fixture(scope="function")
async def db() -> AsyncGenerator:
    """Crée une nouvelle connexion de base de données pour chaque test."""
    # Créer toutes les tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Créer une nouvelle session
    async with TestingSessionLocal() as session:
        # Commencer une transaction
        await session.begin()
        
        # Remplacer la dépendance get_db pour utiliser notre session de test
        async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
            try:
                yield session
            finally:
                pass
        
        app.dependency_overrides[get_db] = override_get_db
        
        try:
            yield session
        finally:
            # Annuler la transaction
            await session.rollback()
    
    # Créer un utilisateur de test par défaut
    test_user = UserFactory()
    db_session.add(test_user)
    db_session.commit()
    
    # Surcharger les dépendances d'authentification pour les tests
    def override_get_current_user():
        # Retourne l'utilisateur de test par défaut
        return test_user
        
    def override_get_current_active_user(current_user = Depends(override_get_current_user)):
        return current_user
        
    def override_get_current_active_superuser():
        # Créer un superutilisateur pour les tests
        superuser = UserFactory(is_superuser=True)
        db_session.add(superuser)
        db_session.commit()
        return superuser
    
    # Surcharger les dépendances
    app.dependency_overrides[deps_get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
    app.dependency_overrides[get_current_active_superuser] = override_get_current_active_superuser
    
    # Créer le client de test
    with TestClient(app) as test_client:
        # Ajouter un helper pour l'authentification
        def auth_header(user=None):
            if user is None:
                user = test_user
                db_session.add(user)
                db_session.commit()
            token = create_access_token(subject=user.id)
            return {"Authorization": f"Bearer {token}"}
            
        # Ajouter les méthodes d'aide au client
        test_client.auth_header = auth_header
        test_client.test_user = test_user
        
        def clear_auth():
            if hasattr(test_client, 'test_user'):
                delattr(test_client, 'test_user')
                
        test_client.clear_auth = clear_auth
        
        # Set up default auth header
        test_client.headers.update(auth_header())
        
        yield test_client
    
    # Nettoyage après les tests
    app.dependency_overrides.clear()
=======
def get_test_database_url() -> str:
    """Get the test database URL, creating a unique database for each test run."""
    db_url = settings.get_async_database_url()
    if "sqlite" in db_url:
        # For SQLite, use in-memory database with shared cache
        return "sqlite+aiosqlite:///:memory:?cache=shared"
    else:
        # For other databases, append a unique identifier
        return f"{db_url}_{TEST_DB_NAME}"
>>>>>>> a023051 (feat: optimized CRUD with Redis caching + full test coverage + docs and monitoring guide)


def create_test_engine() -> AsyncEngine:
    """Create a test database engine with appropriate settings."""
    test_db_url = get_test_database_url()
    logger.info(f"Creating test database engine for: {test_db_url}")

    # For SQLite, ensure foreign keys are enabled
    connect_args = {}
    if "sqlite" in test_db_url:
        connect_args = {
            "check_same_thread": False,
            "timeout": 30,  # Increase timeout for SQLite
            "uri": True,  # Enable URI format for additional options
            "isolation_level": "IMMEDIATE",  # Better transaction isolation
        }

    engine = create_async_engine(
        test_db_url,
        echo=True,  # Enable SQL logging
        future=True,
        poolclass=NullPool,  # Use NullPool for tests to ensure clean state
        connect_args=connect_args,
    )

    logger.info(f"Engine created with URL: {engine.url}")
    return engine


def log_metadata_tables(metadata):
    """Log information about tables in metadata for debugging."""
    logger.info("\n=== Debug: All tables in metadata ===")
    for table_name, table in metadata.tables.items():
        logger.info(f"- {table_name}")
        logger.info(f"  Columns: {[c.name for c in table.columns]}")
        if table.foreign_keys:
            logger.info(f"  Foreign keys: {[str(fk) for fk in table.foreign_keys]}")
    logger.info("")


# ============================================
# 3. Database Setup and Teardown
# ============================================


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the event loop for the test session."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create and configure the test database engine."""
    engine = create_test_engine()

    # Debug: Print all tables in metadata before creating them
    logger.info("\n=== DEBUG: Tables in Base.metadata before any operation ===")
    for table_name, table in Base.metadata.tables.items():
        logger.info("Table: %s", table_name)
        logger.info("  Columns: %s", [c.name for c in table.columns])
        if table.foreign_keys:
            logger.info("  Foreign keys: %s", [str(fk) for fk in table.foreign_keys])

    # Create all tables in the correct order
    async with engine.begin() as conn:
        # Drop all tables first to ensure a clean state
        try:
            logger.info("\n=== DEBUG: Dropping all tables ===")
            # Vérifier les tables existantes avant la suppression
            result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            )
            tables_before_drop = [row[0] for row in result.fetchall()]
            logger.info("Tables before drop: %s", tables_before_drop)

            # Afficher les métadonnées des tables
            logger.info("\n=== DEBUG: Tables in metadata before drop ===")
            for table_name, table in Base.metadata.tables.items():
                logger.info("Table: %s", table_name)
                logger.info("  Columns: %s", [c.name for c in table.columns])

            # Supprimer les tables
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("Successfully dropped all tables")

            # Vérifier les tables après la suppression
            result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            )
            tables_after_drop = [row[0] for row in result.fetchall()]
            logger.info("Tables after drop: %s", tables_after_drop)

        except Exception as e:
            logger.error("Error dropping tables: %s", e, exc_info=True)
            raise

        # Debug: Print SQL that would be executed
        logger.info("\n=== DEBUG: Tables to be created (in order) ===")
        for table in Base.metadata.sorted_tables:
            logger.info("\nTable: %s", table.name)
            logger.info("  Columns:")
            for col in table.columns:
                fk_info = f" (FK: {col.foreign_keys})" if col.foreign_keys else ""
                logger.info("    - %s: %s%s", col.name, col.type, fk_info)

            if table.foreign_keys:
                logger.info("  Foreign keys:")
                for fk in table.foreign_keys:
                    logger.info("    - %s", fk)

        # Create all tables
        logger.info("\n=== DEBUG: Creating all tables ===")
        try:
            # Afficher les métadonnées avant la création
            logger.info("\n=== DEBUG: Tables in metadata before create ===")
            for table_name, table in Base.metadata.tables.items():
                logger.info("Table: %s", table_name)
                logger.info("  Columns: %s", [c.name for c in table.columns])
                if hasattr(table, "foreign_keys") and table.foreign_keys:
                    logger.info(
                        "  Foreign keys: %s", [str(fk) for fk in table.foreign_keys]
                    )

            # Créer les tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Successfully created all tables")

            # Vérifier les tables après création
            result = await conn.execute(
                text("SELECT name, sql FROM sqlite_master WHERE type='table'")
            )
            created_tables = {row[0]: row[1] for row in result.fetchall()}
            logger.info("\n=== DEBUG: Tables created in database ===")
            for table_name, create_sql in created_tables.items():
                logger.info("\nTable: %s", table_name)
                logger.debug("  SQL: %s", create_sql)

                # Afficher les colonnes de chaque table
                result = await conn.execute(text(f"PRAGMA table_info({table_name})"))
                columns = [row[1] for row in result.fetchall()]
                logger.info("  Columns: %s", columns)

        except Exception as e:
            logger.error("Error creating tables: %s", e, exc_info=True)
            # Essayer d'obtenir plus d'informations sur l'erreur
            try:
                result = await conn.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table'")
                )
                tables_after_error = [row[0] for row in result.fetchall()]
                logger.error("Tables after error: %s", tables_after_error)
            except Exception as inner_e:
                logger.error("Could not get tables after error: %s", str(inner_e))
            raise

    # Verify tables were created
    async with engine.connect() as conn:
        # Get all tables in the database
        result = await conn.execute(
            text("SELECT name, sql FROM sqlite_master WHERE type='table'")
        )
        created_tables = {row[0]: row[1] for row in result.fetchall()}

        logger.info("\n=== DEBUG: Tables in database ===")
        for table_name, create_sql in created_tables.items():
            logger.info("\nTable: %s", table_name)
            logger.debug("  SQL: %s", create_sql)

        # Check for the users table
        result = await conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        )
        users_table = result.first()

        if not users_table:
            logger.error("\n=== ERROR: Users table was not created! ===")
            # Check for any tables with similar names (case-insensitive)
            result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            )
            all_tables = [row[0] for row in result.fetchall()]
            logger.error("Available tables: %s", all_tables)

            # Check for case variations
            for table in all_tables:
                if table.lower() == "users":
                    logger.error("Found table with different case: %s", table)
        else:
            logger.info("\n=== SUCCESS: Users table exists ===")
            # Get columns in users table
            result = await conn.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]
            logger.info("Columns in users table: %s", columns)

    try:
        yield engine
    finally:
        # Clean up
        logger.info("\n=== DEBUG: Cleaning up test database ===")
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            logger.info("Successfully cleaned up test database")
        except Exception as e:
            logger.error("Error during cleanup: %s", e, exc_info=True)
        await engine.dispose()


@pytest.fixture
def db_session_factory(engine: AsyncEngine):
    """Create a session factory for tests."""
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


@pytest.fixture
async def db(db_session_factory) -> AsyncGenerator[AsyncSession, None]:
    """
    Create and manage a database session for tests.

    This fixture creates a new session and transaction for each test,
    and ensures proper cleanup after the test completes.

    Yields:
        AsyncSession: A database session for testing
    """
    async with db_session_factory() as session:
        # Start a transaction
        await session.begin()

        # Enable SQLite foreign key support
        await session.execute(text("PRAGMA foreign_keys = ON"))

        try:
            yield session
        finally:
            # Rollback any changes made during the test
            await session.rollback()

            # Close the session
            await session.close()


@pytest.fixture(autouse=True)
async def clean_db(db: AsyncSession):
    """Clean the database before and after each test."""
    # Get all tables
    meta = MetaData()
    await db.run_sync(meta.reflect, bind=db.bind)

    # Truncate all tables in reverse order to respect foreign key constraints
    for table in reversed(meta.sorted_tables):
        await db.execute(table.delete())

    await db.commit()

    yield

    # Cleanup after test
    await db.rollback()


@pytest.fixture
async def clean_db(db: AsyncSession) -> AsyncIterator[None]:
    """
    Clean up the database before and after each test.

    This fixture ensures that:
    - All tables are empty before each test
    - Changes are rolled back after each test
    - The database is in a consistent state

    Args:
        db: The database session fixture

    Yields:
        None
    """

    async def _clean_tables():
        """Helper to clean all tables."""
        # Disable foreign key checks temporarily
        await db.execute(text("PRAGMA foreign_keys = OFF"))

        # Delete data from all tables in reverse order of foreign key dependencies
        for table in reversed(Base.metadata.sorted_tables):
            try:
                await db.execute(table.delete())
            except Exception as e:
                logger.warning("Error cleaning table %s: %s", table.name, str(e))

        # Re-enable foreign key checks
        await db.execute(text("PRAGMA foreign_keys = ON"))
        await db.commit()

    # Clean before test
    await _clean_tables()

    # Create a savepoint for the test
    savepoint = await db.begin_nested()

    try:
        yield  # Run the test
    finally:
        # Rollback to the savepoint to undo any changes made during the test
        await savepoint.rollback()

        # Clean up any remaining data
        await _clean_tables()


# ============================================
# 4. Clients de test HTTP
# ============================================


@pytest.fixture
def client() -> TestClient:
    """
    Provide a synchronous HTTP test client.

    This client is useful for tests that don't require async operations.

    Yields:
        TestClient: A FastAPI test client
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def async_client() -> AsyncIterator[AsyncClient]:
    """
    Provide an asynchronous HTTP test client.

    This client is necessary for testing endpoints with async dependencies.

    Yields:
        AsyncClient: An async HTTP test client
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# ============================================
# 5. Authentification et données de test
# ============================================


@pytest.fixture
async def test_user(db: AsyncSession) -> User:
    """
    Create and return a test user with admin role.
    Each test will get a user with a unique email and username to avoid conflicts.

    Args:
        db: Database session

    Returns:
        User: The created test user with admin privileges
    """
    import uuid
    
    # Generate a unique identifier for this test user
    unique_id = str(uuid.uuid4())[:8]  # Take first 8 chars of UUID
    username = f"testuser_{unique_id}"
    email = f"test_{unique_id}@example.com"
    
    # Create admin role if it doesn't exist
    admin_role = await db.execute(text("SELECT * FROM roles WHERE name = 'admin'"))
    admin_role = admin_role.first()

    if not admin_role:
        admin_role = Role(name="admin", description="Administrator")
        db.add(admin_role)
        await db.commit()
        await db.refresh(admin_role)

    # Create regular user role if it doesn't exist
    user_role = await db.execute(text("SELECT * FROM roles WHERE name = 'user'"))
    user_role = user_role.first()

    if not user_role:
        user_role = Role(name="user", description="Regular user")
        db.add(user_role)
        await db.commit()
        await db.refresh(user_role)

    # Create test user with unique email and username
    user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash("testpassword"),
        full_name=f"Test User {unique_id}",
        is_active=True,
        is_superuser=True,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Add admin role to the user
    await db.execute(
        text("INSERT INTO user_roles (user_id, role_id) VALUES (:user_id, :role_id)"),
        {"user_id": user.id, "role_id": admin_role.id},
    )

    # Create a regular test user as well with unique identifiers
    regular_username = f"regularuser_{unique_id}"
    regular_email = f"regular_{unique_id}@example.com"
    
    regular_user = User(
        username=regular_username,
        email=regular_email,
        hashed_password=get_password_hash("regularpassword"),
        full_name=f"Regular User {unique_id}",
        is_active=True,
        is_superuser=False,
    )
    db.add(regular_user)
    await db.commit()
    await db.refresh(regular_user)

    # Add user role to the regular user
    await db.execute(
        text("INSERT INTO user_roles (user_id, role_id) VALUES (:user_id, :role_id)"),
        {"user_id": regular_user.id, "role_id": user_role.id},
    )

    await db.commit()
    
    # Return the admin user
    return user

    return user


@pytest.fixture
async def test_tokens(
    async_client: AsyncClient, test_user: User, db: AsyncSession
) -> Dict[str, str]:
    """
    Generate access tokens for test users.

    Args:
        async_client: Async HTTP client
        test_user: The test user fixture
        db: Database session

    Returns:
        Dict[str, str]: Dictionary containing access tokens for different user roles
    """
    # Get the regular user (non-admin)
    regular_user = await db.execute(
        text("SELECT * FROM users WHERE email = 'regular@example.com'")
    )
    regular_user = regular_user.first()

    if not regular_user:
        raise RuntimeError("Regular test user not found")

    # Create tokens
    admin_token = create_access_token(subject=test_user.id)
    user_token = create_access_token(subject=regular_user.id)

    return {
        "admin": admin_token,
        "user": user_token,
    }


@pytest.fixture
def auth_headers(test_tokens: Dict[str, str]) -> Dict[str, Dict[str, str]]:
    """
    Return authentication headers for API requests.

    This fixture provides pre-configured authentication headers for different
    user roles that can be used in API tests.

    Args:
        test_tokens: Dictionary containing access tokens for different user roles

    Returns:
        Dict[str, Dict[str, str]]: Dictionary mapping role names to their
            respective authentication headers
    """
    return {
        "admin": {"Authorization": f"Bearer {test_tokens['admin']}"},
        "user": {"Authorization": f"Bearer {test_tokens['user']}"},
    }
