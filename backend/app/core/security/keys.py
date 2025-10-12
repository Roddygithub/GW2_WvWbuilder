"""
Key Management Service for handling cryptographic keys.

This module provides functionality for generating, storing, and rotating
cryptographic keys used for JWT signing and other security purposes.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import secrets
import string
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)

KEY_FILE = Path("keys.json")
KEY_ROTATION_DAYS = 30
KEY_RETENTION_DAYS = 90


class KeyManager:
    """
    Manages cryptographic keys for the application.

    Handles key generation, rotation, and retrieval with support for
    key versioning and automatic rotation.
    """

    def __init__(self, key_file: Optional[Path] = None):
        """Initialize the key manager."""
        self.key_file = (
            key_file or Path(settings.SECRETS_DIR) / "keys.json" if hasattr(settings, "SECRETS_DIR") else KEY_FILE
        )
        self.keys: Dict[str, Dict] = {}
        self.current_key_id: Optional[str] = None
        self._load_keys()

    def _load_keys(self) -> None:
        """Load keys from the key file."""
        try:
            if self.key_file.exists():
                with open(self.key_file, "r") as f:
                    data = json.load(f)
                    self.keys = data.get("keys", {})
                    self.current_key_id = data.get("current_key_id")

            # Ensure we have at least one key
            if not self.keys:
                self._generate_new_key()
            elif not self.current_key_id or self.current_key_id not in self.keys:
                self.current_key_id = next(iter(self.keys.keys()))

            # Check if current key needs rotation
            self._check_rotation()

        except Exception as e:
            logger.error(f"Failed to load keys: {e}")
            self.keys = {}
            self._generate_new_key()

    def _save_keys(self) -> None:
        """Save keys to the key file."""
        try:
            # Ensure directory exists
            self.key_file.parent.mkdir(parents=True, exist_ok=True)

            # Prepare data for saving
            data = {
                "current_key_id": self.current_key_id,
                "keys": self.keys,
                "updated_at": datetime.utcnow().isoformat(),
            }

            # Save to file with secure permissions
            temp_file = self.key_file.with_suffix(".tmp")
            with open(temp_file, "w") as f:
                json.dump(data, f, indent=2)

            # Atomic write
            temp_file.replace(self.key_file)
            self.key_file.chmod(0o600)  # rw-------

        except Exception as e:
            logger.error(f"Failed to save keys: {e}")
            raise

    def _generate_key_id(self) -> str:
        """Generate a unique key ID."""
        return f"key_{secrets.token_hex(8)}"

    def _generate_secret_key(self) -> str:
        """Generate a secure random secret key."""
        alphabet = string.ascii_letters + string.digits + "-._~"
        return "".join(secrets.choice(alphabet) for _ in range(64))

    def _generate_new_key(self) -> str:
        """Generate a new key and make it current."""
        key_id = self._generate_key_id()
        now = datetime.utcnow()

        self.keys[key_id] = {
            "key": self._generate_secret_key(),
            "created_at": now.isoformat(),
            "expires_at": (now + timedelta(days=KEY_ROTATION_DAYS * 2)).isoformat(),
            "last_rotated": now.isoformat(),
            "is_active": True,
        }

        self.current_key_id = key_id
        self._save_keys()
        return key_id

    def _check_rotation(self) -> None:
        """Check if the current key needs to be rotated."""
        if not self.current_key_id:
            self._generate_new_key()
            return

        current_key = self.keys.get(self.current_key_id, {})
        if not current_key:
            self._generate_new_key()
            return

        last_rotated = datetime.fromisoformat(current_key.get("last_rotated", datetime.utcnow().isoformat()))
        if datetime.utcnow() - last_rotated > timedelta(days=KEY_ROTATION_DAYS):
            self.rotate_keys()

    def rotate_keys(self) -> str:
        """
        Rotate the current key.

        Generates a new key and makes it the current key. The old key is kept
        for a grace period to allow for validation of existing tokens.

        Returns:
            str: The ID of the new current key
        """
        # Generate new key
        new_key_id = self._generate_new_key()

        # Mark old keys for cleanup (they'll be removed after KEY_RETENTION_DAYS)
        now = datetime.utcnow()
        for key_id, key_data in list(self.keys.items()):
            if key_id != new_key_id and key_data.get("is_active", True):
                self.keys[key_id]["is_active"] = False
                self.keys[key_id]["deactivated_at"] = now.isoformat()

        # Clean up old keys
        self._cleanup_old_keys()

        # Save changes
        self.current_key_id = new_key_id
        self._save_keys()

        logger.info(f"Rotated keys. New current key: {new_key_id}")
        return new_key_id

    def _cleanup_old_keys(self) -> None:
        """Remove keys that are no longer needed."""
        now = datetime.utcnow()
        cutoff = now - timedelta(days=KEY_RETENTION_DAYS)

        for key_id in list(self.keys.keys()):
            key_data = self.keys[key_id]
            deactivated_at = key_data.get("deactivated_at")

            # Skip active and current keys
            if key_data.get("is_active", True) or key_id == self.current_key_id:
                continue

            # Remove keys that were deactivated before the cutoff
            if deactivated_at and datetime.fromisoformat(deactivated_at) < cutoff:
                del self.keys[key_id]

    def get_current_key(self) -> Tuple[str, str]:
        """
        Get the current key ID and value.

        Returns:
            Tuple[str, str]: A tuple of (key_id, key_value)
        """
        if not self.current_key_id or self.current_key_id not in self.keys:
            self._generate_new_key()

        return self.current_key_id, self.keys[self.current_key_id]["key"]

    def get_key(self, key_id: str) -> Optional[str]:
        """
        Get a key by ID.

        Args:
            key_id: The ID of the key to retrieve

        Returns:
            Optional[str]: The key value, or None if not found
        """
        key_data = self.keys.get(key_id, {})
        return key_data.get("key") if key_data else None

    def get_all_active_keys(self) -> Dict[str, str]:
        """
        Get all active keys.

        Returns:
            Dict[str, str]: A dictionary mapping key IDs to key values
        """
        return {
            key_id: key_data["key"]
            for key_id, key_data in self.keys.items()
            if key_data.get("is_active", True) or key_id == self.current_key_id
        }


# Global key manager instance
key_manager = KeyManager()


def get_key_manager() -> KeyManager:
    """Get the global key manager instance."""
    return key_manager
