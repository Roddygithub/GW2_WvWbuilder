"""
Package principal de l'application GW2 WvW Builder.
Ce package expose les composants principaux de l'application.
"""
from typing import Any, Dict, List, Optional, Union
from fastapi import FastAPI

# Import des modèles depuis leurs modules individuels
from .models.base import Base
from .models.user import User
from .models.role import Role
from .models.permission import Permission
from .models.build import Build
from .models.composition import Composition
from .models.composition_tag import CompositionTag
from .models.profession import Profession
from .models.elite_specialization import EliteSpecialization
from .models.team import Team
from .models.tag import Tag

# Import des opérations CRUD
from .crud import (
    user_crud,
    permission_crud,
    build_crud,
    composition_crud,
    profession_crud,
    elite_spec_crud,
    team_crud,
    tag_crud,
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
