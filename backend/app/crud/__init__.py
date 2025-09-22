"""
CRUD operations for the application.

This module exports all CRUD operations for the application.
"""

from .base import CRUDBase
from .base_async import CRUDBaseAsync
from .crud_user import user as user_crud, CRUDUser
from .crud_role import role as role_crud, CRUDRole
from .crud_permission import permission as permission_crud
from .crud_profession import profession as profession_crud, CRUDProfession
from .crud_elite_specialization import elite_specialization as elite_spec_crud, CRUDEliteSpecialization
from .crud_build import build as build_crud, CRUDBuild
from .crud_team import team as team_crud, CRUDTeam
from .crud_team_member import team_member as team_member_crud, CRUDTeamMember
from .crud_tag import tag as tag_crud, CRUDTag
from .crud_composition import composition as composition_crud, CRUDComposition

# For backward compatibility
auth = user_crud  # Alias for auth operations

# Export all CRUD operations
__all__ = [
    # Base
    "CRUDBase",
    "CRUDBaseAsync",
    
    # User & Auth
    "CRUDUser",
    "user_crud",
    "auth",
    
    # Roles & Permissions
    "CRUDRole",
    "role_crud",
    "permission_crud",
    
    # Game Data - Builds & Professions
    "CRUDBuild",
    "build_crud",
    "CRUDProfession",
    "profession_crud",
    "CRUDEliteSpecialization",
    "elite_spec_crud",
    
    # Teams & Team Members
    "CRUDTeam",
    "team_crud",
    "CRUDTeamMember",
    "team_member_crud",
    
    # Compositions & Tags
    "CRUDComposition",
    "composition_crud",
    "CRUDTag",
    "tag_crud",
]