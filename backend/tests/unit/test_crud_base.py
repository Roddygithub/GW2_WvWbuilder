"""Tests for base CRUD operations."""
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.crud.base import CRUDBase
from app.models import Profession as ProfessionModel
from app.schemas.profession import ProfessionCreate, ProfessionUpdate
from tests.utils.utils import random_lower_string


# Create a test model class that uses the base CRUD operations
class CRUDTestModel(CRUDBase[ProfessionModel, ProfessionCreate, ProfessionUpdate]):
    """Test CRUD class that uses the base operations."""
    pass


# Create an instance of the test CRUD class
test_crud = CRUDTestModel(ProfessionModel)


def test_create(db: Session) -> None:
    """Test creating a model instance."""
    # Create test data
    obj_in = ProfessionCreate(
        name="Test Profession",
        description="Test Description",
        game_modes=["WvW", "PvP"]
    )
    
    # Create the model instance
    obj = test_crud.create(db, obj_in=obj_in)
    
    # Assertions
    assert obj.id is not None
    assert obj.name == obj_in.name
    assert obj.description == obj_in.description
    assert obj.game_modes == obj_in.game_modes


@pytest.mark.asyncio
async def test_create_async(async_db: AsyncSession) -> None:
    """Test creating a model instance asynchronously."""
    # Create test data
    obj_in = ProfessionCreate(
        name="Test Async Profession",
        description="Test Async Description",
        game_modes=["PvE"]
    )
    
    # Create the model instance asynchronously
    obj = await test_crud.create_async(async_db, obj_in=obj_in)
    
    # Assertions
    assert obj.id is not None
    assert obj.name == obj_in.name
    assert obj.description == obj_in.description
    assert obj.game_modes == obj_in.game_modes


def test_get(db: Session) -> None:
    """Test retrieving a model instance by ID."""
    # Create a test instance
    obj_in = ProfessionCreate(
        name="Test Get",
        description="Test Get Description",
        game_modes=["WvW"]
    )
    created_obj = test_crud.create(db, obj_in=obj_in)
    
    # Retrieve the instance
    stored_obj = test_crud.get(db, id=created_obj.id)
    
    # Assertions
    assert stored_obj
    assert stored_obj.id == created_obj.id
    assert stored_obj.name == created_obj.name


def test_get_multi(db: Session) -> None:
    """Test retrieving multiple model instances with pagination."""
    # Create test instances
    for i in range(5):
        test_crud.create(
            db,
            obj_in=ProfessionCreate(
                name=f"Profession {i}",
                description=f"Description {i}",
                game_modes=["WvW"]
            )
        )
    
    # Get first page
    objs_page1 = test_crud.get_multi(db, skip=0, limit=3)
    
    # Get second page
    objs_page2 = test_crud.get_multi(db, skip=3, limit=3)
    
    # Assertions
    assert len(objs_page1) == 3
    assert len(objs_page2) == 2  # Only 2 items left
    assert objs_page1[0].id != objs_page2[0].id  # Different items


def test_update(db: Session) -> None:
    """Test updating a model instance."""
    # Create a test instance
    obj_in = ProfessionCreate(
        name="Original Name",
        description="Original Description",
        game_modes=["WvW"]
    )
    obj = test_crud.create(db, obj_in=obj_in)
    
    # Update the instance
    update_data = {
        "name": "Updated Name",
        "description": "Updated Description",
        "game_modes": ["WvW", "PvP"]
    }
    update_in = ProfessionUpdate(**update_data)
    updated_obj = test_crud.update(db, db_obj=obj, obj_in=update_in)
    
    # Assertions
    assert updated_obj.id == obj.id
    assert updated_obj.name == update_data["name"]
    assert updated_obj.description == update_data["description"]
    assert updated_obj.game_modes == update_data["game_modes"]


def test_remove(db: Session) -> None:
    """Test removing a model instance."""
    # Create a test instance
    obj_in = ProfessionCreate(
        name="To be removed",
        description="Will be deleted",
        game_modes=["WvW"]
    )
    obj = test_crud.create(db, obj_in=obj_in)
    
    # Remove the instance
    removed_obj = test_crud.remove(db, id=obj.id)
    
    # Try to retrieve the removed instance
    db_obj = test_crud.get(db, id=obj.id)
    
    # Assertions
    assert removed_obj.id == obj.id
    assert db_obj is None
