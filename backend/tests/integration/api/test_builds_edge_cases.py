from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4

from app.core.config import settings


def test_create_build_with_empty_name(client: TestClient, db: Session) -> None:
    """Test creating a build with an empty name."""
    build_data = {
        "name": "",  # Empty name
        "description": "Test description",
        "game_mode": "wvw",
        "team_size": 5,
        "is_public": True,
        "profession_ids": [1, 2, 3],
    }

    response = client.post(f"{settings.API_V1_STR}/builds/", json=build_data, headers=client.headers)
    assert response.status_code == 422  # Should fail validation


def test_create_build_with_invalid_game_mode(client: TestClient, db: Session) -> None:
    """Test creating a build with an invalid game mode."""
    build_data = {
        "name": f"Test Build {uuid4()}",
        "description": "Test description",
        "game_mode": "invalid_mode",  # Invalid game mode
        "team_size": 5,
        "is_public": True,
        "profession_ids": [1, 2, 3],
    }

    response = client.post(f"{settings.API_V1_STR}/builds/", json=build_data, headers=client.headers)
    assert response.status_code == 422  # Should fail validation


def test_update_nonexistent_build(client: TestClient, db: Session) -> None:
    """Test updating a build that doesn't exist."""
    update_data = {"name": "Updated Name", "description": "This build doesn't exist"}

    response = client.put(
        f"{settings.API_V1_STR}/builds/999999", json=update_data, headers=client.headers  # Non-existent ID
    )
    assert response.status_code == 404


def test_delete_nonexistent_build(client: TestClient, db: Session) -> None:
    """Test deleting a build that doesn't exist."""
    response = client.delete(f"{settings.API_V1_STR}/builds/999999", headers=client.headers)  # Non-existent ID
    assert response.status_code == 404


def test_generate_build_with_no_professions(client: TestClient, db: Session) -> None:
    """Test generating a build with no professions available."""
    # Clear all professions
    db.query(Profession).delete()
    db.commit()

    build_data = {
        "team_size": 3,
        "required_roles": ["healer", "dps", "support"],
        "preferred_professions": [],
        "max_duplicates": 2,
        "min_healers": 1,
        "min_dps": 1,
        "min_support": 1,
        "constraints": {},
    }

    response = client.post(f"{settings.API_V1_STR}/builds/generate", json=build_data, headers=client.headers)

    assert response.status_code == 200
    assert response.json()["success"] is False
    assert "No valid professions" in response.json()["message"]


def test_list_builds_with_filters(client: TestClient, db: Session) -> None:
    """Test listing builds with various filters."""
    # Create test builds with different attributes
    builds = [{"name": f"Public Build {i}", "is_public": True, "game_mode": "wvw"} for i in range(3)] + [
        {"name": f"Private Build {i}", "is_public": False, "game_mode": "pvp"} for i in range(2)
    ]

    for build_data in builds:
        data = {
            "name": f"{build_data['name']} {uuid4()}",
            "description": "Test build",
            "game_mode": build_data["game_mode"],
            "team_size": 5,
            "is_public": build_data["is_public"],
            "profession_ids": [1, 2, 3],
        }
        client.post(f"{settings.API_V1_STR}/builds/", json=data, headers=client.headers)

    # Test filtering by game_mode
    response = client.get(f"{settings.API_V1_STR}/builds/", params={"game_mode": "wvw"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3  # At least the 3 we created

    # Test filtering by is_public
    response = client.get(f"{settings.API_V1_STR}/builds/", params={"is_public": "true"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3  # At least the 3 public builds

    # Test searching by name
    response = client.get(f"{settings.API_V1_STR}/builds/", params={"search": "Public Build"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3  # Should find all public builds
