from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class UserBase(BaseModel):
    """Base schema for user data"""
    username: str = Field(..., min_length=3, max_length=50, example="john_doe")
    email: EmailStr = Field(..., example="user@example.com")
    is_active: bool = Field(default=True, example=True)
    is_superuser: bool = Field(default=False, example=False)

class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8, example="securepassword123")

class UserUpdate(BaseModel):
    """Schema for updating user data"""
    username: Optional[str] = Field(None, min_length=3, max_length=50, example="new_username")
    email: Optional[EmailStr] = Field(None, example="new_email@example.com")
    password: Optional[str] = Field(None, min_length=8, example="newpassword123")
    is_active: Optional[bool] = Field(None, example=True)

class UserInDBBase(UserBase):
    """Base schema for user data in database"""
    id: int = Field(..., example=1)
    created_at: datetime = Field(..., example="2023-01-01T00:00:00")
    updated_at: Optional[datetime] = Field(None, example="2023-01-01T00:00:00")

    class Config:
        orm_mode = True

class User(UserInDBBase):
    """Schema for user data returned by API"""
    pass

class UserInDB(UserInDBBase):
    """Schema for user data stored in database"""
    hashed_password: str = Field(..., example="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW")

class Token(BaseModel):
    """Schema for authentication token"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schema for token data"""
    username: Optional[str] = None
