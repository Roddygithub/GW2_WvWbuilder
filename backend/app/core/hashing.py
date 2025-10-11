"""
Password hashing utilities.

This module provides secure password hashing and verification using bcrypt.
"""

import logging
from typing import Optional

from passlib.context import CryptContext
from passlib.exc import UnknownHashError

# Configure logging
logger = logging.getLogger(__name__)

# Configure password hashing context
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    # Additional security parameters
    bcrypt__rounds=12,  # Number of hashing rounds (increased for better security)
    bcrypt__ident="2b",  # Use the latest bcrypt version
)


def verify_password(plain_password: Optional[str], hashed_password: Optional[str]) -> bool:
    """Verify if the provided plain password matches the hashed password.

    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to compare against

    Returns:
        bool: True if the password matches, False otherwise

    Examples:
        >>> verify_password("my_password", "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW")
        True
    """
    if not plain_password or not hashed_password:
        logger.warning("Missing password or hash for verification")
        return False

    try:
        return pwd_context.verify(plain_password, hashed_password)
    except (ValueError, TypeError, UnknownHashError) as e:
        logger.warning(f"Password verification failed: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during password verification: {str(e)}", exc_info=True)
        return False


def get_password_hash(password: str) -> str:
    """Generate a secure hash of the password.

    Args:
        password: The plain text password to hash

    Returns:
        str: The hashed password

    Raises:
        ValueError: If the password is empty or invalid

    Examples:
        >>> hashed = get_password_hash("my_secure_password")
    """
    if not password:
        raise ValueError("Password cannot be empty")

    try:
        return pwd_context.hash(password)
    except (ValueError, TypeError) as e:
        logger.error(f"Failed to hash password: {str(e)}")
        raise ValueError("Invalid password format") from e
    except Exception as e:
        logger.error(f"Unexpected error hashing password: {str(e)}", exc_info=True)
        raise


# Keep for backward compatibility
def get_password_hash_sha256(password: str) -> str:
    """Generate a SHA-256 hash of the password (for backward compatibility).

    WARNING: This method is less secure than bcrypt and is only maintained
    for backward compatibility. Prefer get_password_hash() for new code.

    Args:
        password: The plain text password to hash

    Returns:
        str: The hex-encoded SHA-256 hash of the password
    """
    import hashlib

    if not password:
        raise ValueError("Password cannot be empty")

    try:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()
    except Exception as e:
        logger.error(f"Failed to generate SHA-256 hash: {str(e)}")
        raise
    return hashlib.sha256(password.encode()).hexdigest()
