"""
Core functionality for the application.

This module exports core components like configurations, security, and utilities.
"""

from .config import settings
from .database import (
    AsyncSessionLocal,
    engine,
    get_db,
    transaction,
    Transaction,
    close_db,
    init_db,
    TestSessionLocal,
    TestAsyncSessionLocal,
    get_test_db,
)
from .database_utils import db_manager, test_db_manager, DatabaseManager
from .db_monitor import db_monitor, DatabaseMonitor
from .security import (
    create_access_token,
    get_current_user,
    get_current_active_user,
    get_current_active_superuser,
)
from .hashing import get_password_hash, verify_password, get_password_hash_sha256
from .exceptions import (
    NotFoundException,
    UnauthorizedException,
    ForbiddenException,
    ValidationException,
    ConflictException,
    ServiceUnavailableException,
)

# Export all core components
__all__ = [
    # Config
    "settings",
    # Security
    "get_password_hash",
    "verify_password",
    "create_access_token",
    "get_current_user",
    "get_current_active_user",
    "get_current_active_superuser",
    # Exceptions
    "NotFoundException",
    "UnauthorizedException",
    "ForbiddenException",
    "ValidationException",
    "ConflictException",
    "ServiceUnavailableException",
]
