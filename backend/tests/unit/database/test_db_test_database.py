"""Tests for database initialization and models."""
import pytest
from sqlalchemy import inspect

from app.database.base import Base
from app.models import (
    User, Role, user_roles, 
    Build, Profession, build_profession,
    Composition, composition_members, CompositionTag,
    EliteSpecialization
)


def test_base_metadata_initialized():
    """Test that Base metadata is properly initialized with all models."""
    # Get all table names from metadata
    metadata_tables = set(Base.metadata.tables.keys())
    
    # List of expected table names
    expected_tables = {
        'users', 'roles', 'user_roles',
        'professions', 'elite_specializations',
        'builds', 'build_professions',
        'compositions', 'composition_members', 'composition_tags'
    }
    
    # Check that all expected tables are in metadata
    missing_tables = expected_tables - metadata_tables
    assert not missing_tables, f"Tables missing from metadata: {missing_tables}"


def test_all_models_have_table_representation():
    """Test that all SQLAlchemy models have a table representation."""
    # Get all models that should have a table
    models = [
        User, Role, 
        Build, Profession, 
        Composition, CompositionTag,
        EliteSpecialization
    ]
    
    for model in models:
        assert hasattr(model, '__tablename__'), f"{model.__name__} has no __tablename__"
        assert model.__tablename__, f"Model {model.__name__} has an empty __tablename__"


def test_all_models_have_primary_key():
    """Test that all SQLAlchemy models have a primary key defined."""
    # Get all models that should have a primary key
    models = [
        User, Role, 
        Build, Profession, 
        Composition, CompositionTag,
        EliteSpecialization
    ]
    
    for model in models:
        # Get the table object from the model
        table = model.__table__
        # Check that the table has a primary key
        assert len(table.primary_key.columns) > 0, f"{model.__name__} has no primary key defined"


def test_all_models_have_table_in_metadata():
    """Test that all models are properly registered with Base's metadata."""
    models = [
        User, Role, 
        Build, Profession, 
        Composition, CompositionTag,
        EliteSpecialization
    ]
    
    for model in models:
        assert model.__table__ is not None, f"Model {model.__name__} is not in Base.metadata"
        assert model.__table__ in Base.metadata.sorted_tables, \
            f"Model {model.__name__} is not in Base.metadata.sorted_tables"


@pytest.mark.asyncio
async def test_models_can_be_imported():
    """Test that all models can be imported without errors."""
    # This test just verifies that all models can be imported
    models = [
        'User', 'Role',
        'Build', 'Profession',
        'Composition', 'CompositionTag',
        'EliteSpecialization'
    ]
    
    for model_name in models:
        try:
            exec(f'from app.models import {model_name}')
        except ImportError as e:
            pytest.fail(f"Failed to import {model_name}: {e}")
