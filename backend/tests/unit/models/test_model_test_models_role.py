"""Tests for the Role model."""
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.models.base_models import Role, User, user_roles

class TestRoleModel:
    """Tests for the Role model."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        # Create an in-memory SQLite database for testing
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        
        # Create test data
        self.user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password"
        )
        
        self.role = Role(
            name="test_role",
            description="Test Role",
            permission_level=1,
            is_default=False
        )
        
        self.session.add_all([self.user, self.role])
        self.session.commit()
        
        yield
        
        # Clean up
        self.session.close()
        Base.metadata.drop_all(self.engine)
    
    def test_role_creation(self):
        """Test creating a new role."""
        assert self.role.id is not None
        assert self.role.name == "test_role"
        assert self.role.description == "Test Role"
        assert self.role.permission_level == 1
        assert self.role.is_default is False
        assert isinstance(self.role.created_at, datetime)
    
    def test_role_relationships(self):
        """Test role relationships with users."""
        # Test initial relationships
        assert len(self.role.users) == 0
        
        # Add user to role
        stmt = user_roles.insert().values(user_id=self.user.id, role_id=self.role.id)
        self.session.execute(stmt)
        self.session.commit()
        
        # Refresh role to get updated relationships
        self.session.refresh(self.role)
        
        # Test relationship after adding
        assert len(self.role.users) == 1
        assert self.role.users[0].username == "testuser"
    
    def test_role_str_representation(self):
        """Test the string representation of a role."""
        assert str(self.role) == f"<Role {self.role.name}>"
    
    def test_role_equality(self):
        """Test role equality comparison."""
        # Create another role
        role2 = Role(
            name="test_role2",
            description="Test Role 2",
            permission_level=2
        )
        
        self.session.add(role2)
        self.session.commit()
        
        assert self.role == self.role  # Same object
        assert self.role != role2      # Different objects
        assert self.role != "not a role"  # Different type
