from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Import Base from the local models package to avoid circular imports
from .base import Base

# Table de jonction pour la relation many-to-many entre Composition et User
composition_members = Table(
    'composition_members',
    Base.metadata,
    Column('composition_id', Integer, ForeignKey('compositions.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id')),
    Column('profession_id', Integer, ForeignKey('professions.id')),
    Column('elite_specialization_id', Integer, ForeignKey('elite_specializations.id')),
    Column('notes', Text, nullable=True)
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    compositions = relationship(
        "Composition", 
        secondary=composition_members, 
        back_populates="members",
        overlaps="members"
    )
    roles = relationship(
        "Role", 
        secondary=composition_members, 
        back_populates="members",
        viewonly=True
    )

    def __repr__(self):
        return f"<User {self.username}>"

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    icon_url = Column(String, nullable=True)
    
    # Relations
    members = relationship(
        "User", 
        secondary=composition_members, 
        back_populates="roles",
        viewonly=True
    )

    def __repr__(self):
        return f"<Role {self.name}>"

class Profession(Base):
    __tablename__ = "professions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    icon_url = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    
    # Relations
    elite_specializations = relationship("EliteSpecialization", back_populates="profession")
    
    def __repr__(self):
        return f"<Profession {self.name}>"

class EliteSpecialization(Base):
    __tablename__ = "elite_specializations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    profession_id = Column(Integer, ForeignKey('professions.id'), nullable=False)
    icon_url = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    
    # Relations
    profession = relationship("Profession", back_populates="elite_specializations")
    
    def __repr__(self):
        return f"<EliteSpecialization {self.name} ({self.profession.name})>"

class Composition(Base):
    __tablename__ = "compositions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    squad_size = Column(Integer, default=10)
    is_public = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relations
    members = relationship(
        "User", 
        secondary=composition_members, 
        back_populates="compositions",
        overlaps="members"
    )
    tags = relationship("CompositionTag", back_populates="composition")
    
    # Relation avec le créateur
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<Composition {self.name}>"

class CompositionTag(Base):
    __tablename__ = "composition_tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    composition_id = Column(Integer, ForeignKey('compositions.id'))

    # Relations
    composition = relationship("Composition", back_populates="tags")
