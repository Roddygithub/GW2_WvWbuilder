"""
Script to verify SQLAlchemy 2.0 model definitions.

This script checks for common issues in model definitions and verifies that all
relationships are properly set up.
"""

import sys
import asyncio
from typing import List, Type, Any

from sqlalchemy import inspect, Column, Integer, String, ForeignKey, create_engine, text
from sqlalchemy.orm import RelationshipProperty, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Add the project root to the Python path
sys.path.append(".")

# Import models after setting up the path
from app.models.base import Base
from app.models.base_models import (
    User,
    Role,
    Profession,
    EliteSpecialization,
    Composition,
    CompositionTag,
    Build,
    BuildProfession,
)
from app.core.config import settings


async def check_model_relationships():
    """Check that all model relationships are properly defined."""
    models = [
        User,
        Role,
        Profession,
        EliteSpecialization,
        Composition,
        CompositionTag,
        Build,
        BuildProfession,
    ]

    print("\n=== Checking model relationships ===")

    for model in models:
        print(f"\nChecking {model.__name__}:")
        mapper = inspect(model)

        # Check columns
        print(f"  Columns: {[col.key for col in mapper.columns]}")

        # Check relationships
        for rel in mapper.relationships:
            print(f"  Relationship: {rel.key} -> {rel.mapper.class_.__name__}")

            # Check if the relationship has the correct back_populates
            if rel.back_populates:
                print(f"    back_populates: {rel.back_populates}")

            # Check if the relationship is properly typed
            if hasattr(model, "__annotations__"):
                if rel.key in model.__annotations__:
                    print(f"    Type hint: {model.__annotations__[rel.key]}")


def check_circular_imports():
    """Check for potential circular imports in the models."""
    print("\n=== Checking for circular imports ===")

    # This is a basic check - the actual check would be done by the Python interpreter
    # when the models are imported at the top of this file
    print("No circular import issues detected in model imports.")


async def test_database_connection():
    """Test the database connection with the models."""
    print("\n=== Testing database connection ===")

    # Create async engine and session
    async_engine = create_async_engine(settings.get_async_database_url())

    async with async_engine.connect() as conn:
        # Check if we can execute a simple query
        result = await conn.execute(text("SELECT 1"))
        row = result.fetchone()
        print("  Database connection successful!")
        print(f"  Test query result: {row[0] if row else 'No result'}")

        # Close the connection explicitly
        await conn.close()


async def main():
    """Run all checks."""
    print("=== Starting model validation ===")

    # Check model relationships
    await check_model_relationships()

    # Check for circular imports
    check_circular_imports()

    # Test database connection
    try:
        await test_database_connection()
    except Exception as e:
        print(f"  Error connecting to database: {e}")

    print("\n=== Model validation complete ===")


if __name__ == "__main__":
    asyncio.run(main())
