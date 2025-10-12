"""
Guild Wars 2 API Integration Module

This module provides a client for interacting with the Guild Wars 2 API (v2).
It includes features like request caching, error handling, and response validation.
"""

from .client import GW2Client
from .exceptions import GW2APIError, GW2APINotFoundError, GW2APIUnauthorizedError
from .models import (
    Account,
    Character,
    Item,
    ItemPrice,
    Profession,
    Skill,
    Trait,
    BuildTab,
    EquipmentTab,
)

__all__ = [
    "GW2Client",
    "GW2APIError",
    "GW2APINotFoundError",
    "GW2APIUnauthorizedError",
    "Account",
    "Character",
    "Item",
    "ItemPrice",
    "Profession",
    "Skill",
    "Trait",
    "BuildTab",
    "EquipmentTab",
]
