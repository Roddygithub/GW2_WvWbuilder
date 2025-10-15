"""Tests for the User model."""

import pytest
import uuid
from datetime import datetime
from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker

from app.models import (
    Base,
    User,
    Role,
    Build,
    Composition,
    Profession,
    EliteSpecialization,
)
from app.models.association_tables import composition_members


class TestUserModel:
    """Tests for the User model."""

    def create_test_user(self, username_suffix=""):
        """Helper method to create a test user with a unique username."""
        unique_id = str(uuid.uuid4())[:8]
        return User(
            username=f"testuser_{username_suffix}_{unique_id}",
            email=f"test_{unique_id}@example.com",
            hashed_password="hashed_password",
        )

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        # Create an in-memory SQLite database for testing
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        # Create test data with unique usernames
        self.user = self.create_test_user("main")
        self.role = Role(name="test_role", description="Test Role", permission_level=1)
        self.profession = Profession(name="Test Profession")
        self.elite_spec = EliteSpecialization(
            name="Test Elite Spec", profession=self.profession
        )

        # Add and commit user first to get an ID
        self.session.add(self.user)
        self.session.commit()

        # Now create build with the user's ID
        self.build = Build(
            name="Test Build", created_by_id=self.user.id, config={"test": "config"}
        )
        self.composition = Composition(
            name="Test Composition", created_by=self.user.id, build=self.build
        )

        self.session.add_all(
            [self.role, self.profession, self.elite_spec, self.build, self.composition]
        )
        self.session.commit()

        # Add user to composition_members
        stmt = insert(composition_members).values(
            composition_id=self.composition.id,
            user_id=self.user.id,
            role_id=self.role.id,
            profession_id=self.profession.id,
            elite_specialization_id=self.elite_spec.id,
        )
        self.session.execute(stmt)
        self.session.commit()

        yield

        # Clean up
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_user_creation(self):
        """Test creating a new user."""
        # Create a new user with a unique username and email
        unique_id = str(uuid.uuid4())[:8]
        user = User(
            username=f"newuser_{unique_id}",
            email=f"newuser_{unique_id}@example.com",
            hashed_password="hashed_password",
            full_name="Test User",
        )

        self.session.add(user)
        self.session.commit()

        assert user.id is not None
        assert user.username == f"newuser_{unique_id}"
        assert user.email == f"newuser_{unique_id}@example.com"
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert user.is_superuser is False
        assert isinstance(user.created_at, datetime)

    def test_user_relationships(self):
        """Test user relationships with roles, builds, and compositions."""
        # Test initial relationships
        assert len(self.user.roles) == 0  # No roles assigned yet

        # There should be one build already created in setup (Test Build)
        assert len(self.user.builds) == 1
        assert self.user.builds[0].name == "Test Build"

        # Create a new build for the user
        new_build = Build(
            name="User's Build", created_by_id=self.user.id, config={"test": "config"}
        )
        self.session.add(new_build)
        self.session.commit()

        # Test builds relationship after adding
        self.session.refresh(self.user)
        assert len(self.user.builds) == 2
        assert any(build.name == "User's Build" for build in self.user.builds)

        # Test composition relationship through association table
        stmt = composition_members.select().where(
            composition_members.c.user_id == self.user.id
        )
        result = self.session.execute(stmt).fetchone()
        assert result is not None
        assert result.composition_id == self.composition.id

    def test_user_equality(self):
        """Test user equality comparison."""
        # Create users with unique usernames and emails
        user1 = self.create_test_user("eq1")
        user2 = self.create_test_user("eq2")

        self.session.add_all([user1, user2])
        self.session.commit()

        # Test equality
        assert user1 == user1  # Same object
        assert user1 != user2  # Different objects with different IDs

        # Test with non-User object
        assert user1 != "not a user"

    def test_user_password_hashing(self):
        """Test that the password is properly hashed."""
        from app.core.security import get_password_hash, verify_password

        # Create a new user with a unique username and email
        unique_id = str(uuid.uuid4())[:8]
        password = f"testpassword_{unique_id}"
        hashed_password = get_password_hash(password)

        user = User(
            username=f"pwduser_{unique_id}",
            email=f"pwduser_{unique_id}@example.com",
            hashed_password=hashed_password,
        )

        self.session.add(user)
        self.session.commit()

        # Should not be able to access plain password
        with pytest.raises(AttributeError):
            _ = user.password

        # Should have hashed password
        assert user.hashed_password is not None
        assert user.hashed_password != password

        # Should be able to verify password
        assert verify_password(password, user.hashed_password) is True
        assert verify_password(f"wrong_{password}", user.hashed_password) is False

    def test_user_activation(self):
        """Test user activation and deactivation."""
        # Create a new user with a unique username and email
        unique_id = str(uuid.uuid4())[:8]
        user = User(
            username=f"activeuser_{unique_id}",
            email=f"activeuser_{unique_id}@example.com",
            hashed_password="hashed_password",
            is_active=True,
        )

        self.session.add(user)
        self.session.commit()

        # Test initial state
        assert user.is_active is True

        # Test deactivation
        user.is_active = False
        self.session.commit()
        self.session.refresh(user)
        assert user.is_active is False

        # Test reactivation
        user.is_active = True
        self.session.commit()
        self.session.refresh(user)
        assert user.is_active is True

    def test_user_str_representation(self):
        """Test the string representation of a user."""
        # Create a new user with a unique username and email
        unique_id = str(uuid.uuid4())[:8]
        user = User(
            username=f"struser_{unique_id}",
            email=f"struser_{unique_id}@example.com",
            hashed_password="hashed_password",
        )

        self.session.add(user)
        self.session.commit()

        # The __repr__ method returns the username, not the ID
        assert str(user) == f"<User {user.username}>"
