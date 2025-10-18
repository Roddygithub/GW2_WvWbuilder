"""
Dépendances pour les routes de l'API.

Ce module contient les dépendances réutilisables pour l'API, notamment pour l'authentification,
l'autorisation et la validation des données.
"""

from typing import Callable, Dict, List, TypeVar

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import (
    CredentialsException,
    ForbiddenException,
    InactiveUserException,
    InvalidTokenException,
    NotSuperUserException,
    UserNotFoundException,
)
from app.core.gw2.client import get_gw2_client
from app.core.security import oauth2_scheme
from app.db.dependencies import get_async_db
from app.db.session import get_db
from app.models.user import User
from app.schemas.token import TokenPayload

# Type variable pour les modèles Pydantic
ModelType = TypeVar("ModelType")

# Schéma d'authentification HTTP Bearer
security = HTTPBearer()


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    """
    Obtient l'utilisateur actuellement authentifié à partir du token JWT.

    Args:
        request: Requête HTTP actuelle
        db: Session de base de données
        token: Token JWT d'authentification

    Returns:
        User: L'utilisateur authentifié

    Raises:
        CredentialsException: Si le token est invalide ou expiré
        UserNotFoundException: Si l'utilisateur n'existe pas
    """
    if not token:
        raise CredentialsException()

    try:
        # Décoder le token JWT
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_aud": False},
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError) as e:
        raise InvalidTokenException(detail=str(e))

    # Récupérer l'utilisateur depuis la base de données
    user = db.query(User).filter(User.id == token_data.sub).first()
    if not user:
        raise UserNotFoundException()

    # Vérifier si l'utilisateur est actif
    if not user.is_active:
        raise InactiveUserException()

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Vérifie que l'utilisateur actuel est actif.

    Args:
        current_user: L'utilisateur actuellement authentifié

    Returns:
        User: L'utilisateur actif

    Raises:
        InactiveUserException: Si l'utilisateur est inactif
    """
    if not current_user.is_active:
        raise InactiveUserException()
    return current_user


def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Vérifie que l'utilisateur actuel est un superutilisateur.

    Args:
        current_user: L'utilisateur actuellement authentifié

    Returns:
        User: L'utilisateur superadmin

    Raises:
        NotSuperUserException: Si l'utilisateur n'est pas un superutilisateur
    """
    if not current_user.is_superuser:
        raise NotSuperUserException()
    return current_user


def get_authorization_header(
    authorization: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Extrait le token d'authentification depuis l'en-tête Authorization.

    Args:
        authorization: En-tête d'autorisation

    Returns:
        str: Le token d'authentification

    Raises:
        CredentialsException: Si l'en-tête est manquant ou invalide
    """
    if not authorization:
        raise CredentialsException("Missing Authorization header")

    scheme, _, token = authorization.credentials.partition(" ")
    if not token or scheme.lower() != "bearer":
        raise CredentialsException("Invalid authentication scheme")

    return token


# Alias for backward compatibility
get_current_user_dep = get_current_user


async def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User | None:
    """
    Obtient l'utilisateur actuellement authentifié, ou None si non authentifié.
    
    Version optionnelle de get_current_user qui ne lève pas d'exception.
    
    Args:
        request: Requête HTTP actuelle
        db: Session de base de données
        token: Token JWT d'authentification (optionnel)
        
    Returns:
        User | None: L'utilisateur authentifié ou None
    """
    if not token:
        return None
    
    try:
        # Décoder le token JWT
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_aud": False},
        )
        token_data = TokenPayload(**payload)
        
        # Récupérer l'utilisateur depuis la base de données
        user = db.query(User).filter(User.id == token_data.sub).first()
        if user and user.is_active:
            return user
        return None
    except (JWTError, ValidationError):
        return None


def has_permission(required_permissions: List[str]) -> Callable[..., User]:
    """
    Vérifie que l'utilisateur a les permissions requises.

    Args:
        required_permissions: Liste des permissions requises

    Returns:
        Callable: Une fonction de dépendance qui vérifie les permissions
    """

    def dependency(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        # Les superutilisateurs ont toutes les permissions
        if current_user.is_superuser:
            return current_user

        # Vérifier que l'utilisateur a toutes les permissions requises
        user_permissions = {p.name for p in current_user.permissions}
        if not all(perm in user_permissions for perm in required_permissions):
            raise ForbiddenException(
                detail="You don't have permission to perform this action"
            )

        return current_user

    return dependency


def get_pagination_params(skip: int = 0, limit: int = 100) -> Dict[str, int]:
    """
    Fournit les paramètres de pagination pour les requêtes de liste.

    Args:
        skip: Nombre d'éléments à sauter
        limit: Nombre maximum d'éléments à retourner (max 1000)

    Returns:
        Dict[str, int]: Paramètres de pagination
    """
    # Limiter le nombre maximum d'éléments par page
    limit = min(limit, 1000)
    return {"skip": max(0, skip), "limit": limit}
