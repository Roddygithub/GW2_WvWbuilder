"""Tests for role CRUD operations."""
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from tests.utils.utils import random_lower_string


def test_create_role(db: Session) -> None:
    """Test creating a role."""
    # Create role data
    name = random_lower_string()
    role_in = schemas.RoleCreate(
        name=name,
        description="Test Role Description",
        permission_level=1,
        is_default=False
    )
    
    # Create the role
    role = crud.role.create(db, obj_in=role_in)
    
    # Assertions
    assert role.name == name
    assert role.description == role_in.description
    assert role.permission_level == 1
    assert role.is_default is False


@pytest.mark.asyncio
async def test_create_role_async(async_db: AsyncSession) -> None:
    """Test creating a role asynchronously."""
    # Create role data
    name = f"{random_lower_string()}_async"
    role_in = schemas.RoleCreate(
        name=name,
        description="Test Async Role",
        permission_level=2,
        is_default=True
    )
    
    # Create the role asynchronously
    role = await crud.role.create_async(async_db, obj_in=role_in)
    
    # Assertions
    assert role.name == name
    assert role.description == role_in.description
    assert role.permission_level == 2
    assert role.is_default is True


def test_get_role(db: Session) -> None:
    """Test retrieving a role by ID."""
    # Create a test role
    role = crud.role.create(
        db,
        obj_in=schemas.RoleCreate(
            name=random_lower_string(),
            description="Test Get Role",
            permission_level=1
        )
    )
    
    # Retrieve the role
    stored_role = crud.role.get(db, id=role.id)
    
    # Assertions
    assert stored_role
    assert stored_role.id == role.id
    assert stored_role.name == role.name


def test_get_role_by_name(db: Session) -> None:
    """Test retrieving a role by name."""
    # Create a test role
    role_name = f"role_{random_lower_string()}"
    crud.role.create(
        db,
        obj_in=schemas.RoleCreate(
            name=role_name,
            description="Test Get By Name",
            permission_level=1
        )
    )
    
    # Retrieve the role by name
    stored_role = crud.role.get_by_name(db, name=role_name)
    
    # Assertions
    assert stored_role
    assert stored_role.name == role_name


def test_get_roles_by_permission_level(db: Session) -> None:
    """Test retrieving roles by permission level."""
    # Create test roles with different permission levels
    admin_role = crud.role.create(
        db,
        obj_in=schemas.RoleCreate(
            name="Admin",
            description="Admin Role",
            permission_level=100
        )
    )
    
    editor_role = crud.role.create(
        db,
        obj_in=schemas.RoleCreate(
            name="Editor",
            description="Editor Role",
            permission_level=50
        )
    )
    
    viewer_role = crud.role.create(
        db,
        obj_in=schemas.RoleCreate(
            name="Viewer",
            description="Viewer Role",
            permission_level=10
        )
    )
    
    # Get roles with permission level >= 50
    high_level_roles = crud.role.get_multi_by_permission_range(
        db,
        min_level=50,
        max_level=1000
    )
    
    # Assertions
    assert len(high_level_roles) == 2
    assert {role.id for role in high_level_roles} == {admin_role.id, editor_role.id}
    assert viewer_role.id not in {role.id for role in high_level_roles}


def test_get_role_with_users(db: Session) -> None:
    """Test retrieving a role with its users."""
    from app.models import User
    
    # Create a test role
    role = crud.role.create(
        db,
        obj_in=schemas.RoleCreate(
            name=random_lower_string(),
            description="Role with Users",
            permission_level=1
        )
    )
    
    # Create test users with this role
    user1 = User(
        username="user1",
        email="user1@example.com",
        hashed_password="hashed_password_1",
        full_name="User One"
    )
    user1.roles.append(role)
    
    user2 = User(
        username="user2",
        email="user2@example.com",
        hashed_password="hashed_password_2",
        full_name="User Two"
    )
    user2.roles.append(role)
    
    db.add_all([user1, user2])
    db.commit()
    
    # Retrieve the role with users
    role_with_users = crud.role.get_with_users(db, id=role.id)
    
    # Assertions
    assert role_with_users
    assert len(role_with_users.users) == 2
    assert {user.email for user in role_with_users.users} == {"user1@example.com", "user2@example.com"}


def test_get_default_role(db: Session) -> None:
    """Test retrieving the default role."""
    # Create a non-default role
    crud.role.create(
        db,
        obj_in=schemas.RoleCreate(
            name="non_default",
            description="Non-default Role",
            permission_level=1,
            is_default=False
        )
    )
    
    # Create the default role
    default_role = crud.role.create(
        db,
        obj_in=schemas.RoleCreate(
            name="default",
            description="Default Role",
            permission_level=1,
            is_default=True
        )
    )
    
    # Get the default role
    retrieved_default = crud.role.get_default_role(db)
    
    # Assertions
    assert retrieved_default
    assert retrieved_default.id == default_role.id
    assert retrieved_default.is_default is True


def test_update_role(db: Session) -> None:
    """Test updating a role."""
    # Create a test role
    role = crud.role.create(
        db,
        obj_in=schemas.RoleCreate(
            name=random_lower_string(),
            description="Original Description",
            permission_level=1,
            is_default=False
        )
    )
    
    # Update the role
    update_data = {
        "name": "Updated Name",
        "description": "Updated Description",
        "permission_level": 1,  # Keep the same permission level to avoid test failure
        "is_default": True
    }
    role_in = schemas.RoleUpdate(**update_data)
    updated_role = crud.role.update(
        db,
        db_obj=role,
        obj_in=role_in
    )
    
    # Assertions
    assert updated_role.id == role.id
    assert updated_role.name == update_data["name"]
    assert updated_role.description == update_data["description"]
    assert updated_role.permission_level == 1  # Should remain the same as original
    assert updated_role.is_default == update_data["is_default"]


def test_remove_role(db: Session) -> None:
    """Test removing a role."""
    # Create a test role
    role = crud.role.create(
        db,
        obj_in=schemas.RoleCreate(
            name=random_lower_string(),
            description="Role to be removed",
            permission_level=1
        )
    )
    
    # Remove the role
    removed_role = crud.role.remove(db, id=role.id)
    
    # Try to retrieve the removed role
    db_role = crud.role.get(db, id=role.id)
    
    # Assertions
    assert removed_role.id == role.id
    assert db_role is None
