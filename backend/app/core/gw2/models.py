"""
GW2 API Data Models

This module contains Pydantic models for GW2 API responses.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, HttpUrl


class ItemBase(BaseModel):
    """Base model for items."""

    id: int
    name: str
    description: Optional[str] = None
    type: str
    level: int
    rarity: str
    vendor_value: int
    default_skin: Optional[int] = None
    icon: Optional[HttpUrl] = None
    flags: List[str] = []
    game_types: List[str] = []
    restrictions: List[str] = []


class Item(ItemBase):
    """Full item model with details."""

    details: Optional[Dict[str, Any]] = None


class ItemPrice(BaseModel):
    """Trading post price information for an item."""

    id: int
    whitelisted: bool
    buys: Dict[str, Union[int, str]]
    sells: Dict[str, Union[int, str]]


class Profession(BaseModel):
    """Profession information."""

    id: str
    name: str
    icon: HttpUrl
    icon_big: HttpUrl
    specializations: List[int]
    weapons: Dict[str, List[str]]
    training: List[Dict[str, Any]]
    flags: List[str] = []


class Skill(BaseModel):
    """Skill information."""

    id: int
    name: str
    description: Optional[str] = None
    icon: Optional[HttpUrl] = None
    chat_link: str
    type: str
    weapon_type: Optional[str] = None
    professions: List[str] = []
    slot: Optional[str] = None
    facts: List[Dict[str, Any]] = []
    traited_facts: List[Dict[str, Any]] = []
    categories: List[str] = []


class Trait(BaseModel):
    """Trait information."""

    id: int
    name: str
    icon: Optional[HttpUrl] = None
    description: Optional[str] = None
    facts: List[Dict[str, Any]] = []
    traited_facts: List[Dict[str, Any]] = []
    skills: List[Dict[str, Any]] = []
    specialization: int
    tier: int
    slot: str
    categories: List[str] = []


class EquipmentItem(BaseModel):
    """Equipment item in a character's equipment."""

    id: int
    slot: str
    binding: Optional[str] = None
    bound_to: Optional[str] = None
    charges: Optional[int] = None
    skin: Optional[int] = None
    dyes: Optional[List[int]] = None
    upgrades: Optional[List[int]] = None
    infusions: Optional[List[int]] = None
    stats: Optional[Dict[str, Any]] = None


class Character(BaseModel):
    """Character information."""

    name: str
    race: str
    gender: str
    profession: str
    level: int
    guild: Optional[str] = None
    age: int
    created: datetime
    deaths: int
    title: Optional[int] = None
    crafting: List[Dict[str, Any]] = []
    equipment: List[EquipmentItem] = []
    equipment_pvp: Dict[str, Any] = {}
    specializations: Dict[str, List[Optional[Dict[str, Any]]]] = {}
    skills: Dict[str, List[Optional[Dict[str, Any]]]] = {}
    equipment_tabs: List[Dict[str, Any]] = []
    build_tabs: List[Dict[str, Any]] = []
    build_tabs_unlocked: Optional[int] = None
    active_equipment_tab: Optional[int] = None
    active_build_tab: Optional[int] = None


class Account(BaseModel):
    """Account information."""

    id: str
    name: str
    age: int
    world: int
    guilds: List[str] = []
    guild_leader: List[str] = []
    created: datetime
    access: List[str] = []
    commander: bool
    fractal_level: Optional[int] = None
    daily_ap: Optional[int] = None
    monthly_ap: Optional[int] = None
    wvw_rank: Optional[int] = None
    last_modified: datetime


class BuildTab(BaseModel):
    """Build tab information."""

    tab: int
    is_active: bool
    build: Dict[str, Any]


class EquipmentTab(BaseModel):
    """Equipment tab information."""

    tab: int
    is_active: bool
    items: List[EquipmentItem]
