"""Test helper functions for integration tests."""
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.models import Profession, EliteSpecialization


def create_test_profession(
    db: Session, 
    name: str = None, 
    description: str = None,
    icon_url: str = None
) -> Profession:
    """Create a test profession in the database."""
    profession = Profession(
        name=name or "Test Profession",
        description=description or "A test profession",
        icon_url=icon_url or "http://example.com/icon.png"
    )
    db.add(profession)
    db.commit()
    db.refresh(profession)
    return profession


def create_test_professions(
    db: Session, 
    count: int = 3
) -> List[Profession]:
    """Create multiple test professions in the database."""
    professions = []
    for i in range(count):
        profession = create_test_profession(
            db=db,
            name=f"Test Profession {i + 1}",
            description=f"Test Profession {i + 1} Description"
        )
        professions.append(profession)
    return professions


def create_test_elite_specialization(
    db: Session,
    profession: Profession,
    name: str = None,
    description: str = None,
    icon_url: str = None
) -> EliteSpecialization:
    """Create a test elite specialization in the database."""
    elite_spec = EliteSpecialization(
        name=name or "Test Elite Spec",
        description=description or "A test elite specialization",
        icon_url=icon_url or "http://example.com/elite_spec_icon.png",
        profession=profession
    )
    db.add(elite_spec)
    db.commit()
    db.refresh(elite_spec)
    return elite_spec
