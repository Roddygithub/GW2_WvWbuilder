from pydantic import BaseModel, Field
from typing import Optional, List

class ProfessionBase(BaseModel):
    """Base schema for profession data"""
    name: str = Field(..., min_length=2, max_length=50, example="Guardian")
    icon_url: Optional[str] = Field(None, example="https://example.com/icons/guardian.png")
    description: Optional[str] = Field(None, example="A profession that uses magical powers to protect allies and smite foes.")

class ProfessionCreate(ProfessionBase):
    """Schema for creating a new profession"""
    pass

class ProfessionUpdate(BaseModel):
    """Schema for updating profession data"""
    name: Optional[str] = Field(None, min_length=2, max_length=50, example="Guardian")
    icon_url: Optional[str] = Field(None, example="https://example.com/icons/guardian_updated.png")
    description: Optional[str] = Field(None, example="Updated description of the Guardian profession.")

class ProfessionInDBBase(ProfessionBase):
    """Base schema for profession data in database"""
    id: int = Field(..., example=1)

    class Config:
        orm_mode = True

class Profession(ProfessionInDBBase):
    """Schema for profession data returned by API"""
    pass

class ProfessionInDB(ProfessionInDBBase):
    """Schema for profession data stored in database"""
    pass

class EliteSpecializationBase(BaseModel):
    """Base schema for elite specialization data"""
    name: str = Field(..., min_length=2, max_length=50, example="Firebrand")
    profession_id: int = Field(..., example=1)
    icon_url: Optional[str] = Field(None, example="https://example.com/icons/firebrand.png")
    description: Optional[str] = Field(None, example="Elite specialization that wields an axe and focuses on support and condition damage.")

class EliteSpecializationCreate(EliteSpecializationBase):
    """Schema for creating a new elite specialization"""
    pass

class EliteSpecializationUpdate(BaseModel):
    """Schema for updating elite specialization data"""
    name: Optional[str] = Field(None, min_length=2, max_length=50, example="Firebrand")
    profession_id: Optional[int] = Field(None, example=1)
    icon_url: Optional[str] = Field(None, example="https://example.com/icons/firebrand_updated.png")
    description: Optional[str] = Field(None, example="Updated description of the Firebrand specialization.")

class EliteSpecializationInDBBase(EliteSpecializationBase):
    """Base schema for elite specialization data in database"""
    id: int = Field(..., example=1)

    class Config:
        orm_mode = True

class EliteSpecialization(EliteSpecializationInDBBase):
    """Schema for elite specialization data returned by API"""
    pass

class EliteSpecializationInDB(EliteSpecializationInDBBase):
    """Schema for elite specialization data stored in database"""
    pass
