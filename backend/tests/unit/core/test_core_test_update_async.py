"""Tests for async update operations."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.crud.base import CRUDBase
from app.models import Profession as ProfessionModel
from app.schemas.profession import ProfessionCreate, ProfessionUpdate

# Create a test CRUD class
class TestCRUD(CRUDBase[ProfessionModel, ProfessionCreate, ProfessionUpdate]):
    """Test CRUD class for Profession model."""
    pass

test_crud = TestCRUD(ProfessionModel)

@pytest.mark.asyncio
async def test_update_async() -> None:
    """Test updating a model instance asynchronously."""
    # Setup database
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    
    # Create test data
    obj_in = ProfessionCreate(
        name="Test Update Async",
        description="Test Update Async Description",
        game_modes=["PvE"]
    )
    
    async with async_session() as db:
        # Create the object
        created_obj = await test_crud.create_async(db, obj_in=obj_in)
        await db.commit()
        
        # Verify the object was created
        assert created_obj is not None
        assert created_obj.name == "Test Update Async"
        
        # Update the object
        update_data = ProfessionUpdate(
            name="Updated Name Async",
            description="Updated Description Async"
        )
        
        # Test update_async
        updated_obj = await test_crud.update_async(
            db,
            db_obj=created_obj,
            obj_in=update_data
        )
        
        # Verify the update
        assert updated_obj is not None
        assert updated_obj.id == created_obj.id
        assert updated_obj.name == "Updated Name Async"
        assert updated_obj.description == "Updated Description Async"
        assert updated_obj.game_modes == ["PvE"]  # Should not change
        
        # Verify the update is persisted
        await db.refresh(updated_obj)
        refreshed_obj = await test_crud.get_async(db, id=created_obj.id)
        assert refreshed_obj is not None
        assert refreshed_obj.name == "Updated Name Async"
    
    await engine.dispose()


@pytest.mark.asyncio
async def test_remove_async() -> None:
    """Test removing a model instance asynchronously."""
    # Setup database
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    
    # Create test data
    obj_in = ProfessionCreate(
        name="Test Remove Async",
        description="Test Remove Async Description",
        game_modes=["WvW"]
    )
    
    async with async_session() as db:
        # Create the object
        created_obj = await test_crud.create_async(db, obj_in=obj_in)
        await db.commit()
        
        # Verify the object was created
        assert created_obj is not None
        assert created_obj.name == "Test Remove Async"
        
        # Test remove_async
        removed_obj = await test_crud.remove_async(db, id=created_obj.id)
        
        # Verify the remove
        assert removed_obj is not None
        assert removed_obj.id == created_obj.id
        
        # Verify the object is no longer in the database
        result = await test_crud.get_async(db, id=created_obj.id)
        assert result is None
    
    await engine.dispose()
