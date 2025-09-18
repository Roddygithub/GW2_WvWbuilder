from typing import List
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, JSON, DateTime, Text, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base
from .build_profession import BuildProfession

# Remove circular imports by using string-based relationships
__all__ = ["Build"]

class Build(Base):
    __tablename__ = "builds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String)
    game_mode = Column(String, default="wvw")  # Could be "wvw", "pvp", etc.
    team_size = Column(Integer, default=5)  # Default to 5-man squads
    is_public = Column(Boolean, default=False)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    created_by = relationship("User", back_populates="builds")
    compositions = relationship("Composition", back_populates="build", cascade="all, delete-orphan")
    build_professions = relationship("BuildProfession", back_populates="build", cascade="all, delete-orphan")
    
    # Many-to-many relationship with Profession through BuildProfession
    professions = relationship(
        "Profession",
        secondary="build_professions",
        back_populates="builds",
        overlaps="build_professions,profession"
    )
    
    # Store build configuration as JSON for flexibility
    config = Column(JSON, nullable=False, default=dict)
    
    # Constraints and rules for the build
    constraints = Column(JSON, default=dict)  # E.g., max of 2 of same profession
    
    @property
    def owner_id(self) -> int:
        """Alias for created_by_id for API compatibility."""
        return self.created_by_id
        
    @owner_id.setter
    def owner_id(self, value: int) -> None:
        """Set the owner ID (alias for created_by_id)."""
        self.created_by_id = value

    def __repr__(self):
        return f"<Build {self.name}>"

# BuildProfession model has been moved to app.models.build_profession
