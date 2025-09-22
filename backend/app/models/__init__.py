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

<<<<<<< HEAD
from .build import Build
from .build_profession import BuildProfession

__all__ = [
    # Classe de base
    "Base",
    
    # Modèles principaux
    "User",
    "Role",
    "Profession",
    "EliteSpecialization",
    "Composition",
    "CompositionTag",
    "composition_members",
    "Build",
    "BuildProfession"
=======
# Import des modèles
from .user import User
from .role import Role
from .permission import Permission
from .token_models import Token, TokenPayload
from .build import Build
from .profession import Profession
from .elite_specialization import EliteSpecialization
from .team import Team
from .composition import Composition
from .composition_tag import CompositionTag
from .tag import Tag

# Tables d'association
from .association_tables import (
    user_roles,
    build_profession,
    composition_members,
    role_permissions,
    team_members,
    # composition_tags est maintenant défini dans composition_tag.py
)

# Export des modèles et énumérations
__all__: List[str] = [
    # Classes de base
    'Base',
    'BaseModel',
    'UUIDMixin',
    'TimeStampedMixin',
    'BaseUUIDModel',
    'BaseTimeStampedModel',
    'BaseUUIDTimeStampedModel',
    
    # Énumérations
    'GameMode',
    'RoleType',
    'BuildStatus',
    'CompositionStatus',
    'ProfessionType',
    'EliteSpecializationType',
    'BuildType',
    'CompositionRole',
    'Visibility',
    'PermissionLevel',
    'TeamRole',
    'TeamStatus',
    
    # Modèles principaux
    'User',
    'Role',
    'Permission',
    'Team',
    'Composition',
    'Build',
    'Tag',
    'CompositionTag',
    'EliteSpecialization',
    'Profession',
    'Token',
    'TokenPayload',
    
    # Tables d'association
    'user_roles',
    'build_profession',
    'composition_members',
    'role_permissions',
    'team_members'
>>>>>>> a023051 (feat: optimized CRUD with Redis caching + full test coverage + docs and monitoring guide)
]
