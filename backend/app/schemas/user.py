from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional, List

from .role import Role


class UserBase(BaseModel):
    """Base schema for user data"""

    username: str = Field(..., min_length=3, max_length=50, examples=["john_doe"])
    email: EmailStr = Field(..., examples=["user@example.com"])
    is_active: bool = Field(default=True, examples=[True])
    is_superuser: bool = Field(default=False, examples=[False])


class UserCreate(UserBase):
    """Schema for creating a new user (admin/system use)"""

    password: str = Field(..., min_length=8, examples=["securepassword123"])
    full_name: Optional[str] = Field(None, max_length=100, examples=["John Doe"])


class UserRegister(BaseModel):
    """Schema for user registration (public endpoint)"""
    
    email: EmailStr = Field(..., examples=["user@example.com"])
    password: str = Field(..., min_length=8, examples=["securepassword123"])
    username: Optional[str] = Field(None, min_length=3, max_length=50, examples=["john_doe"])
    full_name: Optional[str] = Field(None, max_length=100, examples=["John Doe"])


class UserUpdate(BaseModel):
    """Schema for updating user data"""

    username: Optional[str] = Field(None, min_length=3, max_length=50, examples=["new_username"])
    email: Optional[EmailStr] = Field(None, examples=["new_email@example.com"])
    password: Optional[str] = Field(None, min_length=8, examples=["newpassword123"])
    is_active: Optional[bool] = Field(None, examples=[True])
    full_name: Optional[str] = Field(None, max_length=100, examples=["John Doe"])


class UserInDBBase(UserBase):
    """Base schema for user data in database"""

    id: int = Field(..., examples=[1])
    created_at: datetime = Field(..., examples=["2023-01-01T00:00:00"])
    updated_at: Optional[datetime] = Field(None, examples=["2023-01-01T00:00:00"])

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "username": "john_doe",
                    "email": "user@example.com",
                    "is_active": True,
                    "is_superuser": False,
                    "created_at": "2023-01-01T00:00:00",
                    "updated_at": "2023-01-01T00:00:00",
                }
            ]
        },
    )


class User(UserInDBBase):
    """Schema for user data returned by API"""

    roles: List[Role] = []


class UserInDB(UserInDBBase):
    """Schema for user data stored in database"""

    hashed_password: str = Field(..., examples=["$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"])

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "username": "john_doe",
                    "email": "user@example.com",
                    "is_active": True,
                    "is_superuser": False,
                    "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
                    "created_at": "2023-01-01T00:00:00",
                    "updated_at": "2023-01-01T00:00:00",
                }
            ]
        },
    )


class Token(BaseModel):
    """Schema for authentication token"""

    access_token: str = Field(..., examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])
    token_type: str = "bearer"
    refresh_token: str = Field(..., examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                }
            ]
        }
    )


class TokenData(BaseModel):
    """Schema for token data"""

    username: Optional[str] = None

    model_config = ConfigDict(json_schema_extra={"examples": [{"username": "john_doe"}]})
