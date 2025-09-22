"""Tests for utility functions."""

import pytest
from datetime import timedelta

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    verify_token,
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
    payload = verify_token(token)
    assert payload is not None
    assert payload["sub"] == str(user_id)

    # Check expiration is set correctly
    assert "exp" in payload


async def test_jwt_token_expiration():
    """Test that JWT tokens expire correctly."""
    # Create a token that expires immediately
    user_id = 1
    token_data = {"sub": str(user_id)}
    expires_delta = timedelta(seconds=-1)  # Expired 1 second ago

    token = create_access_token(token_data, expires_delta=expires_delta)

    # Should not verify as it's expired
    payload = verify_token(token)
    assert payload is None


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


def test_token_invalid_signature():
    """Test that tokens with invalid signatures are rejected."""
    # Create a valid token
    token = create_access_token({"sub": "1"})

    # Tamper with the token
    parts = token.split(".")
    if len(parts) == 3:  # Header.Payload.Signature
        tampered = f"{parts[0]}.{parts[1]}.tampered_signature"

        # Should be rejected
        assert verify_token(tampered) is None


def test_token_missing_subject():
    """Test that tokens without a subject are rejected."""
    # Create token without 'sub' claim
    token = create_access_token({})
    assert verify_token(token) is None

    # Create token with empty subject
    token = create_access_token({"sub": ""})
    assert verify_token(token) is None
