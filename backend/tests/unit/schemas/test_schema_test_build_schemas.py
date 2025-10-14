"""Tests for build-related Pydantic schemas."""

import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from app.schemas.build import (
    BuildBase,
    BuildCreate,
    BuildUpdate,
    BuildInDBBase,
    BuildProfessionBase,
    GameMode,
    RoleType,
    BuildGenerationRequest,
    TeamMember,
    BuildGenerationResponse,
)


class TestBuildBase:
    """Tests for the BuildBase schema."""

    def test_valid_build_base(self):
        """Test valid BuildBase creation."""
        data = {
            "name": "WvW Zerg Firebrand",
            "description": "Support build for WvW zergs",
            "game_mode": "wvw",
            "team_size": 5,
            "is_public": True,
            "config": {"weapons": ["Axe", "Shield"]},
            "constraints": {"min_healers": 1},
            "profession_ids": [1, 2],
        }
        build = BuildBase(**data)
        assert build.name == data["name"]
        assert build.description == data["description"]
        assert build.game_mode == GameMode.WVW
        assert build.team_size == data["team_size"]
        assert build.is_public is True
        assert build.config == data["config"]
        assert build.constraints == data["constraints"]
        assert build.profession_ids == data["profession_ids"]

    def test_build_base_validation_errors(self):
        """Test BuildBase validation errors."""
        # Test name too short
        with pytest.raises(ValidationError) as exc_info:
            BuildBase(name="ab", game_mode="wvw")
        assert "String should have at least 3 characters" in str(exc_info.value)

        # Test invalid game mode
        with pytest.raises(ValidationError) as exc_info:
            BuildBase(name="Test Build", game_mode="invalid")
        assert "Input should be 'wvw', 'pvp', 'pve', 'raids' or 'fractals'" in str(exc_info.value)

        # Test team size out of range
        with pytest.raises(ValidationError) as exc_info:
            BuildBase(name="Test Build", game_mode="wvw", team_size=0)
        assert "Input should be greater than or equal to 1" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            BuildBase(name="Test Build", game_mode="wvw", team_size=51)
        assert "Input should be less than or equal to 50" in str(exc_info.value)


class TestBuildCreate:
    """Tests for the BuildCreate schema."""

    def test_build_create_valid(self):
        """Test valid BuildCreate creation."""
        data = {
            "name": "WvW Zerg Firebrand",
            "game_mode": "wvw",
            "profession_ids": [1, 2],
        }
        build = BuildCreate(**data)
        assert build.name == data["name"]
        assert build.game_mode == GameMode.WVW
        assert build.profession_ids == data["profession_ids"]

    def test_build_create_validation(self):
        """Test BuildCreate validation."""
        # Test empty profession_ids
        with pytest.raises(ValidationError) as exc_info:
            BuildCreate(name="Test Build", game_mode="wvw", profession_ids=[])
        assert "List should have at least 1 item after validation, not 0" in str(exc_info.value)

        # Test too many profession_ids
        with pytest.raises(ValidationError) as exc_info:
            BuildCreate(name="Test Build", game_mode="wvw", profession_ids=[1, 2, 3, 4])
        assert "List should have at most 3 items" in str(exc_info.value)

    def test_validate_name(self):
        """Test name validation in BuildCreate."""
        # Test valid name
        build = BuildCreate(name="Valid Name 123", game_mode="wvw", profession_ids=[1])
        assert build.name == "Valid Name 123"

        # Test invalid characters
        with pytest.raises(ValueError) as exc_info:
            BuildCreate(name="Invalid@Name!", game_mode="wvw", profession_ids=[1])
        assert "Name can only contain alphanumeric characters, spaces, and hyphens" in str(exc_info.value)


class TestBuildUpdate:
    """Tests for the BuildUpdate schema."""

    def test_build_update_partial(self):
        """Test partial updates with BuildUpdate."""
        # Test updating just name
        update = BuildUpdate(name="Updated Name")
        assert update.name == "Updated Name"
        assert update.description is None

        # Test updating all fields
        data = {
            "name": "Updated Name",
            "description": "Updated description",
            "game_mode": "pve",
            "team_size": 10,
            "is_public": False,
            "config": {"new": "config"},
            "constraints": {"new": "constraints"},
            "profession_ids": [3, 4],
        }
        update = BuildUpdate(**data)
        for field, value in data.items():
            assert getattr(update, field) == value

    def test_build_update_validation(self):
        """Test BuildUpdate validation."""
        # Test empty profession_ids
        with pytest.raises(ValidationError) as exc_info:
            BuildUpdate(profession_ids=[])
        assert "List should have at least 1 item after validation, not 0" in str(exc_info.value)

        # Test too many profession_ids
        with pytest.raises(ValidationError) as exc_info:
            BuildUpdate(profession_ids=[1, 2, 3, 4])
        assert "List should have at most 3 items" in str(exc_info.value)


class TestBuildInDBBase:
    """Tests for the BuildInDBBase schema."""

    def test_build_in_db_base(self):
        """Test BuildInDBBase with all fields."""
        now = datetime.now(timezone.utc)
        data = {
            "id": 1,
            "owner_id": 1,
            "created_by_id": 1,
            "created_at": now,
            "updated_at": now,
            "name": "Test Build",
            "description": "A test build",
            "game_mode": "wvw",
            "team_size": 5,
            "is_public": True,
            "config": {"key": "value"},
            "constraints": {"min_healers": 1},
            "profession_ids": [1, 2],
            "professions": [
                {"id": 1, "name": "Guardian", "description": "Heavy armor"},
                {"id": 2, "name": "Warrior", "description": "Heavy armor"},
            ],
        }
        build = BuildInDBBase(**data)
        assert build.id == 1
        assert build.created_by_id == 1
        assert build.created_at == now
        assert build.updated_at == now
        assert build.name == "Test Build"
        assert build.game_mode == GameMode.WVW
        assert build.profession_ids == [1, 2]
        assert len(build.professions) == 2
        assert build.professions[0].id == 1
        assert build.professions[0].name == "Guardian"


class TestBuildProfessionBase:
    """Tests for the BuildProfessionBase schema."""

    def test_build_profession_base(self):
        """Test BuildProfessionBase creation."""
        data = {"id": 1, "name": "Guardian", "description": "Heavy armor profession"}
        prof = BuildProfessionBase(**data)
        assert prof.id == 1
        assert prof.name == "Guardian"
        assert prof.description == "Heavy armor profession"


class TestBuildGenerationRequest:
    """Tests for the BuildGenerationRequest schema."""

    def test_valid_generation_request(self):
        """Test valid BuildGenerationRequest creation."""
        data = {
            "team_size": 5,
            "required_roles": ["healer", "quickness", "alacrity"],
            "preferred_professions": [1, 2, 3],
            "max_duplicates": 2,
            "min_healers": 1,
            "min_dps": 2,
            "min_support": 1,
            "constraints": {"require_cc": True, "require_cleanses": True},
        }
        req = BuildGenerationRequest(**data)
        assert req.team_size == 5
        assert req.required_roles == [
            RoleType.HEALER,
            RoleType.QUICKNESS,
            RoleType.ALACRITY,
        ]
        assert req.preferred_professions == [1, 2, 3]
        assert req.max_duplicates == 2
        assert req.min_healers == 1
        assert req.min_dps == 2
        assert req.min_support == 1
        assert req.constraints["require_cc"] is True

    def test_validate_roles(self):
        """Test role validation in BuildGenerationRequest."""
        # Test valid roles
        req = BuildGenerationRequest(required_roles=["healer", "quickness", "alacrity"])
        assert len(req.required_roles) == 3

        # Test invalid role
        with pytest.raises(ValueError) as exc_info:
            BuildGenerationRequest(required_roles=["invalid_role"])
        assert (
            "Input should be 'healer', 'quickness', 'alacrity', 'might', 'fury', 'aegis', 'stability', 'dps', 'support' or 'utility'"
            in str(exc_info.value)
        )


class TestTeamMember:
    """Tests for the TeamMember schema."""

    def test_team_member_creation(self):
        """Test TeamMember creation."""
        data = {
            "position": 1,
            "profession": "Guardian",
            "role": "Healer/Support",
            "build": "Firebrand - Quickness Support",
            "required_boons": ["Quickness", "Stability"],
            "required_utilities": ["Stability on Aegis"],
        }
        member = TeamMember(**data)
        assert member.position == 1
        assert member.profession == "Guardian"
        assert member.role == "Healer/Support"
        assert member.build == "Firebrand - Quickness Support"
        assert member.required_boons == ["Quickness", "Stability"]
        assert member.required_utilities == ["Stability on Aegis"]


class TestBuildGenerationResponse:
    """Tests for the BuildGenerationResponse schema."""

    def test_build_generation_response(self):
        """Test BuildGenerationResponse creation."""
        now = datetime.now(timezone.utc)
        build_data = {
            "id": 1,
            "owner_id": 1,
            "created_by_id": 1,
            "created_at": now,
            "updated_at": now,
            "name": "Test Build",
            "description": "A test build",
            "game_mode": "wvw",
            "team_size": 5,
            "is_public": True,
            "config": {"key": "value"},
            "constraints": {"min_healers": 1},
            "profession_ids": [1, 2],
            "professions": [
                {"id": 1, "name": "Guardian", "description": "Heavy armor"},
                {"id": 2, "name": "Warrior", "description": "Heavy armor"},
            ],
        }
        build = BuildInDBBase(**build_data)

        member = TeamMember(
            position=1,
            profession="Guardian",
            role="Healer/Support",
            build="Firebrand - Quickness Support",
        )

        metrics = {
            "boon_coverage": {"quickness": 100.0, "alacrity": 100.0},
            "role_distribution": {"healer": 1, "dps": 2, "support": 2},
        }

        response = BuildGenerationResponse(
            success=True,
            message="Build generated successfully",
            build=build,
            suggested_composition=[member],
            metrics=metrics,
        )

        assert response.success is True
        assert response.message == "Build generated successfully"
        assert response.build.name == "Test Build"
        assert len(response.suggested_composition) == 1
        assert response.suggested_composition[0].profession == "Guardian"
        assert response.metrics["boon_coverage"]["quickness"] == 100.0
