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
    "Build",
    
    # Tables de jonction
    "composition_members",
    "user_roles",
    "build_profession"
]
