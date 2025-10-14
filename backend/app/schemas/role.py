from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class RoleBase(BaseModel):
    """Base schema for role data"""

    name: str = Field(..., min_length=2, max_length=50, examples=["Healer"])
    description: Optional[str] = Field(None, examples=["Responsible for keeping the group alive with healing"])
    permission_level: int = Field(default=0, ge=0, le=100, description="Permission level (0-100)")
    is_default: bool = Field(default=False, description="Whether this is a default role for new users")
    icon_url: Optional[str] = Field(None, examples=["https://example.com/icons/healer.png"])

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Healer",
                    "description": "Responsible for keeping the group alive with healing",
                    "icon_url": "https://example.com/icons/healer.png",
                }
            ]
        }
    )


class RoleCreate(RoleBase):
    """Schema for creating a new role"""


class RoleUpdate(BaseModel):
    """Schema for updating role data"""

    name: Optional[str] = Field(None, min_length=2, max_length=50, examples=["Support Healer"])
    description: Optional[str] = Field(None, examples=["Provides healing and support to the group"])
    icon_url: Optional[str] = Field(None, examples=["https://example.com/icons/support_healer.png"])
    permission_level: Optional[int] = Field(None, ge=0, le=100, description="Permission level (0-100)")
    is_default: Optional[bool] = Field(None, description="Whether this is a default role for new users")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Support Healer",
                    "description": "Provides healing and support to the group",
                    "icon_url": "https://example.com/icons/support_healer.png",
                }
            ]
        }
    )


class RoleInDBBase(RoleBase):
    """Base schema for role data in database"""

    id: int = Field(..., examples=[1])

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "name": "Healer",
                    "description": "Responsible for keeping the group alive with healing",
                    "icon_url": "https://example.com/icons/healer.png",
                }
            ]
        },
    )


class Role(RoleInDBBase):
    """Schema for role data returned by API"""


class RoleInDB(RoleInDBBase):
    """Schema for role data stored in database"""
