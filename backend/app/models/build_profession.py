from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class BuildProfession(Base):
    """Association table for many-to-many relationship between Build and Profession."""
    __tablename__ = "build_professions"

    build_id = Column(Integer, ForeignKey("builds.id"), primary_key=True)
    profession_id = Column(Integer, ForeignKey("professions.id"), primary_key=True)

    # Relationships
    build = relationship(
        "Build", 
        back_populates="build_professions",
        overlaps="builds,professions"
    )
    profession = relationship(
        "Profession", 
        back_populates="build_professions",
        overlaps="builds"
    )

    def __repr__(self):
        return f"<BuildProfession build_id={self.build_id} profession_id={self.profession_id}>"
