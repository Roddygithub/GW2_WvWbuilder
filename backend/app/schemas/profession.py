from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Dict, Any

class ProfessionBase(BaseModel):
    """Base schema for profession data"""
    name: str = Field(..., min_length=2, max_length=50, examples=["Guardian"])
    icon_url: Optional[str] = Field(None, examples=["https://example.com/icons/guardian.png"])
    description: Optional[str] = Field(None, examples=["A profession that uses magical powers to protect allies and smite foes."])
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "name": "Guardian",
                "icon_url": "https://example.com/icons/guardian.png",
                "description": "A profession that uses magical powers to protect allies and smite foes."
            }]
        }
    )

class ProfessionCreate(ProfessionBase):
    """Schema for creating a new profession"""
    pass

class ProfessionUpdate(BaseModel):
    """Schema for updating profession data"""
    name: Optional[str] = Field(None, min_length=2, max_length=50, examples=["Guardian"])
    icon_url: Optional[str] = Field(None, examples=["https://example.com/icons/guardian_updated.png"])
    description: Optional[str] = Field(None, examples=["Updated description of the Guardian profession."])
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "name": "Guardian",
                "icon_url": "https://example.com/icons/guardian_updated.png",
                "description": "Updated description of the Guardian profession."
            }]
        }
    )

class ProfessionInDBBase(ProfessionBase):
    """Base schema for profession data in database"""
    id: int = Field(..., examples=[1])
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [{
                "id": 1,
                "name": "Guardian",
                "icon_url": "https://example.com/icons/guardian.png",
                "description": "A profession that uses magical powers to protect allies and smite foes."
            }]
        }
    )

class Profession(ProfessionInDBBase):
    """Schema for profession data returned by API"""
    pass

class ProfessionInDB(ProfessionInDBBase):
    """Schema for profession data stored in database"""
    pass

class EliteSpecializationBase(BaseModel):
    """Base schema for elite specialization data"""
    name: str = Field(..., min_length=2, max_length=50, examples=["Firebrand"])
    profession_id: int = Field(..., examples=[1])
    icon_url: Optional[str] = Field(None, examples=["https://example.com/icons/firebrand.png"])
    description: Optional[str] = Field(None, examples=["Elite specialization that wields an axe and focuses on support and condition damage."])
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "name": "Firebrand",
                "profession_id": 1,
                "icon_url": "https://example.com/icons/firebrand.png",
                "description": "Elite specialization that wields an axe and focuses on support and condition damage."
            }]
        }
    )

class EliteSpecializationCreate(EliteSpecializationBase):
    """Schema for creating a new elite specialization"""
    pass

class EliteSpecializationUpdate(BaseModel):
    """Schema for updating elite specialization data"""
    name: Optional[str] = Field(None, min_length=2, max_length=50, examples=["Firebrand"])
    profession_id: Optional[int] = Field(None, examples=[1])
    icon_url: Optional[str] = Field(None, examples=["https://example.com/icons/firebrand_updated.png"])
    description: Optional[str] = Field(None, examples=["Updated description of the Firebrand specialization."])
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "name": "Firebrand",
                "profession_id": 1,
                "icon_url": "https://example.com/icons/firebrand_updated.png",
                "description": "Updated description of the Firebrand specialization."
            }]
        }
    )

class EliteSpecializationInDBBase(EliteSpecializationBase):
    """Base schema for elite specialization data in database"""
    id: int = Field(..., examples=[1])
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [{
                "id": 1,
                "name": "Firebrand",
                "profession_id": 1,
                "icon_url": "https://example.com/icons/firebrand.png",
                "description": "Elite specialization that wields an axe and focuses on support and condition damage."
            }]
        }
    )

class EliteSpecialization(EliteSpecializationInDBBase):
    """Schema for elite specialization data returned by API"""
    pass

class EliteSpecializationInDB(EliteSpecializationInDBBase):
    """Schema for elite specialization data stored in database"""
    pass
