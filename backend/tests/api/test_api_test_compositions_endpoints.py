"""
Tests for the Compositions API endpoints.
"""

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import Composition


@pytest.mark.asyncio
class TestCompositionsAPI:
    """Test suite for Compositions API endpoints."""

    async def test_create_composition(self, async_client: AsyncClient, db: AsyncSession, user_factory, auth_headers):
        """Test creating a new composition."""
        user = await user_factory(username="comp_creator")
        headers = await auth_headers(username=user.username, password="testpassword")
        composition_data = {
            "name": "My WvW Zerg",
            "description": "A composition for WvW zerging.",
            "squad_size": 20,
            "is_public": True,
            "game_mode": "wvw",
        }

        response = await async_client.post(
            f"{settings.API_V1_STR}/compositions/", json=composition_data, headers=headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == composition_data["name"]
        assert data["created_by_id"] == user.id

        # Verify in DB
        comp = await db.get(Composition, data["id"])
        assert comp is not None
        assert comp.name == "My WvW Zerg"

    async def test_read_compositions(self, async_client: AsyncClient, composition_factory, user_factory, auth_headers):
        """Test reading a list of compositions."""
        user = await user_factory(username="comp_user")
        await composition_factory(name="Public Comp", is_public=True)
        await composition_factory(name="Private Comp", is_public=False, user=user)

        headers = await auth_headers(username=user.username, password="testpassword")
        response = await async_client.get(f"{settings.API_V1_STR}/compositions/", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2  # User sees their own private + public comps
        assert any(c["name"] == "Public Comp" for c in data)
        assert any(c["name"] == "Private Comp" for c in data)

    async def test_read_composition(self, async_client: AsyncClient, composition_factory, auth_headers):
        """Test retrieving a single composition by ID."""
        comp = await composition_factory(name="Readable Comp")
        headers = await auth_headers(username="reader")

        response = await async_client.get(f"{settings.API_V1_STR}/compositions/{comp.id}", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == comp.id
        assert data["name"] == "Readable Comp"

    async def test_read_nonexistent_composition(self, async_client: AsyncClient, auth_headers):
        """Test retrieving a non-existent composition by ID."""
        headers = await auth_headers()
        response = await async_client.get(f"{settings.API_V1_STR}/compositions/999999", headers=headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        error_data = response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()

    async def test_update_composition(self, async_client: AsyncClient, composition_factory, user_factory, auth_headers):
        """Test updating an existing composition."""
        user = await user_factory(username="updater")
        comp = await composition_factory(user=user)
        headers = await auth_headers(username=user.username, password="testpassword")

        update_data = {"name": "Updated Name", "is_public": False}
        response = await async_client.put(
            f"{settings.API_V1_STR}/compositions/{comp.id}", json=update_data, headers=headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["is_public"] is False

    async def test_update_nonexistent_composition(self, async_client: AsyncClient, auth_headers):
        """Test updating a non-existent composition."""
        headers = await auth_headers()
        update_data = {"name": "This will fail"}

        response = await async_client.put(
            f"{settings.API_V1_STR}/compositions/999999", json=update_data, headers=headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_composition(
        self, async_client: AsyncClient, db: AsyncSession, composition_factory, user_factory, auth_headers
    ):
        """Test deleting a composition."""
        user = await user_factory(username="deleter")
        comp = await composition_factory(user=user)
        headers = await auth_headers(username=user.username, password="testpassword")

        response = await async_client.delete(f"{settings.API_V1_STR}/compositions/{comp.id}", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        assert "deleted successfully" in response.json()["detail"]

        # Verify it's gone from DB
        deleted_comp = await db.get(Composition, comp.id)
        assert deleted_comp is None

    async def test_delete_nonexistent_composition(self, async_client: AsyncClient, auth_headers):
        """Test deleting a non-existent composition."""
        headers = await auth_headers()

        response = await async_client.delete(f"{settings.API_V1_STR}/compositions/999999", headers=headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        error_data = response.json()
        assert "not found" in error_data["detail"].lower()

    async def test_unauthorized_update_composition(
        self, async_client: AsyncClient, composition_factory, user_factory, auth_headers
    ):
        """Test that a user cannot update a composition they don't own."""
        owner = await user_factory(username="owner1")
        other_user = await user_factory(username="other1")
        comp = await composition_factory(user=owner)

        other_user_headers = await auth_headers(username=other_user.username, password="testpassword")

        update_data = {"name": "Unauthorized Update"}
        response = await async_client.put(
            f"{settings.API_V1_STR}/compositions/{comp.id}", json=update_data, headers=other_user_headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_unauthorized_delete_composition(
        self, async_client: AsyncClient, composition_factory, user_factory, auth_headers
    ):
        """Test that a user cannot delete a composition they don't own."""
        owner = await user_factory(username="owner2")
        other_user = await user_factory(username="other2")
        comp = await composition_factory(user=owner)

        other_user_headers = await auth_headers(username=other_user.username, password="testpassword")

        response = await async_client.delete(
            f"{settings.API_V1_STR}/compositions/{comp.id}", headers=other_user_headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_read_private_composition_unauthorized(
        self, async_client: AsyncClient, composition_factory, user_factory, auth_headers
    ):
        """Test that a user cannot read a private composition they don't own."""
        owner = await user_factory(username="owner3")
        other_user = await user_factory(username="other3")
        private_comp = await composition_factory(user=owner, is_public=False)

        other_user_headers = await auth_headers(username=other_user.username, password="testpassword")

        response = await async_client.get(
            f"{settings.API_V1_STR}/compositions/{private_comp.id}", headers=other_user_headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "detail" in response.json()
        assert "Not enough permissions" in response.json()["detail"]

    async def test_read_private_composition_as_unauthenticated(
        self, async_client: AsyncClient, composition_factory, user_factory
    ):
        """Test that an unauthenticated user cannot read a private composition."""
        owner = await user_factory(username="owner_unauth")
        private_comp = await composition_factory(user=owner, is_public=False)

        response = await async_client.get(f"{settings.API_V1_STR}/compositions/{private_comp.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_read_private_composition_as_admin(
        self, async_client: AsyncClient, composition_factory, user_factory, auth_headers
    ):
        """Test that an admin can read any private composition."""
        owner = await user_factory(username="owner_admin_read")
        private_comp = await composition_factory(user=owner, is_public=False)

        admin_headers = await auth_headers(username="admin_comp_reader", is_superuser=True)

        response = await async_client.get(
            f"{settings.API_V1_STR}/compositions/{private_comp.id}", headers=admin_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == private_comp.id
        assert data["name"] == private_comp.name
        assert data["is_public"] is False

    async def test_admin_can_access_private_composition(
        self, async_client: AsyncClient, composition_factory, user_factory, auth_headers
    ):
        """Test that an admin can read any private composition."""
        owner = await user_factory(username="owner4")
        private_comp = await composition_factory(user=owner, is_public=False)

        admin_headers = await auth_headers(username="admin", password="password", is_superuser=True)

        response = await async_client.get(
            f"{settings.API_V1_STR}/compositions/{private_comp.id}", headers=admin_headers
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == private_comp.id


@pytest.mark.asyncio
class TestCompositionAPIEdgeCases:
    """Tests for edge cases and validation errors in Compositions API."""

    @pytest.mark.parametrize(
        "name, error_message",
        [
            ("a", "at least 2 characters"),  # Too short
            ("", "at least 2 characters"),  # Empty string
            ("a" * 101, "at most 100 characters"),  # Too long
        ],
    )
    async def test_create_composition_name_validation(
        self, async_client: AsyncClient, auth_headers, name, error_message
    ):
        """Test creating a composition with invalid name lengths."""
        headers = await auth_headers()
        composition_data = {"name": name, "squad_size": 5}

        response = await async_client.post(
            f"{settings.API_V1_STR}/compositions/", json=composition_data, headers=headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        errors = response.json()["detail"]
        assert any(
            error_message in err["msg"] for err in errors if "name" in err["loc"]
        ), f"Expected error '{error_message}' for name '{name}'"

    @pytest.mark.parametrize(
        "size, error_part",
        [
            (0, "greater than or equal to 1"),
            (51, "less than or equal to 50"),
            (-1, "greater than or equal to 1"),
            ("not-an-int", "Input should be a valid integer"),
            (None, "Input should be a valid integer"),
        ],
    )
    async def test_create_composition_invalid_squad_size(
        self, async_client: AsyncClient, auth_headers, size, error_part
    ):
        """Test creating a composition with an invalid squad size."""
        headers = await auth_headers()
        composition_data = {"name": "Invalid Size", "squad_size": size}

        response = await async_client.post(
            f"{settings.API_V1_STR}/compositions/", json=composition_data, headers=headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        errors = response.json()["detail"]
        assert any(
            error_part in err["msg"] for err in errors if "squad_size" in err["loc"]
        ), f"Expected error containing '{error_part}' for squad_size={size}, got: {errors}"

    @pytest.mark.parametrize("size", [1, 50])
    async def test_create_composition_valid_squad_size(self, async_client: AsyncClient, auth_headers, size):
        """Test creating a composition with valid boundary squad sizes."""
        headers = await auth_headers()
        composition_data = {
            "name": f"Valid Size {size}",
            "squad_size": size,
            "is_public": True,
            "game_mode": "wvw",
        }
        response = await async_client.post(
            f"{settings.API_V1_STR}/compositions/", json=composition_data, headers=headers
        )
        assert (
            response.status_code == status.HTTP_201_CREATED
        ), f"Failed for valid size {size}. Response: {response.json()}"

    @pytest.mark.parametrize("missing_field", ["name", "squad_size"])
    async def test_create_composition_missing_required_field(
        self, async_client: AsyncClient, auth_headers, missing_field
    ):
        """Test creating a composition with a missing required field."""
        headers = await auth_headers()
        composition_data = {"name": "Test Comp", "description": "This will fail", "squad_size": 5}
        del composition_data[missing_field]

        response = await async_client.post(
            f"{settings.API_V1_STR}/compositions/", json=composition_data, headers=headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        errors = response.json()["detail"]
        assert any(
            err["type"] == "missing" and missing_field in err["loc"] for err in errors
        ), f"Expected 'missing' error for field '{missing_field}'"

    @pytest.mark.parametrize(
        "field, value, error_type",
        [
            ("name", 123, "string_type"),
            ("squad_size", "not-an-int", "int_parsing"),
            ("is_public", "not-a-bool", "bool_parsing"),
        ],
    )
    async def test_create_composition_invalid_types(
        self, async_client: AsyncClient, auth_headers, field, value, error_type
    ):
        """Test creating a composition with invalid data types."""
        headers = await auth_headers()
        composition_data = {"name": "Valid Name", "squad_size": 5, field: value}

        response = await async_client.post(
            f"{settings.API_V1_STR}/compositions/", json=composition_data, headers=headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        errors = response.json()["detail"]
        assert any(error_type in err["type"] for err in errors if field in err["loc"])
