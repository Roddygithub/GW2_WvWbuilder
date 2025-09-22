"""
Package principal de l'application GW2 WvW Builder.

Ce package expose les composants principaux de l'application.
"""
from typing import Any, Dict, List, Optional, Union
from fastapi import FastAPI

# Import des modèles
from .models import (
    Base,
    User,
    Role,
    Permission,
    Build,
    Composition,
    Profession,
    EliteSpecialization,
    Team,
    Tag,
    CompositionTag,
)

# Import des schémas
from .schemas import (
    user as user_schemas,
    role as role_schemas,
    build as build_schemas,
    composition as composition_schemas,
    profession as profession_schemas,
    elite_specialization as elite_spec_schemas,
    team as team_schemas,
    token as token_schemas,
)

# Import de la configuration
from .core.config import Settings, get_settings

# Import du cache
from .core.cache import cache as redis_cache

# Import de la sécurité
from .core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    get_current_user,
    get_current_active_user,
    get_current_active_superuser,
)

# Import des dépendances API
from .api.deps import (
    get_async_db,
    get_current_user_dep,
    get_current_active_user,
    get_current_active_superuser,
)

# Import de l'application FastAPI
from .main import app

# Types communs
TokenPayload = Dict[str, Any]

# Variables exportées
__all__ = [
    # Models
    'Base',
    'User',
    'Role',
    'Permission',
    'Build',
    'Composition',
    'Profession',
    'EliteSpecialization',
    'Team',
    'Tag',
    'CompositionTag',
    'UserRole',
    
    # Schemas
    'user_schemas',
    'role_schemas',
    'build_schemas',
    'composition_schemas',
    'profession_schemas',
    'elite_spec_schemas',
    'team_schemas',
    'token_schemas',
    
    # Core
    'Settings',
    'get_settings',
    'get_password_hash',
    'verify_password',
    'create_access_token',
    'create_refresh_token',
    'verify_refresh_token',
    'get_current_user',
    'get_current_active_user',
    'get_current_active_superuser',
    
    # API
    'get_async_db',
    'get_current_user_dep',
    'app',
    
    # Types
    'TokenPayload',
]
