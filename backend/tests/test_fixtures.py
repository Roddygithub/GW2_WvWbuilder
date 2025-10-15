"""Tests for pytest fixtures."""

import logging
from typing import Dict
from sqlalchemy import text

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.role import Role

# Set up logging
logger = logging.getLogger(__name__)


class TestAuthHeaders:
    """Tests for the auth_headers fixture."""

    async def test_auth_headers_returns_expected_structure(self, auth_headers):
        """Test that auth_headers returns the expected structure."""
        assert isinstance(auth_headers, dict)
        assert "admin" in auth_headers
        assert "user" in auth_headers
        assert "Authorization" in auth_headers["admin"]
        assert "Authorization" in auth_headers["user"]
        assert auth_headers["admin"]["Authorization"].startswith("Bearer ")
        assert auth_headers["user"]["Authorization"].startswith("Bearer ")

    async def test_auth_headers_contains_valid_tokens(
        self, auth_headers: Dict[str, Dict[str, str]], async_client: AsyncClient
    ):
        """Test that the tokens in auth_headers are valid."""
        # Test admin token
        response = await async_client.get(
            "/api/v1/auth/me", headers=auth_headers["admin"]
        )
        assert response.status_code == 200
        data = response.json()
        assert "is_superuser" in data
        assert data["is_superuser"] is True

        # Test user token
        response = await async_client.get(
            "/api/v1/auth/me", headers=auth_headers["user"]
        )
        assert response.status_code == 200
        data = response.json()
        assert "is_superuser" in data
        assert data["is_superuser"] is False


class TestCleanDB:
    """Tests for the clean_db fixture."""

    async def test_clean_db_cleans_tables(
        self, db: AsyncSession, test_user: User, clean_db
    ):
        """Test that clean_db removes all data from tables."""
        # Verify user was created by test_user fixture
        result = await db.execute(text("SELECT COUNT(*) FROM users"))
        count = result.scalar_one()
        assert count > 0, "Test user should exist before cleanup"

        # Trigger cleanup by yielding from the fixture
        async with clean_db():
            # Verify all tables are empty
            result = await db.execute(text("SELECT COUNT(*) FROM users"))
            count = result.scalar_one()
            assert count == 0, "Users table should be empty after cleanup"

            # Verify we can still use the database
            new_user = User(
                username="newuser", email="test@example.com", hashed_password="password"
            )
            db.add(new_user)
            await db.commit()

            result = await db.execute("SELECT COUNT(*) FROM users")
            count = result.scalar_one()
            assert count == 1, "Should be able to add data after cleanup"

    async def test_clean_db_handles_foreign_keys(
        self, db: AsyncSession, test_user: User, clean_db
    ):
        """Test that clean_db handles foreign key constraints correctly."""
        # Create test data with relationships
        role = Role(name="test_role")
        db.add(role)
        await db.flush()

        # This should work because the session rollback handles foreign key constraints
        async with clean_db():
            # Verify all tables are empty
            result = await db.execute(text("SELECT COUNT(*) FROM roles"))
            assert result.scalar_one() == 0, "Roles table should be empty after cleanup"


class TestDatabaseSetup:
    """Tests for database setup and teardown."""

    async def test_database_tables_created(self, db: AsyncSession, setup_database):
        """Test that all expected tables are created."""
        # Get list of tables from the database
        sql = text(
            """
            SELECT name 
            FROM sqlite_master 
            WHERE type='table' 
            AND name NOT LIKE 'sqlite_%'"""
        )
        result = await db.execute(sql)
        tables = {row[0] for row in result.fetchall()}

        # Verify all expected tables exist
        expected_tables = {
            "roles",
            "user_roles",
            "users",
            "builds",
            "compositions",
            "composition_tags",
            "professions",
            "elite_specializations",
            "build_profession",
        }

        missing_tables = expected_tables - tables
        assert not missing_tables, f"Missing tables: {missing_tables}"

    async def test_database_rollback_works(self, db: AsyncSession, clean_db):
        """Test that database rollback works as expected."""
        # Start a transaction
        async with db.begin_nested():
            # Add test data
            user = User(
                username="rollbackuser",
                email="rollback@test.com",
                hashed_password="password",
            )
            db.add(user)
            await db.flush()

            # Verify data is in the database within the transaction
            result = await db.execute(text("SELECT COUNT(*) FROM users"))
            assert result.scalar_one() > 0

        # After rollback, the user should not exist
        result = await db.execute(text("SELECT COUNT(*) FROM users"))
        assert result.scalar_one() == 0, "Data should be rolled back"


class TestFixturesIntegration:
    """Integration tests for fixture interactions."""

    async def test_fixtures_work_together(
        self,
        db: AsyncSession,
        test_user: User,
        auth_headers: Dict[str, Dict[str, str]],
        async_client: AsyncClient,
        clean_db,
    ):
        """Test that all fixtures work together correctly."""
        # Verify test user exists
        result = await db.execute(text("SELECT COUNT(*) FROM users"))
        assert result.scalar_one() > 0, "Test user should exist"

        # Test API access with auth headers
        response = await async_client.get(
            "/api/v1/auth/me", headers=auth_headers["user"]
        )
        assert response.status_code == 200

        # Clean up and verify
        async with clean_db():
            result = await db.execute(text("SELECT COUNT(*) FROM users"))
            assert result.scalar_one() == 0, "Users table should be empty after cleanup"

            # Test that we can still use the database
            new_user = User(
                username="newuser2", email="new@example.com", hashed_password="password"
            )
            db.add(new_user)
            await db.commit()

            result = await db.execute("SELECT COUNT(*) FROM users")
            assert result.scalar_one() == 1, "Should be able to add data after cleanup"
