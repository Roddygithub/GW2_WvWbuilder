"""
Schémas Pydantic pour la gestion des tokens JWT.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TokenPayload(BaseModel):
    """Payload du token JWT."""
    sub: str = Field(..., description="Sujet du token (généralement l'ID utilisateur)")
    exp: datetime = Field(..., description="Date d'expiration du token")
    iat: Optional[datetime] = Field(None, description="Date d'émission du token")
    jti: Optional[str] = Field(None, description="Identifiant unique du token")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.timestamp(),
        }
        schema_extra = {
            "example": {
                "sub": "123",
                "exp": 1672531200,
                "iat": 1672527600,
                "jti": "550e8400-e29b-41d4-a716-446655440000"
            }
        }
