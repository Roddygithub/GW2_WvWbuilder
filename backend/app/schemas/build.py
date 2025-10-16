from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from datetime import datetime
from enum import Enum
import logging
from app.core.config import settings


# Enums for better type safety and documentation
class GameMode(str, Enum):
    WVW = "wvw"
    PVP = "pvp"
    PVE = "pve"
    RAIDS = "raids"
    FRACTALS = "fractals"


class RoleType(str, Enum):
    HEALER = "healer"
    QUICKNESS = "quickness"
    ALACRITY = "alacrity"
    MIGHT = "might"
    FURY = "fury"
    AEGIS = "aegis"
    STABILITY = "stability"
    DPS = "dps"
    SUPPORT = "support"
    UTILITY = "utility"


class BuildBase(BaseModel):
    """Base model for build data with common fields."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "name": "WvW Zerg Firebrand",
                    "description": "Support build for WvW zergs",
                    "game_mode": "wvw",
                    "team_size": 5,
                    "is_public": True,
                }
            ]
        },
    )

    name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Name of the build (3-100 characters)",
        examples=["WvW Zerg Firebrand"],
    )

    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Detailed description of the build",
        examples=[
            "A support Firebrand build focused on providing quickness and stability in WvW zergs"
        ],
    )

    game_mode: GameMode = Field(
        ..., description="Game mode this build is designed for", examples=["wvw"]
    )

    team_size: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Number of players this build is designed for (1-50)",
        examples=[5],
    )

    is_public: bool = Field(
        default=True,
        description="Whether this build is visible to other users",
        examples=[True],
    )

    config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Build configuration (weapons, traits, skills, etc.)",
        examples=[
            {
                "weapons": ["Axe", "Shield", "Mace", "Focus"],
                "traits": ["Radiance", "Honor", "Firebrand"],
                "skills": [
                    "Mantra of Potence",
                    "Mantra of Solace",
                    "Mantra of Liberation",
                ],
            }
        ],
    )

    constraints: Dict[str, Any] = Field(
        default_factory=dict,
        description="Team composition constraints and requirements",
        examples=[
            {
                "required_roles": ["quickness", "stability"],
                "min_healers": 1,
                "max_duplicate_professions": 2,
                "required_boons": ["might", "fury", "protection"],
                "required_cc": 10,
            }
        ],
    )

    profession_ids: List[int] = Field(
        default_factory=list,
        description="""Liste des IDs de professions qui peuvent utiliser ce build.
- Must contain between 1 and 3 unique profession IDs.
- Each ID must reference an existing profession.
- **Validation**: Certaines combinaisons de professions sont interdites (ex: Gardien et Incendiaire). L'API retournera une erreur 422 si une combinaison invalide est fournie.
""",
        json_schema_extra={
            "example": [1, 2],
            "notes": "Référez-vous à /api/v1/professions pour les IDs valides. Les combinaisons interdites sont définies dans la configuration du backend.",
        },
        min_items=1,
        max_items=3,
    )

    @field_validator("profession_ids")
    @classmethod
    def validate_unique_professions(cls, v: List[int]) -> List[int]:
        if len(v) != len(set(v)):
            raise ValueError("Profession IDs must be unique")
        return v

    @field_validator("profession_ids")
    @classmethod
    def validate_profession_combinations(cls, v: List[int]) -> List[int]:
        """
        Valide que certaines professions ne sont pas utilisées ensemble.
        Exemple : Un build ne peut pas être pour Gardien et Incendiaire en même temps.
        NOTE : Cette logique est un exemple et devrait être affinée selon les règles métier.
        """
        # Exemple de combinaisons interdites (IDs de professions)
        logger = logging.getLogger(__name__)
        forbidden_combinations: List[set[int]] = getattr(
            settings, "FORBIDDEN_PROFESSION_COMBINATIONS", []
        )

        profession_set = set(v)
        for combo in forbidden_combinations:
            if combo.issubset(profession_set):
                logger.warning(
                    f"Attempted to use forbidden profession combination: {combo} in build creation/update. Input professions: {v}"
                )
                raise ValueError(
                    f"Professions with IDs {combo} cannot be used together in the same build."
                )
        return v

    @field_validator("config")
    @classmethod
    def validate_config(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if v is None:
            return v

        if not isinstance(v, dict):
            raise ValueError("Config must be a dictionary")

        if "weapons" in v and (
            not isinstance(v["weapons"], list) or len(v["weapons"]) == 0
        ):
            raise ValueError("Weapons list cannot be empty")

        return v


class BuildCreate(BuildBase):
    """Schema for creating a new build."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "WvW Zerg Firebrand",
                    "description": "Support build for WvW zergs",
                    "game_mode": "wvw",
                    "team_size": 5,
                    "is_public": True,
                    "config": {
                        "weapons": ["Axe", "Shield", "Mace", "Focus"],
                        "traits": ["Radiance", "Honor", "Firebrand"],
                        "skills": [
                            "Mantra of Potence",
                            "Mantra of Solace",
                            "Mantra of Liberation",
                        ],
                    },
                    "constraints": {
                        "required_roles": ["quickness", "stability"],
                        "min_healers": 1,
                    },
                    "profession_ids": [1, 2],
                }
            ]
        }
    )

    name: str = Field(
        ..., min_length=3, max_length=100, examples=["WvW Zerg Firebrand"]
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate build name."""
        if not v or not v.strip():
            raise ValueError("Build name cannot be empty or whitespace")
        if len(v) < 3:
            raise ValueError("Build name must be at least 3 characters long")
        if len(v) > 100:
            raise ValueError("Build name cannot exceed 100 characters")
        return v.strip()


class BuildUpdate(BaseModel):
    """Schema for updating an existing build. All fields are optional."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "name": "Updated WvW Zerg Firebrand",
                    "description": "Updated Firebrand support build with new trait choices",
                    "game_mode": "wvw",
                    "team_size": 5,
                    "is_public": True,
                    "config": {
                        "weapons": ["Axe", "Shield", "Mace", "Focus"],
                        "traits": ["Radiance", "Honor", "Firebrand"],
                        "skills": [
                            "Mantra of Potence",
                            "Mantra of Solace",
                            "Mantra of Liberation",
                        ],
                    },
                    "constraints": {
                        "required_roles": ["quickness", "stability", "aegis"],
                        "min_healers": 2,
                    },
                    "profession_ids": [1, 2, 3],
                }
            ]
        },
    )

    name: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=100,
        examples=["Updated WvW Zerg Firebrand"],
    )

    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        examples=["Updated Firebrand support build with new trait choices"],
    )

    game_mode: Optional[GameMode] = None
    team_size: Optional[int] = Field(default=None, ge=1, le=50)
    is_public: Optional[bool] = None

    config: Optional[Dict[str, Any]] = Field(
        default=None,
        examples=[
            {
                "weapons": ["Axe", "Shield", "Mace", "Focus"],
                "traits": ["Radiance", "Honor", "Firebrand"],
                "skills": [
                    "Mantra of Potence",
                    "Mantra of Solace",
                    "Mantra of Liberation",
                ],
            }
        ],
    )

    constraints: Optional[Dict[str, Any]] = Field(
        default=None,
        examples=[
            {"required_roles": ["quickness", "stability", "aegis"], "min_healers": 2}
        ],
    )

    profession_ids: Optional[List[int]] = Field(
        default=None, min_items=1, max_items=3, examples=[[1, 2, 3]]
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate build name."""
        if v is None:
            return v
        if not v or not v.strip():
            raise ValueError("Build name cannot be empty or whitespace")
        if len(v) < 3:
            raise ValueError("Build name must be at least 3 characters long")
        return v.strip()


class BuildProfessionBase(BaseModel):
    """Base schema for build-profession relationship."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "name": "Guardian",
                    "description": "Heavy armor profession that uses virtues to protect allies",
                }
            ]
        }
    )

    id: int = Field(..., description="Unique identifier for the profession")
    name: str = Field(..., description="Name of the profession")
    description: Optional[str] = Field(
        default=None, description="Brief description of the profession"
    )


# Move BuildProfessionBase before BuildInDBBase to avoid circular imports
class BuildInDBBase(BaseModel):
    """Base model for build data stored in the database."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "name": "WvW Zerg Firebrand",
                    "description": "Support build for WvW zergs",
                    "game_mode": "wvw",
                    "team_size": 5,
                    "is_public": True,
                    "created_by_id": 1,
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                    "professions": [
                        {
                            "id": 1,
                            "name": "Guardian",
                            "description": "Heavy armor profession",
                        },
                        {
                            "id": 2,
                            "name": "Firebrand",
                            "description": "Guardian elite specialization",
                        },
                    ],
                }
            ]
        },
    )

    id: int = Field(..., description="Unique identifier for the build")
    created_by_id: int = Field(..., description="ID of the user who created the build")
    created_at: datetime = Field(
        ..., description="Timestamp when the build was created"
    )
    updated_at: Optional[datetime] = Field(
        None, description="Timestamp when the build was last updated"
    )
    profession_ids: List[int] = Field(
        default_factory=list,
        description="List of profession IDs associated with this build",
    )

    # This will be populated by the handler
    professions: List[BuildProfessionBase] = Field(
        default_factory=list,
        description="List of profession details associated with this build",
    )

    @model_validator(mode="wrap")
    @classmethod
    def handle_professions(cls, data: Any, handler: Any) -> Any:
        if isinstance(data, dict):
            # Handle case where data is a dict (from_orm or direct dict)
            if "professions" not in data:
                if hasattr(data.get("_sa_instance_state", None), "attrs"):
                    # This is an ORM model, try to get professions from the relationship
                    orm_obj = data
                    if hasattr(orm_obj, "professions"):
                        data = dict(data)
                        data["professions"] = [
                            {"id": p.id, "name": p.name, "description": p.description}
                            for p in orm_obj.professions
                        ]

                        # Also ensure profession_ids is set
                        if not data.get("profession_ids"):
                            data["profession_ids"] = [p.id for p in orm_obj.professions]

                # Handle build_professions relationship if it exists
                elif hasattr(data.get("_sa_instance_state", None), "attrs") and hasattr(
                    data, "build_professions"
                ):
                    orm_obj = data
                    data = dict(data)
                    data["professions"] = [
                        {
                            "id": bp.profession.id,
                            "name": bp.profession.name,
                            "description": bp.profession.description,
                        }
                        for bp in orm_obj.build_professions
                        if hasattr(bp, "profession") and bp.profession
                    ]

                    # Also ensure profession_ids is set
                    if not data.get("profession_ids") and data["professions"]:
                        data["profession_ids"] = [p["id"] for p in data["professions"]]

            # Handle case where professions is a list of ORM objects
            elif (
                "professions" in data
                and data["professions"]
                and hasattr(data["professions"][0], "id")
            ):
                data = dict(data)
                data["professions"] = [
                    {"id": p.id, "name": p.name, "description": p.description}
                    for p in data["professions"]
                ]

                # Also ensure profession_ids is set
                if not data.get("profession_ids"):
                    data["profession_ids"] = [p.id for p in data["professions"]]

            # Handle case where build_professions is provided instead of professions
            elif "build_professions" in data and data["build_professions"]:
                data = dict(data)
                data["professions"] = [
                    {
                        "id": bp.profession.id,
                        "name": bp.profession.name,
                        "description": bp.profession.description,
                    }
                    for bp in data["build_professions"]
                    if hasattr(bp, "profession") and bp.profession
                ]

                # Also ensure profession_ids is set
                if not data.get("profession_ids") and data["professions"]:
                    data["profession_ids"] = [p["id"] for p in data["professions"]]

        # Let Pydantic handle the rest
        return handler(data)


class Build(BuildInDBBase, BuildBase):
    """Schema for build responses."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "name": "WvW Zerg Firebrand",
                    "description": "Support build for WvW zergs",
                    "game_mode": "wvw",
                    "team_size": 5,
                    "is_public": True,
                    "created_by_id": 1,
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                    "config": {
                        "weapons": ["Axe", "Shield", "Mace", "Focus"],
                        "traits": ["Radiance", "Honor", "Firebrand"],
                        "skills": [
                            "Mantra of Potence",
                            "Mantra of Solace",
                            "Mantra of Liberation",
                        ],
                    },
                    "constraints": {
                        "required_roles": ["quickness", "stability", "aegis"],
                        "min_healers": 2,
                    },
                    "profession_ids": [1, 2, 3],
                    "owner_id": 1,
                    "professions": [
                        {
                            "id": 1,
                            "name": "Guardian",
                            "description": "Heavy armor profession",
                        },
                        {
                            "id": 2,
                            "name": "Firebrand",
                            "description": "Guardian elite specialization",
                        },
                    ],
                }
            ]
        },
    )

    professions: List[BuildProfessionBase] = Field(
        default_factory=list,
        description="List of professions associated with this build",
    )


class BuildInDB(BuildInDBBase):
    pass


# Schema for build generation request
class BuildGenerationRequest(BaseModel):
    """Request schema for generating a new build composition."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "name": "WvW Zerg Firebrand",
                    "description": "Support build for WvW zergs",
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
            ]
        },
    )

    team_size: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Number of players in the team (1-50)",
        examples=[5],
    )

    required_roles: List[RoleType] = Field(
        default_factory=list,
        description="List of required roles that must be present in the composition",
        examples=[["healer", "quickness", "alacrity"]],
    )

    preferred_professions: List[int] = Field(
        default_factory=list,
        description="List of preferred profession IDs to prioritize in the composition",
        examples=[[1, 2, 3]],
    )

    max_duplicates: int = Field(
        default=2,
        ge=1,
        le=10,
        description="Maximum number of duplicates allowed for any single profession",
        examples=[2],
    )

    min_healers: int = Field(
        default=1,
        ge=0,
        description="Minimum number of healers required in the composition",
        examples=[1],
    )

    min_dps: int = Field(
        default=2,
        ge=0,
        description="Minimum number of DPS roles required in the composition",
        examples=[2],
    )

    min_support: int = Field(
        default=1,
        ge=0,
        description="Minimum number of support roles required in the composition",
        examples=[1],
    )

    constraints: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional constraints for build generation",
        examples=[
            {
                "require_cc": True,
                "require_cleanses": True,
                "require_stability": True,
                "require_projectile_mitigation": True,
            }
        ],
    )

    @field_validator("required_roles")
    @classmethod
    def validate_roles(cls, v: List[RoleType]) -> List[RoleType]:
        """Validate that required roles are valid."""
        if not v:
            return v

        valid_roles = set(RoleType)
        invalid_roles = set(v) - valid_roles

        if invalid_roles:
            raise ValueError(
                f"Invalid role(s): {', '.join(invalid_roles)}. "
                f"Valid roles are: {', '.join(valid_roles)}"
            )
        return v


# Schema for build generation response
class TeamMember(BaseModel):
    """Schema for a single team member in the suggested composition."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "position": 1,
                    "profession": "Guardian",
                    "role": "Healer/Support",
                    "build": "Firebrand - Quickness Support",
                    "required_boons": ["Quickness", "Stability", "Aegis"],
                    "required_utilities": ["Stability on Aegis", "Condition Cleanse"],
                }
            ]
        }
    )

    position: int = Field(
        ..., description="Position in the team (1-based)", examples=[1]
    )
    profession: str = Field(
        ..., description="Name of the profession", examples=["Guardian"]
    )
    role: str = Field(
        ..., description="Primary role in the team", examples=["Healer/Support"]
    )
    build: str = Field(
        ...,
        description="Recommended build name",
        examples=["Firebrand - Quickness Support"],
    )
    required_boons: List[str] = Field(
        default_factory=list,
        description="List of boons this member provides",
        examples=[["Quickness", "Stability", "Aegis"]],
    )
    required_utilities: List[str] = Field(
        default_factory=list,
        description="List of utility skills this member brings",
        examples=[["Stability on Aegis", "Condition Cleanse"]],
    )


class BuildGenerationResponse(BaseModel):
    """Response schema for build generation."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "success": True,
                    "message": "Build generated successfully",
                    "build": Build.model_config["json_schema_extra"]["examples"][0],
                    "suggested_composition": [
                        TeamMember.model_config["json_schema_extra"]["examples"][0]
                    ],
                    "metrics": {
                        "boon_coverage": {
                            "quickness": 100.0,
                            "alacrity": 100.0,
                            "might": 25.0,
                            "fury": 100.0,
                        },
                        "role_distribution": {
                            "healer": 1,
                            "support": 2,
                            "dps": 2,
                            "utility": 1,
                        },
                        "profession_distribution": {
                            "Guardian": 2,
                            "Elementalist": 1,
                            "Revenant": 1,
                            "Engineer": 1,
                        },
                    },
                }
            ]
        }
    )

    success: bool = Field(
        ..., description="Whether the generation was successful", examples=[True]
    )
    message: str = Field(
        ...,
        description="Status message or error description",
        examples=["Build generated successfully"],
    )
    build: Optional[Build] = Field(
        default=None, description="Generated build details if successful"
    )
    suggested_composition: List[TeamMember] = Field(
        default_factory=list,
        description="List of team members in the suggested composition",
    )
    metrics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Performance metrics and statistics about the generated composition",
        examples=[
            {
                "boon_coverage": {
                    "quickness": 100.0,
                    "alacrity": 100.0,
                    "might": 25.0,
                    "fury": 100.0,
                },
                "role_distribution": {
                    "healer": 1,
                    "support": 2,
                    "dps": 2,
                    "utility": 1,
                },
                "profession_distribution": {
                    "Guardian": 2,
                    "Elementalist": 1,
                    "Revenant": 1,
                    "Engineer": 1,
                },
            }
        ],
    )
