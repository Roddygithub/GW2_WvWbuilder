"""
Package des modèles SQLAlchemy pour l'application GW2_WvWbuilder.

Ce package expose tous les modèles de données utilisés dans l'application.
"""

from app.models.base import Base
from .base_models import (
    # Modèles principaux
    User,
    Role,
    Profession,
    EliteSpecialization,
    Composition,
    CompositionTag,
    Build,
    
    # Tables de jonction
    composition_members,
    user_roles,
    build_profession
)

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
]
