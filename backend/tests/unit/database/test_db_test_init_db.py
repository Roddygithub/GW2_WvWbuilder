"""Test the init_db function directly."""
import os
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Import the application's database initialization
from app.db.session import init_db, Base
from app.db.session import async_engine as original_async_engine

# Test database path
TEST_DB = "test_init_db.db"

def test_database_tables_created_sync():
    """Test that all expected tables are created (synchronous version)."""
    # List of expected tables
    expected_tables = {
        'users', 'roles', 'user_roles', 'professions',
        'elite_specializations', 'compositions', 'composition_tags',
        'composition_members', 'builds', 'build_professions'
    }
    
    # Create a synchronous engine for testing
    from sqlalchemy import create_engine
    sync_engine = create_engine(f"sqlite:///{TEST_DB}")
    
    try:
        # Create tables
        Base.metadata.create_all(sync_engine)
        
        # Query the database for tables
        with sync_engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
            tables = {row[0] for row in result}
            
            # Check for missing tables
            missing_tables = expected_tables - tables
            assert not missing_tables, f"Missing tables: {missing_tables}"
            
    finally:
        # Clean up
        sync_engine.dispose()
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

@pytest.mark.asyncio
async def test_init_db_function():
    """Test that init_db() creates all tables."""
    test_db = "test_init_db_function.db"
    
    # Remove existing test database if it exists
    if os.path.exists(test_db):
        os.remove(test_db)
    
    try:
        # Create a new engine for this test
        test_engine = create_async_engine(
            f"sqlite+aiosqlite:///{test_db}",
            echo=True
        )
        
        # Override the global async_engine for init_db
        import app.db.session as session_module
        original_engine = session_module.async_engine
        session_module.async_engine = test_engine
        
        try:
            # Initialize the database
            await init_db()
            
            # Verify tables were created using a synchronous engine
            from sqlalchemy import create_engine
            sync_engine = create_engine(f"sqlite:///{test_db}")
            
            with sync_engine.connect() as conn:
                result = conn.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table';")
                )
                tables = {row[0] for row in result}
                
                expected_tables = {
                    'users', 'roles', 'user_roles', 'professions',
                    'elite_specializations', 'compositions', 'composition_tags',
                    'composition_members', 'builds', 'build_professions'
                }
                
                missing_tables = expected_tables - tables
                assert not missing_tables, f"Missing tables: {missing_tables}"
                
        finally:
            # Restore the original engine
            session_module.async_engine = original_engine
            await test_engine.dispose()
            
    finally:
        if os.path.exists(test_db):
            os.remove(test_db)
