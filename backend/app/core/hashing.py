"""
Password hashing utilities.

This module provides secure password hashing and verification using bcrypt.
"""

import logging
import hashlib
from typing import Optional
import bcrypt

# Configure logging
logger = logging.getLogger(__name__)


def verify_password(
    plain_password: Optional[str], hashed_password: Optional[str]
) -> bool:
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
        # Handle long passwords (>72 bytes) with SHA-256 pre-hash
        password_bytes = plain_password.encode("utf-8")
        if len(password_bytes) > 72:
            logger.debug("Password exceeds 72 bytes, using SHA-256 pre-hash")
            plain_password = hashlib.sha256(password_bytes).hexdigest()
            password_bytes = plain_password.encode("utf-8")

        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception as e:
        logger.error(f"Error verifying password: {str(e)}")
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
        # Handle long passwords (>72 bytes) with SHA-256 pre-hash
        password_bytes = password.encode("utf-8")
        if len(password_bytes) > 72:
            logger.debug(
                f"Password exceeds 72 bytes ({len(password_bytes)} bytes), pre-hashing with SHA-256"
            )
            password = hashlib.sha256(password_bytes).hexdigest()
            password_bytes = password.encode("utf-8")

        # Hash with bcrypt (12 rounds)
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode("utf-8")
    except Exception as e:
        logger.error(f"Unexpected error hashing password: {str(e)}", exc_info=True)
        raise ValueError("Failed to hash password") from e


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
