# This file makes the schemas directory a Python package
# Import all schemas to make them available when importing from app.schemas
from .user import (
    UserBase, UserCreate, UserUpdate, UserInDB, User, Token, TokenData
)
from .role import RoleBase, RoleCreate, RoleUpdate, RoleInDB, Role
from .profession import (
    ProfessionBase, ProfessionCreate, ProfessionUpdate, ProfessionInDB, Profession,
    EliteSpecializationBase, EliteSpecializationCreate, EliteSpecializationUpdate,
    EliteSpecializationInDB, EliteSpecialization
)
from .composition import (
    CompositionMemberRole, CompositionMemberBase, CompositionBase, CompositionCreate,
    CompositionUpdate, CompositionInDB, Composition, CompositionTagBase,
    CompositionTagCreate, CompositionTagUpdate, CompositionTagInDB, CompositionTag,
    CompositionSearch, CompositionOptimizationRequest, CompositionOptimizationResult,
    CompositionEvaluation
)

# Re-export all schemas
__all__ = [
    # User schemas
    'UserBase', 'UserCreate', 'UserUpdate', 'UserInDB', 'User', 'Token', 'TokenData',
    
    # Role schemas
    'RoleBase', 'RoleCreate', 'RoleUpdate', 'RoleInDB', 'Role',
    
    # Profession schemas
    'ProfessionBase', 'ProfessionCreate', 'ProfessionUpdate', 'ProfessionInDB', 'Profession',
    'EliteSpecializationBase', 'EliteSpecializationCreate', 'EliteSpecializationUpdate',
    'EliteSpecializationInDB', 'EliteSpecialization',
    
    # Composition schemas
    'CompositionMemberRole', 'CompositionMemberBase', 'CompositionBase', 'CompositionCreate',
    'CompositionUpdate', 'CompositionInDB', 'Composition', 'CompositionTagBase',
    'CompositionTagCreate', 'CompositionTagUpdate', 'CompositionTagInDB', 'CompositionTag',
    'CompositionSearch', 'CompositionOptimizationRequest', 'CompositionOptimizationResult',
    'CompositionEvaluation'
]
