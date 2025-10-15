# This file makes the schemas directory a Python package
# Import all schemas to make them available when importing from app.schemas
from .user import UserBase, UserCreate, UserUpdate, UserInDB, User, Token, TokenData
from .token import TokenPayload
from .role import RoleBase, RoleCreate, RoleUpdate, RoleInDB, Role
from .profession import (
    ProfessionBase,
    ProfessionCreate,
    ProfessionUpdate,
    ProfessionInDB,
    Profession,
    EliteSpecializationBase,
    EliteSpecializationCreate,
    EliteSpecializationUpdate,
    EliteSpecializationInDB,
    EliteSpecialization,
)
from .build import (
    GameMode,
    RoleType,
    Build,
    BuildCreate,
    BuildUpdate,
    BuildInDB,
    BuildInDBBase,
    BuildProfessionBase,
    BuildGenerationRequest,
    TeamMember,
    BuildGenerationResponse,
)
from .msg import Msg, MsgWithCount
from .team import TeamBase, TeamCreate, TeamUpdate, TeamInDBBase, Team, TeamResponse
from .team_member import (
    TeamMemberBase,
    TeamMemberCreate,
    TeamMemberUpdate,
    TeamMember,
    TeamMemberResponse,
)
from .tag import TagBase, TagCreate, TagUpdate, TagInDBBase, Tag, TagStats, TagResponse
from .composition import (
    CompositionMemberRole,
    CompositionMemberBase,
    CompositionBase,
    CompositionCreate,
    CompositionUpdate,
    CompositionInDB,
    Composition,
    CompositionTagBase,
    CompositionTagCreate,
    CompositionTagUpdate,
    CompositionTagInDB,
    CompositionTag,
    CompositionSearch,
    CompositionOptimizationRequest,
    CompositionOptimizationResult,
    CompositionEvaluation,
)

from .build import (
    BuildBase,
)

from .response import (
    APIResponse,
    PaginatedResponse,
    ErrorResponse,
    SuccessResponse,
    create_success_response,
    create_error_response,
    create_paginated_response,
)

# Re-export all schemas
__all__ = [
    # User
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "User",
    "Token",
    "TokenData",
    "TokenPayload",
    # Role schemas
    "RoleBase",
    "RoleCreate",
    "RoleUpdate",
    "RoleInDB",
    "Role",
    # Profession schemas
    "ProfessionBase",
    "ProfessionCreate",
    "ProfessionUpdate",
    "ProfessionInDB",
    "Profession",
    "EliteSpecializationBase",
    "EliteSpecializationCreate",
    "EliteSpecializationUpdate",
    "EliteSpecializationInDB",
    "EliteSpecialization",
    # Composition schemas
    "CompositionMemberRole",
    "CompositionMemberBase",
    "CompositionBase",
    "CompositionCreate",
    "CompositionUpdate",
    "CompositionInDB",
    "Composition",
    "CompositionTagBase",
    "CompositionTagCreate",
    "CompositionTagUpdate",
    "CompositionTagInDB",
    "CompositionTag",
    "CompositionSearch",
    "CompositionOptimizationRequest",
    "CompositionOptimizationResult",
    "CompositionEvaluation",
    # Team
    "TeamBase",
    "TeamCreate",
    "TeamUpdate",
    "TeamInDBBase",
    "Team",
    "TeamMemberBase",
    "TeamMemberCreate",
    "TeamMemberUpdate",
    "TeamMember",
    "TeamResponse",
    # Build
    "Build",
    "BuildCreate",
    "BuildUpdate",
    "BuildInDB",
    "BuildInDBBase",
    "BuildProfessionBase",
    "BuildGenerationRequest",
    "BuildGenerationResponse",
    # Message schemas
    "Msg",
    "MsgWithCount",
    # Response schemas
    "APIResponse",
    "PaginatedResponse",
    "ErrorResponse",
    "SuccessResponse",
    "create_success_response",
    "create_error_response",
    "create_paginated_response",
]
