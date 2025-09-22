"""Tests for elite specialization schemas."""

# Import the modules/classes to test
from app.schemas.profession import (
    EliteSpecializationBase,
    EliteSpecializationCreate,
    EliteSpecializationUpdate,
    EliteSpecializationInDB,
)


# Test cases for EliteSpecialization schemas
class TestEliteSpecializationSchemas:
    """Test cases for EliteSpecialization related schemas."""

    def test_elite_specialization_base(self):
        """Test EliteSpecializationBase schema."""
        data = {
            "name": "Firebrand",
            "profession_id": 1,
            "icon_url": "https://example.com/firebrand.png",
            "description": "A support-focused elite specialization.",
        }
        elite_spec = EliteSpecializationBase(**data)
        assert elite_spec.name == "Firebrand"
        assert elite_spec.profession_id == 1
        assert elite_spec.icon_url == "https://example.com/firebrand.png"
        assert elite_spec.description == "A support-focused elite specialization."

    def test_elite_specialization_create(self):
        """Test EliteSpecializationCreate schema."""
        data = {
            "name": "Firebrand",
            "profession_id": 1,
            "description": "A support-focused elite specialization.",
        }
        elite_spec = EliteSpecializationCreate(**data)
        assert elite_spec.name == "Firebrand"
        assert elite_spec.profession_id == 1
        assert elite_spec.description == "A support-focused elite specialization."

    def test_elite_specialization_update(self):
        """Test EliteSpecializationUpdate schema with partial data."""
        data = {"name": "Firebrand", "description": "Updated description"}
        elite_spec = EliteSpecializationUpdate(**data)
        assert elite_spec.name == "Firebrand"
        assert elite_spec.description == "Updated description"
        assert elite_spec.profession_id is None
        assert elite_spec.icon_url is None

    def test_elite_specialization_in_db(self):
        """Test EliteSpecializationInDB schema."""
        data = {
            "id": 1,
            "name": "Firebrand",
            "profession_id": 1,
            "icon_url": "https://example.com/firebrand.png",
            "description": "A support-focused elite specialization.",
        }
        elite_spec = EliteSpecializationInDB(**data)
        assert elite_spec.id == 1
        assert elite_spec.name == "Firebrand"
        assert elite_spec.profession_id == 1
