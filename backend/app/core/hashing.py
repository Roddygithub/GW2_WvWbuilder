"""
Password hashing utilities.

This module provides functions for hashing and verifying passwords.
"""
from typing import Optional

from passlib.context import CryptContext

# Configuration du contexte de hachage
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: Optional[str], hashed_password: Optional[str]) -> bool:
    """Vérifie si le mot de passe en clair correspond au hash.

    Args:
        plain_password: Mot de passe en clair (peut être None)
        hashed_password: Mot de passe hashé (peut être None)

    Returns:
        bool: True si la vérification réussit, False sinon
    """
    if not plain_password or not hashed_password:
        return False
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash un mot de passe.

    Args:
        password: Mot de passe en clair

    Returns:
        str: Le mot de passe hashé
    """
    return pwd_context.hash(password)

def get_password_hash_sha256(password: str) -> str:
    """Hash un mot de passe avec SHA-256 (pour rétrocompatibilité).
    
    Note: Cette fonction est maintenue pour la rétrocompatibilité.
    La fonction get_password_hash avec bcrypt est recommandée pour les nouveaux développements.
    
    Args:
        password: Mot de passe en clair
        
    Returns:
        str: Le mot de passe hashé avec SHA-256
    """
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()
