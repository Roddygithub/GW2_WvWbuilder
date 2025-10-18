"""
Module pour les tables d'association many-to-many.

Ce module contient les définitions de tables de jonction utilisées pour les relations many-to-many.
"""

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Table,
    Text,
    func,
    UniqueConstraint,
)

from .base import Base

# Table de jonction pour les membres des compositions
composition_members = Table(
    "composition_members",
    Base.metadata,
    Column(
        "composition_id",
        Integer,
        ForeignKey("compositions.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
    ),
    Column(
        "user_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
    ),
    Column(
        "role_id",
        Integer,
        ForeignKey("roles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    ),
    Column(
        "profession_id",
        Integer,
        ForeignKey("professions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    ),
    Column(
        "elite_specialization_id",
        Integer,
        ForeignKey("elite_specializations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    ),
    Column("notes", Text, nullable=True),
    Column(
        "created_at", DateTime(timezone=True), server_default=func.now(), nullable=False
    ),
    Column("updated_at", DateTime(timezone=True), onupdate=func.now()),
    # Ajout d'une contrainte d'unicité pour éviter les doublons
    UniqueConstraint("composition_id", "user_id", name="uq_composition_member"),
    # Ajout d'un commentaire pour la documentation
    comment="Table de jonction pour la relation many-to-many entre les compositions et les utilisateurs",
)

# La table user_roles est maintenant définie dans user_role.py comme un modèle complet
# pour gérer les relations many-to-many entre les utilisateurs et les rôles avec des attributs supplémentaires

# Table de jonction pour les permissions des rôles
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column(
        "role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "permission_id",
        Integer,
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

# Table d'association pour la relation many-to-many entre les builds et les professions
build_profession = Table(
    "build_professions",
    Base.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column(
        "build_id",
        Integer,
        ForeignKey("builds.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column(
        "profession_id",
        Integer,
        ForeignKey("professions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column(
        "created_at", DateTime(timezone=True), server_default=func.now(), nullable=False
    ),
    Column("updated_at", DateTime(timezone=True), onupdate=func.now()),
    UniqueConstraint("build_id", "profession_id", name="uq_build_profession"),
)

# La table team_members est maintenant définie dans team_member.py comme un modèle complet
# pour gérer les relations many-to-many entre les utilisateurs et les équipes avec des attributs supplémentaires
# Compatibilité: exposer un alias de table pour le code/test existant
from .team_member import TeamMember  # type: ignore F401

team_members = TeamMember.__table__

# La table composition_tags est maintenant définie dans composition_tag.py
# pour éviter les conflits de définition
