"""Create a fresh database with the correct schema."""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sqlalchemy import create_engine, text
from app.db.base import Base
from app.core.config import settings


def create_fresh_db():
    """Create a fresh database with the correct schema."""
    print("🔄 Creating fresh database...")

    # Get database URL from settings
    database_url = settings.get_database_url()
    print(f"Using database URL: {database_url}")

    # Remove existing database file if it exists
    if database_url.startswith("sqlite:///") and os.path.exists(database_url[10:]):
        db_path = database_url[10:]
        print(f"Removing existing database at {db_path}")
        os.remove(db_path)

    # Create engine and create all tables
    engine = create_engine(database_url)
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    # Verify tables were created
    with engine.connect() as conn:
        # Get all tables
        result = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table';")
        )
        tables = [row[0] for row in result]
        print("\nTables created:")
        for table in tables:
            print(f"- {table}")

            # Show table schema
            result = conn.execute(text(f"PRAGMA table_info({table});"))
            print("  Columns:")
            for col in result:
                pk_info = "PRIMARY KEY" if col[5] else ""
                not_null = "NOT NULL" if col[3] else ""
                default = f"DEFAULT {col[4]}" if col[4] else ""
                print(f"  - {col[1]} ({col[2]}) {pk_info} {not_null} {default}".strip())

    print("\n✅ Fresh database created successfully!")
    return engine


if __name__ == "__main__":
    create_fresh_db()
