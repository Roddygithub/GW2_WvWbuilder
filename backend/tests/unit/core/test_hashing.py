"""Tests for hashing utilities."""

import pytest
from app.core.hashing import (
    get_password_hash,
    get_password_hash_sha256,
    verify_password,
)


def test_get_password_hash():
    """Test password hashing."""
    password = "secure_password_123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert len(hashed) > 0
    assert isinstance(hashed, str)
    assert hashed.startswith("$2b$")  # bcrypt format


def test_get_password_hash_different_hashes():
    """Test that same password produces different hashes."""
    password = "test_password"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    
    # Hashes should be different due to different salts
    assert hash1 != hash2


def test_verify_password_correct():
    """Test password verification with correct password."""
    password = "my_password_123"
    hashed = get_password_hash(password)
    
    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    """Test password verification with incorrect password."""
    password = "correct_password"
    wrong_password = "wrong_password"
    hashed = get_password_hash(password)
    
    assert verify_password(wrong_password, hashed) is False


def test_verify_password_empty():
    """Test password verification with empty password."""
    hashed = get_password_hash("password")
    
    assert verify_password("", hashed) is False
    assert verify_password(None, hashed) is False


def test_verify_password_none_hash():
    """Test password verification with None hash."""
    assert verify_password("password", None) is False


def test_get_password_hash_empty():
    """Test hashing empty password raises error."""
    with pytest.raises(ValueError):
        get_password_hash("")


def test_get_password_hash_sha256():
    """Test SHA-256 password hashing (backward compatibility)."""
    password = "test_password"
    hashed = get_password_hash_sha256(password)
    
    assert hashed != password
    assert len(hashed) == 64  # SHA-256 produces 64 hex chars
    assert isinstance(hashed, str)


def test_get_password_hash_sha256_deterministic():
    """Test SHA-256 produces same hash for same password."""
    password = "test_password"
    hash1 = get_password_hash_sha256(password)
    hash2 = get_password_hash_sha256(password)
    
    # SHA-256 is deterministic
    assert hash1 == hash2
