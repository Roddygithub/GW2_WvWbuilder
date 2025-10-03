"""Tests for profession schemas."""

# Import the modules/classes to test
from app.schemas.profession import (
    ProfessionBase,
    ProfessionCreate,
    ProfessionUpdate,
    EliteSpecializationBase,
    EliteSpecializationCreate,
    EliteSpecializationUpdate,
)


# Test cases for Profession schemas
class TestProfessionSchemas:
    """Test cases for Profession related schemas."""

    def test_profession_base(self):
        """Test ProfessionBase schema."""
        data = {
            "name": "Guardian",
            "icon_url": "https://example.com/guardian.png",
            "description": "A profession that uses magical powers.",
            "game_modes": ["PvE", "WvW", "PvP"],
        }
        profession = ProfessionBase(**data)
        assert profession.name == "Guardian"
        assert profession.icon_url == "https://example.com/guardian.png"
        assert profession.description == "A profession that uses magical powers."
        assert profession.game_modes == ["PvE", "WvW", "PvP"]

    def test_profession_create(self):
        """Test ProfessionCreate schema."""
        data = {
            "name": "Guardian",
            "description": "A profession that uses magical powers.",
        }
        profession = ProfessionCreate(**data)
        assert profession.name == "Guardian"
        assert profession.description == "A profession that uses magical powers."

    def test_profession_update(self):
        """Test ProfessionUpdate schema with partial data."""
        data = {"name": "Guardian", "description": "Updated description"}
        profession = ProfessionUpdate(**data)
        assert profession.name == "Guardian"
        assert profession.description == "Updated description"
        assert profession.icon_url is None


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
