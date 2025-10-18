"""
Security utilities for the application.

This module provides security-related functionality including:
- JWT token handling
- Password hashing and verification
- Authentication utilities
"""

from .jwt import (
    create_token,
    decode_token,
    verify_token,
    get_current_user,
    get_current_active_user,
    get_current_active_superuser,
    create_access_token,
    create_refresh_token,
    create_password_reset_token,
    verify_refresh_token,
    verify_password_reset_token as jwt_verify_password_reset_token,
    get_token_from_request,
    oauth2_scheme,
    JWTError,
    JWTExpiredSignatureError,
    JWTInvalidTokenError,
    TOKEN_TYPE_ACCESS,
    TOKEN_TYPE_REFRESH,
    TOKEN_TYPE_RESET,
)
from .password_utils import (
    get_password_hash,
    get_password_hash_sha256,
    verify_password,
    is_password_strong,
    generate_password_reset_token,
    verify_password_reset_token,
)

# Re-export key components
__all__ = [
    # JWT
    "create_token",
    "decode_token",
    "verify_token",
    "get_current_user",
    "get_current_active_user",
    "get_current_active_superuser",
    "create_access_token",
    "create_refresh_token",
    "create_password_reset_token",
    "verify_refresh_token",
    "get_token_from_request",
    "oauth2_scheme",
    # JWT Types and Exceptions
    "JWTError",
    "JWTExpiredSignatureError",
    "JWTInvalidTokenError",
    "TOKEN_TYPE_ACCESS",
    "TOKEN_TYPE_REFRESH",
    "TOKEN_TYPE_RESET",
    # Password utilities
    "verify_password",
    "get_password_hash",
    "get_password_hash_sha256",
    "is_password_strong",
    "generate_password_reset_token",
    "verify_password_reset_token",
    "pwd_context",
]
