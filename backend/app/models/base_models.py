"""
Modèles SQLAlchemy pour l'application GW2_WvWbuilder.

Ce module contient toutes les définitions de modèles SQLAlchemy pour l'application.
Les modèles sont organisés de manière logique avec des commentaires pour une meilleure lisibilité.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, String, Table, Text, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base

# Tables de jonction
try:
    # Table de jonction pour les membres des compositions
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

    # Table de jonction pour les rôles des utilisateurs
    user_roles = Table(
        'user_roles',
        Base.metadata,
        Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
        Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    )

    # Table de jonction pour les builds et les professions
    build_professions = Table(
        'build_professions',
        Base.metadata,
        Column('build_id', Integer, ForeignKey('builds.id'), primary_key=True),
        Column('profession_id', Integer, ForeignKey('professions.id'), primary_key=True)
    )

except Exception as e:
    print(f"Erreur lors de la création des tables de jonction: {e}")
    raise


class User(Base):
    """Modèle utilisateur avec authentification et autorisations."""
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
        back_populates="members"
    )
    
    roles = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users",
    )
    
    builds = relationship("Build", back_populates="created_by")

    def __repr__(self):
        return f"<User {self.username}>"
        
    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return self.id == other.id
        
    def __hash__(self):
        return hash((self.id,))


class Role(Base):
    """Modèle de rôle pour les autorisations des utilisateurs."""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    icon_url = Column(String, nullable=True)
    
    # Relations
    users = relationship(
        "User",
        secondary=user_roles,
        back_populates="roles",
    )

    def __repr__(self):
        return f"<Role {self.name}>"


class Profession(Base):
    """Modèle de profession (classe) dans Guild Wars 2."""
    __tablename__ = "professions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    icon_url = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    
    # Relations
    elite_specializations = relationship(
        "EliteSpecialization", 
        back_populates="profession",
        cascade="all, delete-orphan"
    )
    
    builds = relationship(
        "Build",
        secondary="build_professions",
        viewonly=True
    )
    
    build_professions = relationship("BuildProfession", back_populates="profession")

    def __repr__(self):
        return f"<Profession {self.name}>"


class EliteSpecialization(Base):
    """Modèle de spécialisation d'élite pour les professions."""
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
    """Modèle de composition d'équipe WvW."""
    __tablename__ = "compositions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    squad_size = Column(Integer, default=10)
    is_public = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    build_id = Column(Integer, ForeignKey('builds.id'), nullable=True)

    # Relations
    members = relationship(
        "User", 
        secondary=composition_members, 
        back_populates="compositions"
    )
    
    tags = relationship("CompositionTag", back_populates="composition", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])
    build = relationship("Build", back_populates="compositions")

    def __repr__(self):
        return f"<Composition {self.name}>"


class CompositionTag(Base):
    """Modèle d'étiquette pour les compositions."""
    __tablename__ = "composition_tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    composition_id = Column(Integer, ForeignKey('compositions.id'))

    # Relations
    composition = relationship("Composition", back_populates="tags")

    def __repr__(self):
        return f"<CompositionTag {self.name}>"


class Build(Base):
    """Modèle de build pour les compositions."""
    __tablename__ = "builds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    game_mode = Column(String, default="wvw")
    team_size = Column(Integer, default=5)
    is_public = Column(Boolean, default=False)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    config = Column(JSON, nullable=False, default=dict)
    constraints = Column(JSON, default=dict)
    
    # Relations
    created_by = relationship("User", back_populates="builds")
    compositions = relationship("Composition", back_populates="build", cascade="all, delete-orphan")
    build_professions = relationship(
        "BuildProfession", 
        back_populates="build", 
        cascade="all, delete-orphan"
    )
    
    professions = relationship(
        "Profession",
        secondary="build_professions",
        viewonly=True
    )

    @property
    def owner_id(self) -> int:
        """Alias pour created_by_id pour la compatibilité avec l'API."""
        return self.created_by_id
        
    @owner_id.setter
    def owner_id(self, value: int) -> None:
        """Définit l'ID du propriétaire (alias pour created_by_id)."""
        self.created_by_id = value

    def __repr__(self):
        return f"<Build {self.name}>"


class BuildProfession(Base):
    """Table d'association pour la relation many-to-many entre Build et Profession."""
    __tablename__ = "build_professions"
    __table_args__ = {'extend_existing': True}

    build_id = Column(Integer, ForeignKey("builds.id"), primary_key=True)
    profession_id = Column(Integer, ForeignKey("professions.id"), primary_key=True)
    
    # Relations
    build = relationship("Build", back_populates="build_professions")
    profession = relationship("Profession", back_populates="build_professions")

    def __repr__(self):
        return f"<BuildProfession build_id={self.build_id} profession_id={self.profession_id}>"
