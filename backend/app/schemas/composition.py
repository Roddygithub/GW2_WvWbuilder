from pydantic import BaseModel, Field, field_validator, ConfigDict, model_validator
from typing import Optional, List, Dict, Any, ClassVar
from datetime import datetime, UTC
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
    user_id: int = Field(..., examples=[1])
    role_id: int = Field(..., examples=[1])
    profession_id: int = Field(..., examples=[1])
    elite_specialization_id: Optional[int] = Field(None, examples=[1])
    role_type: CompositionMemberRole = Field(..., examples=["healer"])
    notes: Optional[str] = Field(None, examples=["Focus on healing the frontline"])
    is_commander: bool = Field(default=False, examples=[False])
    is_secondary_commander: bool = Field(default=False, examples=[False])
    custom_build_url: Optional[str] = Field(None, examples=["https://snowcrows.com/builds/guardian/firebrand"])
    priority: int = Field(
        default=1,
        ge=1,
        le=3,
        examples=[1],
        description="Priority level (1=high, 2=medium, 3=low)",
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "user_id": 1,
                "role_id": 1,
                "profession_id": 1,
                "elite_specialization_id": 1,
                "role_type": "healer",
                "notes": "Focus on healing the frontline",
                "is_commander": False,
                "is_secondary_commander": False,
                "custom_build_url": "https://snowcrows.com/builds/guardian/firebrand",
                "priority": 1
            }]
        }
    )

class CompositionBase(BaseModel):
    """Base schema for composition data"""
    name: str = Field(..., min_length=2, max_length=100, examples=["Zerg Frontline"])
    description: Optional[str] = Field(
        None,
        examples=["A balanced frontline composition with strong healing and boon support"],
    )
    squad_size: int = Field(
        ..., ge=1, le=50, examples=[10], description="Number of players in the squad (1-50)"
    )
    is_public: bool = Field(default=True, examples=[True])
    tags: Optional[List[str]] = Field(None, examples=[["zerg", "frontline", "meta"]])
    game_mode: str = Field(
        default="wvw",
        examples=["wvw"],
        description="Game mode this composition is designed for (wvw, pvp, etc.)",
    )
    min_players: int = Field(
        default=1,
        ge=1,
        le=50,
        examples=[5],
        description="Minimum number of players required for this composition",
    )
    max_players: int = Field(
        default=50,
        ge=1,
        le=50,
        examples=[10],
        description="Maximum number of players for this composition",
    )

    @field_validator("max_players")
    @classmethod
    def max_players_must_be_gte_min_players(cls, v: int, info: Any) -> int:
        if hasattr(info, 'data') and 'min_players' in info.data and v < info.data["min_players"]:
            raise ValueError("max_players must be greater than or equal to min_players")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "name": "Zerg Frontline",
                "description": "A balanced frontline composition with strong healing and boon support",
                "squad_size": 10,
                "is_public": True,
                "tags": ["zerg", "frontline", "meta"],
                "game_mode": "wvw",
                "min_players": 5,
                "max_players": 15
            }]
        }
    )

class CompositionCreate(CompositionBase):
    """Schema for creating a new composition"""
    members: Optional[List[CompositionMemberBase]] = None
    created_by: Optional[int] = Field(None, examples=[1])
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                **CompositionBase.model_config["json_schema_extra"]["examples"][0],
                "members": [
                    {
                        "user_id": 1,
                        "role_id": 1,
                        "profession_id": 1,
                        "elite_specialization_id": 1,
                        "role_type": "healer",
                        "is_commander": True
                    }
                ],
                "created_by": 1
            }]
        }
    )

class CompositionUpdate(BaseModel):
    """Schema for updating composition data"""
    name: Optional[str] = Field(None, min_length=2, max_length=100, examples=["Updated Zerg Frontline"])
    description: Optional[str] = None
    squad_size: Optional[int] = Field(None, ge=1, le=50, examples=[15])
    is_public: Optional[bool] = None
    tags: Optional[List[str]] = None
    game_mode: Optional[str] = None
    min_players: Optional[int] = Field(None, ge=1, le=50)
    max_players: Optional[int] = Field(None, ge=1, le=50)
    members: Optional[List[CompositionMemberBase]] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "name": "Updated Zerg Frontline",
                "description": "Updated description with more details",
                "squad_size": 15,
                "is_public": True,
                "tags": ["zerg", "frontline", "meta", "updated"],
                "min_players": 8,
                "max_players": 20
            }]
        }
    )

class CompositionInDBBase(CompositionBase):
    """Base schema for composition data in database"""
    id: int = Field(..., examples=[1])
    created_by: int = Field(..., examples=[1])
    created_at: datetime = Field(..., examples=["2023-01-01T00:00:00"])
    updated_at: Optional[datetime] = Field(None, examples=["2023-01-01T00:00:00"])
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [{
                "id": 1,
                "created_by": 1,
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00",
                **CompositionBase.model_config["json_schema_extra"]["examples"][0]
            }]
        }
    )

class Composition(CompositionInDBBase):
    """Schema for composition data returned by API"""
    members: List[Dict[str, Any]] = Field(default_factory=list)
    tags: List[Dict[str, Any]] = Field(default_factory=list)
    created_by_username: Optional[str] = Field(None, examples=["john_doe"])
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                **CompositionInDBBase.model_config["json_schema_extra"]["examples"][0],
                "members": [
                    {
                        "id": 1,
                        "user_id": 1,
                        "role_id": 1,
                        "profession_id": 1,
                        "elite_specialization_id": 1,
                        "role_type": "healer",
                        "is_commander": True,
                        "username": "john_doe",
                        "profession_name": "Guardian",
                        "elite_specialization_name": "Firebrand"
                    }
                ],
                "tags": [
                    {"id": 1, "name": "zerg", "description": "Ideal for large scale battles"},
                    {"id": 2, "name": "frontline", "description": "Frontline composition"}
                ],
                "created_by_username": "john_doe"
            }]
        }
    )

class CompositionInDB(CompositionInDBBase):
    """Schema for composition data stored in database"""
    pass

class CompositionTagBase(BaseModel):
    """Base schema for composition tag data"""
    name: str = Field(..., min_length=1, max_length=50, examples=["zerg"])
    description: Optional[str] = Field(None, examples=["Ideal for large scale battles"])
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "name": "zerg",
                "description": "Ideal for large scale battles"
            }]
        }
    )

class CompositionTagCreate(CompositionTagBase):
    """Schema for creating a new composition tag"""
    pass

class CompositionTagUpdate(BaseModel):
    """Schema for updating composition tag data"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, examples=["zerg_updated"])
    description: Optional[str] = Field(None, examples=["Updated description"])
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "name": "zerg_updated",
                "description": "Updated description for zerg tag"
            }]
        }
    )

class CompositionTagInDBBase(CompositionTagBase):
    """Base schema for composition tag data in database"""
    id: int = Field(..., examples=[1])
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [{
                "id": 1,
                "name": "zerg",
                "description": "Ideal for large scale battles"
            }]
        }
    )

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
    sort_by: Optional[str] = Field("created_at", examples=["created_at"])
    sort_order: Optional[str] = Field("desc", pattern=r"^(asc|desc)$", examples=["desc"])
    offset: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "name": "zerg",
                "min_players": 5,
                "max_players": 20,
                "tags": ["frontline", "meta"],
                "game_mode": "wvw",
                "is_public": True,
                "sort_by": "created_at",
                "sort_order": "desc",
                "offset": 0,
                "limit": 10
            }]
        }
    )

class CompositionOptimizationRequest(BaseModel):
    """Schema for composition optimization request"""
    squad_size: int = Field(..., ge=1, le=50, examples=[10])
    fixed_roles: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        examples=[[
            {"profession_id": 1, "elite_specialization_id": 3, "count": 2, "role_type": "healer"},
            {"profession_id": 2, "elite_specialization_id": 5, "count": 3, "role_type": "dps"}
        ]]
    )
    game_mode: str = Field(default="wvw", examples=["wvw"])
    preferred_roles: Optional[Dict[str, int]] = Field(
        default=None,
        examples=[{"healer": 2, "dps": 5, "support": 3}]
    )
    min_boon_uptime: Optional[Dict[str, float]] = Field(
        default=None,
        examples=[{"might": 0.9, "quickness": 0.8, "alacrity": 0.7}]
    )
    min_healing: Optional[float] = Field(
        default=None,
        ge=0,
        le=1,
        examples=[0.8],
        description="Minimum healing output required (0-1 scale)"
    )
    min_damage: Optional[float] = Field(
        default=None,
        ge=0,
        le=1,
        examples=[0.7],
        description="Minimum damage output required (0-1 scale)"
    )
    min_cc: Optional[float] = Field(
        default=None,
        ge=0,
        le=1,
        examples=[0.6],
        description="Minimum crowd control capability (0-1 scale)"
    )
    min_cleanses: Optional[int] = Field(
        default=None,
        ge=0,
        examples=[5],
        description="Minimum number of condition cleanses per second"
    )
    preferred_weapons: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        examples=[[
            {"profession_id": 1, "weapon": "staff", "role_type": "healer"},
            {"profession_id": 2, "weapon": "greatsword", "role_type": "dps"}
        ]]
    )
    excluded_elite_specializations: Optional[List[int]] = Field(
        default=None,
        examples=[[10, 15]],
        description="List of elite specialization IDs to exclude from optimization"
    )
    optimization_goals: List[str] = Field(
        default_factory=lambda: ["boon_uptime", "healing", "damage"],
        examples=[["boon_uptime", "healing", "damage"]],
        description="List of optimization goals in order of priority"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "squad_size": 10,
                "fixed_roles": [
                    {"profession_id": 1, "elite_specialization_id": 3, "count": 2, "role_type": "healer"},
                    {"profession_id": 2, "elite_specialization_id": 5, "count": 3, "role_type": "dps"}
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
                    {"profession_id": 2, "weapon": "greatsword", "role_type": "dps"}
                ],
                "excluded_elite_specializations": [10, 15],
                "optimization_goals": ["boon_uptime", "healing", "damage"]
            }]
        }
    )

class CompositionOptimizationResult(BaseModel):
    """Schema for composition optimization result"""
    composition: Composition
    score: float = Field(..., ge=0, le=1, examples=[0.85])
    metrics: Dict[str, float] = Field(
        ...,
        examples=[{
            "boon_uptime": 0.9,
            "healing": 0.85,
            "damage": 0.75,
            "crowd_control": 0.8,
            "survivability": 0.9
        }]
    )
    role_distribution: Dict[str, int] = Field(
        ...,
        examples=[{"healer": 2, "dps": 5, "support": 3}]
    )
    boon_coverage: Dict[str, float] = Field(
        ...,
        examples=[{"might": 0.95, "quickness": 0.9, "alacrity": 0.8}]
    )
    notes: Optional[List[str]] = Field(
        default=None,
        examples=[["Consider adding more condition cleanses", "Good balance of damage and support"]]
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "composition": Composition.model_config["json_schema_extra"]["examples"][0],
                "score": 0.85,
                "metrics": {
                    "boon_uptime": 0.9,
                    "healing": 0.85,
                    "damage": 0.75,
                    "crowd_control": 0.8,
                    "survivability": 0.9
                },
                "role_distribution": {"healer": 2, "dps": 5, "support": 3},
                "boon_coverage": {"might": 0.95, "quickness": 0.9, "alacrity": 0.8},
                "notes": ["Consider adding more condition cleanses", "Good balance of damage and support"]
            }]
        }
    )

class CompositionEvaluation(BaseModel):
    """Schema for composition evaluation"""
    composition_id: int = Field(..., examples=[1])
    evaluator_id: int = Field(..., examples=[1])
    rating: int = Field(..., ge=1, le=5, examples=[4])
    feedback: Optional[str] = Field(default=None, examples=["Great composition for zerg fights!"])
    suggested_improvements: Optional[List[str]] = Field(
        default=None,
        examples=[["Add more condition cleanses", "Consider adding more stability"]]
    )
    is_public: bool = Field(default=True, examples=[True])
    game_version: Optional[str] = Field(
        default=None,
        examples=["2023-11-28"],
        description="Game version this evaluation is based on"
    )
    game_mode: str = Field(
        default="wvw",
        examples=["wvw"],
        description="Game mode this evaluation is for"
    )
    tags: Optional[List[str]] = Field(
        default=None,
        examples=[["zerg", "frontline", "meta"]],
        description="Tags to help categorize this evaluation"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "composition_id": 1,
                "evaluator_id": 1,
                "rating": 4,
                "feedback": "Great composition for zerg fights!",
                "suggested_improvements": ["Add more condition cleanses", "Consider adding more stability"],
                "is_public": True,
                "game_version": "2023-11-28",
                "game_mode": "wvw",
                "tags": ["zerg", "frontline", "meta"]
            }]
        }
    )
