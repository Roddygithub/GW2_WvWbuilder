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

    Args:
        password: The plain text password to hash

    Returns:
        str: The hashed password
    """
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Error hashing password: {str(e)}")
        raise ValueError("Failed to hash password")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to verify against

    Returns:
        bool: True if the password matches, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
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
