"""
Simple test file to verify the test configuration.
"""

from sqlalchemy import select

from app.models import User


class TestSimpleDB:
    """Simple test class to verify the database setup."""

    async def test_create_user(self, db):
        """Test creating a simple user."""
        # Create a test user
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            full_name="Test User",
        )

        # Add to session and commit
        db.add(user)
        await db.commit()
        await db.refresh(user)

        # Verify the user was created
        assert user.id is not None
        assert user.username == "testuser"

        # Query the user
        result = await db.execute(select(User).where(User.id == user.id))
        db_user = result.scalars().first()
        assert db_user is not None
        assert db_user.username == "testuser"

    async def test_tables_exist(self, db):
        """Verify that all expected tables exist."""
        # Get all table names from the database
        result = await db.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in result.fetchall()}

        # Check for expected tables
        expected_tables = {
            "users",
            "roles",
            "professions",
            "elite_specializations",
            "compositions",
            "composition_tags",
            "builds",
            "user_roles",
            "composition_members",
            "build_profession",
        }

        # Verify all expected tables exist
        for table in expected_tables:
            assert table in tables, f"Table {table} not found in database"
