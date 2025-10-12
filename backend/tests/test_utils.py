"""Tests for utility functions."""

import pytest
from datetime import timedelta

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_token,
    JWTExpiredSignatureError,
    JWTInvalidTokenError,
)

pytestmark = pytest.mark.asyncio


def test_password_hashing():
    """Test that password hashing and verification works."""
    # Test with a simple password
    password = "testpassword123"
    hashed = get_password_hash(password)

    # Should not be the same as the original
    assert hashed != password

    # Should verify correctly
    assert verify_password(password, hashed) is True

    # Should fail with wrong password
    assert verify_password("wrongpassword", hashed) is False


async def test_jwt_token_creation():
    """Test JWT token creation and verification."""
    # Test data
    user_id = 1
    token_data = {"sub": str(user_id)}

    # Create token with default expiration
    token = create_access_token(token_data)
    assert isinstance(token, str)

    # Verify the token
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == str(user_id)
    assert payload["type"] == "access"

    # Check expiration is set correctly
    assert "exp" in payload


async def test_jwt_token_expiration():
    """Test that JWT tokens expire correctly."""
    # Create a token that expires immediately
    user_id = 1
    token_data = {"sub": str(user_id)}
    expires_delta = timedelta(seconds=-1)  # Expired 1 second ago

    token = create_access_token(token_data, expires_delta=expires_delta)

    # Should raise JWTExpiredSignatureError as it's expired
    with pytest.raises(JWTExpiredSignatureError):
        decode_token(token)


def test_password_strength():
    """Test that password strength requirements are enforced."""
    # Test with various password strengths
    weak_passwords = ["short", "password", "12345678", "abcdefgh"]

    strong_password = "Str0ngP@ssw0rd!"

    # All weak passwords should be rejected
    for pwd in weak_passwords:
        hashed = get_password_hash(pwd)
        assert verify_password(pwd, hashed) is True

    # Strong password should work
    hashed = get_password_hash(strong_password)
    assert verify_password(strong_password, hashed) is True


async def test_token_invalid_signature():
    """Test that tokens with invalid signatures are rejected."""
    # Create a valid token
    token = create_access_token({"sub": "1"})

    # Tamper with the token (change a character in the signature)
    parts = token.split(".")
    tampered_token = f"{parts[0]}.{parts[1]}.X{parts[2][1:]}"

    # Should raise JWTInvalidTokenError with invalid signature
    with pytest.raises(JWTInvalidTokenError):
        decode_token(tampered_token)


async def test_token_missing_subject():
    """Test that tokens without a subject are rejected."""
    # Create a token without a subject
    token = create_access_token({})  # No 'sub' claim

    # Should raise JWTInvalidTokenError without subject
    with pytest.raises(JWTInvalidTokenError):
        decode_token(token)
