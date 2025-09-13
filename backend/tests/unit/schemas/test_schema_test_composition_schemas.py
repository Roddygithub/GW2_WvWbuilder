"""Tests for composition-related Pydantic schemas."""
import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from app.schemas.composition import (
    CompositionMemberRole,
    CompositionMemberBase,
    CompositionBase,
    CompositionCreate,
    CompositionUpdate,
    CompositionInDBBase,
    Composition,
    CompositionTagBase,
    CompositionTagCreate,
    CompositionTagUpdate,
    CompositionTagInDBBase,
    CompositionSearch,
    CompositionOptimizationRequest,
    CompositionOptimizationResult,
    CompositionEvaluation,
)

class TestCompositionMemberRole:
    """Tests for the CompositionMemberRole enum."""
    
    def test_role_values(self):
        """Test that all role values are correct."""
        assert CompositionMemberRole.HEALER == "healer"
        assert CompositionMemberRole.DPS == "dps"
        assert CompositionMemberRole.SUPPORT == "support"
        assert CompositionMemberRole.TANK == "tank"
        assert CompositionMemberRole.BOON_SUPPORT == "boon_support"
        assert CompositionMemberRole.CONDITION_DAMAGE == "condition_damage"
        assert CompositionMemberRole.POWER_DAMAGE == "power_damage"
        assert CompositionMemberRole.HYBRID == "hybrid"
        assert CompositionMemberRole.CROWD_CONTROL == "crowd_control"
        assert CompositionMemberRole.UTILITY == "utility"


class TestCompositionMemberBase:
    """Tests for the CompositionMemberBase schema."""
    
    def test_valid_member(self):
        """Test valid composition member creation."""
        data = {
            "user_id": 1,
            "role_id": 2,
            "profession_id": 3,
            "elite_specialization_id": 4,
            "role_type": "healer",
            "notes": "Focus on healing",
            "is_commander": True,
            "is_secondary_commander": False,
            "custom_build_url": "https://example.com/build",
            "priority": 1
        }
        member = CompositionMemberBase(**data)
        assert member.user_id == data["user_id"]
        assert member.role_type == CompositionMemberRole.HEALER
        assert member.priority == 1
    
    def test_priority_validation(self):
        """Test priority validation."""
        # Test priority below minimum
        with pytest.raises(ValidationError):
            CompositionMemberBase(
                user_id=1, 
                role_id=1, 
                profession_id=1, 
                role_type="healer",
                priority=0
            )
        
        # Test priority above maximum
        with pytest.raises(ValidationError):
            CompositionMemberBase(
                user_id=1, 
                role_id=1, 
                profession_id=1, 
                role_type="healer",
                priority=4
            )


class TestCompositionBase:
    """Tests for the CompositionBase schema."""
    
    def test_valid_composition(self):
        """Test valid composition creation."""
        data = {
            "name": "Test Composition",
            "description": "A test composition",
            "squad_size": 10,
            "is_public": True,
            "tags": ["test", "wvw"],
            "game_mode": "wvw",
            "min_players": 5,
            "max_players": 15
        }
        comp = CompositionBase(**data)
        assert comp.name == data["name"]
        assert comp.squad_size == 10
        assert comp.is_public is True
        assert comp.tags == ["test", "wvw"]
    
    def test_squad_size_validation(self):
        """Test squad size validation."""
        # Test squad size below minimum
        with pytest.raises(ValidationError):
            CompositionBase(
                name="Test",
                squad_size=0,
                game_mode="wvw"
            )
        
        # Test squad size above maximum
        with pytest.raises(ValidationError):
            CompositionBase(
                name="Test",
                squad_size=51,
                game_mode="wvw"
            )
    
    def test_max_players_gte_min_players(self):
        """Test that max_players cannot be less than min_players."""
        with pytest.raises(ValueError, match="max_players must be greater than or equal to min_players"):
            CompositionBase(
                name="Test",
                squad_size=10,
                game_mode="wvw",
                min_players=5,
                max_players=4
            )


class TestCompositionCreate:
    """Tests for the CompositionCreate schema."""
    
    def test_create_with_members(self):
        """Test creating a composition with members."""
        data = {
            "name": "Test Comp",
            "squad_size": 5,
            "game_mode": "wvw",
            "members": [
                {
                    "user_id": 1,
                    "role_id": 1,
                    "profession_id": 1,
                    "role_type": "healer"
                }
            ],
            "created_by": 1
        }
        comp = CompositionCreate(**data)
        assert len(comp.members) == 1
        assert comp.members[0].user_id == 1
        assert comp.created_by == 1


class TestCompositionUpdate:
    """Tests for the CompositionUpdate schema."""
    
    def test_partial_update(self):
        """Test updating a subset of fields."""
        update = CompositionUpdate(name="Updated Name")
        assert update.name == "Updated Name"
        assert update.description is None
    
    def test_update_with_members(self):
        """Test updating composition members."""
        update = CompositionUpdate(
            name="Updated",
            members=[
                {
                    "user_id": 2,
                    "role_id": 2,
                    "profession_id": 2,
                    "role_type": "dps"
                }
            ]
        )
        assert update.name == "Updated"
        assert len(update.members) == 1
        assert update.members[0].user_id == 2


class TestCompositionSearch:
    """Tests for the CompositionSearch schema."""
    
    def test_search_params(self):
        """Test search parameters."""
        search = CompositionSearch(
            name="zerg",
            min_players=5,
            max_players=20,
            tags=["frontline", "meta"],
            game_mode="wvw",
            is_public=True,
            sort_by="created_at",
            sort_order="desc",
            offset=0,
            limit=10
        )
        assert search.name == "zerg"
        assert search.min_players == 5
        assert search.max_players == 20
        assert search.tags == ["frontline", "meta"]
        assert search.limit == 10
    
    def test_sort_order_validation(self):
        """Test sort order validation."""
        with pytest.raises(ValidationError):
            CompositionSearch(sort_order="invalid")


class TestCompositionOptimizationRequest:
    """Tests for the CompositionOptimizationRequest schema."""
    
    def test_optimization_request(self):
        """Test optimization request creation."""
        request = CompositionOptimizationRequest(
            squad_size=10,
            fixed_roles=[
                {"profession_id": 1, "elite_specialization_id": 3, "count": 2, "role_type": "healer"}
            ],
            game_mode="wvw",
            preferred_roles={"healer": 2, "dps": 5, "support": 3},
            min_boon_uptime={"might": 0.9, "quickness": 0.8},
            min_healing=0.8,
            min_damage=0.7,
            min_cc=0.6,
            min_cleanses=5,
            preferred_weapons=[
                {"profession_id": 1, "weapon": "staff", "role_type": "healer"}
            ],
            excluded_elite_specializations=[10, 15],
            optimization_goals=["boon_uptime", "healing", "damage"]
        )
        assert request.squad_size == 10
        assert len(request.fixed_roles) == 1
        assert request.preferred_roles["healer"] == 2
        assert request.min_boon_uptime["might"] == 0.9
        assert request.optimization_goals == ["boon_uptime", "healing", "damage"]


class TestCompositionTagBase:
    """Tests for the CompositionTagBase schema."""
    
    def test_tag_creation(self):
        """Test tag creation."""
        tag = CompositionTagBase(
            name="zerg",
            description="Ideal for large scale battles"
        )
        assert tag.name == "zerg"
        assert tag.description == "Ideal for large scale battles"
    
    def test_name_validation(self):
        """Test name validation."""
        # Test empty name
        with pytest.raises(ValidationError):
            CompositionTagBase(name="")
        
        # Test name too long
        with pytest.raises(ValidationError):
            CompositionTagBase(name="a" * 51)


class TestCompositionEvaluation:
    """Tests for the CompositionEvaluation schema."""
    
    def test_evaluation_creation(self):
        """Test evaluation creation."""
        eval_data = {
            "composition_id": 1,
            "evaluator_id": 1,
            "rating": 4,
            "feedback": "Great composition!",
            "suggested_improvements": ["Add more condition cleanses"],
            "is_public": True,
            "game_version": "2023-11-28",
            "game_mode": "wvw",
            "tags": ["zerg", "frontline"]
        }
        evaluation = CompositionEvaluation(**eval_data)
        assert evaluation.composition_id == 1
        assert evaluation.rating == 4
        assert evaluation.feedback == "Great composition!"
        assert evaluation.tags == ["zerg", "frontline"]
    
    def test_rating_validation(self):
        """Test rating validation."""
        # Test rating below minimum
        with pytest.raises(ValidationError):
            CompositionEvaluation(
                composition_id=1,
                evaluator_id=1,
                rating=0
            )
        
        # Test rating above maximum
        with pytest.raises(ValidationError):
            CompositionEvaluation(
                composition_id=1,
                evaluator_id=1,
                rating=6
            )


if __name__ == "__main__":
    pytest.main([__file__])
