"""Test database schema and table definitions."""
import pytest
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

def test_database_schema(db: Session):
    """Test that the database schema is correctly set up."""
    # Get the database inspector
    inspector = inspect(db.get_bind())
    
    # Get all table names
    tables = inspector.get_table_names()
    print("\nTables in database:", tables)
    
    # Check if required tables exist
    required_tables = ['users', 'roles', 'professions', 'elite_specializations', 'builds', 'build_professions']
    for table in required_tables:
        assert table in tables, f"Table '{table}' not found in database"
    
    # Check build_professions table structure
    if 'build_professions' in tables:
        print("\nbuild_professions table structure:")
        for column in inspector.get_columns('build_professions'):
            print(f"- {column['name']}: {column['type']} (PK: {column.get('primary_key', False)})")
    
    # Check foreign key constraints
    if 'build_professions' in tables:
        print("\nForeign keys in build_professions:")
        for fk in inspector.get_foreign_keys('build_professions'):
            print(f"- {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
    
    # Check if there are any foreign key constraint violations
    try:
        # Try to insert a record into build_professions with invalid foreign keys
        # This should fail if the foreign key constraints are working
        db.execute(text("""
            INSERT INTO build_professions (build_id, profession_id) 
            VALUES (999, 999)
        """))
        db.commit()
        print("\nWARNING: Foreign key constraints are not enforced!")
    except Exception as e:
        print(f"\nForeign key constraint error (expected): {e}")
        db.rollback()
    
    # Check if we can create a build_professions record with valid foreign keys
    try:
        # Create a test user, profession, and build
        db.execute(text("""
            INSERT INTO users (id, username, email, hashed_password, is_active, is_superuser)
            VALUES (1, 'testuser', 'test@example.com', 'hashed_password', 1, 0)
        """))
        
        db.execute(text("""
            INSERT INTO professions (id, name, game_modes)
            VALUES (1, 'Test Profession', '["WvW"]')
        """))
        
        db.execute(text("""
            INSERT INTO builds (id, name, created_by_id, is_public, game_mode, team_size, config)
            VALUES (1, 'Test Build', 1, 1, 'WvW', 5, '{}')
        """))
        
        # Now try to insert a valid record into build_professions
        db.execute(text("""
            INSERT INTO build_professions (build_id, profession_id)
            VALUES (1, 1)
        """))
        
        db.commit()
        print("\nSuccessfully inserted valid build_professions record")
        
        # Clean up
        db.execute(text("DELETE FROM build_professions"))
        db.execute(text("DELETE FROM builds"))
        db.execute(text("DELETE FROM professions"))
        db.execute(text("DELETE FROM users"))
        db.commit()
        
    except Exception as e:
        db.rollback()
        print(f"\nError inserting valid build_professions record: {e}")
        raise

if __name__ == "__main__":
    # This allows running the test directly for debugging
    from app.db.session import SessionLocal
    db = SessionLocal()
    try:
        test_database_schema(db)
    finally:
        db.close()
