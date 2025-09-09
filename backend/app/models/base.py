"""
Module de base pour les modèles SQLAlchemy.

Ce module fournit la classe de base pour tous les modèles de l'application.
"""

from typing import Any

from sqlalchemy import Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr


class Base(DeclarativeBase):
    """Classe de base pour tous les modèles SQLAlchemy."""
    
    # Ajout d'un ID de type générique pour faciliter le typage
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Génère automatiquement le nom de la table à partir du nom de la classe
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.id}>"
