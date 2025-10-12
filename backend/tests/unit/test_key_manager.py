"""Unit tests for the KeyManager class."""

import os
import json
import tempfile
import pytest
from datetime import datetime, timedelta
from pathlib import Path

from app.core.security.keys import KeyManager

# Test data
TEST_KEY_ID = "test_key_123"
TEST_KEY = "test_secret_key_1234567890_abcdefghijklmnopqrstuvwxyz"


@pytest.fixture
def temp_key_file():
    """Create a temporary key file for testing."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
        yield Path(f.name)

    # Cleanup
    if os.path.exists(f.name):
        os.unlink(f.name)


def test_key_manager_initialization(temp_key_file):
    """Test that KeyManager initializes correctly with no existing key file."""
    # Ensure file doesn't exist
    if temp_key_file.exists():
        temp_key_file.unlink()

    # Initialize with non-existent file
    manager = KeyManager(key_file=temp_key_file)

    # Should have created a new key
    assert manager.current_key_id is not None
    assert manager.keys
    assert temp_key_file.exists()


def test_key_manager_load_existing(temp_key_file):
    """Test loading existing keys from a file."""
    # Create test key file
    test_data = {
        "current_key_id": TEST_KEY_ID,
        "keys": {
            TEST_KEY_ID: {
                "key": TEST_KEY,
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(days=60)).isoformat(),
                "last_rotated": datetime.utcnow().isoformat(),
                "is_active": True,
            }
        },
        "updated_at": datetime.utcnow().isoformat(),
    }

    with open(temp_key_file, "w") as f:
        json.dump(test_data, f)

    # Load the key file
    manager = KeyManager(key_file=temp_key_file)

    # Verify the key was loaded
    assert manager.current_key_id == TEST_KEY_ID
    assert TEST_KEY_ID in manager.keys
    assert manager.keys[TEST_KEY_ID]["key"] == TEST_KEY


def test_key_rotation(temp_key_file):
    """Test key rotation functionality."""
    manager = KeyManager(key_file=temp_key_file)
    old_key_id = manager.current_key_id
    old_key = manager.keys[old_key_id]["key"]

    # Rotate keys
    new_key_id = manager.rotate_keys()

    # Verify rotation
    assert new_key_id != old_key_id
    assert manager.current_key_id == new_key_id
    assert not manager.keys[old_key_id]["is_active"]
    assert manager.keys[new_key_id]["is_active"]
    assert manager.keys[new_key_id]["key"] != old_key

    # Verify old key is still retrievable
    assert manager.get_key(old_key_id) == old_key


def test_get_current_key(temp_key_file):
    """Test getting the current key."""
    manager = KeyManager(key_file=temp_key_file)
    key_id, key = manager.get_current_key()

    assert key_id == manager.current_key_id
    assert key == manager.keys[key_id]["key"]


def test_get_all_active_keys(temp_key_file):
    """Test getting all active keys."""
    manager = KeyManager(key_file=temp_key_file)

    # Add an inactive key
    inactive_key_id = "inactive_key_123"
    manager.keys[inactive_key_id] = {
        "key": "inactive_key_value",
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(days=60)).isoformat(),
        "last_rotated": datetime.utcnow().isoformat(),
        "is_active": False,
        "deactivated_at": datetime.utcnow().isoformat(),
    }

    active_keys = manager.get_all_active_keys()

    # Should only return the current key (active)
    assert len(active_keys) == 1
    assert manager.current_key_id in active_keys
    assert inactive_key_id not in active_keys


def test_cleanup_old_keys(temp_key_file):
    """Test cleanup of old, inactive keys."""
    manager = KeyManager(key_file=temp_key_file)

    # Add an old, inactive key
    old_key_id = "old_key_123"
    manager.keys[old_key_id] = {
        "key": "old_key_value",
        "created_at": (datetime.utcnow() - timedelta(days=100)).isoformat(),
        "expires_at": (datetime.utcnow() - timedelta(days=40)).isoformat(),
        "last_rotated": (datetime.utcnow() - timedelta(days=100)).isoformat(),
        "is_active": False,
        "deactivated_at": (datetime.utcnow() - timedelta(days=91)).isoformat(),  # Older than 90 days
    }

    # Add a recently deactivated key (should be kept)
    recent_key_id = "recent_key_123"
    manager.keys[recent_key_id] = {
        "key": "recent_key_value",
        "created_at": (datetime.utcnow() - timedelta(days=10)).isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(days=50)).isoformat(),
        "last_rotated": (datetime.utcnow() - timedelta(days=10)).isoformat(),
        "is_active": False,
        "deactivated_at": (datetime.utcnow() - timedelta(days=5)).isoformat(),  # Less than 90 days
    }

    # Force cleanup
    manager._cleanup_old_keys()

    # Verify old key was removed, recent key was kept
    assert old_key_id not in manager.keys
    assert recent_key_id in manager.keys
    assert manager.current_key_id in manager.keys  # Current key should still be there
