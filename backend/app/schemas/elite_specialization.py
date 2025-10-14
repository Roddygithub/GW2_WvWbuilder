"""Pydantic schemas for Elite Specialization models.

This module defines the data validation and serialization schemas for elite specializations,
which are advanced specializations that can be unlocked for each profession in Guild Wars 2.

Key Features:
- Data validation for elite specialization creation and updates
- Serialization of elite specialization data for API responses
- Support for game mode affinity (PVE, PVP, WVW)
- Integration with profession system

Example Usage:
    ```python
    # Creating a new elite specialization
    new_spec = EliteSpecializationCreate(
        name="Firebrand",
        description="Wields fire and tomes to support allies...",
        weapon_type="Axe",
        profession_id=1,
        game_mode_affinity=[GameMode.PVE, GameMode.WVW]
    )

    # Updating an existing elite specialization
    update_data = EliteSpecializationUpdate(
        description="Updated description...",
        game_mode_affinity=[GameMode.PVP, GameMode.WVW]
    )
    ```
"""

from enum import Enum
from typing import Optional, List, Annotated
from pydantic import BaseModel, Field, ConfigDict, field_validator, StringConstraints
from datetime import datetime


class GameMode(str, Enum):
    """Available game modes for elite specializations.

    Elite specializations can be viable in different game modes, and this enum
    defines the possible game modes that can be associated with them.

    Attributes:
        PVE: Player vs Environment (PvE) content like open world and dungeons
        PVP: Player vs Player (sPvP) content in structured arenas
        WVW: World vs World large-scale PvP with siege warfare

    Example:
        ```python
        # Check if an elite spec is viable in WvW
        if GameMode.WVW in elite_spec.game_mode_affinity:
            print("This spec is viable in WvW")
        ```
    """

    PVE = "PVE"
    PVP = "PVP"
    WVW = "WVW"


class EliteSpecializationBase(BaseModel):
    """Base schema for Elite Specialization.

    This schema defines the core fields that are common across all elite specialization
    operations. It serves as the foundation for other schemas in this module.

    Attributes:
        name: The unique name of the elite specialization (1-100 chars)
        description: Detailed description of the elite specialization
        weapon_type: Type of weapon associated with this elite spec
        icon_url: URL to the elite specialization's icon image
        background_url: URL to the background image for this elite spec
        profession_id: ID of the parent profession
        is_active: Whether this elite spec is currently active/available
        game_mode_affinity: List of game modes this spec is viable in (PVE, PVP, WVW)

    Validation Rules:
        - Name must be 1-100 characters long and non-empty
        - Description is required but can be empty
        - Weapon type is required
        - Profession ID must reference an existing profession

    Example:
        ```python
        base_spec = EliteSpecializationBase(
            name="Firebrand",
            description="Wields fire and tomes to support allies...",
            weapon_type="Axe",
            profession_id=1,
            game_mode_affinity=[GameMode.PVE, GameMode.WVW]
        )
        ```
    """

    name: Annotated[str, StringConstraints(min_length=1, max_length=100)] = Field(
        ..., description="Unique name of the elite specialization (1-100 characters)", examples=["Firebrand"]
    )
    description: str = Field(
        ...,
        max_length=2000,
        description="Detailed description of the elite specialization's theme and abilities",
        example="Wields fire and tomes to support allies and burn foes with righteous flames.",
    )
    weapon_type: str = Field(
        ..., max_length=50, description="Type of weapon this elite specialization introduces", example="Axe"
    )
    icon_url: Optional[str] = Field(
        default=None,
        max_length=500,
        description="URL to the elite specialization's icon image (PNG, 64x64px recommended)",
        example="https://example.com/icons/firebrand.png",
    )
    background_url: Optional[str] = Field(
        default=None,
        max_length=500,
        description="URL to the background image for this elite spec (1920x1080px recommended)",
        example="https://example.com/backgrounds/firebrand.jpg",
    )
    profession_id: int = Field(..., description="ID of the parent profession this elite spec belongs to", example=1)
    is_active: bool = Field(default=True, description="Whether this elite spec is currently available in the game")
    game_mode_affinity: List[GameMode] = Field(
        default_factory=list,
        description="List of game modes this spec is viable in (PVE, PVP, WVW)",
        example=["PVE", "WVW"],
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate the name field."""
        if not v.strip():
            raise ValueError("Name cannot be empty or whitespace")
        return v.strip()

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "Firebrand",
                "description": "Wields fire and tomes to support allies and burn foes with righteous flames.",
                "weapon_type": "Axe",
                "icon_url": "https://example.com/icons/firebrand.png",
                "background_url": "https://example.com/backgrounds/firebrand.jpg",
                "profession_id": 1,
                "is_active": True,
                "game_mode_affinity": ["PVE", "WVW"],
            }
        },
        arbitrary_types_allowed=True,
    )


class EliteSpecializationCreate(EliteSpecializationBase):
    """Schema for creating a new elite specialization.

    This schema is used when creating a new elite specialization through the API.
    It inherits all fields from the base schema and adds creation-specific validation.

    Key Features:
    - Requires all non-optional fields from the base schema
    - Validates that the profession exists
    - Ensures the elite spec name is unique within the profession

    Example API Request:
        ```http
        POST /api/v1/elite-specializations/
        Content-Type: application/json

        {
            "name": "Firebrand",
            "description": "Wields fire and tomes to support allies and burn foes...",
            "weapon_type": "Axe",
            "icon_url": "https://example.com/icons/firebrand.png",
            "background_url": "https://example.com/backgrounds/firebrand.jpg",
            "profession_id": 1,
            "is_active": true,
            "game_mode_affinity": ["PVE", "WVW"]
        }
        ```

    Python Usage:
        ```python
        from app.schemas.elite_specialization import EliteSpecializationCreate, GameMode

        # Create a new elite spec
        new_spec = EliteSpecializationCreate(
            name="Firebrand",
            description="Wields fire and tomes to support allies...",
            weapon_type="Axe",
            profession_id=1,
            game_mode_affinity=[GameMode.PVE, GameMode.WVW]
        )
        ```
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Firebrand",
                "description": "Wields fire and tomes to support allies and burn foes with righteous flames.",
                "weapon_type": "Axe",
                "icon_url": "https://example.com/icons/firebrand.png",
                "background_url": "https://example.com/backgrounds/firebrand.jpg",
                "profession_id": 1,
                "is_active": True,
                "game_mode_affinity": ["PVE", "WVW"],
            }
        },
        arbitrary_types_allowed=True,
    )


class EliteSpecializationUpdate(BaseModel):
    """Schema for updating an existing elite specialization.

    All fields are optional - only provided fields will be updated. This follows
    the PATCH semantics where only the fields that need to be changed are included.

    Key Features:
    - All fields are optional
    - Only updates the fields that are provided
    - Validates each field according to its type
    - Maintains data consistency with related models

    Attributes:
        name: New name for the elite specialization (1-100 chars)
        description: Updated description of the elite spec
        weapon_type: Type of weapon this elite spec uses
        icon_url: URL to the elite spec's icon image
        background_url: URL to the background image
        profession_id: ID of the parent profession (if changing professions)
        is_active: Whether this elite spec is active
        game_mode_affinity: List of game modes this spec is viable in

    Example API Request:
        ```http
        PATCH /api/v1/elite-specializations/1
        Content-Type: application/json

        {
            "description": "Updated description with more details...",
            "game_mode_affinity": ["PVE", "PVP", "WVW"]
        }
        ```

    Python Usage:
        ```python
        from app.schemas.elite_specialization import EliteSpecializationUpdate, GameMode

        # Update specific fields of an elite spec
        update_data = EliteSpecializationUpdate(
            description="Updated with new abilities...",
            game_mode_affinity=[GameMode.PVE, GameMode.PVP, GameMode.WVW],
            is_active=True
        )
        ```
    """

    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Updated name of the elite specialization (1-100 characters)",
        example="Dragonhunter",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Updated description of the elite specialization",
        example="Uses traps and virtues to smite enemies from range.",
    )
    weapon_type: Optional[str] = Field(
        default=None, max_length=50, description="Updated weapon type for this elite spec", example="Longbow"
    )
    icon_url: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Updated URL to the elite spec's icon",
        example="https://example.com/icons/dragonhunter.png",
    )
    background_url: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Updated URL to the background image",
        example="https://example.com/backgrounds/dragonhunter.jpg",
    )
    profession_id: Optional[int] = Field(
        default=None, description="New parent profession ID if changing professions", example=2
    )
    is_active: Optional[bool] = Field(default=None, description="Set to false to mark this spec as inactive")
    game_mode_affinity: Optional[List[GameMode]] = Field(
        default=None, description="Updated list of game modes this spec is viable in", example=["PVE", "PVP"]
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "Dragonhunter",
                "description": "Uses traps and virtues to smite enemies from range.",
                "weapon_type": "Longbow",
                "icon_url": "https://example.com/icons/dragonhunter.png",
                "background_url": "https://example.com/backgrounds/dragonhunter.jpg",
                "profession_id": 2,
                "is_active": True,
                "game_mode_affinity": ["PVE", "PVP"],
            }
        },
    )


class EliteSpecializationInDBBase(EliteSpecializationBase):
    """Base schema for elite specialization in database.

    This schema extends EliteSpecializationBase with database-specific fields
    like IDs and timestamps. It serves as the foundation for schemas that
    interact with the database or return database records.

    Key Features:
    - Includes database primary key (id)
    - Tracks record creation and update timestamps
    - Inherits all validation from EliteSpecializationBase
    - Used internally by the application

    Attributes:
        id: Unique database identifier (auto-incremented integer)
        created_at: Timestamp when the record was created (UTC)
        updated_at: Timestamp when the record was last updated (UTC, nullable)

    Note:
        This schema should not be used directly in API responses. Use the
        EliteSpecialization schema instead, which is designed for public consumption.

    Example:
        ```python
        # In a database query result
        {
            "id": 1,
            "name": "Firebrand",
            "description": "Wields fire and tomes...",
            # ... other fields ...
            "created_at": "2023-01-01T12:00:00Z",
            "updated_at": "2023-01-02T14:30:00Z"
        }
        ```
    """

    id: int = Field(..., description="Unique database identifier")
    created_at: datetime = Field(..., description="Timestamp when the record was created")
    updated_at: Optional[datetime] = Field(None, description="Timestamp when the record was last updated")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Firebrand",
                "description": "Wields fire and tomes to support allies and burn foes with righteous flames.",
                "weapon_type": "Axe",
                "icon_url": "https://example.com/icons/firebrand.png",
                "background_url": "https://example.com/backgrounds/firebrand.jpg",
                "profession_id": 1,
                "is_active": True,
                "game_mode_affinity": ["PVE", "WVW"],
                "created_at": "2023-01-01T12:00:00Z",
                "updated_at": "2023-01-02T14:30:00Z",
            }
        },
        arbitrary_types_allowed=True,
    )


class EliteSpecialization(EliteSpecializationInDBBase):
    """Schema for returning elite specialization data in API responses.

    This is the main schema used when returning elite specialization data to API clients.
    It includes all the fields from EliteSpecializationInDBBase and can be extended with
    additional computed or related fields as needed.

    Key Features:
    - Includes all database fields (id, timestamps)
    - Designed for public API consumption
    - Can be extended with relationships (e.g., profession details)
    - Follows RESTful API best practices

    Example API Response:
        ```http
        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "id": 1,
            "name": "Firebrand",
            "description": "Wields fire and tomes to support allies...",
            "weapon_type": "Axe",
            "icon_url": "https://example.com/icons/firebrand.png",
            "background_url": "https://example.com/backgrounds/firebrand.jpg",
            "profession_id": 1,
            "is_active": true,
            "game_mode_affinity": ["PVE", "WVW"],
            "created_at": "2023-01-01T12:00:00Z",
            "updated_at": "2023-01-02T14:30:00Z"
        }
        ```

    Python Usage:
        ```python
        # In a FastAPI route
        @router.get("/{elite_spec_id}", response_model=EliteSpecialization)
        async def get_elite_spec(
            elite_spec_id: int,
            db: AsyncSession = Depends(get_db)
        ):
            elite_spec = await crud.elite_specialization.get(db, id=elite_spec_id)
            if not elite_spec:
                raise HTTPException(status_code=404, detail="Elite specialization not found")
            return elite_spec
        ```
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Firebrand",
                "description": "Wields fire and tomes to support allies and burn foes with righteous flames.",
                "weapon_type": "Axe",
                "icon_url": "https://example.com/icons/firebrand.png",
                "background_url": "https://example.com/backgrounds/firebrand.jpg",
                "profession_id": 1,
                "is_active": True,
                "game_mode_affinity": ["PVE", "WVW"],
                "created_at": "2023-01-01T12:00:00Z",
                "updated_at": "2023-01-02T14:30:00Z",
            }
        },
        arbitrary_types_allowed=True,
    )


class EliteSpecializationInDB(EliteSpecializationInDBBase):
    """Schema for elite specialization data stored in the database.

    This schema is used internally for database operations and includes all fields
    that are stored in the database. It's not meant to be exposed directly via the API.

    Example:
        ```python
        # In a database operation
        result = await db.execute(
            select(EliteSpecializationModel)
            .where(EliteSpecializationModel.id == elite_spec_id)
        )
        return result.scalars().first()
        ```
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Firebrand",
                "description": "Wields fire and tomes to support allies and burn foes with righteous flames.",
                "weapon_type": "Axe",
                "icon_url": "https://example.com/icons/firebrand.png",
                "background_url": "https://example.com/backgrounds/firebrand.jpg",
                "profession_id": 1,
                "is_active": True,
                "game_mode_affinity": ["PVE", "WVW"],
                "created_at": "2023-01-01T12:00:00Z",
                "updated_at": "2023-01-02T14:30:00Z",
            }
        },
        arbitrary_types_allowed=True,
    )
