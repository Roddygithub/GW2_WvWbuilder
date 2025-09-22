"""
Enums used across the application.

This module contains all enumerations used in the application models and schemas.
"""

from enum import Enum, IntEnum


class GameMode(str, Enum):
    """Game modes supported by the application."""

    WvW = "wvw"
    PvP = "pvp"
    PvE = "pve"


class RoleType(str, Enum):
    """User role types."""

    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"
    GUEST = "guest"


class BuildStatus(str, Enum):
    """Build status types."""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class CompositionStatus(str, Enum):
    """Composition status types."""

    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class ProfessionType(str, Enum):
    """Guild Wars 2 profession types."""

    ELEMENTALIST = "Elementalist"
    ENGINEER = "Engineer"
    GUARDIAN = "Guardian"
    MESMER = "Mesmer"
    NECROMANCER = "Necromancer"
    RANGER = "Ranger"
    REVENANT = "Revenant"
    THIEF = "Thief"
    WARRIOR = "Warrior"


class EliteSpecializationType(str, Enum):
    """Guild Wars 2 elite specialization types."""

    # Elementalist
    TEMPEST = "Tempest"
    WEAVER = "Weaver"
    CATALYST = "Catalyst"

    # Engineer
    SCRAPPER = "Scrapper"
    HOLOSMITH = "Holosmith"
    MECHANIST = "Mechanist"

    # Guardian
    DRAGONHUNTER = "Dragonhunter"
    FIREBRAND = "Firebrand"
    WILLBENDER = "Willbender"

    # Mesmer
    CHRONOMANCER = "Chronomancer"
    MIRAGE = "Mirage"
    VIRTUOSO = "Virtuoso"

    # Necromancer
    REAPER = "Reaper"
    SCOURGE = "Scourge"
    HARBINGER = "Harbinger"

    # Ranger
    DRUID = "Druid"
    SOULBEAST = "Soulbeast"
    UNTAMED = "Untamed"

    # Revenant
    HERALD = "Herald"
    RENEGADE = "Renegade"
    VINDICATOR = "Vindicator"

    # Thief
    DAREDEVIL = "Daredevil"
    DEADEYE = "Deadeye"
    SPECTER = "Specter"

    # Warrior
    BERSERKER = "Berserker"
    SPELLBREAKER = "Spellbreaker"
    BLADESWORN = "Bladesworn"


class BuildType(str, Enum):
    """Build types for categorization."""

    POWER = "power"
    CONDITION = "condition"
    SUPPORT = "support"
    HYBRID = "hybrid"
    ROAMING = "roaming"
    ZERG = "zerg"
    SMALL_SCALE = "small_scale"
    LARGE_SCALE = "large_scale"


class CompositionRole(str, Enum):
    """Roles within a composition."""

    COMMANDER = "commander"
    SUPPORT = "support"
    DPS = "dps"
    HEALER = "healer"
    BOON_SUPPORT = "boon_support"
    UTILITY = "utility"
    SPECIALIST = "specialist"


class Visibility(str, Enum):
    """Visibility levels for builds and compositions."""

    PUBLIC = "public"
    PRIVATE = "private"
    UNLISTED = "unlisted"


class PermissionLevel(IntEnum):
    """Permission levels for access control."""

    READ = 1
    COMMENT = 2
    EDIT = 3
    MANAGE = 4
    ADMIN = 5


class TeamRole(str, Enum):
    """Team member roles."""

    OWNER = "owner"
    ADMIN = "admin"
    OFFICER = "officer"
    MEMBER = "member"
    TRIAL = "trial"


class TeamStatus(str, Enum):
    """Team status types."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
