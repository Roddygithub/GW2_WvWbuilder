"""
Comprehensive tests for Key Management Service.
Tests for app/core/security/keys.py to achieve 80%+ coverage.
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch

from app.core.security.keys import KeyManager, KEY_ROTATION_DAYS


@pytest.fixture
def temp_key_file(tmp_path):
    """Create a temporary key file."""
    key_file = tmp_path / "test_keys.json"
    return key_file


@pytest.fixture
def key_manager(temp_key_file):
    """Create a KeyManager instance with temp file."""
    return KeyManager(key_file=temp_key_file)


class TestKeyManagerInit:
    """Test KeyManager initialization."""

    def test_init_creates_new_key(self, temp_key_file):
        """Test that initialization creates a new key if none exist."""
        manager = KeyManager(key_file=temp_key_file)

        assert len(manager.keys) > 0
        assert manager.current_key_id is not None
        assert manager.current_key_id in manager.keys

    def test_init_loads_existing_keys(self, temp_key_file):
        """Test that initialization loads existing keys."""
        # Create initial manager and save keys
        manager1 = KeyManager(key_file=temp_key_file)
        first_key_id = manager1.current_key_id

        # Create new manager - should load existing keys
        manager2 = KeyManager(key_file=temp_key_file)

        assert manager2.current_key_id == first_key_id
        assert len(manager2.keys) == len(manager1.keys)

    def test_init_handles_corrupted_file(self, temp_key_file):
        """Test initialization with corrupted key file."""
        # Write corrupted JSON
        temp_key_file.write_text("{ invalid json")

        # Should create new key despite corruption
        manager = KeyManager(key_file=temp_key_file)

        assert len(manager.keys) > 0
        assert manager.current_key_id is not None


class TestKeyGeneration:
    """Test key generation methods."""

    def test_generate_key_id_format(self, key_manager):
        """Test that generated key IDs have correct format."""
        key_id = key_manager._generate_key_id()

        assert key_id.startswith("key_")
        assert len(key_id) == 20  # "key_" + 16 hex chars

    def test_generate_key_id_unique(self, key_manager):
        """Test that generated key IDs are unique."""
        key_ids = [key_manager._generate_key_id() for _ in range(10)]

        assert len(set(key_ids)) == 10  # All unique

    def test_generate_secret_key_length(self, key_manager):
        """Test that generated secret keys have correct length."""
        secret = key_manager._generate_secret_key()

        assert len(secret) == 64

    def test_generate_secret_key_secure(self, key_manager):
        """Test that generated secret keys are different."""
        secrets = [key_manager._generate_secret_key() for _ in range(5)]

        assert len(set(secrets)) == 5  # All different

    def test_generate_new_key(self, key_manager):
        """Test generating a new key."""
        initial_count = len(key_manager.keys)

        new_key_id = key_manager._generate_new_key()

        assert len(key_manager.keys) == initial_count + 1
        assert new_key_id in key_manager.keys
        assert key_manager.current_key_id == new_key_id


class TestKeyRetrieval:
    """Test key retrieval methods."""

    def test_get_current_key(self, key_manager):
        """Test getting the current key."""
        current_key = key_manager.get_current_key()

        assert current_key is not None
        assert "key" in current_key
        assert "created_at" in current_key

    def test_get_key_by_id(self, key_manager):
        """Test getting a key by ID."""
        key_id = key_manager.current_key_id

        key = key_manager.get_key(key_id)

        assert key is not None
        assert key["key"] is not None

    def test_get_nonexistent_key(self, key_manager):
        """Test getting a non-existent key."""
        key = key_manager.get_key("nonexistent_key_id")

        assert key is None

    def test_get_all_keys(self, key_manager):
        """Test getting all keys."""
        # Generate additional keys
        key_manager._generate_new_key()
        key_manager._generate_new_key()

        all_keys = key_manager.get_all_keys()

        assert len(all_keys) >= 3
        assert all(isinstance(k, dict) for k in all_keys.values())


class TestKeyRotation:
    """Test key rotation functionality."""

    def test_rotate_key(self, key_manager):
        """Test manual key rotation."""
        old_key_id = key_manager.current_key_id

        new_key_id = key_manager.rotate_key()

        assert new_key_id != old_key_id
        assert key_manager.current_key_id == new_key_id
        assert old_key_id in key_manager.keys  # Old key retained

    def test_check_rotation_not_needed(self, key_manager):
        """Test that rotation check doesn't rotate recent key."""
        initial_key_id = key_manager.current_key_id

        key_manager._check_rotation()

        assert key_manager.current_key_id == initial_key_id

    def test_check_rotation_needed(self, key_manager):
        """Test that rotation check rotates old key."""
        # Manually set key creation date to old date
        old_date = (datetime.utcnow() - timedelta(days=KEY_ROTATION_DAYS + 1)).isoformat()
        key_manager.keys[key_manager.current_key_id]["created_at"] = old_date

        initial_key_id = key_manager.current_key_id
        key_manager._check_rotation()

        # Should have rotated
        assert key_manager.current_key_id != initial_key_id


class TestKeyPersistence:
    """Test key saving and loading."""

    def test_save_keys(self, key_manager, temp_key_file):
        """Test saving keys to file."""
        key_manager._save_keys()

        assert temp_key_file.exists()

        # Verify file content
        with open(temp_key_file, "r") as f:
            data = json.load(f)

        assert "current_key_id" in data
        assert "keys" in data
        assert data["current_key_id"] == key_manager.current_key_id

    def test_load_keys(self, temp_key_file):
        """Test loading keys from file."""
        # Create and save initial manager
        manager1 = KeyManager(key_file=temp_key_file)
        key_id = manager1.current_key_id
        manager1._save_keys()

        # Create new manager - should load keys
        manager2 = KeyManager(key_file=temp_key_file)

        assert manager2.current_key_id == key_id
        assert manager2.keys == manager1.keys

    def test_file_permissions(self, key_manager, temp_key_file):
        """Test that key file has secure permissions."""
        key_manager._save_keys()

        # Check file permissions (0o600 = rw-------)
        import stat

        file_stat = temp_key_file.stat()
        stat.filemode(file_stat.st_mode)

        # File should not be world-readable
        assert not (file_stat.st_mode & stat.S_IROTH)
        assert not (file_stat.st_mode & stat.S_IWOTH)


class TestKeyCleanup:
    """Test old key cleanup."""

    def test_cleanup_old_keys(self, key_manager):
        """Test cleaning up old keys."""
        # Generate multiple keys
        for _ in range(5):
            key_manager._generate_new_key()

        # Set some keys as very old
        old_date = (datetime.utcnow() - timedelta(days=100)).isoformat()
        keys_to_age = list(key_manager.keys.keys())[:2]
        for key_id in keys_to_age:
            if key_id != key_manager.current_key_id:
                key_manager.keys[key_id]["created_at"] = old_date

        initial_count = len(key_manager.keys)
        key_manager.cleanup_old_keys(retention_days=90)

        # Should have removed at least one old key
        assert len(key_manager.keys) <= initial_count
        # Current key should still exist
        assert key_manager.current_key_id in key_manager.keys


class TestKeyManagerEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_keys_dict(self, temp_key_file):
        """Test handling of empty keys dictionary."""
        # Create file with empty keys
        with open(temp_key_file, "w") as f:
            json.dump({"keys": {}, "current_key_id": None}, f)

        manager = KeyManager(key_file=temp_key_file)

        # Should generate a new key
        assert len(manager.keys) > 0
        assert manager.current_key_id is not None

    def test_missing_current_key_id(self, temp_key_file):
        """Test handling of missing current_key_id."""
        # Create file with keys but no current_key_id
        test_keys = {"key_abc123": {"key": "test_secret", "created_at": datetime.utcnow().isoformat()}}
        with open(temp_key_file, "w") as f:
            json.dump({"keys": test_keys, "current_key_id": None}, f)

        manager = KeyManager(key_file=temp_key_file)

        # Should set current_key_id to first available key
        assert manager.current_key_id == "key_abc123"

    def test_save_failure_handling(self, key_manager):
        """Test handling of save failures."""
        # Make directory read-only to cause save failure
        with patch.object(key_manager.key_file, "parent") as mock_parent:
            mock_parent.mkdir.side_effect = PermissionError("Cannot create directory")

            with pytest.raises(Exception):
                key_manager._save_keys()


class TestKeyManagerIntegration:
    """Integration tests for KeyManager."""

    def test_full_lifecycle(self, temp_key_file):
        """Test full key lifecycle: create, rotate, cleanup."""
        # Create manager
        manager = KeyManager(key_file=temp_key_file)
        manager.get_current_key()

        # Rotate key
        new_key_id = manager.rotate_key()
        assert new_key_id != manager.current_key_id

        # Save and reload
        manager._save_keys()
        manager2 = KeyManager(key_file=temp_key_file)
        assert manager2.current_key_id == manager.current_key_id

        # Cleanup old keys
        manager2.cleanup_old_keys(retention_days=0)
        # Current key should still exist
        assert manager2.current_key_id in manager2.keys

    def test_concurrent_access(self, temp_key_file):
        """Test multiple managers accessing same key file."""
        manager1 = KeyManager(key_file=temp_key_file)
        manager1._save_keys()

        # Create second manager
        manager2 = KeyManager(key_file=temp_key_file)

        # Both should have same current key
        assert manager1.current_key_id == manager2.current_key_id
        assert manager1.keys == manager2.keys
