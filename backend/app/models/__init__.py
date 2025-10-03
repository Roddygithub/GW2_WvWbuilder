"""
Package des modèles SQLAlchemy pour l'application GW2 WvW Builder.

Ce package expose tous les modèles de données utilisés dans l'application.
"""

import logging
from typing import List

# Configuration du logger
logger = logging.getLogger(__name__)
logger.info("Chargement du package models...")

# Import des classes de base
from .base import Base, BaseModel, UUIDMixin, TimeStampedMixin, BaseUUIDModel, BaseTimeStampedModel, BaseUUIDTimeStampedModel

# Import des énumérations
from .enums import (
    GameMode, RoleType, BuildStatus, CompositionStatus, ProfessionType, 
    EliteSpecializationType, BuildType, CompositionRole, Visibility, 
    PermissionLevel, TeamRole, TeamStatus
)

# Import des modèles
from .user import User
from .role import Role
from .permission import Permission
from .token_models import Token, TokenPayload
from .build import Build
from .profession import Profession
from .elite_specialization import EliteSpecialization
from .composition import Composition, composition_members
from .composition_tag import CompositionTag
from .team import Team
from .team_member import TeamMember
from .tag import Tag

# Tables d'association
from .association_tables import user_roles, build_profession, role_permissions

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
    
    # Modèles principaux
    "User",
    "Role",
    "Permission",
    "Token",
    "TokenPayload",
    "Build",
    "Profession",
    "EliteSpecialization",
    "Composition",
    "CompositionTag",
    "Team",
    "TeamMember",
    "Tag",
    
    # Tables d'association
    "user_roles",
    "build_profession",
    "role_permissions",
    "composition_members"
]
