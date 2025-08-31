from typing import Optional, Any, ClassVar, Dict
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class EliteSpecializationBase(BaseModel):
    """Base schema for Elite Specialization."""
    name: str = Field(..., min_length=1, max_length=100, description="Name of the elite specialization")
    description: Optional[str] = Field(default=None, max_length=1000, description="Description of the elite specialization")
    icon_url: Optional[str] = Field(default=None, max_length=500, description="URL to the elite specialization's icon")
    profession_id: int = Field(..., description="ID of the parent profession")

    model_config: ClassVar[ConfigDict] = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "Firebrand",
                "description": "Wields fire and tomes to support allies and burn foes",
                "icon_url": "https://example.com/icons/firebrand.png",
                "profession_id": 1
            }
        }
    )

class EliteSpecializationCreate(EliteSpecializationBase):
    """Schema for creating a new elite specialization."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Firebrand",
                "description": "Wields fire and tomes to support allies and burn foes",
                "icon_url": "https://example.com/icons/firebrand.png",
                "profession_id": 1
            }
        }
    )

class EliteSpecializationUpdate(BaseModel):
    """Schema for updating an existing elite specialization."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100, description="Updated name of the elite specialization")
    description: Optional[str] = Field(default=None, max_length=1000, description="Updated description")
    icon_url: Optional[str] = Field(default=None, max_length=500, description="Updated icon URL")
    profession_id: Optional[int] = Field(default=None, description="Updated ID of the parent profession")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "Dragonhunter",
                "description": "Uses traps and virtues to smite enemies",
                "icon_url": "https://example.com/icons/dragonhunter.png",
                "profession_id": 2
            }
        }
    )

class EliteSpecializationInDBBase(EliteSpecializationBase):
    """Base schema for elite specialization in database."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Firebrand",
                "description": "Wields fire and tomes to support allies and burn foes",
                "icon_url": "https://example.com/icons/firebrand.png",
                "profession_id": 1,
                "created_at": "2022-01-01T00:00:00",
                "updated_at": "2022-01-01T00:00:00"
            }
        }
    )

class EliteSpecialization(EliteSpecializationInDBBase):
    """Schema for returning elite specialization data."""
    model_config = ConfigDict(
        from_attributes=True
    )

class EliteSpecializationInDB(EliteSpecializationInDBBase):
    """Schema for elite specialization data in database."""
    model_config = ConfigDict(
        from_attributes=True
    )
