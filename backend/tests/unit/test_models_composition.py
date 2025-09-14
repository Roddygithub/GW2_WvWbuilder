"""
Tests for the Composition model and its relationships.

This module contains unit tests for the Composition model, including:
- Model validations and constraints
- Relationships with other models (User, Build, CompositionTag)
- CRUD operations with edge cases
"""
import pytest
from datetime import datetime, timedelta
from typing import Dict, List
from unittest.mock import patch, MagicMock

from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.base_models import Composition, User, Build, CompositionTag, Role, Profession
from app.models.enums import GameMode

# Test data
TEST_COMPOSITION_DATA = {
    "name": "Test Composition",
    "description": "A test composition",
    "squad_size": 10,
    "is_public": False
}

# Fixtures

@pytest.fixture
def sample_user(db):
    """Create a sample user for testing."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def sample_build(db, sample_user):
    """Create a sample build for testing."""
    build = Build(
        name="Test Build",
        game_mode="wvw",
        created_by_id=sample_user.id
    )
    db.add(build)
    db.commit()
    db.refresh(build)
    return build

@pytest.fixture
def sample_role(db):
    """Create a sample role for testing."""
    role = Role(
        name="Test Role",
        description="Test Role Description",
        permission_level=1
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    return role

@pytest.fixture
def sample_profession(db):
    """Create a sample profession for testing."""
    prof = Profession(
        name="Test Profession",
        game_modes=["wvw", "pve"]
    )
    db.add(prof)
    db.commit()
    db.refresh(prof)
    return prof

@pytest.fixture
def sample_composition(db, sample_user, sample_build):
    """Create a sample composition for testing."""
    composition = Composition(
        **TEST_COMPOSITION_DATA,
        created_by=sample_user.id,
        build_id=sample_build.id
    )
    db.add(composition)
    db.commit()
    db.refresh(composition)
    return composition

# Test cases

class TestCompositionModel:
    """Test cases for the Composition model."""
    
    def test_composition_creation(self, db, sample_user, sample_build):
        """Test basic composition creation with valid data."""
        # Arrange
        comp_data = {
            **TEST_COMPOSITION_DATA,
            "created_by": sample_user.id,
            "build_id": sample_build.id
        }
        
        # Act
        composition = Composition(**comp_data)
        db.add(composition)
        db.commit()
        db.refresh(composition)
        
        # Assert
        assert composition.id is not None
        assert composition.name == TEST_COMPOSITION_DATA["name"]
        assert composition.created_by == sample_user.id
        assert composition.build_id == sample_build.id
        assert composition.created_at is not None
        assert composition.updated_at is None  # Not updated yet
    
    def test_composition_required_fields(self, db, sample_user):
        """Test that required fields are enforced."""
        # Test missing name
        with pytest.raises(IntegrityError):
            composition = Composition(
                description="No name",
                created_by=sample_user.id
            )
            db.add(composition)
            db.commit()
        db.rollback()
        
        # Test missing created_by
        with pytest.raises(IntegrityError):
            composition = Composition(
                name="No creator"
            )
            db.add(composition)
            db.commit()
        db.rollback()
    
    def test_composition_relationships(self, db, sample_composition, sample_user, sample_build):
        """Test relationships with User and Build models."""
        # Test relationship with User
        assert sample_composition.creator.id == sample_user.id
        assert sample_composition in sample_user.created_compositions
        
        # Test relationship with Build
        assert sample_composition.build.id == sample_build.id
        assert sample_composition in sample_build.compositions
    
    def test_composition_members(self, db, sample_composition, sample_user, sample_role, sample_profession):
        """Test adding members to a composition."""
        from app.models.base_models import composition_members
        
        # Add member to composition
        stmt = composition_members.insert().values(
            composition_id=sample_composition.id,
            user_id=sample_user.id,
            role_id=sample_role.id,
            profession_id=sample_profession.id,
            notes="Test member"
        )
        db.execute(stmt)
        db.commit()
        
        # Test the relationship
        assert len(sample_composition.members) == 1
        assert sample_composition.members[0].id == sample_user.id
        
        # Test the through table attributes
        member = sample_composition.composition_memberships[0]
        assert member.role_id == sample_role.id
        assert member.profession_id == sample_profession.id
        assert member.notes == "Test member"
    
    def test_composition_tags(self, db, sample_composition):
        """Test adding tags to a composition."""
        # Create a tag
        tag = CompositionTag(
            name="Test Tag",
            composition_id=sample_composition.id
        )
        db.add(tag)
        db.commit()
        
        # Test the relationship
        assert len(sample_composition.tags) == 1
        assert sample_composition.tags[0].name == "Test Tag"
    
    def test_composition_validation(self, db, sample_user):
        """Test field validations."""
        # Test invalid squad size
        with pytest.raises(ValueError):
            Composition(
                name="Invalid Squad Size",
                squad_size=0,
                created_by=sample_user.id
            )
        
        # Test long name
        with pytest.raises(ValueError):
            Composition(
                name="X" * 256,  # Too long
                created_by=sample_user.id
            )
    
    def test_composition_update_timestamp(self, db, sample_composition):
        """Test that updated_at is set when composition is modified."""
        original_updated_at = sample_composition.updated_at
        
        # Make a change
        sample_composition.name = "Updated Name"
        db.add(sample_composition)
        db.commit()
        db.refresh(sample_composition)
        
        assert sample_composition.updated_at is not None
        if original_updated_at is not None:
            assert sample_composition.updated_at > original_updated_at


class TestCompositionCRUD:
    """Test CRUD operations for the Composition model."""
    
    def test_create_composition(self, db, sample_user, sample_build):
        """Test creating a new composition."""
        from app.crud.composition import create_composition
        
        # Prepare data
        comp_data = {
            **TEST_COMPOSITION_DATA,
            "build_id": sample_build.id,
            "user_id": sample_user.id
        }
        
        # Act
        composition = create_composition(db, comp_data)
        
        # Assert
        assert composition.id is not None
        assert composition.name == TEST_COMPOSITION_DATA["name"]
        assert composition.created_by == sample_user.id
        assert composition.build_id == sample_build.id
    
    def test_get_composition(self, db, sample_composition):
        """Test retrieving a composition by ID."""
        from app.crud.composition import get_composition
        
        # Act
        result = get_composition(db, composition_id=sample_composition.id)
        
        # Assert
        assert result is not None
        assert result.id == sample_composition.id
        assert result.name == sample_composition.name
    
    def test_update_composition(self, db, sample_composition):
        """Test updating a composition."""
        from app.crud.composition import update_composition
        
        # Prepare update data
        update_data = {
            "name": "Updated Composition",
            "is_public": True,
            "description": "Updated description"
        }
        
        # Act
        updated_comp = update_composition(
            db, 
            composition_id=sample_composition.id, 
            composition_data=update_data
        )
        
        # Assert
        assert updated_comp.name == "Updated Composition"
        assert updated_comp.is_public is True
        assert updated_comp.description == "Updated description"
        assert updated_comp.updated_at is not None
    
    def test_delete_composition(self, db, sample_composition):
        """Test deleting a composition."""
        from app.crud.composition import delete_composition, get_composition
        
        # Act
        deleted = delete_composition(db, composition_id=sample_composition.id)
        
        # Assert
        assert deleted is True
        assert get_composition(db, composition_id=sample_composition.id) is None
    
    def test_composition_search(self, db, sample_composition, sample_user):
        """Test searching for compositions."""
        from app.crud.composition import search_compositions
        
        # Create a public composition
        public_comp = Composition(
            name="Public Test Composition",
            is_public=True,
            created_by=sample_user.id,
            build_id=sample_composition.build_id
        )
        db.add(public_comp)
        db.commit()
        
        # Test search by name
        results = search_compositions(db, name="Test")
        assert len(results) >= 1
        
        # Test search by is_public
        results = search_compositions(db, is_public=True)
        assert len(results) == 1
        assert results[0].id == public_comp.id
        
        # Test search by creator
        results = search_compositions(db, created_by=sample_user.id)
        assert len(results) >= 2


class TestCompositionEdgeCases:
    """Test edge cases and error conditions for Composition operations."""
    
    def test_create_composition_nonexistent_build(self, db, sample_user):
        """Test creating a composition with a non-existent build."""
        from app.crud.composition import create_composition
        
        # Prepare data with non-existent build ID
        comp_data = {
            **TEST_COMPOSITION_DATA,
            "build_id": 999,  # Non-existent
            "user_id": sample_user.id
        }
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            create_composition(db, comp_data)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_nonexistent_composition(self, db):
        """Test updating a non-existent composition."""
        from app.crud.composition import update_composition
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            update_composition(
                db, 
                composition_id=999, 
                composition_data={"name": "New Name"}
            )
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_nonexistent_composition(self, db):
        """Test deleting a non-existent composition."""
        from app.crud.composition import delete_composition
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            delete_composition(db, composition_id=999)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    
    def test_composition_permissions(self, db, sample_composition):
        """Test composition ownership and permissions."""
        from app.crud.composition import update_composition, delete_composition
        
        # Create a different user
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password="hashed_password"
        )
        db.add(other_user)
        db.commit()
        
        # Test updating someone else's composition
        with pytest.raises(HTTPException) as exc_info:
            update_composition(
                db, 
                composition_id=sample_composition.id, 
                composition_data={"name": "Hacked"},
                user_id=other_user.id
            )
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        
        # Test deleting someone else's composition
        with pytest.raises(HTTPException) as exc_info:
            delete_composition(
                db, 
                composition_id=sample_composition.id, 
                user_id=other_user.id
            )
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    
    def test_composition_member_management(self, db, sample_composition, sample_user, sample_role, sample_profession):
        """Test adding and removing members from a composition."""
        from app.crud.composition import (
            add_composition_member,
            remove_composition_member,
            get_composition_members
        )
        
        # Test adding a member
        composition = add_composition_member(
            db,
            composition_id=sample_composition.id,
            user_id=sample_user.id,
            role_id=sample_role.id,
            profession_id=sample_profession.id,
            notes="Test member"
        )
        
        # Verify the member was added
        members = get_composition_members(db, composition_id=sample_composition.id)
        assert len(members) == 1
        assert members[0].id == sample_user.id
        
        # Test removing the member
        composition = remove_composition_member(
            db,
            composition_id=sample_composition.id,
            user_id=sample_user.id
        )
        
        # Verify the member was removed
        members = get_composition_members(db, composition_id=sample_composition.id)
        assert len(members) == 0
    
    def test_composition_tag_management(self, db, sample_composition):
        """Test adding and removing tags from a composition."""
        from app.crud.composition import (
            add_composition_tag,
            remove_composition_tag,
            get_composition_tags
        )
        
        # Test adding a tag
        composition = add_composition_tag(
            db,
            composition_id=sample_composition.id,
            tag_name="Test Tag"
        )
        
        # Verify the tag was added
        tags = get_composition_tags(db, composition_id=sample_composition.id)
        assert len(tags) == 1
        assert tags[0].name == "Test Tag"
        
        # Test removing the tag
        composition = remove_composition_tag(
            db,
            composition_id=sample_composition.id,
            tag_name="Test Tag"
        )
        
        # Verify the tag was removed
        tags = get_composition_tags(db, composition_id=sample_composition.id)
        assert len(tags) == 0
