"""
Package des modèles SQLAlchemy pour l'application GW2 WvW Builder.

Ce package expose tous les modèles de données utilisés dans l'application.
"""

import logging
from typing import List, Type, Any, Dict

# Configuration du logger
logger = logging.getLogger(__name__)
logger.info("Chargement du package models...")

# Import des classes de base depuis le module séparé
from .base_model import (
    Base,
    BaseModel,
    UUIDMixin,
    TimeStampedMixin,
    BaseUUIDModel,
    BaseTimeStampedModel,
    BaseUUIDTimeStampedModel,
)

# Import des énumérations
from .enums import (
    GameMode,
    RoleType,
    BuildStatus,
    CompositionStatus,
    ProfessionType,
    EliteSpecializationType,
    BuildType,
    CompositionRole,
    Visibility,
    PermissionLevel,
    TeamRole,
    TeamStatus,
)

# Import des modèles principaux
from .user import User
from .role import Role
from .permission import Permission
from .profession import Profession
from .elite_specialization import EliteSpecialization
from .build import Build
from .composition import Composition
from .team import Team
from .team_member import TeamMember
from .token_models import Token, TokenPayload
from .composition_tag import CompositionTag
from .tag import Tag
from .user_role import UserRole
from .association_tables import composition_members, build_profession

# Les autres modèles sont importés dynamiquement dans app.db.__init__ pour éviter les imports circulaires

# Liste de tous les éléments à exporter
__all__ = [
    # Classes de base
    "Base",
    "BaseModel",
    "UUIDMixin",
    "TimeStampedMixin",
    "BaseUUIDModel",
    "BaseTimeStampedModel",
    "BaseUUIDTimeStampedModel",
    # Modèles
    "User",
    "Role",
    "Permission",
    "Profession",
    "EliteSpecialization",
    "Build",
    "Composition",
    "Team",
    "TeamMember",
    "Token",
    "TokenPayload",
    "CompositionTag",
    "Tag",
    "UserRole",
    "composition_members",
    "build_profession",
    # Énumérations
    "GameMode",
    "RoleType",
    "BuildStatus",
    "CompositionStatus",
    "ProfessionType",
    "EliteSpecializationType",
    "BuildType",
    "CompositionRole",
    "Visibility",
    "PermissionLevel",
    "TeamRole",
    "TeamStatus",
]
