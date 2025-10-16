"""
JWT Authentication Utilities.

This module provides JWT token creation, validation, and management.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING

# Définir les types de base pour éviter les problèmes d'importation circulaire
if TYPE_CHECKING:

    # Définir des types de base sûrs
    StrType = str
    IntType = int
    AnyType = Any
else:
    # En mode d'exécution normal, utiliser les types natifs
    StrType = str
    IntType = int
    AnyType = Any

# Importer les autres dépendances
try:
    from fastapi import Depends, HTTPException, Request, status
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
    from jose import JWTError as JoseJWTError
    from jose import jwt as jose_jwt
    from jose.exceptions import ExpiredSignatureError, JWTClaimsError
    import secrets
    from pydantic import BaseModel
    from app.core.config import settings

    # Importations réussies
except Exception as e:
    print(f"ERREUR lors de l'importation: {e}")
    raise

# Configure logging
logger = logging.getLogger(__name__)

# JWT Bearer token scheme
security = HTTPBearer()

# Token types
TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"
TOKEN_TYPE_RESET = "reset"

# JWT Token prefix for HTTP headers
JWT_TOKEN_PREFIX = "Bearer"

# Use settings directly instead of creating module-level variables
# This ensures we always get the latest values from settings

# Types des constantes JWT


# Debug: Afficher les valeurs des variables d'environnement et de configuration
def log_jwt_config() -> None:
    print("=== Configuration JWT ===")
    print(f"JWT_ALGORITHM: {settings.JWT_ALGORITHM}")
    print(
        f"JWT_ACCESS_TOKEN_EXPIRE_MINUTES: {settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES}"
    )
    print(
        f"JWT_REFRESH_TOKEN_EXPIRE_MINUTES: {settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES}"
    )
    print(
        f"JWT_SECRET_KEY: {'*' * 8} (longueur: {len(settings.JWT_SECRET_KEY) if settings.JWT_SECRET_KEY else 0})"
    )
    print(
        f"JWT_REFRESH_SECRET_KEY: {'*' * 8} (longueur: {len(settings.JWT_REFRESH_SECRET_KEY) if settings.JWT_REFRESH_SECRET_KEY else 0})"
    )
    print(f"Type de JWT_SECRET_KEY: {type(settings.JWT_SECRET_KEY)}")
    print(f"Type de JWT_ALGORITHM: {type(settings.JWT_ALGORITHM)}")
    print("=== Fin de la configuration JWT ===\n")


# Appeler la fonction de log après la définition de toutes les variables (désactivé pour les tests)


class JWTError(Exception):
    """Base JWT exception."""

    pass


class JWTExpiredSignatureError(JWTError):
    """Raised when a token has expired."""

    pass


class JWTInvalidTokenError(JWTError):
    """Raised when a token is invalid."""

    pass


class TokenData(BaseModel):
    """Token data model."""

    sub: str
    scopes: List[str] = []
    type: Optional[str] = None


def create_token(
    subject,  # type: Union[str, int]
    token_type=TOKEN_TYPE_ACCESS,  # type: str
    expires_delta=None,  # type: Optional[timedelta]
    **kwargs,  # type: Any
):
    # type: (...) -> str
    """
    Create a new JWT token.

    Args:
        subject: The subject of the token (usually user ID or email)
        token_type: Type of token (access, refresh, reset)
        expires_delta: Optional expiration time delta
        **kwargs: Additional claims to include in the token

    Returns:

    Raises:
        JWTError: If there's an error creating the token
    """
    try:
        # Vérification des types de manière plus robuste
        if not isinstance(subject, (str, int)):
            raise JWTError(
                f"Subject must be a string or integer, got {type(subject).__name__}"
            )

        # Convertir le sujet en chaîne pour assurer la cohérence
        subject_str = str(subject)

        # Valider le type de token
        if not isinstance(token_type, str) and token_type is not None:
            raise JWTError(
                f"Token type must be a string or None, got {type(token_type).__name__}"
            )

        # Valider expires_delta si fourni
        if expires_delta is not None and not isinstance(expires_delta, timedelta):
            raise JWTError(
                f"expires_delta must be a timedelta object or None, got {type(expires_delta).__name__}"
            )

        # Valider le type de token
        valid_token_types = (TOKEN_TYPE_ACCESS, TOKEN_TYPE_REFRESH, TOKEN_TYPE_RESET)
        if token_type is not None and token_type not in valid_token_types:
            raise JWTError(
                f"Invalid token type: {token_type}. Must be one of {valid_token_types}"
            )

        # Sélectionner la clé secrète appropriée en fonction du type de token
        secret_key = (
            settings.JWT_REFRESH_SECRET_KEY
            if token_type == TOKEN_TYPE_REFRESH
            else settings.JWT_SECRET_KEY
        )

        if not secret_key:
            raise JWTError(f"No secret key configured for token type: {token_type}")

        # Encoder la clé secrète si c'est une chaîne
        if isinstance(secret_key, str):
            secret_key = secret_key.encode("utf-8")

        # Définir le temps d'expiration
        now = datetime.utcnow()
        if expires_delta:
            expire = now + expires_delta
        elif token_type == TOKEN_TYPE_ACCESS:
            expire = now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        elif token_type == TOKEN_TYPE_REFRESH:
            expire = now + timedelta(minutes=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES)
        else:  # Valeur par défaut pour les autres types de tokens (par exemple, reset)
            expire = now + timedelta(hours=1)

        # Préparer les données du token
        to_encode = {
            "sub": subject_str,
            "type": token_type,
            "exp": expire,
            "iat": now,
            "jti": secrets.token_hex(16),  # Identifiant unique
        }

        # Ajouter l'émetteur et l'audience s'ils sont définis dans les paramètres
        if hasattr(settings, "JWT_ISSUER") and settings.JWT_ISSUER:
            to_encode["iss"] = settings.JWT_ISSUER
        if hasattr(settings, "JWT_AUDIENCE") and settings.JWT_AUDIENCE:
            to_encode["aud"] = settings.JWT_AUDIENCE

        # Ajouter les revendications supplémentaires
        to_encode.update(kwargs)

        # Convertir les objets datetime en timestamps
        if "exp" in to_encode and hasattr(to_encode["exp"], "timestamp"):
            to_encode["exp"] = int(to_encode["exp"].timestamp())
        if "iat" in to_encode and hasattr(to_encode["iat"], "timestamp"):
            to_encode["iat"] = int(to_encode["iat"].timestamp())

        # Encoder et retourner le token
        return jose_jwt.encode(to_encode, secret_key, algorithm=settings.JWT_ALGORITHM)

    except Exception as e:
        error_msg = f"Erreur lors de la création du token: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise JWTError(error_msg) from e


def decode_token(
    token: str,
    token_type: Optional[str] = None,
    leeway: int = 0,
) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.

    Args:
        token: The JWT token to decode
        token_type: Expected token type (access, refresh, etc.)
        leeway: Leeway in seconds for expiration validation

    Returns:
        Dict[str, Any]: The decoded token payload

    Raises:
        JWTExpiredSignatureError: If the token has expired
        JWTInvalidTokenError: If the token is invalid
    """
    try:
        if not token:
            raise JWTInvalidTokenError("No token provided")

        # Get the appropriate secret key based on token type
        if token_type == TOKEN_TYPE_REFRESH:
            secret_key = settings.JWT_REFRESH_SECRET_KEY
        else:
            secret_key = settings.JWT_SECRET_KEY

        # Ensure secret_key is a string and encode it if it's not already bytes
        if not secret_key:
            raise JWTInvalidTokenError("No secret key configured")

        if isinstance(secret_key, str):
            secret_key = secret_key.encode("utf-8")

        # Prepare options for token validation
        options = {
            "verify_signature": True,
            "verify_exp": True,
            "verify_iss": hasattr(settings, "JWT_ISSUER") and bool(settings.JWT_ISSUER),
            "verify_aud": hasattr(settings, "JWT_AUDIENCE")
            and bool(settings.JWT_AUDIENCE),
            "verify_iat": True,
            "verify_nbf": False,
            "leeway": leeway,
        }

        # Get issuer and audience from settings if they exist
        issuer = getattr(settings, "JWT_ISSUER", None)
        audience = getattr(settings, "JWT_AUDIENCE", None)

        # Log debug information
        logger.debug(f"Decoding token with options: {options}")
        logger.debug(f"Issuer: {issuer}, Audience: {audience}")

        # Decode the token
        payload = jose_jwt.decode(
            token=token,
            key=secret_key,
            algorithms=[settings.JWT_ALGORITHM],
            options=options,
            issuer=issuer,
            audience=audience,
        )

        # Verify token type if specified
        if token_type and payload.get("type") != token_type:
            raise JWTInvalidTokenError(
                f"Invalid token type: expected {token_type}, got {payload.get('type')}"
            )

        return payload

    except ExpiredSignatureError as e:
        logger.error(f"Token has expired: {str(e)}", exc_info=True)
        raise JWTExpiredSignatureError("Token has expired") from e
    except JWTClaimsError as e:
        logger.error(f"Invalid token claims: {str(e)}", exc_info=True)
        raise JWTInvalidTokenError(f"Invalid token claims: {str(e)}") from e
    except JoseJWTError as e:
        logger.error(f"JWT error: {str(e)}", exc_info=True)
        raise JWTInvalidTokenError(f"Invalid token: {str(e)}") from e
    except Exception as e:
        logger.error(f"Unexpected error decoding token: {str(e)}", exc_info=True)
        raise JWTInvalidTokenError("Failed to decode token") from e


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    """
    Dependency to get the current user from a JWT token.

    Args:
        credentials: The HTTP authorization credentials

    Returns:
        Dict[str, Any]: The decoded token payload with user information

    Raises:
        HTTPException: If the token is invalid, expired, or missing
    """
    if not credentials or not credentials.scheme.lower() == "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme. Use Bearer authentication.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing access token",
            headers={"WWW-Authenticate": f"{JWT_TOKEN_PREFIX}"},
        )

    try:
        token = credentials.credentials
        payload = decode_token(token, token_type=TOKEN_TYPE_ACCESS)
        return payload

    except JWTExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token has expired",
            headers={"WWW-Authenticate": f'{JWT_TOKEN_PREFIX} error="invalid_token"'},
        )
    except JWTInvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": f'{JWT_TOKEN_PREFIX} error="invalid_token"'},
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while validating the token",
        )


def create_access_token(
    subject: Union[str, int],
    expires_delta: Optional[timedelta] = None,
    **kwargs: Any,
) -> str:
    """
    Create a new access token.

    Args:
        subject: The subject of the token (usually user ID or email)
        expires_delta: Optional expiration time delta
        **kwargs: Additional claims to include in the token

    Returns:
        str: The encoded JWT access token
    """
    logger.debug(f"Creating access token for subject: {subject}")
    logger.debug(
        f"JWT_ACCESS_TOKEN_EXPIRE_MINUTES: {settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES}"
    )
    logger.debug(f"JWT_ALGORITHM: {settings.JWT_ALGORITHM}")
    logger.debug(f"JWT_SECRET_KEY: {settings.JWT_SECRET_KEY}")

    if not expires_delta:
        expires_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    logger.debug(f"Using expires_delta: {expires_delta}")

    try:
        token = create_token(
            subject=subject,
            token_type=TOKEN_TYPE_ACCESS,
            expires_delta=expires_delta,
            **kwargs,
        )
        logger.debug("Access token created successfully")
        return token
    except Exception as e:
        logger.error(f"Error creating access token: {str(e)}", exc_info=True)
        raise


def create_refresh_token(
    subject: Union[str, int],
    expires_delta: Optional[timedelta] = None,
    **kwargs: Any,
) -> str:
    """
    Create a new refresh token.

    Args:
        subject: The subject of the token (usually user ID or email)
        expires_delta: Optional expiration time delta
        **kwargs: Additional claims to include in the token

    Returns:
        str: The encoded JWT refresh token
    """
    if not expires_delta:
        expires_delta = timedelta(minutes=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES)

    return create_token(
        subject=subject,
        token_type=TOKEN_TYPE_REFRESH,
        expires_delta=expires_delta,
        **kwargs,
    )


def create_password_reset_token(
    email: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a password reset token.

    Args:
        email: The user's email address
        expires_delta: Optional expiration time delta (default: 1 hour)

    Returns:
        str: JWT token for password reset

    Raises:
        JWTError: If there's an error creating the token
    """
    if not email:
        raise ValueError("Email is required for password reset token")

    if not expires_delta:
        expires_delta = timedelta(hours=1)

    try:
        return create_token(
            subject=email,
            token_type=TOKEN_TYPE_RESET,
            expires_delta=expires_delta,
            scope="password_reset",
        )
    except Exception as e:
        raise JWTError(f"Error creating password reset token: {str(e)}")


def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Dependency to get the current active user.

    Args:
        current_user: The current user from the JWT token

    Returns:
        Dict[str, Any]: The current user if active

    Raises:
        HTTPException: If the user is not active
    """
    if not current_user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


def get_current_active_superuser(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Dependency to get the current active superuser.

    Args:
        current_user: The current user from the JWT token

    Returns:
        Dict[str, Any]: The current user if superuser

    Raises:
        HTTPException: If the user is not a superuser
    """
    if not current_user.get("is_superuser", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode an access token.

    Args:
        token: The access token to verify

    Returns:
        Optional[Dict[str, Any]]: The decoded token payload, or None if invalid
    """
    try:
        if not token:
            return None
        payload = decode_token(token, token_type=TOKEN_TYPE_ACCESS)
        return payload
    except (JWTExpiredSignatureError, JWTInvalidTokenError):
        return None
    except Exception:
        return None


def verify_refresh_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode a refresh token.

    Args:
        token: The refresh token to verify

    Returns:
        Dict[str, Any]: The decoded token payload

    Raises:
        JWTExpiredSignatureError: If the token has expired
        JWTInvalidTokenError: If the token is invalid or not a refresh token
    """
    try:
        payload = decode_token(token, token_type=TOKEN_TYPE_REFRESH)
        return payload
    except JWTExpiredSignatureError:
        raise JWTExpiredSignatureError("Refresh token has expired")
    except JWTError as e:
        raise JWTInvalidTokenError(f"Invalid refresh token: {str(e)}")


def verify_password_reset_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode a password reset token.

    Args:
        token: The password reset token to verify

    Returns:
        Dict[str, Any]: The decoded token payload with email in the 'sub' field

    Raises:
        JWTExpiredSignatureError: If the token has expired
        JWTInvalidTokenError: If the token is invalid or not a password reset token
    """
    try:
        if not token:
            logger.warning("No token provided")
            raise JWTInvalidTokenError("No token provided")

        # Decode the token
        payload = decode_token(token, token_type=TOKEN_TYPE_RESET)

        # Verify the token has an email as subject
        email = payload.get("sub")
        if not email or "@" not in email:
            logger.warning("Invalid email in token")
            raise JWTInvalidTokenError("Invalid email in token")

        # Verify the purpose is password reset
        if payload.get("scope") != "password_reset":
            logger.warning("Invalid token scope")
            raise JWTInvalidTokenError("Invalid token scope")

        return payload

    except JWTExpiredSignatureError as e:
        logger.warning("Password reset token expired")
        raise JWTExpiredSignatureError("Password reset token has expired") from e
    except JWTInvalidTokenError:
        logger.warning("Invalid password reset token")
        raise
    except Exception as e:
        logger.error("Error verifying password reset token", exc_info=True)
        raise JWTInvalidTokenError("Failed to verify password reset token") from e


def get_token_from_request(request: Request) -> Optional[str]:
    """
    Extract JWT token from the request.

    Args:
        request: The FastAPI request object

    Returns:
        Optional[str]: The JWT token if found, None otherwise
    """
    # Check Authorization header first
    authorization = request.headers.get("Authorization")
    if authorization and authorization.lower().startswith("bearer "):
        return authorization.split(" ")[1]

    # Check for token in query parameters
    token = request.query_params.get("token")
    if token:
        return token

    # Check for token in cookies
    token = request.cookies.get("access_token")
    if token:
        return token

    return None
