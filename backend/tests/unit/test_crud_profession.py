"""Tests for profession CRUD operations."""
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from tests.utils.utils import random_lower_string


def test_create_profession(db: Session) -> None:
    """Test creating a profession."""
    # Create profession data
    name = random_lower_string()
    profession_in = schemas.ProfessionCreate(
        name=name,
        description="Test Profession Description",
        game_modes=["WvW", "PvP"],
        icon_url="http://example.com/icon.png"
    )
    
    # Create the profession
    profession = crud.profession.create(db, obj_in=profession_in)
    
    # Assertions
    assert profession.name == name
    assert profession.description == profession_in.description
    assert profession.game_modes == profession_in.game_modes
    assert profession.icon_url == profession_in.icon_url


@pytest.mark.asyncio
async def test_create_profession_async(async_db: AsyncSession) -> None:
    """Test creating a profession asynchronously."""
    # Create profession data
    name = f"{random_lower_string()}_async"
    profession_in = schemas.ProfessionCreate(
        name=name,
        description="Test Async Profession Description",
        game_modes=["WvW", "PvE"],
        icon_url="http://example.com/icon_async.png"
    )
    
    # Create the profession asynchronously
    profession = await crud.profession.create_async(async_db, obj_in=profession_in)
    
    # Assertions
    assert profession.name == name
    assert profession.description == profession_in.description
    assert profession.game_modes == profession_in.game_modes
    assert profession.icon_url == profession_in.icon_url


def test_get_profession(db: Session) -> None:
    """Test retrieving a profession by ID."""
    # Create a test profession
    name = random_lower_string()
    profession_in = schemas.ProfessionCreate(
        name=name,
        description="Test Get Profession",
        game_modes=["WvW"]
    )
    profession = crud.profession.create(db, obj_in=profession_in)
    
    # Retrieve the profession
    stored_profession = crud.profession.get(db, id=profession.id)
    
    # Assertions
    assert stored_profession
    assert stored_profession.id == profession.id
    assert stored_profession.name == name


def test_get_profession_by_name(db: Session) -> None:
    """Test retrieving a profession by name."""
    # Create a test profession
    name = random_lower_string()
    profession_in = schemas.ProfessionCreate(
        name=name,
        description="Test Get By Name",
        game_modes=["WvW"]
    )
    crud.profession.create(db, obj_in=profession_in)
    
    # Retrieve the profession by name
    stored_profession = crud.profession.get_by_name(db, name=name)
    
    # Assertions
    assert stored_profession
    assert stored_profession.name == name


def test_get_profession_with_elite_specs(db: Session) -> None:
    """Test retrieving a profession with its elite specializations."""
    # Create a test profession
    profession = crud.profession.create(
        db,
        obj_in=schemas.ProfessionCreate(
            name=random_lower_string(),
            description="Test Profession",
            game_modes=["WvW"]
        )
    )
    
    # Create test elite specializations
    elite_spec1 = crud.elite_specialization.create(
        db,
        obj_in=schemas.EliteSpecializationCreate(
            name="Spec 1",
            profession_id=profession.id,
            description="Test Spec 1"
        )
    )
    elite_spec2 = crud.elite_specialization.create(
        db,
        obj_in=schemas.EliteSpecializationCreate(
            name="Spec 2",
            profession_id=profession.id,
            description="Test Spec 2"
        )
    )
    
    # Get the profession with elite specializations
    db_profession = crud.profession.get_with_elite_specs(db, id=profession.id)
    
    # Assertions
    assert db_profession.id == profession.id
    assert len(db_profession.elite_specializations) == 2
    assert {spec.id for spec in db_profession.elite_specializations} == {elite_spec1.id, elite_spec2.id}


def test_get_multi_by_game_mode(db: Session) -> None:
    """Test retrieving professions by game mode."""
    # Create test professions for different game modes
    wvw_professions = []
    for i in range(3):
        profession = crud.profession.create(
            db,
            obj_in=schemas.ProfessionCreate(
                name=f"WvW Profession {i}",
                description=f"WvW Profession {i} Description",
                game_modes=["WvW"]
            )
        )
        wvw_professions.append(profession)
    
    pvp_professions = []
    for i in range(2):
        profession = crud.profession.create(
            db,
            obj_in=schemas.ProfessionCreate(
                name=f"PvP Profession {i}",
                description=f"PvP Profession {i} Description",
                game_modes=["PvP"]
            )
        )
        pvp_professions.append(profession)
    
    # Get WvW professions
    wvw_results = crud.profession.get_multi_by_game_mode(db, game_mode="WvW")
    
    # Get PvP professions
    pvp_results = crud.profession.get_multi_by_game_mode(db, game_mode="PvP")
    
    # Assertions
    assert len(wvw_results) == 3
    assert {p.id for p in wvw_results} == {p.id for p in wvw_professions}
    
    assert len(pvp_results) == 2
    assert {p.id for p in pvp_results} == {p.id for p in pvp_professions}
    
    # Get PvE professions
    pve_results = crud.profession.get_multi_by_game_mode(
        db,
        game_mode="PvE",
        skip=0,
        limit=10
    )
    
    # Assertions
    assert len(pve_results) == 1
    assert pve_results[0].id == pve_profession.id


def test_update_profession(db: Session) -> None:
    """Test updating a profession."""
    # Create a test profession
    profession = crud.profession.create(
        db,
        obj_in=schemas.ProfessionCreate(
            name=random_lower_string(),
            description="Original Description",
            game_modes=["WvW"]
        )
    )
    
    # Update the profession
    updated_name = random_lower_string()
    updated_description = "Updated Description"
    updated_game_modes = ["WvW", "PvP"]
    
    updated_profession = crud.profession.update(
        db,
        db_obj=profession,
        obj_in=schemas.ProfessionUpdate(
            name=updated_name,
            description=updated_description,
            game_modes=updated_game_modes
        )
    )
    
    # Assertions
    assert updated_profession.id == profession.id
    assert updated_profession.name == updated_name
    assert updated_profession.description == updated_description
    assert updated_profession.game_modes == updated_game_modes


def test_remove_profession(db: Session) -> None:
    """Test removing a profession."""
    # Create a test profession
    profession = crud.profession.create(
        db,
        obj_in=schemas.ProfessionCreate(
            name=random_lower_string(),
            description="To be removed",
            game_modes=["WvW"]
        )
    )
    
    # Remove the profession
    removed_profession = crud.profession.remove(db, id=profession.id)
    
    # Try to retrieve the removed profession
    db_profession = crud.profession.get(db, id=profession.id)
    
    # Assertions
    assert removed_profession.id == profession.id
    assert db_profession is None
