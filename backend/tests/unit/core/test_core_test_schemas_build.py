"""Test build schemas and validations."""

import pytest
from datetime import datetime, UTC
from pydantic import ValidationError

from app.schemas.build import (
    BuildBase,
    BuildCreate,
    BuildUpdate,
    BuildInDBBase,
    Build,
    BuildInDB,
)

# Test data
TEST_BUILD_DATA = {
    "name": "Test Build",
    "description": "A test build for WvW",
    "game_mode": "wvw",
    "team_size": 5,
    "is_public": True,
    "config": {"roles": ["heal", "dps"]},
    "constraints": {"max_duplicates": 2},
    "profession_ids": [1, 2, 3],
}

# Test data for database models
TEST_DB_BUILD_DATA = {
    **TEST_BUILD_DATA,
    "id": 1,
    "owner_id": 1,  # Required field for BuildInDBBase
    "created_by_id": 1,
    "created_at": datetime.now(UTC),
    "updated_at": datetime.now(UTC),
    "professions": [
        {"id": 1, "name": "Guardian", "description": "Heavy armor profession"},
        {"id": 2, "name": "Firebrand", "description": "Elite specialization"},
    ],
}


class TestBuildBase:
    """Test the BuildBase schema."""

    def test_valid_build_base(self):
        """Test creating a valid BuildBase instance."""
        build = BuildBase(**TEST_BUILD_DATA)
        assert build.name == "Test Build"
        assert build.game_mode == "wvw"
        assert build.team_size == 5
        assert build.is_public is True
        assert build.config == {"roles": ["heal", "dps"]}
        assert build.constraints == {"max_duplicates": 2}
        assert build.profession_ids == [1, 2, 3]

    def test_invalid_game_mode(self):
        """Test invalid game mode raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            BuildBase(**{**TEST_BUILD_DATA, "game_mode": "invalid_mode"})

        assert "Input should be 'wvw', 'pvp', 'pve', 'raids' or 'fractals'" in str(
            exc_info.value
        )

    def test_team_size_validation(self):
        """Test team size validation."""
        # Test minimum team size
        with pytest.raises(ValidationError) as exc_info:
            BuildBase(**{**TEST_BUILD_DATA, "team_size": 0})
        assert "Input should be greater than or equal to 1" in str(exc_info.value)

        # Test maximum team size
        with pytest.raises(ValidationError) as exc_info:
            BuildBase(**{**TEST_BUILD_DATA, "team_size": 51})
        assert "Input should be less than or equal to 50" in str(exc_info.value)

    def test_name_validation(self):
        """Test name validation."""
        # Test min length
        with pytest.raises(ValidationError) as exc_info:
            BuildBase(**{**TEST_BUILD_DATA, "name": "ab"})
        assert "String should have at least 3 characters" in str(exc_info.value)

        # Test max length
        long_name = "a" * 101
        with pytest.raises(ValidationError) as exc_info:
            BuildBase(**{**TEST_BUILD_DATA, "name": long_name})
        assert "String should have at most 100 characters" in str(exc_info.value)

    def test_default_values(self):
        """Test default values for optional fields."""
        minimal_data = {"name": "Minimal Build", "game_mode": "wvw"}
        build = BuildBase(**minimal_data)
        assert build.team_size == 5
        assert build.is_public is True
        assert build.config is None
        assert build.constraints == {}
        assert build.profession_ids == []


class TestBuildCreate:
    """Test the BuildCreate schema."""

    def test_valid_build_create(self):
        """Test creating a valid BuildCreate instance."""
        build = BuildCreate(**TEST_BUILD_DATA)
        assert build.name == "Test Build"
        assert build.game_mode == "wvw"
        assert build.team_size == 5
        assert build.profession_ids == [1, 2, 3]

    def test_missing_required_fields(self):
        """Test missing required fields raise validation errors."""
        # Missing name
        with pytest.raises(ValidationError) as exc_info:
            BuildCreate(**{**TEST_BUILD_DATA, "name": ""})
        assert "String should have at least 3 characters" in str(exc_info.value)

        # Missing game_mode
        with pytest.raises(ValidationError) as exc_info:
            BuildCreate(**{**TEST_BUILD_DATA, "game_mode": None})
        assert "Input should be 'wvw', 'pvp', 'pve', 'raids' or 'fractals'" in str(
            exc_info.value
        )

        # Missing profession_ids
        with pytest.raises(ValidationError) as exc_info:
            BuildCreate(**{**TEST_BUILD_DATA, "profession_ids": []})
        assert "List should have at least 1 item after validation, not 0" in str(
            exc_info.value
        )

    def test_profession_ids_validation(self):
        """Test profession_ids validation."""
        # Test minimum length
        with pytest.raises(ValidationError) as exc_info:
            BuildCreate(**{**TEST_BUILD_DATA, "profession_ids": []})
        assert "List should have at least 1 item after validation, not 0" in str(
            exc_info.value
        )

        # Test maximum length
        with pytest.raises(ValidationError) as exc_info:
            BuildCreate(**{**TEST_BUILD_DATA, "profession_ids": [1, 2, 3, 4]})
        assert "List should have at most 3 items after validation, not 4" in str(
            exc_info.value
        )

    def test_optional_fields(self):
        """Test that optional fields work as expected."""
        # Create a copy of the test data without constraints
        test_data = {k: v for k, v in TEST_BUILD_DATA.items() if k != "constraints"}

        build_data = {
            **test_data,
            "description": None,  # Optional field
            "config": None,  # Optional field
        }

        BuildCreate(**build_data)
        with pytest.raises(ValidationError) as exc_info:
            BuildCreate(**{**TEST_BUILD_DATA, "profession_ids": [1, 2, 3, 4]})
        assert "List should have at most 3 items after validation, not 4" in str(
            exc_info.value
        )

        # Test invalid profession ID type (string instead of integer)
        with pytest.raises(ValidationError) as exc_info:
            BuildCreate(**{**TEST_BUILD_DATA, "profession_ids": ["not_an_integer"]})
        assert "Input should be a valid integer" in str(exc_info.value)

    def test_build_create_with_minimal_data(self):
        """Test creating a build with minimal required data."""
        minimal_data = {
            "name": "Minimal Build",
            "game_mode": "wvw",
            "profession_ids": [1],
        }
        build = BuildCreate(**minimal_data)
        assert build.name == "Minimal Build"
        assert build.game_mode == "wvw"
        assert build.team_size == 5  # Default value
        assert build.is_public is True  # Default value
        assert build.profession_ids == [1]
        assert build.is_public is True  # Default value
        assert build.constraints == {}  # Should be an empty dict by default


class TestBuildUpdate:
    """Test the BuildUpdate schema."""

    def test_build_update_partial(self):
        """Test that BuildUpdate allows partial updates."""
        # Update just the name
        update_data = {"name": "Updated Build Name"}
        build_update = BuildUpdate(**update_data)
        assert build_update.name == "Updated Build Name"
        assert build_update.description is None

        # Update just the description
        update_data = {"description": "Updated description"}
        build_update = BuildUpdate(**update_data)
        assert build_update.description == "Updated description"
        assert build_update.name is None

        # Update profession_ids
        update_data = {"profession_ids": [4, 5]}
        build_update = BuildUpdate(**update_data)
        assert build_update.profession_ids == [4, 5]

    def test_build_update_validation(self):
        """Test validation in BuildUpdate."""
        # Test invalid game mode
        with pytest.raises(ValidationError):
            BuildUpdate(game_mode="invalid_mode")

        # Test team size validation
        with pytest.raises(ValidationError):
            BuildUpdate(team_size=0)

        with pytest.raises(ValidationError):
            BuildUpdate(team_size=51)

        # Test profession_ids validation
        with pytest.raises(ValidationError):
            BuildUpdate(profession_ids=[])

        with pytest.raises(ValidationError):
            BuildUpdate(profession_ids=[1, 2, 3, 4])


class TestBuildModels:
    """Test the Build model schemas (BuildInDBBase, Build, BuildInDB)."""

    def test_build_in_db_base(self):
        """Test the BuildInDBBase schema."""
        build = BuildInDBBase(**TEST_DB_BUILD_DATA)
        assert build.id == 1
        assert build.created_by_id == 1
        assert len(build.professions) == 2
        assert build.professions[0].name == "Guardian"

    def test_build_model(self):
        """Test the Build schema (API response model)."""
        # Create a Build instance with the test data
        build = Build(**TEST_DB_BUILD_DATA)  # owner_id is already in TEST_DB_BUILD_DATA
        assert build.id == 1
        assert build.owner_id == 1
        assert build.name == "Test Build"
        assert build.game_mode == "wvw"
        assert build.team_size == 5
        assert build.is_public is True
        assert len(build.professions) == 2
        assert build.professions[0].name == "Guardian"
        assert "constraints" in build.model_dump()

    def test_build_in_db(self):
        """Test the BuildInDB schema (database model)."""
        # Create the BuildInDB instance with the test data
        build = BuildInDB(**TEST_DB_BUILD_DATA)

        # Assert the expected values
        assert build.id == 1
        assert build.created_by_id == 1
        assert build.created_at is not None
        assert build.updated_at is not None
        assert len(build.professions) == 2
        assert build.professions[0].name == "Guardian"

        # Check that the model_dump includes all expected fields
        dump = build.model_dump()
        assert "id" in dump
        assert "created_by_id" in dump
        assert "created_at" in dump
        assert "updated_at" in dump
        assert "professions" in dump
        assert "profession_ids" in dump
