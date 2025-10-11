"""
Registry for all SQLAlchemy models.

This module defines all the models to ensure they are registered with SQLAlchemy
before database operations are performed.
"""

# Import all models to ensure they are registered with SQLAlchemy
from .user import User
from .role import Role
from .permission import Permission
from .token_models import Token
from .build import Build
from .profession import Profession
from .tag import Tag
from .elite_specialization import EliteSpecialization
from .composition import Composition
from .composition_tag import CompositionTag
from .team import Team
from .team_member import TeamMember

# Import association tables
from .association_tables import build_profession, role_permissions, composition_members
from .user_role import UserRole

# List of all models to be imported for table creation
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

__all__ = ["MODELS"]
