"""Tests for hashing utilities."""

import pytest
from app.core.hashing import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)


def test_hash_password():
    """Test password hashing."""
    password = "secure_password_123"
    hashed = hash_password(password)
    
    assert hashed != password
    assert len(hashed) > 0
    assert isinstance(hashed, str)


def test_hash_password_different_hashes():
    """Test that same password produces different hashes."""
    password = "test_password"
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    
    # Hashes should be different due to salt
    assert hash1 != hash2


def test_verify_password_correct():
    """Test password verification with correct password."""
    password = "my_password_123"
    hashed = hash_password(password)
    
    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    """Test password verification with incorrect password."""
    password = "correct_password"
    wrong_password = "wrong_password"
    hashed = hash_password(password)
    
    assert verify_password(wrong_password, hashed) is False


def test_verify_password_empty():
    """Test password verification with empty password."""
    hashed = hash_password("password")
    
    assert verify_password("", hashed) is False


def test_create_access_token():
    """Test access token creation."""
    data = {"sub": "user@example.com", "user_id": 1}
    token = create_access_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_create_access_token_with_expiry():
    """Test access token with custom expiry."""
    from datetime import timedelta
    
    data = {"sub": "user@example.com"}
    token = create_access_token(data, expires_delta=timedelta(minutes=30))
    
    assert token is not None
    assert isinstance(token, str)


def test_create_refresh_token():
    """Test refresh token creation."""
    data = {"sub": "user@example.com", "user_id": 1}
    token = create_refresh_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_tokens_are_different():
    """Test that access and refresh tokens are different."""
    data = {"sub": "user@example.com"}
    access_token = create_access_token(data)
    refresh_token = create_refresh_token(data)
    
    assert access_token != refresh_token
