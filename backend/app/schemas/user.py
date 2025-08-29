from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional, List
from enum import Enum

class UserBase(BaseModel):
    """Base schema for user data"""
    username: str = Field(..., min_length=3, max_length=50, json_schema_extra={"example": "john_doe"})
    email: EmailStr = Field(..., json_schema_extra={"example": "user@example.com"})
    is_active: bool = Field(default=True, json_schema_extra={"example": True})
    is_superuser: bool = Field(default=False, json_schema_extra={"example": False})

class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8, json_schema_extra={"example": "securepassword123"})

class UserUpdate(BaseModel):
    """Schema for updating user data"""
    username: Optional[str] = Field(None, min_length=3, max_length=50, json_schema_extra={"example": "new_username"})
    email: Optional[EmailStr] = Field(None, json_schema_extra={"example": "new_email@example.com"})
    password: Optional[str] = Field(None, min_length=8, json_schema_extra={"example": "newpassword123"})
    is_active: Optional[bool] = Field(None, json_schema_extra={"example": True})

class UserInDBBase(UserBase):
    """Base schema for user data in database"""
    id: int = Field(..., json_schema_extra={"example": 1})
    created_at: datetime = Field(..., json_schema_extra={"example": "2023-01-01T00:00:00"})
    updated_at: Optional[datetime] = Field(None, json_schema_extra={"example": "2023-01-01T00:00:00"})
    model_config = ConfigDict(from_attributes=True)

class User(UserInDBBase):
    """Schema for user data returned by API"""
    pass

class UserInDB(UserInDBBase):
    """Schema for user data stored in database"""
    hashed_password: str = Field(..., json_schema_extra={"example": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"})

class Token(BaseModel):
    """Schema for authentication token"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schema for token data"""
    username: Optional[str] = None
