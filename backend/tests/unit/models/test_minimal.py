"""
Minimal test to verify database setup.
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def test_database_tables_exist(db: AsyncSession):
    """Test that the database tables exist."""
    # Get list of tables
    result = await db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
    tables = {row[0] for row in result.fetchall()}

    # Check for required tables
    required_tables = {
        "users",
        "roles",
        "user_roles",
        "professions",
        "elite_specializations",
        "builds",
        "build_profession",
        "compositions",
        "composition_tags",
        "composition_members",
    }

    # Check if all required tables exist
    missing_tables = required_tables - tables
    assert not missing_tables, f"Missing tables: {missing_tables}"


async def test_create_user(db: AsyncSession):
    """Test creating a user in the database."""
    # Create a test user
    result = await db.execute(
        text(
            """
        INSERT INTO users (username, email, hashed_password, is_active, is_superuser)
        VALUES (:username, :email, :hashed_password, :is_active, :is_superuser)
        RETURNING id, username, email, is_active, is_superuser
        """
        ),
        {
            "username": "testuser",
            "email": "test@example.com",
            "hashed_password": "hashed_password",
            "is_active": True,
            "is_superuser": False,
        },
    )
    user = result.fetchone()
    await db.commit()

    # Verify the user was created
    assert user is not None
    assert user["username"] == "testuser"
    assert user["email"] == "test@example.com"
    assert user["is_active"] is True
    assert user["is_superuser"] is False

    # Clean up
    await db.execute(text("DELETE FROM users WHERE id = :id"), {"id": user["id"]})
    await db.commit()
