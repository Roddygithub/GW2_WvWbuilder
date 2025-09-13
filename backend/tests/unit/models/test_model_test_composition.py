"""Tests for the Composition model."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Composition, User, Build
from app.schemas.composition import CompositionCreate, CompositionUpdate

@pytest.mark.asyncio
async def test_create_composition(db_session: AsyncSession, test_user: User):
    """Test creating a composition."""
    # Create a test composition
    composition = Composition(
        name="Test Composition",
        description="Test Composition Description",
        created_by=test_user.id,
        is_public=True,
        squad_size=5
    )
    
    # Add to database
    db_session.add(composition)
    await db_session.commit()
    await db_session.refresh(composition)
    
    # Assertions
    assert composition.id is not None
    assert composition.name == "Test Composition"
    assert composition.description == "Test Composition Description"
    assert composition.created_by == test_user.id
    assert composition.is_public is True
    assert composition.squad_size == 5

@pytest.mark.asyncio
async def test_composition_relationships(db_session: AsyncSession, test_composition: Composition, test_user: User, test_build: Build):
    """Test composition relationships."""
    # Set build for composition
    test_composition.build_id = test_build.id
    await db_session.commit()
    await db_session.refresh(test_composition)
    
    # Test creator relationship
    assert test_composition.creator is not None
    assert test_composition.creator.id == test_user.id
    
    # Test build relationship
    assert test_composition.build is not None
    assert test_composition.build.id == test_build.id

@pytest.mark.asyncio
async def test_composition_update_from_schema(db_session: AsyncSession, test_composition: Composition):
    """Test updating composition from schema."""
    update_data = CompositionUpdate(
        name="Updated Composition",
        description="Updated Description",
        is_public=False,
        squad_size=10
    )
    
    # Update composition
    test_composition.update_from_schema(update_data)
    await db_session.commit()
    await db_session.refresh(test_composition)
    
    # Assertions
    assert test_composition.name == "Updated Composition"
    assert test_composition.description == "Updated Description"
    assert test_composition.is_public is False
    assert test_composition.squad_size == 10

@pytest.mark.asyncio
async def test_composition_representation(test_composition: Composition):
    """Test composition string representation."""
    assert str(test_composition) == f"<Composition {test_composition.name}>"
    assert repr(test_composition) == f"<Composition(id={test_composition.id}, name='{test_composition.name}')>"

@pytest.mark.asyncio
async def test_composition_tags(db_session: AsyncSession, test_composition: Composition):
    """Test composition tags."""
    # Add tags to composition
    tag1 = test_composition.add_tag("tag1")
    tag2 = test_composition.add_tag("tag2")
    
    db_session.add_all([tag1, tag2])
    await db_session.commit()
    await db_session.refresh(test_composition)
    
    # Assertions
    assert len(test_composition.tags) == 2
    assert {tag.name for tag in test_composition.tags} == {"tag1", "tag2"}
    
    # Test removing a tag
    test_composition.remove_tag("tag1")
    await db_session.commit()
    await db_session.refresh(test_composition)
    
    assert len(test_composition.tags) == 1
    assert test_composition.tags[0].name == "tag2"

@pytest.mark.asyncio
async def test_composition_members(db_session: AsyncSession, test_composition: Composition, test_user: User):
    """Test composition members."""
    # Add member to composition
    member = test_composition.add_member(
        user_id=test_user.id,
        role_id=1,
        profession_id=1,
        role_type="DPS"
    )
    
    db_session.add(member)
    await db_session.commit()
    await db_session.refresh(test_composition)
    
    # Assertions
    assert len(test_composition.members) == 1
    member = test_composition.members[0]
    assert member.user_id == test_user.id
    assert member.role_type == "DPS"
    
    # Test removing a member
    test_composition.remove_member(test_user.id)
    await db_session.commit()
    await db_session.refresh(test_composition)
    
    assert len(test_composition.members) == 0
