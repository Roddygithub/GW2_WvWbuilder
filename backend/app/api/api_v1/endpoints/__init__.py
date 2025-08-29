"""Expose existing endpoint modules for easy import in api.py."""

from . import users
from . import roles
from . import professions
from . import compositions

__all__ = [
    "users",
    "roles",
    "professions",
    "compositions",
]
