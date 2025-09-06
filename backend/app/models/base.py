"""
Module de base pour les modèles SQLAlchemy.

Ce module fournit la classe de base pour tous les modèles de l'application.
"""

from sqlalchemy.ext.declarative import declarative_base

# Création de la classe de base pour tous les modèles
Base = declarative_base()

# Cette classe est importée dans d'autres parties de l'application pour être utilisée
# comme classe de base pour les modèles SQLAlchemy.
