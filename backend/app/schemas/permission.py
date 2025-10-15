"""
Pydantic models for Permission.

This module defines the Pydantic models used for permission validation and serialization.
"""

from typing import Optional

from pydantic import BaseModel, Field


# Shared properties
class PermissionBase(BaseModel):
    """Base model for Permission with common attributes."""

    name: str = Field(..., max_length=100, description="Name of the permission")
    code: str = Field(..., max_length=100, description="Unique code for the permission")
    description: Optional[str] = Field(
        None, description="Description of the permission"
    )
    is_active: bool = Field(True, description="Whether the permission is active")


# Properties to receive on permission creation
class PermissionCreate(PermissionBase):
    """Model for creating a new permission."""

    pass


# Properties to receive on permission update
class PermissionUpdate(PermissionBase):
    """Model for updating an existing permission."""

    name: Optional[str] = Field(
        None, max_length=100, description="Name of the permission"
    )
    code: Optional[str] = Field(
        None, max_length=100, description="Unique code for the permission"
    )
    is_active: Optional[bool] = Field(
        None, description="Whether the permission is active"
    )


# Properties shared by models stored in DB
class PermissionInDBBase(PermissionBase):
    """Base model for permission stored in the database."""

    id: int

    class Config:
        from_attributes = True


# Properties to return to client
class Permission(PermissionInDBBase):
    """Model for permission data returned to the client."""

    pass


# Properties stored in DB
class PermissionInDB(PermissionInDBBase):
    """Model for permission data as stored in the database."""

    pass
