"""
Guild Wars 2 API Endpoints

This module provides FastAPI endpoints for interacting with the Guild Wars 2 API.
"""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_gw2_client
from app.core.gw2.client import GW2Client
from app.core.gw2.exceptions import (
    GW2APIError,
    GW2APINotFoundError,
    GW2APIUnauthorizedError,
)

router = APIRouter()


@router.get("/account", response_model=Dict[str, Any])
async def get_account_info(gw2_client: GW2Client = Depends(get_gw2_client)) -> Dict[str, Any]:
    """
    Get the account information for the authenticated user.

    Requires a valid GW2 API key with the 'account' permission.
    """
    try:
        account = await gw2_client.get_account()
        return account.dict()
    except GW2APIUnauthorizedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Guild Wars 2 API key",
        ) from e
    except GW2APIError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Guild Wars 2 API is currently unavailable",
        ) from e


@router.get("/characters", response_model=List[str])
async def list_characters(gw2_client: GW2Client = Depends(get_gw2_client)) -> List[str]:
    """
    Get the list of character names for the authenticated account.

    Requires a valid GW2 API key with the 'characters' permission.
    """
    try:
        characters = await gw2_client.get_characters()
        return characters
    except GW2APIUnauthorizedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Guild Wars 2 API key",
        ) from e
    except GW2APIError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Guild Wars 2 API is currently unavailable",
        ) from e


@router.get("/characters/{character_name}", response_model=Dict[str, Any])
async def get_character(
    character_name: str, gw2_client: GW2Client = Depends(get_gw2_client)
) -> Dict[str, Any]:
    """
    Get detailed information about a specific character.

    Args:
        character_name: The name of the character to retrieve

    Requires a valid GW2 API key with the 'characters' permission.
    """
    try:
        character = await gw2_client.get_character(character_name)
        return character.dict()
    except GW2APINotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character '{character_name}' not found",
        ) from e
    except GW2APIUnauthorizedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Guild Wars 2 API key",
        ) from e
    except GW2APIError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Guild Wars 2 API is currently unavailable",
        ) from e


@router.get("/items/{item_id}", response_model=Dict[str, Any])
async def get_item(item_id: int, gw2_client: GW2Client = Depends(get_gw2_client)) -> Dict[str, Any]:
    """
    Get information about an item by its ID.

    Args:
        item_id: The ID of the item to retrieve
    """
    try:
        item = await gw2_client.get_item(item_id)
        return item.dict()
    except GW2APINotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found",
        ) from e
    except GW2APIError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Guild Wars 2 API is currently unavailable",
        ) from e


@router.get("/professions", response_model=List[str])
async def list_professions(gw2_client: GW2Client = Depends(get_gw2_client)) -> List[str]:
    """Get a list of all profession IDs."""
    try:
        professions = await gw2_client.get_professions()
        return professions
    except GW2APIError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Guild Wars 2 API is currently unavailable",
        ) from e


@router.get("/professions/{profession_id}", response_model=Dict[str, Any])
async def get_profession(
    profession_id: str, gw2_client: GW2Client = Depends(get_gw2_client)
) -> Dict[str, Any]:
    """
    Get detailed information about a profession.

    Args:
        profession_id: The ID of the profession (e.g., 'Elementalist', 'Warrior')
    """
    try:
        profession = await gw2_client.get_profession(profession_id)
        return profession.dict()
    except GW2APINotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profession '{profession_id}' not found",
        ) from e
    except GW2APIError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Guild Wars 2 API is currently unavailable",
        ) from e
