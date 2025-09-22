"""
Module pour les tables d'association many-to-many.

Ce module contient les définitions de tables de jonction utilisées pour les relations many-to-many.
"""
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Table, Text, func, UniqueConstraint

from .base import Base

# Table de jonction pour les membres des compositions
composition_members = Table(
    "composition_members",
    Base.metadata,
    Column("composition_id", Integer, ForeignKey("compositions.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="SET NULL"), nullable=True),
    Column("profession_id", Integer, ForeignKey("professions.id", ondelete="SET NULL"), nullable=True),
    Column("elite_specialization_id", Integer, ForeignKey("elite_specializations.id", ondelete="SET NULL"), nullable=True),
    Column("notes", Text, nullable=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), onupdate=func.now()),
)

# Table de jonction pour les rôles des utilisateurs
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

# Table de jonction pour les permissions des rôles
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

# Table d'association pour la relation many-to-many entre les builds et les professions
build_profession = Table(
    "build_professions",
    Base.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("build_id", Integer, ForeignKey("builds.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("profession_id", Integer, ForeignKey("professions.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
    Column("updated_at", DateTime(timezone=True), onupdate=func.now()),
    UniqueConstraint("build_id", "profession_id", name="uq_build_profession"),
)

# Table de jonction pour les membres d'équipe
team_members = Table(
    "team_members",
    Base.metadata,
    Column("team_id", Integer, ForeignKey("teams.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("is_admin", Boolean, default=False, nullable=False),
    Column("joined_at", DateTime(timezone=True), server_default=func.now()),
    Column("left_at", DateTime(timezone=True), nullable=True),
    Column("is_active", Boolean, default=True, nullable=False, index=True),
)

# La table composition_tags est maintenant définie dans composition_tag.py
# pour éviter les conflits de définition
