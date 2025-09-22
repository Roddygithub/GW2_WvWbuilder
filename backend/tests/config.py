"""Test configuration and settings."""

import os
from typing import Dict, Any

# Test database configuration
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:?cache=shared"
TEST_SYNC_DATABASE_URL = "sqlite:///:memory:?cache=shared"

# Test user credentials
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123",
    "is_active": True,
    "is_superuser": False,
}

# Test role configuration
TEST_ROLE = {
    "name": "test_role",
    "description": "Test Role",
    "permission_level": 1,
    "is_default": False,
}

# Test profession data
TEST_PROFESSION = {
    "name": "Test Profession",
    "description": "A test profession",
    "icon": "test_icon.png",
}

# Test build data
TEST_BUILD = {
    "name": "Test Build",
    "description": "A test build",
    "is_public": True,
    "game_mode": "pve",
}

# Test composition data
TEST_COMPOSITION = {
    "name": "Test Composition",
    "description": "A test composition",
    "squad_size": 10,
    "is_public": True,
}


def get_test_db_url() -> str:
    """Get the test database URL."""
    return os.getenv("TEST_DATABASE_URL", TEST_DATABASE_URL)


def get_test_sync_db_url() -> str:
    """Get the test sync database URL."""
    return os.getenv("TEST_SYNC_DATABASE_URL", TEST_SYNC_DATABASE_URL)


def get_test_settings() -> Dict[str, Any]:
    """Get test settings."""
    return {
        "TESTING": True,
        "DATABASE_URL": get_test_sync_db_url(),
        "ASYNC_SQLALCHEMY_DATABASE_URI": get_test_db_url(),
        "SECRET_KEY": "test-secret-key",
        "ACCESS_TOKEN_EXPIRE_MINUTES": 60,
        "ALGORITHM": "HS256",
    }
