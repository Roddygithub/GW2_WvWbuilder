"""Database module for GW2 WvW Builder.

This module provides database session management and initialization.
"""

"""Database module for GW2 WvW Builder.

This module provides database session management and initialization.
"""

import logging
from typing import List, Type, Any

# Import des modèles pour s'assurer qu'ils sont enregistrés avec SQLAlchemy
# avant la création des tables
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.models.token_models import Token
from app.models.build import Build
from app.models.profession import Profession
from app.models.tag import Tag
from app.models.elite_specialization import EliteSpecialization
from app.models.composition import Composition
from app.models.composition_tag import CompositionTag
from app.models.team import Team
from app.models.team_member import TeamMember

# Tables d'association
from app.models.association_tables import (
    build_profession,
    role_permissions,
    composition_members,
)
from app.models.user_role import UserRole

# Liste de tous les modèles à importer pour la création des tables
MODELS = [
    User,
    Role,
    Permission,
    Token,
    Build,
    Profession,
    Tag,
    EliteSpecialization,
    Composition,
    Team,
    TeamMember,
    build_profession,
    role_permissions,
    UserRole,
    composition_members,
    CompositionTag,
]

from .base import Base
from .session import engine, async_engine, init_db, init_async_db
from .factories import SessionLocal, AsyncSessionLocal
from .dependencies import get_db, get_async_db

logger = logging.getLogger(__name__)

# S'assurer que tous les modèles sont importés
logger.info("Chargement des modèles pour la base de données...")
for model in MODELS:
    logger.debug(
        f"Modèle chargé: {model.__name__ if hasattr(model, '__name__') else model}"
    )

__all__ = [
    # SQLAlchemy Base
    "Base",
    # Session factories
    "SessionLocal",
    "AsyncSessionLocal",
    # Engines
    "engine",
    "async_engine",
    # Session getters
    "get_db",
    "get_async_db",
    # Initialization
    "init_db",
    "init_async_db",
]
