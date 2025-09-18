"""Tests for Elite Specialization schemas and validations."""
import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from app.schemas.elite_specialization import (
    EliteSpecializationBase,
    EliteSpecializationCreate,
    EliteSpecializationUpdate,
    EliteSpecializationInDBBase,
    EliteSpecialization,
    EliteSpecializationInDB
)


def test_elite_specialization_base_valid():
    """Test valid EliteSpecializationBase creation."""
    data = {
        "name": "Firebrand",
        "description": "Wields fire and tomes to support allies and burn foes",
        "icon_url": "https://example.com/icon.png",
        "profession_id": 1
    }
    spec = EliteSpecializationBase(**data)
    assert spec.name == data["name"]
    assert spec.description == data["description"]
    assert spec.icon_url == data["icon_url"]
    assert spec.profession_id == data["profession_id"]


def test_elite_specialization_base_invalid():
    """Test EliteSpecializationBase validation errors."""
    # Test empty name
    with pytest.raises(ValidationError) as exc_info:
        EliteSpecializationBase(name="", profession_id=1)
    assert "String should have at least 1 character" in str(exc_info.value)
    
    # Test long name
    with pytest.raises(ValidationError) as exc_info:
        EliteSpecializationBase(name="A" * 101, profession_id=1)
    assert "String should have at most 100 characters" in str(exc_info.value)
    
    # Test missing required field
    with pytest.raises(ValidationError) as exc_info:
        EliteSpecializationBase(name="Firebrand")
    assert "Field required" in str(exc_info.value)


def test_elite_specialization_create_valid():
    """Test valid EliteSpecializationCreate."""
    data = {
        "name": "Firebrand",
        "profession_id": 1
    }
    spec = EliteSpecializationCreate(**data)
    assert spec.name == data["name"]
    assert spec.profession_id == data["profession_id"]
    assert spec.description is None
    assert spec.icon_url is None


def test_elite_specialization_update_partial():
    """Test partial updates with EliteSpecializationUpdate."""
    # Test partial update with just name
    update = EliteSpecializationUpdate(name="Updated Name")
    assert update.name == "Updated Name"
    assert update.description is None
    assert update.icon_url is None
    assert update.profession_id is None
    
    # Test partial update with all fields
    data = {
        "name": "New Name",
        "description": "New Description",
        "icon_url": "https://example.com/new.png",
        "profession_id": 2
    }
    update = EliteSpecializationUpdate(**data)
    for field, value in data.items():
        assert getattr(update, field) == value


def test_elite_specialization_in_db_base():
    """Test EliteSpecializationInDBBase with all fields."""
    now = datetime.now(timezone.utc)
    data = {
        "id": 1,
        "name": "Firebrand",
        "profession_id": 1,
        "created_at": now,
        "updated_at": now
    }
    spec = EliteSpecializationInDBBase(**data)
    assert spec.id == data["id"]
    assert spec.name == data["name"]
    assert spec.created_at == data["created_at"]
    assert spec.updated_at == data["updated_at"]


def test_elite_specialization_serialization():
    """Test serialization of EliteSpecialization model."""
    now = datetime.now(timezone.utc)
    data = {
        "id": 1,
        "name": "Firebrand",
        "description": "Test description",
        "icon_url": "https://example.com/icon.png",
        "profession_id": 1,
        "created_at": now,
        "updated_at": now
    }
    
    # Test serialization to dict
    spec = EliteSpecialization(**data)
    spec_dict = spec.model_dump()
    for field in ["id", "name", "description", "icon_url", "profession_id"]:
        assert spec_dict[field] == data[field]
    
    # Test JSON serialization
    spec_json = spec.model_dump_json()
    assert "Firebrand" in spec_json
    assert str(data["id"]) in spec_json


def test_elite_specialization_in_db():
    """Test EliteSpecializationInDB model."""
    now = datetime.now(timezone.utc)
    data = {
        "id": 1,
        "name": "Firebrand",
        "profession_id": 1,
        "created_at": now,
        "updated_at": now
    }
    spec = EliteSpecializationInDB(**data)
    assert isinstance(spec, EliteSpecializationInDBBase)
    assert spec.id == data["id"]
    assert spec.name == data["name"]


def test_elite_specialization_examples():
    """Test that the example data in schemas is valid."""
    # Test create example
    create_example = EliteSpecializationCreate.model_config["json_schema_extra"]["example"]
    assert EliteSpecializationCreate(**create_example)
    
    # Test update example
    update_example = EliteSpecializationUpdate.model_config["json_schema_extra"]["example"]
    assert EliteSpecializationUpdate(**update_example)
    
    # Test in-db example
    in_db_example = EliteSpecializationInDBBase.model_config["json_schema_extra"]["example"]
    assert EliteSpecializationInDBBase(**in_db_example)
