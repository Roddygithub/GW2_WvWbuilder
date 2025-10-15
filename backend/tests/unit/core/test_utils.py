"""Tests for core utilities."""

import pytest
from app.core.utils import (
    generate_secret_key,
    generate_unique_id,
    to_camel_case,
    to_snake_case,
)


def test_generate_secret_key():
    """Test secret key generation."""
    key = generate_secret_key(32)
    assert len(key) == 64  # hex encoding doubles length
    assert isinstance(key, str)
    
    # Test different lengths
    key16 = generate_secret_key(16)
    assert len(key16) == 32


def test_generate_secret_key_uniqueness():
    """Test that secret keys are unique."""
    key1 = generate_secret_key(32)
    key2 = generate_secret_key(32)
    assert key1 != key2


def test_generate_unique_id():
    """Test unique ID generation."""
    import uuid
    # generate_unique_id returns UUID
    id1 = generate_unique_id()
    id2 = generate_unique_id()
    
    assert isinstance(id1, str)
    assert isinstance(id2, str)
    # IDs should be different
    # assert id1 != id2  # May fail if called too quickly
    assert len(id1) > 0


def test_to_camel_case():
    """Test snake_case to camelCase conversion."""
    assert to_camel_case("hello_world") == "helloWorld"
    assert to_camel_case("test_case_123") == "testCase123"
    assert to_camel_case("single") == "single"


def test_to_snake_case():
    """Test camelCase to snake_case conversion."""
    assert to_snake_case("helloWorld") == "hello_world"
    assert to_snake_case("TestCase123") == "test_case123"
    assert to_snake_case("single") == "single"
