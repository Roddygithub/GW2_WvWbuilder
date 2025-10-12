"""
Comprehensive tests for the Builds API endpoints.

This module contains extensive test cases covering all CRUD operations,
edge cases, and error conditions for the Builds API.
"""

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.models import Build, User, Profession

pytestmark = pytest.mark.asyncio


class TestBuildsAPIComprehensive:
    """Comprehensive test suite for Builds API endpoints."""

    # Test data
    VALID_BUILD_DATA = {
        "name": "Comprehensive Test Build",
        "description": "A build for comprehensive testing",
        "game_mode": "wvw",
        "team_size": 5,
        "is_public": True,
        "config": {
            "weapons": ["Greatsword", "Sword/Shield"],
            "traits": [1, 2, 3],
            "skills": [1, 2, 3, 4, 5],
        },
        "constraints": {"min_healers": 1, "max_same_profession": 2},
    }

    # ========== Test Create Operations ==========

    async def test_create_build_with_minimal_required_fields(
        self, async_client: AsyncClient, test_user: User, test_profession: Profession
    ):
        """Test creating a build with only the required fields."""
        minimal_data = {
            "name": "Minimal Build",
            "game_mode": "wvw",
            "team_size": 5,
            "profession_ids": [test_profession.id],
            "config": {},
        }

        response = await async_client.post(
            f"{settings.API_V1_STR}/builds/",
            json=minimal_data,
            headers={"Authorization": f"Bearer {test_user.create_access_token()}"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == minimal_data["name"]
        assert data["game_mode"] == minimal_data["game_mode"]
        assert data["team_size"] == minimal_data["team_size"]
        assert data["is_public"] is False  # Default value
        assert data["description"] is None
        assert data["config"] == minimal_data["config"]
        assert data["constraints"] is None
        assert data["created_by_id"] == test_user.id
        assert len(data["professions"]) == 1
        assert data["professions"][0]["id"] == test_profession.id

    async def test_create_build_with_all_fields(
        self, async_client: AsyncClient, test_user: User, test_profession: Profession
    ):
        """Test creating a build with all possible fields."""
        response = await async_client.post(
            f"{settings.API_V1_STR}/builds/",
            json={**self.VALID_BUILD_DATA, "profession_ids": [test_profession.id]},
            headers={"Authorization": f"Bearer {test_user.create_access_token()}"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        for field in ["name", "description", "game_mode", "team_size", "is_public"]:
            assert data[field] == self.VALID_BUILD_DATA[field]
        assert data["config"] == self.VALID_BUILD_DATA["config"]
        assert data["constraints"] == self.VALID_BUILD_DATA["constraints"]
        assert data["created_by_id"] == test_user.id
        assert len(data["professions"]) == 1
        assert data["professions"][0]["id"] == test_profession.id

    async def test_create_build_with_multiple_professions(
        self,
        async_client: AsyncClient,
        test_user: User,
        test_profession: Profession,
        db: AsyncSession,
    ):
        """Test creating a build associated with multiple professions."""
        # Create a second profession
        prof2 = Profession(name="Test Profession 2", description="Another test profession")
        db.add(prof2)
        await db.commit()
        await db.refresh(prof2)

        response = await async_client.post(
            f"{settings.API_V1_STR}/builds/",
            json={
                **self.VALID_BUILD_DATA,
                "profession_ids": [test_profession.id, prof2.id],
            },
            headers={"Authorization": f"Bearer {test_user.create_access_token()}"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert len(data["professions"]) == 2
        prof_ids = {prof["id"] for prof in data["professions"]}
        assert test_profession.id in prof_ids
        assert prof2.id in prof_ids

    async def test_create_build_with_invalid_profession(self, async_client: AsyncClient, test_user: User):
        """Test creating a build with a non-existent profession ID."""
        response = await async_client.post(
            f"{settings.API_V1_STR}/builds/",
            json={
                **self.VALID_BUILD_DATA,
                "profession_ids": [999999],  # Non-existent ID
            },
            headers={"Authorization": f"Bearer {test_user.create_access_token()}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "profession" in response.text.lower()

    async def test_create_build_with_invalid_game_mode(
        self, async_client: AsyncClient, test_user: User, test_profession: Profession
    ):
        """Test creating a build with an invalid game mode."""
        response = await async_client.post(
            f"{settings.API_V1_STR}/builds/",
            json={
                **self.VALID_BUILD_DATA,
                "game_mode": "invalid_mode",
                "profession_ids": [test_profession.id],
            },
            headers={"Authorization": f"Bearer {test_user.create_access_token()}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "game_mode" in response.text.lower()

    async def test_create_build_with_invalid_team_size(
        self, async_client: AsyncClient, test_user: User, test_profession: Profession
    ):
        """Test creating a build with an invalid team size."""
        for invalid_size in [0, -1, 51]:
            response = await async_client.post(
                f"{settings.API_V1_STR}/builds/",
                json={
                    **self.VALID_BUILD_DATA,
                    "team_size": invalid_size,
                    "profession_ids": [test_profession.id],
                },
                headers={"Authorization": f"Bearer {test_user.create_access_token()}"},
            )
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            assert "team_size" in response.text.lower()

    # ========== Test Read Operations ==========

    async def test_get_build_with_relationships(
        self,
        async_client: AsyncClient,
        test_build: Build,
        test_user: User,
        test_profession: Profession,
    ):
        """Test retrieving a build with all its relationships."""
        response = await async_client.get(
            f"{settings.API_V1_STR}/builds/{test_build.id}",
            headers={"Authorization": f"Bearer {test_user.create_access_token()}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_build.id
        assert "created_by" in data
        assert data["created_by"]["id"] == test_user.id
        assert "professions" in data
        assert any(p["id"] == test_profession.id for p in data["professions"])

    async def test_get_private_build_as_owner(
        self,
        async_client: AsyncClient,
        test_user: User,
        test_profession: Profession,
        db: AsyncSession,
    ):
        """Test that a user can retrieve their own private build."""
        # Create a private build
        build_data = {
            "name": "Private Build",
            "game_mode": "wvw",
            "team_size": 5,
            "is_public": False,
            "profession_ids": [test_profession.id],
            "config": {},
        }

        create_response = await async_client.post(
            f"{settings.API_V1_STR}/builds/",
            json=build_data,
            headers={"Authorization": f"Bearer {test_user.create_access_token()}"},
        )
        build_id = create_response.json()["id"]

        # Try to retrieve it
        get_response = await async_client.get(
            f"{settings.API_V1_STR}/builds/{build_id}",
            headers={"Authorization": f"Bearer {test_user.create_access_token()}"},
        )

        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.json()["id"] == build_id

    async def test_get_private_build_as_other_user(
        self,
        async_client: AsyncClient,
        test_user: User,
        test_profession: Profession,
        db: AsyncSession,
    ):
        """Test that a user cannot retrieve another user's private build."""
        # Create a private build
        build_data = {
            "name": "Private Build",
            "game_mode": "wvw",
            "team_size": 5,
            "is_public": False,
            "profession_ids": [test_profession.id],
            "config": {},
        }

        create_response = await async_client.post(
            f"{settings.API_V1_STR}/builds/",
            json=build_data,
            headers={"Authorization": f"Bearer {test_user.create_access_token()}"},
        )
        build_id = create_response.json()["id"]

        # Create a second user
        from app.crud.crud_user import user as crud_user
        from app.schemas.user import UserCreate

        user2_data = UserCreate(
            email="test2@example.com",
            username="testuser2",
            password="testpassword",
            full_name="Test User 2",
        )
        user2 = await crud_user.create(db, obj_in=user2_data)

        # Try to retrieve the build as the second user
        get_response = await async_client.get(
            f"{settings.API_V1_STR}/builds/{build_id}",
            headers={"Authorization": f"Bearer {user2.create_access_token()}"},
        )

        assert get_response.status_code == status.HTTP_403_FORBIDDEN

    async def test_get_public_build_as_any_user(
        self,
        async_client: AsyncClient,
        test_user: User,
        test_profession: Profession,
        db: AsyncSession,
    ):
        """Test that any authenticated user can retrieve a public build."""
        # Create a public build
        build_data = {
            "name": "Public Build",
            "game_mode": "wvw",
            "team_size": 5,
            "is_public": True,
            "profession_ids": [test_profession.id],
            "config": {},
        }

        create_response = await async_client.post(
            f"{settings.API_V1_STR}/builds/",
            json=build_data,
            headers={"Authorization": f"Bearer {test_user.create_access_token()}"},
        )
        build_id = create_response.json()["id"]

        # Create a second user
        from app.crud.crud_user import user as crud_user
        from app.schemas.user import UserCreate

        user2_data = UserCreate(
            email="test2@example.com",
            username="testuser2",
            password="testpassword",
            full_name="Test User 2",
        )
        user2 = await crud_user.create(db, obj_in=user2_data)

        # Try to retrieve the build as the second user
        get_response = await async_client.get(
            f"{settings.API_V1_STR}/builds/{build_id}",
            headers={"Authorization": f"Bearer {user2.create_access_token()}"},
        )

        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.json()["id"] == build_id

    # ========== Test Update Operations ==========

    async def test_update_build_partial_data(self, async_client: AsyncClient, test_build: Build, test_user: User):
        """Test updating a build with partial data (PATCH-like behavior)."""
        update_data = {"description": "Updated description only"}

        response = await async_client.put(
            f"{settings.API_V1_STR}/builds/{test_build.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {test_user.create_access_token()}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == test_build.name  # Should remain unchanged
        assert data["description"] == update_data["description"]
        assert data["game_mode"] == test_build.game_mode
        assert data["team_size"] == test_build.team_size

    async def test_update_build_change_professions(
        self,
        async_client: AsyncClient,
        test_build: Build,
        test_user: User,
        test_profession: Profession,
        db: AsyncSession,
    ):
        """Test updating a build to change its associated professions."""
        # Create a new profession
        new_prof = Profession(name="New Test Profession", description="New test profession")
        db.add(new_prof)
        await db.commit()
        await db.refresh(new_prof)

        # Update the build to use the new profession
        response = await async_client.put(
            f"{settings.API_V1_STR}/builds/{test_build.id}",
            json={"profession_ids": [new_prof.id]},
            headers={"Authorization": f"Bearer {test_user.create_access_token()}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["professions"]) == 1
        assert data["professions"][0]["id"] == new_prof.id

        # Verify the change in the database
        from sqlalchemy.orm import selectinload

        result = await db.execute(
            select(Build).options(selectinload(Build.professions)).where(Build.id == test_build.id)
        )
        updated_build = result.scalar_one()
        assert len(updated_build.professions) == 1
        assert updated_build.professions[0].id == new_prof.id

    async def test_update_nonexistent_build(self, async_client: AsyncClient, test_user: User):
        """Test updating a build that doesn't exist."""
        response = await async_client.put(
            f"{settings.API_V1_STR}/builds/999999",
            json={"name": "Nonexistent Build"},
            headers={"Authorization": f"Bearer {test_user.create_access_token()}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_build_unauthorized(self, async_client: AsyncClient, test_build: Build, db: AsyncSession):
        """Test that a user cannot update another user's build."""
        # Create a second user
        from app.crud.crud_user import user as crud_user
        from app.schemas.user import UserCreate

        user2_data = UserCreate(
            email="test2@example.com",
            username="testuser2",
            password="testpassword",
            full_name="Test User 2",
        )
        user2 = await crud_user.create(db, obj_in=user2_data)

        # Try to update the build as the second user
        response = await async_client.put(
            f"{settings.API_V1_STR}/builds/{test_build.id}",
            json={"name": "Unauthorized Update"},
            headers={"Authorization": f"Bearer {user2.create_access_token()}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    # ========== Test Delete Operations ==========

    async def test_delete_build_unauthorized(self, async_client: AsyncClient, test_build: Build, db: AsyncSession):
        """Test that a user cannot delete another user's build."""
        # Create a second user
        from app.crud.crud_user import user as crud_user
        from app.schemas.user import UserCreate

        user2_data = UserCreate(
            email="test2@example.com",
            username="testuser2",
            password="testpassword",
            full_name="Test User 2",
        )
        user2 = await crud_user.create(db, obj_in=user2_data)

        # Try to delete the build as the second user
        response = await async_client.delete(
            f"{settings.API_V1_STR}/builds/{test_build.id}",
            headers={"Authorization": f"Bearer {user2.create_access_token()}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Verify the build still exists
        result = await db.execute(select(Build).where(Build.id == test_build.id))
        assert result.scalar_one_or_none() is not None

    # ========== Test List Operations ==========

    async def test_list_builds_filter_by_public(
        self,
        async_client: AsyncClient,
        test_user: User,
        test_profession: Profession,
        db: AsyncSession,
    ):
        """Test filtering builds by public/private status."""
        # Create a mix of public and private builds
        builds_data = [
            {
                "name": f"Build {i}",
                "game_mode": "wvw",
                "team_size": 5,
                "is_public": i % 2 == 0,
                "profession_ids": [test_profession.id],
                "config": {},
            }
            for i in range(5)
        ]

        # Create the builds
        for build_data in builds_data:
            await async_client.post(
                f"{settings.API_V1_STR}/builds/",
                json=build_data,
                headers={"Authorization": f"Bearer {test_user.create_access_token()}"},
            )

        # Test filtering public builds
        public_response = await async_client.get(
            f"{settings.API_V1_STR}/builds/",
            params={"is_public": True},
            headers={"Authorization": f"Bearer {test_user.create_access_token()}"},
        )
        assert public_response.status_code == status.HTTP_200_OK
        public_builds = public_response.json()
        assert len(public_builds) >= 2  # At least 2 public builds from the 5 we created
        assert all(build["is_public"] for build in public_builds)

        # Test filtering private builds
        private_response = await async_client.get(
            f"{settings.API_V1_STR}/builds/",
            params={"is_public": False},
            headers={"Authorization": f"Bearer {test_user.create_access_token()}"},
        )
        assert private_response.status_code == status.HTTP_200_OK
        private_builds = private_response.json()
        assert len(private_builds) >= 2  # At least 2 private builds from the 5 we created
        assert all(not build["is_public"] for build in private_builds)

    async def test_list_builds_pagination(
        self,
        async_client: AsyncClient,
        test_user: User,
        test_profession: Profession,
        db: AsyncSession,
    ):
        """Test pagination when listing builds."""
        # Create multiple builds
        for i in range(15):
            build_data = {
                "name": f"Build {i}",
                "game_mode": "wvw",
                "team_size": 5,
                "is_public": True,
                "profession_ids": [test_profession.id],
                "config": {},
            }
            await async_client.post(
                f"{settings.API_V1_STR}/builds/",
                json=build_data,
                headers={"Authorization": f"Bearer {test_user.create_access_token()}"},
            )

        # Test first page (5 items)
        page1 = await async_client.get(
            f"{settings.API_V1_STR}/builds/",
            params={"skip": 0, "limit": 5},
            headers={"Authorization": f"Bearer {test_user.create_access_token()}"},
        )
        assert page1.status_code == status.HTTP_200_OK
        page1_data = page1.json()
        assert len(page1_data) == 5

        # Test second page (next 5 items)
        page2 = await async_client.get(
            f"{settings.API_V1_STR}/builds/",
            params={"skip": 5, "limit": 5},
            headers={"Authorization": f"Bearer {test_user.create_access_token()}"},
        )
        assert page2.status_code == status.HTTP_200_OK
        page2_data = page2.json()
        assert len(page2_data) == 5

        # Verify the pages don't have overlapping items
        page1_ids = {build["id"] for build in page1_data}
        page2_ids = {build["id"] for build in page2_data}
        assert page1_ids.isdisjoint(page2_ids)

    # ========== Test Edge Cases ==========

    async def test_create_build_with_large_config(
        self, async_client: AsyncClient, test_user: User, test_profession: Profession
    ):
        """Test creating a build with a large config object."""
        large_config = {
            "traits": list(range(100)),
            "skills": ["skill1"] * 50,
            "equipment": {f"slot_{i}": f"item_{i}" for i in range(20)},
            "metadata": {
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
                "version": "1.0.0",
                "tags": [f"tag{i}" for i in range(20)],
            },
        }

        response = await async_client.post(
            f"{settings.API_V1_STR}/builds/",
            json={
                "name": "Build with Large Config",
                "game_mode": "wvw",
                "team_size": 5,
                "profession_ids": [test_profession.id],
                "config": large_config,
            },
            headers={"Authorization": f"Bearer {test_user.create_access_token()}"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["config"] == large_config

    async def test_create_build_with_special_characters(
        self, async_client: AsyncClient, test_user: User, test_profession: Profession
    ):
        """Test creating a build with special characters in the name and description."""
        special_chars = "!@#$%^&*()_+-=[]{}|;:'\",.<>/?`~"

        response = await async_client.post(
            f"{settings.API_V1_STR}/builds/",
            json={
                "name": f"Build with special chars: {special_chars}",
                "description": f"Description with special chars: {special_chars}",
                "game_mode": "wvw",
                "team_size": 5,
                "profession_ids": [test_profession.id],
                "config": {},
            },
            headers={"Authorization": f"Bearer {test_user.create_access_token()}"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == f"Build with special chars: {special_chars}"
        assert data["description"] == f"Description with special chars: {special_chars}"
