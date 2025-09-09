#!/usr/bin/env python3
"""
Script to reset the test database.

This script drops all tables and recreates them with the latest schema.
"""
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.core.config import settings

def reset_database():
    """Reset the database by dropping and recreating all tables."""
    print("🧹 Resetting database...")
    
    # Create a new session
    db = SessionLocal()
    
    try:
        # Drop all tables
        print("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        
        # Create all tables
        print("Creating all tables...")
        Base.metadata.create_all(bind=engine)
        
        # For SQLite, we need to ensure foreign keys are enabled
        if 'sqlite' in settings.DATABASE_URL:
            with engine.connect() as conn:
                conn.execute(text("PRAGMA foreign_keys=ON"))
        
        print("✅ Database reset successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    if reset_database():
        print("\n✅ Database reset completed successfully!")
    else:
        print("\n❌ Database reset failed. See error messages above.")
        sys.exit(1)
