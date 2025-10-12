"""
Password Utilities.

This module provides password hashing and verification functionality.
"""

import logging
import hashlib

from passlib.context import CryptContext
from passlib.exc import UnknownHashError

# Configure logging
logger = logging.getLogger(__name__)

# Create a password hashing context
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # Number of hashing rounds
)


def get_password_hash(password: str) -> str:
    """
    Hash a password for storing in the database.

    Bcrypt has a 72-byte limit. For passwords longer than 72 bytes,
    we first hash with SHA-256 to ensure compatibility.

    Args:
        password: The plain text password to hash

    Returns:
        str: The hashed password
    """
    try:
        # Bcrypt has a 72-byte limit, so we pre-hash long passwords with SHA-256
        password_bytes = password.encode("utf-8")
        if len(password_bytes) > 72:
            logger.debug(f"Password exceeds 72 bytes ({len(password_bytes)} bytes), pre-hashing with SHA-256")
            # Use SHA-256 to create a fixed-length hash that's always <72 bytes
            password = hashlib.sha256(password_bytes).hexdigest()
        return pwd_context.hash(password)
    except ValueError as e:
        # Handle bcrypt-specific errors
        if "72 bytes" in str(e):
            logger.warning(f"Bcrypt 72-byte limit hit, using SHA-256 pre-hash: {e}")
            # Fallback: hash with SHA-256 first
            password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
            return pwd_context.hash(password_hash)
        logger.error(f"Error hashing password: {str(e)}")
        raise ValueError("Failed to hash password")
    except Exception as e:
        logger.error(f"Unexpected error hashing password: {str(e)}")
        raise ValueError("Failed to hash password")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.

    Handles both regular passwords and pre-hashed passwords (for >72 bytes).

    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to verify against

    Returns:
        bool: True if the password matches, False otherwise
    """
    try:
        # First try direct verification
        if pwd_context.verify(plain_password, hashed_password):
            return True

        # If password is >72 bytes, try with SHA-256 pre-hash
        if len(plain_password.encode("utf-8")) > 72:
            logger.debug("Password exceeds 72 bytes, trying SHA-256 pre-hash")
            prehashed = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
            return pwd_context.verify(prehashed, hashed_password)

        return False
    except UnknownHashError:
        logger.warning("Attempted to verify password with unknown hash")
        return False
    except Exception as e:
        logger.error(f"Error verifying password: {str(e)}")
        return False


def get_password_hash_sha256(password: str) -> str:
    """
    Hash a password using SHA-256.

    This is a legacy hashing function that should only be used for compatibility
    with older password hashes. New passwords should use get_password_hash()
    which uses bcrypt.

    Args:
        password: The plain text password to hash

    Returns:
        str: The SHA-256 hashed password as a hex string
    """
    try:
        # Encode the password as UTF-8 and hash it using SHA-256
        return hashlib.sha256(password.encode("utf-8")).hexdigest()
    except Exception as e:
        logger.error(f"Error hashing password with SHA-256: {str(e)}")
        raise ValueError("Failed to hash password with SHA-256")


def generate_password_reset_token(email: str) -> str:
    """
    Generate a password reset token for the given email.

    Args:
        email: The user's email address

    Returns:
        str: A JWT token for password reset
    """
    from .jwt import create_password_reset_token

    return create_password_reset_token(email)


def verify_password_reset_token(token: str) -> str:
    """
    Verify a password reset token and return the email.

    Args:
        token: The password reset token to verify

    Returns:
        str: The email address if valid, None otherwise
    """
    from .jwt import verify_password_reset_token as jwt_verify

    try:
        payload = jwt_verify(token)
        return payload.get("sub") if payload else None
    except Exception as e:
        logger.error(f"Error verifying password reset token: {str(e)}")
        return None


def is_password_strong(password: str) -> bool:
    """
    Check if a password meets security requirements.

    Args:
        password: The password to check

    Returns:
        bool: True if the password meets the requirements, False otherwise
    """
    if len(password) < 8:
        return False

    # Check for at least one digit
    if not any(char.isdigit() for char in password):
        return False

    # Check for at least one uppercase letter
    if not any(char.isupper() for char in password):
        return False

    # Check for at least one lowercase letter
    if not any(char.islower() for char in password):
        return False

    # Check for at least one special character
    special_chars = "!@#$%^&*()-_=+[]{}|;:,.<>?/`~"
    if not any(char in special_chars for char in password):
        return False

    return True
