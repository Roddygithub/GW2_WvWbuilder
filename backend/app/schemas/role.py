from pydantic import BaseModel, Field
from typing import Optional, List

class RoleBase(BaseModel):
    """Base schema for role data"""
    name: str = Field(..., min_length=2, max_length=50, example="Healer")
    description: Optional[str] = Field(None, example="Responsible for keeping the group alive with healing")
    icon_url: Optional[str] = Field(None, example="https://example.com/icons/healer.png")

class RoleCreate(RoleBase):
    """Schema for creating a new role"""
    pass

class RoleUpdate(BaseModel):
    """Schema for updating role data"""
    name: Optional[str] = Field(None, min_length=2, max_length=50, example="Support Healer")
    description: Optional[str] = Field(None, example="Provides healing and support to the group")
    icon_url: Optional[str] = Field(None, example="https://example.com/icons/support_healer.png")

class RoleInDBBase(RoleBase):
    """Base schema for role data in database"""
    id: int = Field(..., example=1)

    class Config:
        orm_mode = True

class Role(RoleInDBBase):
    """Schema for role data returned by API"""
    pass

class RoleInDB(RoleInDBBase):
    """Schema for role data stored in database"""
    pass
