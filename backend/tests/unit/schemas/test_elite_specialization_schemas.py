"""Tests for elite specialization schemas."""
import pytest
from pydantic import ValidationError

from app.schemas.elite_specialization import (
    EliteSpecializationCreate,
    EliteSpecializationUpdate,
    EliteSpecializationInDB,
    EliteSpecialization
)


def test_elite_specialization_create():
    """Test creating an elite specialization with valid data."""
    data = {
        "name": "Berserker",
        "profession_id": 1,
        "icon": "berserker_icon.png",
        "background": "berserker_bg.png",
        "description": "A powerful melee fighter"
    }
    
    spec = EliteSpecializationCreate(**data)
    
    assert spec.name == "Berserker"
    assert spec.profession_id == 1
    assert spec.icon == "berserker_icon.png"
    assert spec.background == "berserker_bg.png"
    assert spec.description == "A powerful melee fighter"


def test_elite_specialization_create_required_fields():
    """Test that required fields are enforced."""
    # Test missing required field
    with pytest.raises(ValidationError):
        EliteSpecializationCreate(name=None, profession_id=1)  # type: ignore
    
    with pytest.raises(ValidationError):
        EliteSpecializationCreate(name="Berserker", profession_id=None)  # type: ignore


def test_elite_specialization_update():
    """Test updating an elite specialization with partial data."""
    # Test with no data (all fields optional)
    update = EliteSpecializationUpdate()
    assert update.dict(exclude_unset=True) == {}
    
    # Test with partial data
    update = EliteSpecializationUpdate(name="Updated Name")
    assert update.name == "Updated Name"
    assert update.dict(exclude_unset=True) == {"name": "Updated Name"}


def test_elite_specialization_in_db():
    """Test the in-database elite specialization model."""
    data = {
        "id": 1,
        "name": "Berserker",
        "profession_id": 1,
        "icon": "berserker_icon.png",
        "background": "berserker_bg.png",
        "description": "A powerful melee fighter"
    }
    
    spec = EliteSpecializationInDB(**data)
    
    assert spec.id == 1
    assert spec.name == "Berserker"
    assert spec.profession_id == 1


def test_elite_specialization_public():
    """Test the public elite specialization model."""
    data = {
        "id": 1,
        "name": "Berserker",
        "profession_id": 1,
        "icon": "berserker_icon.png",
        "background": "berserker_bg.png",
        "description": "A powerful melee fighter"
    }
    
    spec = EliteSpecialization(**data)
    
    assert spec.id == 1
    assert spec.name == "Berserker"
    assert spec.profession_id == 1
    assert spec.icon == "berserker_icon.png"


def test_elite_specialization_orm_mode():
    """Test that the ORM mode works correctly.
    
    This test ensures that the model can be created from ORM objects.
    """
    class MockProfession:
        def __init__(self, id):
            self.id = id
    
    class MockSpec:
        def __init__(self):
            self.id = 1
            self.name = "Berserker"
            self.profession = MockProfession(1)
            self.icon = "berserker_icon.png"
            self.background = "berserker_bg.png"
            self.description = "A powerful melee fighter"
    
    orm_spec = MockSpec()
    spec = EliteSpecialization.from_orm(orm_spec)
    
    assert spec.id == 1
    assert spec.name == "Berserker"
    assert spec.profession_id == 1
    assert spec.icon == "berserker_icon.png"
