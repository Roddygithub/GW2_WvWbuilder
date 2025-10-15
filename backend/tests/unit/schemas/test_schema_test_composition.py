"""Tests for composition schemas."""

from datetime import datetime, timezone, timedelta
from app.schemas.composition import (
    CompositionBase,
    CompositionCreate,
    CompositionUpdate,
    CompositionInDB,
    CompositionMemberBase,
    CompositionMemberRole,
    CompositionTagBase,
    CompositionTagCreate,
    CompositionTagUpdate,
    CompositionSearch,
    CompositionOptimizationRequest,
    CompositionEvaluation,
)

# Test data
SAMPLE_MEMBER_DATA = {
    "user_id": 1,
    "role_id": 1,
    "profession_id": 1,
    "elite_specialization_id": 3,
    "role_type": "healer",
    "notes": "Focus on healing the frontline",
    "is_commander": True,
    "is_secondary_commander": False,
    "custom_build_url": "https://snowcrows.com/builds/guardian/firebrand",
    "priority": 1,
}

SAMPLE_COMPOSITION_DATA = {
    "name": "WvW Zerg Frontline",
    "description": "Balanced frontline composition with strong healing and boon support",
    "squad_size": 10,
    "is_public": True,
    "tags": ["zerg", "frontline", "meta"],
    "game_mode": "wvw",
    "min_players": 5,
    "max_players": 15,
}


class TestCompositionMemberSchemas:
    """Test cases for CompositionMember related schemas."""

    def test_member_base(self):
        """Test CompositionMemberBase schema."""
        member = CompositionMemberBase(**SAMPLE_MEMBER_DATA)
        assert member.user_id == 1
        assert member.role_id == 1
        assert member.profession_id == 1
        assert member.elite_specialization_id == 3
        assert member.role_type == CompositionMemberRole.HEALER
        assert member.notes == "Focus on healing the frontline"
        assert member.is_commander is True
        assert member.is_secondary_commander is False
        assert (
            member.custom_build_url == "https://snowcrows.com/builds/guardian/firebrand"
        )
        assert member.priority == 1


class TestCompositionSchemas:
    """Test cases for Composition related schemas."""

    def test_composition_base(self):
        """Test CompositionBase schema."""
        comp = CompositionBase(**SAMPLE_COMPOSITION_DATA)
        assert comp.name == "WvW Zerg Frontline"
        assert (
            comp.description
            == "Balanced frontline composition with strong healing and boon support"
        )
        assert comp.squad_size == 10
        assert comp.is_public is True
        assert comp.tags == ["zerg", "frontline", "meta"]
        assert comp.game_mode == "wvw"
        assert comp.min_players == 5
        assert comp.max_players == 15

    def test_composition_create(self):
        """Test CompositionCreate schema."""
        create_data = {
            **SAMPLE_COMPOSITION_DATA,
            "members": [SAMPLE_MEMBER_DATA],
            "created_by": 1,
        }
        comp = CompositionCreate(**create_data)
        assert comp.name == "WvW Zerg Frontline"
        assert len(comp.members) == 1
        assert comp.members[0].user_id == 1
        assert comp.created_by == 1

    def test_composition_update(self):
        """Test CompositionUpdate schema with partial data."""
        update_data = {
            "name": "Updated Zerg Frontline",
            "description": "Updated description",
            "tags": ["zerg", "frontline", "updated"],
        }
        comp = CompositionUpdate(**update_data)
        assert comp.name == "Updated Zerg Frontline"
        assert comp.description == "Updated description"
        assert "updated" in comp.tags
        assert comp.squad_size is None

    def test_composition_in_db(self):
        """Test CompositionInDB schema with database fields."""
        now = datetime.now(timezone.utc)
        db_data = {
            "id": 1,
            "created_by": 1,
            "created_at": now,
            "updated_at": now + timedelta(hours=1),
            **SAMPLE_COMPOSITION_DATA,
        }
        comp = CompositionInDB(**db_data)
        assert comp.id == 1
        assert comp.created_by == 1
        assert comp.created_at == now
        assert comp.updated_at == now + timedelta(hours=1)
        assert comp.name == "WvW Zerg Frontline"


class TestCompositionTagSchemas:
    """Test cases for CompositionTag related schemas."""

    def test_tag_base(self):
        """Test CompositionTagBase schema."""
        tag_data = {"name": "zerg", "description": "Ideal for large scale battles"}
        tag = CompositionTagBase(**tag_data)
        assert tag.name == "zerg"
        assert tag.description == "Ideal for large scale battles"

    def test_tag_create(self):
        """Test CompositionTagCreate schema."""
        tag_data = {"name": "zerg"}
        tag = CompositionTagCreate(**tag_data)
        assert tag.name == "zerg"

    def test_tag_update(self):
        """Test CompositionTagUpdate schema with partial data."""
        update_data = {"name": "zerg_updated", "description": "Updated description"}
        tag = CompositionTagUpdate(**update_data)
        assert tag.name == "zerg_updated"
        assert tag.description == "Updated description"


class TestCompositionSearch:
    """Test cases for CompositionSearch schema."""

    def test_search_defaults(self):
        """Test CompositionSearch with default values."""
        search = CompositionSearch()
        assert search.name is None
        assert search.min_players is None
        assert search.max_players is None
        assert search.tags is None
        assert search.game_mode is None
        assert search.created_by is None
        assert search.is_public is True
        assert search.sort_by == "created_at"
        assert search.sort_order == "desc"
        assert search.offset == 0
        assert search.limit == 10

    def test_search_with_filters(self):
        """Test CompositionSearch with custom filters."""
        search_data = {
            "name": "zerg",
            "min_players": 5,
            "max_players": 20,
            "tags": ["frontline", "meta"],
            "game_mode": "wvw",
            "is_public": True,
            "sort_by": "name",
            "sort_order": "asc",
            "offset": 10,
            "limit": 20,
        }
        search = CompositionSearch(**search_data)
        assert search.name == "zerg"
        assert search.min_players == 5
        assert search.max_players == 20
        assert search.tags == ["frontline", "meta"]
        assert search.game_mode == "wvw"
        assert search.is_public is True
        assert search.sort_by == "name"
        assert search.sort_order == "asc"
        assert search.offset == 10
        assert search.limit == 20


class TestCompositionOptimization:
    """Test cases for composition optimization schemas."""

    def test_optimization_request(self):
        """Test CompositionOptimizationRequest schema."""
        request_data = {
            "squad_size": 10,
            "fixed_roles": [
                {
                    "profession_id": 1,
                    "elite_specialization_id": 3,
                    "count": 2,
                    "role_type": "healer",
                },
                {
                    "profession_id": 2,
                    "elite_specialization_id": 5,
                    "count": 3,
                    "role_type": "dps",
                },
            ],
            "game_mode": "wvw",
            "preferred_roles": {"healer": 2, "dps": 5, "support": 3},
            "min_boon_uptime": {"might": 0.9, "quickness": 0.8, "alacrity": 0.7},
            "min_healing": 0.8,
            "min_damage": 0.7,
            "min_cc": 0.6,
            "min_cleanses": 5,
            "preferred_weapons": [
                {"profession_id": 1, "weapon": "staff", "role_type": "healer"},
                {"profession_id": 2, "weapon": "greatsword", "role_type": "dps"},
            ],
            "excluded_elite_specializations": [10, 15],
            "optimization_goals": ["boon_uptime", "healing", "damage"],
        }
        request = CompositionOptimizationRequest(**request_data)
        assert request.squad_size == 10
        assert len(request.fixed_roles) == 2
        assert request.fixed_roles[0].profession_id == 1
        assert request.fixed_roles[0].role_type == "healer"
        assert request.preferred_roles["healer"] == 2
        assert request.min_boon_uptime["quickness"] == 0.8
        assert request.min_healing == 0.8
        assert request.min_damage == 0.7
        assert request.min_cc == 0.6
        assert request.min_cleanses == 5
        assert len(request.preferred_weapons) == 2
        assert request.preferred_weapons[0].weapon == "staff"
        assert request.excluded_elite_specializations == [10, 15]
        assert request.optimization_goals == ["boon_uptime", "healing", "damage"]


class TestCompositionEvaluationSchema:
    """Test cases for CompositionEvaluation schema."""

    def test_evaluation(self):
        """Test CompositionEvaluation schema."""
        eval_data = {
            "composition_id": 1,
            "evaluator_id": 1,
            "rating": 4,
            "feedback": "Great composition for zerg fights!",
            "suggested_improvements": [
                "Add more condition cleanses",
                "Consider adding more stability",
            ],
            "is_public": True,
            "game_version": "2023-11-28",
            "game_mode": "wvw",
            "tags": ["zerg", "frontline", "meta"],
        }
        evaluation = CompositionEvaluation(**eval_data)
        assert evaluation.composition_id == 1
        assert evaluation.evaluator_id == 1
        assert evaluation.rating == 4
        assert evaluation.feedback == "Great composition for zerg fights!"
        assert len(evaluation.suggested_improvements) == 2
        assert evaluation.is_public is True
        assert evaluation.game_version == "2023-11-28"
        assert evaluation.game_mode == "wvw"
        assert evaluation.tags == ["zerg", "frontline", "meta"]
