from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class CompositionMemberRole(str, Enum):
    """Roles that a member can have in a composition"""
    HEALER = "healer"
    DPS = "dps"
    SUPPORT = "support"
    TANK = "tank"
    BOON_SUPPORT = "boon_support"
    CONDITION_DAMAGE = "condition_damage"
    POWER_DAMAGE = "power_damage"
    HYBRID = "hybrid"
    CROWD_CONTROL = "crowd_control"
    UTILITY = "utility"

class CompositionMemberBase(BaseModel):
    """Base schema for a member in a composition"""
    user_id: int = Field(..., json_schema_extra={"example": 1})
    role_id: int = Field(..., json_schema_extra={"example": 1})
    profession_id: int = Field(..., json_schema_extra={"example": 1})
    elite_specialization_id: Optional[int] = Field(None, json_schema_extra={"example": 1})
    role_type: CompositionMemberRole = Field(..., json_schema_extra={"example": "healer"})
    notes: Optional[str] = Field(None, json_schema_extra={"example": "Focus on healing the frontline"})
    is_commander: bool = Field(default=False, json_schema_extra={"example": False})
    is_secondary_commander: bool = Field(default=False, json_schema_extra={"example": False})
    custom_build_url: Optional[str] = Field(None, json_schema_extra={"example": "https://snowcrows.com/builds/guardian/firebrand"})
    priority: int = Field(
        default=1,
        ge=1,
        le=3,
        json_schema_extra={"example": 1},
        description="Priority level (1=high, 2=medium, 3=low)",
    )

class CompositionBase(BaseModel):
    """Base schema for composition data"""
    name: str = Field(..., min_length=2, max_length=100, json_schema_extra={"example": "Zerg Frontline"})
    description: Optional[str] = Field(
        None,
        json_schema_extra={"example": "A balanced frontline composition with strong healing and boon support"},
    )
    squad_size: int = Field(
        ..., ge=1, le=50, json_schema_extra={"example": 10}, description="Number of players in the squad (1-50)"
    )
    is_public: bool = Field(default=True, json_schema_extra={"example": True})
    tags: Optional[List[str]] = Field(None, json_schema_extra={"example": ["zerg", "frontline", "meta"]})
    game_mode: str = Field(
        default="wvw",
        json_schema_extra={"example": "wvw"},
        description="Game mode this composition is designed for (wvw, pvp, etc.)",
    )
    min_players: int = Field(
        default=1,
        ge=1,
        le=50,
        json_schema_extra={"example": 5},
        description="Minimum number of players required for this composition",
    )
    max_players: int = Field(
        default=50,
        ge=1,
        le=50,
        json_schema_extra={"example": 50},
        description="Maximum number of players this composition supports",
    )

class CompositionCreate(CompositionBase):
    """Schema for creating a new composition"""
    members: Optional[List[CompositionMemberBase]] = None
    created_by: Optional[int] = Field(None, json_schema_extra={"example": 1})

class CompositionUpdate(BaseModel):
    """Schema for updating composition data"""
    name: Optional[str] = Field(None, min_length=2, max_length=100, json_schema_extra={"example": "Updated Zerg Frontline"})
    description: Optional[str] = None
    squad_size: Optional[int] = Field(None, ge=1, le=50, json_schema_extra={"example": 15})
    is_public: Optional[bool] = None
    tags: Optional[List[str]] = None
    game_mode: Optional[str] = None
    min_players: Optional[int] = Field(None, ge=1, le=50)
    max_players: Optional[int] = Field(None, ge=1, le=50)
    members: Optional[List[CompositionMemberBase]] = None

class CompositionInDBBase(CompositionBase):
    """Base schema for composition data in database"""
    id: int = Field(..., json_schema_extra={"example": 1})
    created_by: int = Field(..., json_schema_extra={"example": 1})
    created_at: datetime = Field(..., json_schema_extra={"example": "2023-01-01T00:00:00"})
    updated_at: Optional[datetime] = Field(None, json_schema_extra={"example": "2023-01-01T00:00:00"})
    model_config = ConfigDict(from_attributes=True)

class Composition(CompositionInDBBase):
    """Schema for composition data returned by API"""
    members: List[Dict[str, Any]] = Field(default_factory=list)
    tags: List[Dict[str, Any]] = Field(default_factory=list)
    created_by_username: Optional[str] = Field(None, json_schema_extra={"example": "john_doe"})

class CompositionInDB(CompositionInDBBase):
    """Schema for composition data stored in database"""
    pass

class CompositionTagBase(BaseModel):
    """Base schema for composition tag data"""
    name: str = Field(..., min_length=1, max_length=50, json_schema_extra={"example": "zerg"})
    description: Optional[str] = Field(None, json_schema_extra={"example": "Ideal for large scale battles"})

class CompositionTagCreate(CompositionTagBase):
    """Schema for creating a new composition tag"""
    pass

class CompositionTagUpdate(BaseModel):
    """Schema for updating composition tag data"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, json_schema_extra={"example": "zerg_updated"})
    description: Optional[str] = Field(None, json_schema_extra={"example": "Updated description"})

class CompositionTagInDBBase(CompositionTagBase):
    """Base schema for composition tag data in database"""
    id: int = Field(..., json_schema_extra={"example": 1})
    model_config = ConfigDict(from_attributes=True)

class CompositionTag(CompositionTagInDBBase):
    """Schema for composition tag data returned by API"""
    pass

class CompositionTagInDB(CompositionTagInDBBase):
    """Schema for composition tag data stored in database"""
    pass

class CompositionSearch(BaseModel):
    """Schema for searching compositions"""
    name: Optional[str] = None
    min_players: Optional[int] = Field(None, ge=1, le=50)
    max_players: Optional[int] = Field(None, ge=1, le=50)
    tags: Optional[List[str]] = None
    game_mode: Optional[str] = None
    created_by: Optional[int] = None
    is_public: Optional[bool] = True
    sort_by: Optional[str] = Field("created_at", json_schema_extra={"example": "created_at"})
    sort_order: Optional[str] = Field("desc", pattern="^(asc|desc)$", json_schema_extra={"example": "desc"})
    offset: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)

class CompositionOptimizationRequest(BaseModel):
    """Schema for composition optimization request"""
    squad_size: int = Field(..., ge=1, le=50, json_schema_extra={"example": 10})
    fixed_roles: Optional[List[Dict[str, Any]]] = Field(
        None,
        json_schema_extra={
            "example": [
                {"profession_id": 1, "elite_specialization_id": 3, "count": 2, "role_type": "healer"},
                {"profession_id": 2, "elite_specialization_id": 5, "count": 3, "role_type": "dps"}
            ]
        }
    )
    game_mode: str = Field(default="wvw", json_schema_extra={"example": "wvw"})
    preferred_roles: Optional[Dict[str, int]] = Field(
        None,
        json_schema_extra={"example": {"healer": 2, "dps": 5, "support": 3}}
    )
    min_boon_uptime: Optional[Dict[str, float]] = Field(
        None,
        json_schema_extra={"example": {"might": 0.9, "quickness": 0.8, "alacrity": 0.7}}
    )
    min_healing: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        json_schema_extra={"example": 0.8},
        description="Minimum healing output required (0-1 scale)"
    )
    min_damage: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        json_schema_extra={"example": 0.7},
        description="Minimum damage output required (0-1 scale)"
    )
    min_cc: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        json_schema_extra={"example": 0.6},
        description="Minimum crowd control capability (0-1 scale)"
    )
    min_cleanses: Optional[int] = Field(
        None,
        ge=0,
        json_schema_extra={"example": 5},
        description="Minimum number of condition cleanses per second"
    )
    preferred_weapons: Optional[List[Dict[str, Any]]] = Field(
        None,
        json_schema_extra={
            "example": [
                {"profession_id": 1, "weapon": "staff", "role_type": "healer"},
                {"profession_id": 2, "weapon": "greatsword", "role_type": "dps"}
            ]
        }
    )
    excluded_elite_specializations: Optional[List[int]] = Field(
        None,
        json_schema_extra={"example": [10, 15]},
        description="List of elite specialization IDs to exclude from optimization"
    )
    optimization_goals: List[str] = Field(
        default_factory=lambda: ["boon_uptime", "healing", "damage"],
        json_schema_extra={"example": ["boon_uptime", "healing", "damage"]},
        description="List of optimization goals in order of priority"
    )

class CompositionOptimizationResult(BaseModel):
    """Schema for composition optimization result"""
    composition: Composition
    score: float = Field(..., ge=0, le=1, json_schema_extra={"example": 0.85})
    metrics: Dict[str, float] = Field(
        ...,
        json_schema_extra={
            "example": {
                "boon_uptime": 0.9,
                "healing": 0.85,
                "damage": 0.75,
                "crowd_control": 0.8,
                "survivability": 0.9
            }
        }
    )
    role_distribution: Dict[str, int] = Field(
        ...,
        json_schema_extra={"example": {"healer": 2, "dps": 5, "support": 3}}
    )
    boon_coverage: Dict[str, float] = Field(
        ...,
        json_schema_extra={"example": {"might": 0.95, "quickness": 0.9, "alacrity": 0.8}}
    )
    notes: Optional[List[str]] = Field(
        None,
        json_schema_extra={"example": ["Consider adding more condition cleanses", "Good balance of damage and support"]}
    )

class CompositionEvaluation(BaseModel):
    """Schema for composition evaluation"""
    composition_id: int = Field(..., json_schema_extra={"example": 1})
    evaluator_id: int = Field(..., json_schema_extra={"example": 1})
    rating: int = Field(..., ge=1, le=5, json_schema_extra={"example": 4})
    feedback: Optional[str] = Field(None, json_schema_extra={"example": "Great composition for zerg fights!"})
    suggested_improvements: Optional[List[str]] = Field(
        None,
        json_schema_extra={"example": ["Add more condition cleanses", "Consider adding more stability"]}
    )
    is_public: bool = Field(default=True, json_schema_extra={"example": True})
    game_version: Optional[str] = Field(
        None,
        json_schema_extra={"example": "2023-11-28"},
        description="Game version this evaluation is based on"
    )
    game_mode: str = Field(
        default="wvw",
        json_schema_extra={"example": "wvw"},
        description="Game mode this evaluation is for"
    )
    tags: Optional[List[str]] = Field(
        None,
        json_schema_extra={"example": ["zerg", "frontline", "meta"]},
        description="Tags to help categorize this evaluation"
    )
