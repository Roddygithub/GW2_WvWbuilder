"""
Modèles SQLAlchemy pour l'application GW2_WvWbuilder.

Ce module contient toutes les définitions de modèles SQLAlchemy pour l'application.
Les modèles sont organisés de manière logique avec des commentaires pour une meilleure lisibilité.
"""

from __future__ import annotations
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
    UniqueConstraint,
    PrimaryKeyConstraint,
    Table,
    func,
    or_,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

# Pour les annotations de type en cas d'imports circulaires
if TYPE_CHECKING:
    from .base_models import Composition, Role, Build, Profession, EliteSpecialization

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

    # Association table for build-profession many-to-many relationship
    build_profession = Table(
        "build_professions",
        Base.metadata,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("build_id", Integer, ForeignKey("builds.id", ondelete="CASCADE"), nullable=False, index=True),
        Column("profession_id", Integer, ForeignKey("professions.id", ondelete="CASCADE"), nullable=False, index=True),
        Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
        UniqueConstraint('build_id', 'profession_id', name='uq_build_profession')
    )

except Exception as e:
    print(f"Erreur lors de la création des tables de jonction: {e}")
    raise


class User(Base):
    """Modèle utilisateur avec authentification et autorisations."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    compositions: Mapped[List[Composition]] = relationship(
        "Composition", 
        secondary=composition_members, 
        back_populates="members",
        viewonly=True
    )
    
    roles: Mapped[List[Role]] = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users",
        viewonly=True
    )
    
    builds: Mapped[List[Build]] = relationship("Build", back_populates="created_by")

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

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    permission_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relations
    users: Mapped[List[User]] = relationship(
        "User", 
        secondary=user_roles, 
        back_populates="roles",
        viewonly=True
    )

    def __repr__(self) -> str:
        return f"<Role {self.name}>"


class Profession(Base):
    """Modèle de profession (classe) dans Guild Wars 2."""
    __tablename__ = "professions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    icon_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    game_modes: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True, default=[])
    
    # Relations
    elite_specializations: Mapped[List["EliteSpecialization"]] = relationship(
        "EliteSpecialization", 
        back_populates="profession",
        cascade="all, delete-orphan"
    )
    
    # Relation avec les builds via la table d'association
    builds: Mapped[List["Build"]] = relationship(
        "Build",
        secondary=build_profession,
        back_populates="professions"
    )
    
    def __repr__(self) -> str:
        return f"<Profession {self.name}>"


class EliteSpecialization(Base):
    """Modèle de spécialisation d'élite pour les professions."""
    __tablename__ = "elite_specializations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    profession_id: Mapped[int] = mapped_column(Integer, ForeignKey('professions.id'), nullable=False)
    icon_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relations
    profession: Mapped[Profession] = relationship("Profession", back_populates="elite_specializations")

    def __repr__(self) -> str:
        return f"<EliteSpecialization {self.name} ({self.profession.name})>"


class Composition(Base):
    """Modèle de composition d'équipe WvW."""
    __tablename__ = "compositions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    squad_size: Mapped[int] = mapped_column(Integer, default=10)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    build_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('builds.id'), nullable=True)
    
    # Relations
    members: Mapped[List[User]] = relationship(
        "User", 
        secondary=composition_members, 
        back_populates="compositions",
        viewonly=True
    )
    
    tags: Mapped[List[CompositionTag]] = relationship(
        "CompositionTag", 
        back_populates="composition", 
        cascade="all, delete-orphan"
    )
    
    creator: Mapped[User] = relationship("User", foreign_keys=[created_by])
    build: Mapped[Optional[Build]] = relationship("Build", back_populates="compositions")

    def __repr__(self) -> str:
        return f"<Composition {self.name}>"


class CompositionTag(Base):
    """Modèle d'étiquette pour les compositions."""
    __tablename__ = "composition_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    composition_id: Mapped[int] = mapped_column(Integer, ForeignKey('compositions.id'))
    
    # Relations
    composition: Mapped[Composition] = relationship("Composition", back_populates="tags")

    def __repr__(self) -> str:
        return f"<CompositionTag {self.name}>"


class Build(Base):
    """Modèle de build pour les compositions."""
    __tablename__ = "builds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    game_mode: Mapped[str] = mapped_column(String, default="wvw")
    team_size: Mapped[int] = mapped_column(Integer, default=5)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    config: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    constraints: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    
    # Relations
    created_by: Mapped[User] = relationship("User", back_populates="builds")
    compositions: Mapped[List[Composition]] = relationship(
        "Composition", 
        back_populates="build", 
        cascade="all, delete-orphan"
    )
    
    # Relation avec les professions via la table d'association
    professions: Mapped[List[Profession]] = relationship(
        "Profession",
        secondary=build_profession,
        back_populates="builds"
    )
    
    # Alias pour created_by_id pour la compatibilité avec l'API
    @property
    def owner_id(self) -> int:
        """Retourne l'ID du propriétaire (alias pour created_by_id)."""
        return self.created_by_id
        
    @owner_id.setter
    def owner_id(self, value: int) -> None:
        """Définit l'ID du propriétaire (alias pour created_by_id)."""
        self.created_by_id = value

    def __repr__(self) -> str:
        return f"<Build {self.name}>"
