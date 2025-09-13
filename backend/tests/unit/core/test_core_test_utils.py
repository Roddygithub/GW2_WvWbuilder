"""Test utilities for creating test data."""
from typing import Optional

from sqlalchemy.orm import Session

from app import crud, schemas
from app.models import User
from tests.utils.utils import random_lower_string, random_email


def create_test_user(
    db: Session,
    email: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    full_name: Optional[str] = None,
) -> User:
    """Create a test user with required fields."""
    if email is None:
        email = random_email()
    if username is None:
        username = random_lower_string()
    if password is None:
        password = random_lower_string()
    if full_name is None:
        full_name = f"Test User {random_lower_string(5)}"
        
    user_in = schemas.UserCreate(
        email=email,
        username=username,
        password=password,
        full_name=full_name
    )
    return crud.user.create(db, obj_in=user_in)


def create_test_profession(
    db: Session,
    name: Optional[str] = None,
    game_modes: Optional[list[str]] = None,
) -> schemas.Profession:
    """Create a test profession."""
    if name is None:
        name = f"Test Profession {random_lower_string(5)}"
    if game_modes is None:
        game_modes = ["WvW"]
        
    profession_in = schemas.ProfessionCreate(
        name=name,
        game_modes=game_modes
    )
    return crud.profession.create(db, obj_in=profession_in)
