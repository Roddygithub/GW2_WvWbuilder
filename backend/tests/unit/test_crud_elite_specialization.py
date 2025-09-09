"""Tests for elite specialization CRUD operations."""
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from tests.utils.utils import random_lower_string


def test_create_elite_specialization(db: Session) -> None:
    """Test creating an elite specialization."""
    # Create a test profession
    profession = crud.profession.create(
        db,
        obj_in=schemas.ProfessionCreate(
            name=random_lower_string(),
            description="Test Profession",
            game_modes=["WvW"]
        )
    )
    
    # Create elite specialization data
    elite_spec_in = schemas.EliteSpecializationCreate(
        name="Test Elite Spec",
        profession_id=profession.id,
        icon_url="https://example.com/icon.png",
        description="Test Elite Specialization"
    )
    
    # Create the elite specialization
    elite_spec = crud.elite_specialization.create(db, obj_in=elite_spec_in)
    
    # Assertions
    assert elite_spec.name == elite_spec_in.name
    assert elite_spec.profession_id == profession.id
    assert elite_spec.icon_url == elite_spec_in.icon_url
    assert elite_spec.description == elite_spec_in.description


@pytest.mark.asyncio
async def test_create_elite_specialization_async(async_db: AsyncSession) -> None:
    """Test creating an elite specialization asynchronously."""
    # Create a test profession
    profession = await crud.profession.create_async(
        async_db,
        obj_in=schemas.ProfessionCreate(
            name=f"{random_lower_string()}_async",
            description="Test Profession Async",
            game_modes=["WvW"]
        )
    )
    
    # Create elite specialization data
    elite_spec_in = schemas.EliteSpecializationCreate(
        name="Test Elite Spec Async",
        profession_id=profession.id,
        specialization_id=2,
        icon="test_icon_async.png",
        background="test_bg_async.jpg",
        weapon_type="Staff"
    )
    
    # Create the elite specialization asynchronously
    elite_spec = await crud.elite_specialization.create_async(async_db, obj_in=elite_spec_in)
    
    # Assertions
    assert elite_spec.name == elite_spec_in.name
    assert elite_spec.profession_id == profession.id
    assert elite_spec.specialization_id == elite_spec_in.specialization_id


def test_get_elite_specialization(db: Session) -> None:
    """Test retrieving an elite specialization by ID."""
    # Create a test profession
    profession = crud.profession.create(
        db,
        obj_in=schemas.ProfessionCreate(
            name=random_lower_string(),
            description="Test Profession",
            game_modes=["WvW"]
        )
    )
    
    # Create a test elite specialization
    elite_spec = crud.elite_specialization.create(
        db,
        obj_in=schemas.EliteSpecializationCreate(
            name="Test Get Spec",
            profession_id=profession.id,
            specialization_id=3,
            icon="get_icon.png"
        )
    )
    
    # Retrieve the elite specialization
    stored_spec = crud.elite_specialization.get(db, id=elite_spec.id)
    
    # Assertions
    assert stored_spec
    assert stored_spec.id == elite_spec.id
    assert stored_spec.name == "Test Get Spec"


def test_get_by_name_and_profession(db: Session) -> None:
    """Test retrieving an elite specialization by name and profession."""
    # Create test professions
    profession1 = crud.profession.create(
        db,
        obj_in=schemas.ProfessionCreate(
            name=random_lower_string(),
            description="Profession 1",
            game_modes=["WvW"]
        )
    )
    
    profession2 = crud.profession.create(
        db,
        obj_in=schemas.ProfessionCreate(
            name=random_lower_string(),
            description="Profession 2",
            game_modes=["WvW"]
        )
    )
    
    # Create test elite specializations with same name but different professions
    spec1 = crud.elite_specialization.create(
        db,
        obj_in=schemas.EliteSpecializationCreate(
            name="Druid",
            profession_id=profession1.id,
            specialization_id=5,
            icon="druid.png"
        )
    )
    
    spec2 = crud.elite_specialization.create(
        db,
        obj_in=schemas.EliteSpecializationCreate(
            name="Druid",
            profession_id=profession2.id,
            specialization_id=6,
            icon="druid2.png"
        )
    )
    
    # Retrieve the elite specializations
    stored_spec1 = crud.elite_specialization.get_by_name_and_profession(
        db, 
        name="Druid", 
        profession_id=profession1.id
    )
    
    stored_spec2 = crud.elite_specialization.get_by_name_and_profession(
        db, 
        name="Druid", 
        profession_id=profession2.id
    )
    
    # Assertions
    assert stored_spec1.id == spec1.id
    assert stored_spec2.id == spec2.id
    assert stored_spec1.profession_id == profession1.id
    assert stored_spec2.profession_id == profession2.id


def test_get_by_profession(db: Session) -> None:
    """Test retrieving elite specializations by profession."""
    # Create test professions
    profession1 = crud.profession.create(
        db,
        obj_in=schemas.ProfessionCreate(
            name=random_lower_string(),
            description="Profession 1",
            game_modes=["WvW"]
        )
    )
    
    profession2 = crud.profession.create(
        db,
        obj_in=schemas.ProfessionCreate(
            name=random_lower_string(),
            description="Profession 2",
            game_modes=["WvW"]
        )
    )
    
    # Create test elite specializations
    spec1 = crud.elite_specialization.create(
        db,
        obj_in=schemas.EliteSpecializationCreate(
            name="Spec 1",
            profession_id=profession1.id,
            specialization_id=7,
            icon="spec1.png"
        )
    )
    
    spec2 = crud.elite_specialization.create(
        db,
        obj_in=schemas.EliteSpecializationCreate(
            name="Spec 2",
            profession_id=profession1.id,
            specialization_id=8,
            icon="spec2.png"
        )
    )
    
    # Create a spec for a different profession
    crud.elite_specialization.create(
        db,
        obj_in=schemas.EliteSpecializationCreate(
            name="Spec 3",
            profession_id=profession2.id,
            specialization_id=9,
            icon="spec3.png"
        )
    )
    
    # Get specs for profession1
    profession1_specs = crud.elite_specialization.get_by_profession(
        db,
        profession_id=profession1.id,
        skip=0,
        limit=10
    )
    
    # Assertions
    assert len(profession1_specs) == 2
    assert {spec.id for spec in profession1_specs} == {spec1.id, spec2.id}


def test_get_elite_specialization_by_id(db: Session) -> None:
    """Test retrieving an elite specialization by ID."""
    # Create a test profession
    profession = crud.profession.create(
        db,
        obj_in=schemas.ProfessionCreate(
            name=random_lower_string(),
            description="Test Profession"
        )
    )
    
    # Create test elite specialization
    elite_spec_in = schemas.EliteSpecializationCreate(
        name=random_lower_string(),
        profession_id=profession.id,
        description="Test Elite Spec"
    )
    elite_spec = crud.elite_specialization.create(db, obj_in=elite_spec_in)
    
    # Retrieve by ID
    stored_elite_spec = crud.elite_specialization.get(db, id=elite_spec.id)
    
    # Assertions
    assert stored_elite_spec
    assert stored_elite_spec.id == elite_spec.id
    assert stored_elite_spec.name == elite_spec_in.name
    assert stored_elite_spec.profession_id == profession.id


def test_update_elite_specialization(db: Session) -> None:
    """Test updating an elite specialization."""
    # Create a test profession
    profession = crud.profession.create(
        db,
        obj_in=schemas.ProfessionCreate(
            name=random_lower_string(),
            description="Test Profession"
        )
    )
    
    # Create a test elite specialization
    elite_spec = crud.elite_specialization.create(
        db,
        obj_in=schemas.EliteSpecializationCreate(
            name="Old Name",
            profession_id=profession.id,
            description="Old Description"
        )
    )
    
    # Update the elite specialization
    update_data = schemas.EliteSpecializationUpdate(
        name="Updated Name",
        description="Updated Description",
        icon_url="https://example.com/updated_icon.png"
    )
    updated_elite_spec = crud.elite_specialization.update(
        db,
        db_obj=elite_spec,
        obj_in=update_data
    )
    
    # Assertions
    assert updated_elite_spec.id == elite_spec.id
    assert updated_elite_spec.name == "Updated Name"
    assert updated_elite_spec.description == "Updated Description"
    assert updated_elite_spec.icon_url == "https://example.com/updated_icon.png"


def test_remove_elite_specialization(db: Session) -> None:
    """Test removing an elite specialization."""
    # Create a test profession
    profession = crud.profession.create(
        db,
        obj_in=schemas.ProfessionCreate(
            name=random_lower_string(),
            description="Test Profession"
        )
    )
    
    # Create a test elite specialization
    elite_spec = crud.elite_specialization.create(
        db,
        obj_in=schemas.EliteSpecializationCreate(
            name="Test Spec to Remove",
            profession_id=profession.id,
            description="Test Spec to Remove Description"
        )
    )
    
    # Remove the elite specialization
    removed_elite_spec = crud.elite_specialization.remove(db, id=elite_spec.id)
    
    # Try to retrieve the removed elite specialization
    db_elite_spec = crud.elite_specialization.get(db, id=elite_spec.id)
    
    # Assertions
    assert removed_elite_spec.id == elite_spec.id
    assert db_elite_spec is None
