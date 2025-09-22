"""Tests for build schemas."""

import pytest
from datetime import datetime, timezone
from app.schemas.build import (
    BuildBase,
    BuildCreate,
    BuildUpdate,
    BuildInDB,
    GameMode,
    RoleType,
    BuildGenerationRequest,
    TeamMember,
    BuildGenerationResponse,
)

# Test data
SAMPLE_BUILD_DATA = {
    "name": "WvW Zerg Firebrand",
    "description": "Support build for WvW zergs",
    "game_mode": "wvw",
    "team_size": 5,
    "is_public": True,
    "config": {
        "weapons": ["Axe", "Shield", "Mace", "Focus"],
        "traits": ["Radiance", "Honor", "Firebrand"],
        "skills": ["Mantra of Potence", "Mantra of Solace", "Mantra of Liberation"],
    },
    "constraints": {"required_roles": ["quickness", "stability"], "min_healers": 1},
    "profession_ids": [1, 2],
}


class TestBuildSchemas:
    """Test cases for Build related schemas."""

    def test_build_base(self):
        """Test BuildBase schema with valid data."""
        build = BuildBase(**SAMPLE_BUILD_DATA)
        assert build.name == "WvW Zerg Firebrand"
        assert build.description == "Support build for WvW zergs"
        assert build.game_mode == GameMode.WVW
        assert build.team_size == 5
        assert build.is_public is True
        assert build.config["weapons"] == ["Axe", "Shield", "Mace", "Focus"]
        assert build.constraints["required_roles"] == ["quickness", "stability"]

    def test_build_base_empty_name(self):
        """Test BuildBase with empty name raises validation error."""
        invalid_data = SAMPLE_BUILD_DATA.copy()
        invalid_data["name"] = ""
        with pytest.raises(
            ValueError, match="String should have at least 3 characters"
        ):
            BuildBase(**invalid_data)

    def test_build_base_whitespace_name(self):
        """Test BuildBase with whitespace name is preserved as is."""
        # Pydantic v2 ne supprime pas automatiquement les espaces dans les chaînes
        data = SAMPLE_BUILD_DATA.copy()
        data["name"] = "   Test   "
        build = BuildBase(**data)
        assert build.name == "   Test   "  # Les espaces sont conservés

    def test_build_base_invalid_team_size(self):
        """Test BuildBase with invalid team size raises validation error."""
        invalid_data = SAMPLE_BUILD_DATA.copy()
        invalid_data["team_size"] = 0
        with pytest.raises(
            ValueError, match="Input should be greater than or equal to 1"
        ):
            BuildBase(**invalid_data)

    def test_build_base_invalid_game_mode(self):
        """Test BuildBase with invalid game mode raises validation error."""
        invalid_data = SAMPLE_BUILD_DATA.copy()
        invalid_data["game_mode"] = "invalid_mode"
        with pytest.raises(
            ValueError,
            match="Input should be 'wvw', 'pvp', 'pve', 'raids' or 'fractals'",
        ):
            BuildBase(**invalid_data)

    def test_build_create(self):
        """Test BuildCreate schema with valid data."""
        build = BuildCreate(**SAMPLE_BUILD_DATA)
        assert build.name == "WvW Zerg Firebrand"
        assert build.description == "Support build for WvW zergs"
        assert build.game_mode == GameMode.WVW
        assert build.team_size == 5
        assert build.is_public is True

    def test_build_update_partial(self):
        """Test BuildUpdate schema with partial data."""
        update_data = {
            "name": "Updated WvW Zerg Firebrand",
            "description": "Updated description",
        }
        build = BuildUpdate(**update_data)
        assert build.name == "Updated WvW Zerg Firebrand"
        assert build.description == "Updated description"
        assert build.game_mode is None
        assert build.team_size is None

    def test_build_update_empty_name(self):
        """Test BuildUpdate with empty name raises validation error."""
        with pytest.raises(
            ValueError, match="String should have at least 3 characters"
        ):
            BuildUpdate(name="")

    def test_build_update_invalid_team_size(self):
        """Test BuildUpdate with invalid team size raises validation error."""
        with pytest.raises(
            ValueError, match="Input should be greater than or equal to 1"
        ):
            BuildUpdate(team_size=0)

    def test_build_in_db(self):
        """Test BuildInDB schema with database fields."""
        now = datetime.now(timezone.utc)
        db_data = {
            "id": 1,
            "created_by_id": 1,
            "created_at": now,
            "updated_at": now,
            "profession_ids": [1, 2],
            "professions": [
                {"id": 1, "name": "Guardian", "description": "Heavy armor profession"},
                {"id": 2, "name": "Firebrand", "description": "Elite specialization"},
            ],
            **SAMPLE_BUILD_DATA,
        }
        build = BuildInDB(**db_data)
        assert build.id == 1
        assert build.created_by_id == 1
        assert build.created_at == now
        assert build.updated_at == now
        assert build.profession_ids == [1, 2]
        assert len(build.professions) == 2
        assert build.professions[0].name == "Guardian"
        assert build.professions[1].name == "Firebrand"

    def test_build_in_db_missing_required(self):
        """Test BuildInDB with missing required fields raises validation error."""
        with pytest.raises(ValueError):
            BuildInDB(
                id=1, **SAMPLE_BUILD_DATA
            )  # Missing created_by_id, created_at, updated_at


class TestBuildGeneration:
    """Test cases for build generation schemas."""

    def test_build_generation_request_defaults(self):
        """Test BuildGenerationRequest schema with default values."""
        request = BuildGenerationRequest(required_roles=[])
        assert request.required_roles == []
        assert request.preferred_professions == []
        assert request.max_duplicates == 2
        assert request.min_healers == 1
        assert request.min_dps == 2
        assert request.min_support == 1
        assert request.team_size == 5
        assert request.constraints == {}

    def test_build_generation_request_full(self):
        """Test BuildGenerationRequest schema with all fields."""
        request_data = {
            "required_roles": ["quickness", "alacrity"],
            "preferred_professions": [1, 2, 3],
            "max_duplicates": 2,
            "min_healers": 1,
            "min_dps": 2,
            "min_support": 1,
            "constraints": {
                "require_cc": True,
                "require_cleanses": True,
                "require_stability": True,
                "require_projectile_mitigation": True,
            },
        }
        request = BuildGenerationRequest(**request_data)
        assert request.required_roles == [RoleType.QUICKNESS, RoleType.ALACRITY]
        assert request.preferred_professions == [1, 2, 3]
        assert request.max_duplicates == 2
        assert request.min_healers == 1
        assert request.min_dps == 2
        assert request.min_support == 1
        assert request.team_size == 5
        assert request.constraints["require_cc"] is True

    def test_build_generation_request_invalid_roles(self):
        """Test BuildGenerationRequest with invalid roles raises validation error."""
        with pytest.raises(
            ValueError,
            match="Input should be 'healer', 'quickness', 'alacrity', 'might', 'fury', 'aegis', 'stability', 'dps', 'support' or 'utility'",
        ):
            BuildGenerationRequest(required_roles=["invalid_role"])

    def test_team_member_required_fields(self):
        """Test TeamMember schema with required fields only."""
        member_data = {
            "position": 1,
            "profession": "Guardian",
            "role": "Healer/Support",
            "build": "Firebrand - Quickness Support",
        }
        member = TeamMember(**member_data)
        assert member.position == 1
        assert member.profession == "Guardian"
        assert member.role == "Healer/Support"
        assert member.build == "Firebrand - Quickness Support"
        assert member.required_boons == []
        assert member.required_utilities == []

    def test_team_member_full(self):
        """Test TeamMember schema with all fields."""
        member_data = {
            "position": 1,
            "profession": "Guardian",
            "role": "Healer/Support",
            "build": "Firebrand - Quickness Support",
            "required_boons": ["Quickness", "Stability", "Aegis"],
            "required_utilities": ["Stability on Aegis", "Condition Cleanse"],
        }
        member = TeamMember(**member_data)
        assert member.position == 1
        assert member.profession == "Guardian"
        assert member.role == "Healer/Support"
        assert member.build == "Firebrand - Quickness Support"
        assert "Quickness" in member.required_boons
        assert "Condition Cleanse" in member.required_utilities

    def test_build_generation_response_minimal(self):
        """Test BuildGenerationResponse with minimal required fields."""
        response_data = {
            "success": True,
            "message": "Build generated successfully",
            "build": {
                "id": 1,
                "name": "Test Build",
                "game_mode": "wvw",
                "team_size": 5,
                "is_public": True,
                "created_by_id": 1,
                "owner_id": 1,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
                "profession_ids": [1],
                "professions": [{"id": 1, "name": "Guardian"}],
            },
            "suggested_composition": [],
            "metrics": {},
        }
        response = BuildGenerationResponse(**response_data)
        assert response.success is True
        assert response.message == "Build generated successfully"
        assert response.build.name == "Test Build"
        assert response.suggested_composition == []
        assert response.metrics == {}

    def test_build_generation_response_full(self):
        """Test BuildGenerationResponse with all fields."""
        now = datetime.now(timezone.utc).isoformat()
        build_data = {
            "id": 1,
            "name": "Test Build",
            "description": "Test build description",
            "game_mode": "wvw",
            "team_size": 5,
            "is_public": True,
            "created_by_id": 1,
            "owner_id": 1,
            "created_at": now,
            "updated_at": now,
            "profession_ids": [1, 2],
            "professions": [
                {"id": 1, "name": "Guardian", "description": "Heavy armor profession"},
                {"id": 2, "name": "Firebrand", "description": "Elite specialization"},
            ],
        }
        member_data = {
            "position": 1,
            "profession": "Guardian",
            "role": "Support",
            "build": "Firebrand",
            "required_boons": ["Quickness", "Stability"],
            "required_utilities": ["Stability on Aegis", "Condition Cleanse"],
        }

        response_data = {
            "success": True,
            "message": "Build generated successfully",
            "build": build_data,
            "suggested_composition": [member_data],
            "metrics": {
                "boon_coverage": {"quickness": 100.0, "alacrity": 100.0},
                "role_distribution": {"healer": 1, "dps": 2, "support": 2},
                "profession_distribution": {
                    "Guardian": 2,
                    "Elementalist": 1,
                    "Revenant": 2,
                },
            },
        }

        response = BuildGenerationResponse(**response_data)
        assert response.success is True
        assert response.message == "Build generated successfully"
        assert response.build.name == "Test Build"
        assert len(response.suggested_composition) == 1
        assert response.suggested_composition[0].profession == "Guardian"
        assert "quickness" in response.metrics["boon_coverage"]
        assert response.metrics["role_distribution"]["healer"] == 1

    def test_build_generation_response_missing_required(self):
        """Test BuildGenerationResponse with missing required fields raises validation error."""
        with pytest.raises(ValueError):
            # Missing required fields in the build object
            BuildGenerationResponse(
                success=True,
                message="Test",
                build={
                    # Missing required fields like name, game_mode, etc.
                    "id": 1
                },
                suggested_composition=[],
                metrics={},
            )
