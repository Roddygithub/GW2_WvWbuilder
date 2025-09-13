"""Test application database initialization."""
import os
import asyncio
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the application's database initialization
from app.db.session import init_db, Base, async_engine
from app.models import User, Role, Profession, EliteSpecialization, Composition, Build

# Test database path - using absolute path to avoid any path resolution issues
TEST_DB_PATH = os.path.abspath("test_app_init.db")
TEST_DB_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"

# Create a test engine
test_engine = create_async_engine(
    TEST_DB_URL,
    echo=True,
    connect_args={"check_same_thread": False, "timeout": 30}
)

# Create a test session factory
TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

@pytest.fixture(scope="module")
def event_loop():
    """Create an instance of the default event loop for the test module."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="module")
async def db_setup():
    """Set up the test database."""
    # Remove existing test database if it exists
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    
    # Override the async_engine with our test engine
    import app.db.session
    original_engine = app.db.session.async_engine
    app.db.session.async_engine = test_engine
    
    # Initialize the database
    await init_db()
    
    # Verify the database file was created
    assert os.path.exists(TEST_DB_PATH), f"Database file was not created at {TEST_DB_PATH}"
    logger.info(f"Database file created at: {TEST_DB_PATH}")
    
    # Check the file size to ensure it's not empty
    size = os.path.getsize(TEST_DB_PATH)
    logger.info(f"Database file size: {size} bytes")
    assert size > 0, "Database file is empty"
    
    yield
    
    # Restore the original engine
    app.db.session.async_engine = original_engine
    
    # Clean up (comment out to inspect the database after tests)
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

@pytest.mark.asyncio
async def test_tables_created(db_setup):
    """Test that all expected tables are created."""
    # Get list of tables
    async with test_engine.connect() as conn:
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        tables = [row[0] for row in result.fetchall()]
        
        # Filter out SQLite system tables
        tables = [t for t in tables if not t.startswith('sqlite_')]
        logger.info(f"Tables in database: {tables}")
        
        # Check for expected tables
        expected_tables = [
            'alembic_version',  # Added by Alembic
            'users', 'roles', 'user_roles', 'professions', 
            'elite_specializations', 'compositions', 'composition_tags',
            'composition_members', 'builds', 'build_professions'
        ]
        
        # Verify all expected tables exist
        for table in expected_tables:
            assert table in tables, f"Table {table} not found in database"

@pytest.mark.asyncio
async def test_initial_data_loaded(db_setup):
    """Test that initial data is loaded into the database."""
    async with TestingSessionLocal() as session:
        try:
            # Check if roles are created
            result = await session.execute(text("SELECT * FROM roles"))
            roles = result.fetchall()
            logger.info(f"Found {len(roles)} roles in the database")
            assert len(roles) > 0, "No roles found in the database"
            
            # Check if default roles exist
            result = await session.execute(
                text("SELECT name FROM roles WHERE name IN ('admin', 'user')")
            )
            role_names = [row[0] for row in result.fetchall()]
            assert 'admin' in role_names, "Admin role not found"
            assert 'user' in role_names, "User role not found"
            
            # Check if professions are created
            result = await session.execute(text("SELECT * FROM professions"))
            professions = result.fetchall()
            logger.info(f"Found {len(professions)} professions in the database")
            assert len(professions) > 0, "No professions found in the database"
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error during test: {e}")
            raise
        finally:
            await session.close()

@pytest.mark.asyncio
async def test_crud_operations(db_setup):
    """Test basic CRUD operations on the database."""
    async with TestingSessionLocal() as session:
        try:
            # Create a test user
            await session.execute(text("""
                INSERT INTO users (email, hashed_password, is_active, is_superuser, full_name)
                VALUES ('test@example.com', 'hashed_password', 1, 0, 'Test User')
            
            """))
            
            # Get the user ID
            result = await session.execute(
                text("SELECT id FROM users WHERE email = 'test@example.com'")
            )
            user_id = result.scalar_one()
            
            # Get a role ID
            result = await session.execute(
                text("SELECT id FROM roles WHERE name = 'user'")
            )
            role_id = result.scalar_one()
            
            # Assign role to user
            await session.execute(text("""
                INSERT INTO user_roles (user_id, role_id)
                VALUES (:user_id, :role_id)
            
            """), {"user_id": user_id, "role_id": role_id})
            
            await session.commit()
            
            # Verify the data was inserted
            result = await session.execute(text("""
                SELECT u.email, r.name 
                FROM users u
                JOIN user_roles ur ON u.id = ur.user_id
                JOIN roles r ON ur.role_id = r.id
                WHERE u.email = 'test@example'
            
            """))
            
            user_roles = result.fetchall()
            assert len(user_roles) > 0, "User role assignment failed"
            
            # Clean up
            await session.execute(text("DELETE FROM user_roles WHERE user_id = :user_id"), {"user_id": user_id})
            await session.execute(text("DELETE FROM users WHERE id = :user_id"), {"user_id": user_id})
            await session.commit()
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error during test: {e}")
            raise
        finally:
            await session.close()
