"""Inspect the database schema."""
import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from sqlalchemy import (
    create_engine, inspect, text, MetaData, Table, Column, 
    Integer, String, Boolean, Text, JSON, ForeignKey, DateTime, 
    UniqueConstraint, func
)
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

def create_schema(engine):
    """Create the database schema."""
    metadata = MetaData()
    
    # Create tables in the correct order to satisfy foreign key constraints
    Table(
        'users',
        metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('username', String, unique=True, index=True, nullable=False),
        Column('email', String, unique=True, index=True, nullable=False),
        Column('hashed_password', String, nullable=False),
        Column('full_name', String, nullable=True),
        Column('is_active', Boolean, default=True),
        Column('is_superuser', Boolean, default=False),
        Column('created_at', DateTime(timezone=True), server_default=func.now()),
        Column('updated_at', DateTime(timezone=True), onupdate=func.now())
    )
    
    Table(
        'roles',
        metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('name', String, unique=True, index=True, nullable=False),
        Column('description', Text, nullable=True),
        Column('permission_level', Integer, default=0, nullable=False),
        Column('is_default', Boolean, default=False, nullable=False),
        Column('created_at', DateTime(timezone=True), server_default=func.now()),
        Column('updated_at', DateTime(timezone=True), onupdate=func.now())
    )
    
    Table(
        'professions',
        metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('name', String, unique=True, index=True, nullable=False),
        Column('icon_url', String, nullable=True),
        Column('description', Text, nullable=True),
        Column('game_modes', JSON, nullable=True, default=[]),
        Column('created_at', DateTime(timezone=True), server_default=func.now()),
        Column('updated_at', DateTime(timezone=True), onupdate=func.now())
    )
    
    Table(
        'elite_specializations',
        metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('name', String, index=True, nullable=False),
        Column('profession_id', Integer, ForeignKey('professions.id'), nullable=False),
        Column('icon_url', String, nullable=True),
        Column('description', Text, nullable=True),
        Column('created_at', DateTime(timezone=True), server_default=func.now()),
        Column('updated_at', DateTime(timezone=True), onupdate=func.now())
    )
    
    Table(
        'builds',
        metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('name', String, index=True, nullable=False),
        Column('description', Text, nullable=True),
        Column('game_mode', String, default="wvw"),
        Column('team_size', Integer, default=5),
        Column('is_public', Boolean, default=False),
        Column('created_by_id', Integer, ForeignKey('users.id')),
        Column('created_at', DateTime(timezone=True), server_default=func.now()),
        Column('updated_at', DateTime(timezone=True), onupdate=func.now()),
        Column('config', JSON, nullable=False, default=dict),
        Column('constraints', JSON, nullable=True, default=dict)
    )
    
    # Create the build_professions table
    Table(
        'build_professions',
        metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('build_id', Integer, ForeignKey('builds.id', ondelete='CASCADE'), nullable=False, index=True),
        Column('profession_id', Integer, ForeignKey('professions.id', ondelete='CASCADE'), nullable=False, index=True),
        Column('created_at', DateTime(timezone=True), server_default=func.now(), nullable=False),
        UniqueConstraint('build_id', 'profession_id', name='uq_build_profession')
    )
    
    # Create all tables
    metadata.create_all(engine)

def inspect_database():
    """Inspect the database schema."""
    # Create an in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:")
    
    # Create the schema
    create_schema(engine)
    
    # Create a session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    # Enable foreign key constraints for SQLite
    db.execute(text("PRAGMA foreign_keys=ON"))
    db.commit()
    
    # Get the inspector
    inspector = inspect(engine)
    
    # Get all table names
    tables = inspector.get_table_names()
    print("\nTables in database:", tables)
    
    # Check if required tables exist
    required_tables = ['users', 'roles', 'professions', 'elite_specializations', 'builds', 'build_professions']
    for table in required_tables:
        if table not in tables:
            print(f"\nTable '{table}' not found in database")
    
    # Print schema of each table
    for table_name in tables:
        print(f"\nTable: {table_name}")
        print("-" * 80)
        for column in inspector.get_columns(table_name):
            print(f"- {column['name']}: {column['type']} (PK: {column.get('primary_key', False)})")
        
        # Print foreign keys
        fks = inspector.get_foreign_keys(table_name)
        if fks:
            print("\n  Foreign Keys:")
            for fk in fks:
                print(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
    
    # Close the session
    db.close()

if __name__ == "__main__":
    inspect_database()
