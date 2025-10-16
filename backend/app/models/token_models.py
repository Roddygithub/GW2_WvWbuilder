"""
Modèles liés aux jetons d'authentification.

Ce module contient les modèles pour la gestion des jetons d'authentification.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base, TimeStampedMixin

if TYPE_CHECKING:
    from .user import User


class Token(Base, TimeStampedMixin):
    """Modèle de jeton d'authentification."""

    __tablename__ = "tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    token: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    expires: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # Les champs created_at et updated_at sont fournis par TimeStampedMixin

    # Relations
    user: Mapped["User"] = relationship("User", back_populates="tokens")

    def __repr__(self) -> str:
        return f"<Token {self.token[:10]}..."

    def is_expired(self) -> bool:
        """Vérifie si le jeton est expiré."""
        if not self.expires:
            return False
        return datetime.now(timezone.utc) > self.expires

    def is_valid(self) -> bool:
        """Vérifie si le jeton est valide (actif et non expiré)."""
        return self.is_active and not self.is_expired()


class TokenPayload(PydanticBaseModel):
    """Modèle Pydantic pour les données de charge utile du jeton."""

    sub: Optional[int] = None  # ID de l'utilisateur
    exp: Optional[datetime] = None  # Date d'expiration
    iat: Optional[datetime] = None  # Date d'émission
    jti: Optional[str] = None  # Identifiant unique du jeton
    token_type: Optional[str] = None  # Type de jeton (ex: bearer)
    scopes: List[str] = []  # Scopes d'accès

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}

    def __repr__(self) -> str:
        return f"<TokenPayload sub={self.sub} exp={self.exp} scopes={self.scopes}>"
