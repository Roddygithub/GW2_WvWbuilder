"""Tests for service layer functions."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta

from app.core.security import get_password_hash
from app.crud.user import user as user_crud
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

pytestmark = pytest.mark.asyncio

class TestUserService:
    """Tests for user-related service functions."""
    
    async def test_create_user(self, db: AsyncMock, test_password: str):
        """Test creating a new user."""
        # Test data
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": test_password,
            "full_name": "New User"
        }
        
        # Mock the database methods
        db.execute.return_value = MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None))))
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        
        # Call the service function
        user = await user_crud.create(db, obj_in=UserCreate(**user_data))
        
        # Check the results
        assert user.email == user_data["email"]
        assert user.username == user_data["username"]
        assert user.full_name == user_data["full_name"]
        assert user.hashed_password is not None
        assert user.hashed_password != test_password  # Should be hashed
        
        # Verify the database was called correctly
        db.add.assert_called_once()
        db.commit.assert_awaited_once()
        db.refresh.assert_awaited_once()
    
    async def test_authenticate_user(self, db: AsyncMock, test_user: User, test_password: str):
        """Test authenticating a user with correct password."""
        # Mock the get_by_email method
        user_crud.get_by_email = AsyncMock(return_value=test_user)
        
        # Test with correct password
        authenticated_user = await user_crud.authenticate(
            db, email=test_user.email, password=test_password
        )
        
        assert authenticated_user is not None
        assert authenticated_user.email == test_user.email
        
        # Test with incorrect password
        authenticated_user = await user_crud.authenticate(
            db, email=test_user.email, password="wrong_password"
        )
        
        assert authenticated_user is None
        
        # Test with non-existent user
        user_crud.get_by_email = AsyncMock(return_value=None)
        authenticated_user = await user_crud.authenticate(
            db, email="nonexistent@example.com", password=test_password
        )
        
        assert authenticated_user is None
    
    async def test_update_user(self, db: AsyncMock, test_user: User):
        """Test updating a user's information."""
        # Test update data
        update_data = {
            "full_name": "Updated Name",
            "is_active": False,
            "email": "updated@example.com"
        }
        
        # Mock the get method
        user_crud.get = AsyncMock(return_value=test_user)
        
        # Call the update method
        updated_user = await user_crud.update(
            db, db_obj=test_user, obj_in=UserUpdate(**update_data)
        )
        
        # Check the results
        assert updated_user.full_name == update_data["full_name"]
        assert updated_user.is_active == update_data["is_active"]
        assert updated_user.email == update_data["email"]
        
        # Verify the database was called correctly
        db.add.assert_called_once()
        db.commit.assert_awaited_once()
        db.refresh.assert_awaited_once()
    
    async def test_update_user_password(self, db: AsyncMock, test_user: User, test_password: str):
        """Test updating a user's password."""
        # Store the original password hash
        original_hash = test_user.hashed_password
        
        # New password
        new_password = "new_secure_password123"
        
        # Mock the get method
        user_crud.get = AsyncMock(return_value=test_user)
        
        # Call the update method with a new password
        updated_user = await user_crud.update(
            db, 
            db_obj=test_user, 
            obj_in=UserUpdate(password=new_password)
        )
        
        # Check the results
        assert updated_user.hashed_password != original_hash  # Should be updated
        assert updated_user.hashed_password != new_password  # Should be hashed
        
        # Verify the new password works
        assert user_crud.verify_password(new_password, updated_user.hashed_password)
    
    async def test_delete_user(self, db: AsyncMock, test_user: User):
        """Test deleting a user."""
        # Mock the get method
        user_crud.get = AsyncMock(return_value=test_user)
        
        # Call the delete method
        deleted_user = await user_crud.remove(db, id=test_user.id)
        
        # Check the results
        assert deleted_user is not None
        assert deleted_user.id == test_user.id
        
        # Verify the database was called correctly
        db.delete.assert_called_once()
        db.commit.assert_awaited_once()

class TestBuildService:
    """Tests for build-related service functions."""
    
    async def test_create_build(self, db: AsyncMock, test_user: User, test_profession: dict):
        """Test creating a new build."""
        from app.crud.build import build as build_crud
        from app.schemas.build import BuildCreate
        
        # Test data
        build_data = {
            "name": "Test Build",
            "description": "A test build",
            "profession_id": test_profession["id"],
            "game_mode": "pvp",
            "is_public": True,
            "created_by": test_user.id,
            "build_link": "http://example.com/build"
        }
        
        # Mock the database methods
        db.execute.return_value = MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None))))
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        
        # Call the service function
        build = await build_crud.create(db, obj_in=BuildCreate(**build_data))
        
        # Check the results
        assert build.name == build_data["name"]
        assert build.description == build_data["description"]
        assert build.profession_id == build_data["profession_id"]
        assert build.game_mode == build_data["game_mode"]
        assert build.is_public == build_data["is_public"]
        assert build.created_by == build_data["created_by"]
        assert build.build_link == build_data["build_link"]
        
        # Verify the database was called correctly
        db.add.assert_called_once()
        db.commit.assert_awaited_once()
        db.refresh.assert_awaited_once()

class TestCompositionService:
    """Tests for team composition service functions."""
    
    async def test_create_composition(self, db: AsyncMock, test_user: User, test_builds: list):
        """Test creating a new team composition."""
        from app.crud.composition import composition as composition_crud
        from app.schemas.composition import CompositionCreate
        
        # Test data
        build_ids = [build.id for build in test_builds[:3]]
        composition_data = {
            "name": "Test Composition",
            "description": "A test composition",
            "game_mode": "wvw",
            "is_public": True,
            "created_by": test_user.id,
            "builds": build_ids
        }
        
        # Mock the database methods
        db.execute.return_value = MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None))))
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        
        # Mock the get method for builds
        from app.crud.build import build as build_crud
        build_crud.get = AsyncMock(side_effect=test_builds)
        
        # Call the service function
        composition = await composition_crud.create(
            db, 
            obj_in=CompositionCreate(**composition_data)
        )
        
        # Check the results
        assert composition.name == composition_data["name"]
        assert composition.description == composition_data["description"]
        assert composition.game_mode == composition_data["game_mode"]
        assert composition.is_public == composition_data["is_public"]
        assert composition.created_by == composition_data["created_by"]
        assert len(composition.builds) == len(build_ids)
        
        # Verify the database was called correctly
        db.add.assert_called_once()
        db.commit.assert_awaited_once()
        db.refresh.assert_awaited_once()
