import pytest
from fastapi import status

from app.api import deps
from app.core.config import settings
from app.models.user import User

API_PREFIX = settings.API_V1_STR


def make_superuser(db_session):
    su = User(
        email="admin@example.com",
        username="admin",
        hashed_password="hashed",
        is_active=True,
        is_superuser=True,
    )
    db_session.add(su)
    db_session.commit()
    db_session.refresh(su)
    return su


def make_user(db_session, username="john", email="john@example.com"):
    u = User(
        email=email,
        username=username,
        hashed_password="hashed",
        is_active=True,
        is_superuser=False,
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


@pytest.mark.usefixtures("client")
class TestUsersAPI:
    def test_list_users_requires_superuser(self, client, db_session):
        su = make_superuser(db_session)

        # Override deps to inject superuser
        client.app.dependency_overrides[deps.get_current_active_superuser] = lambda: su

        resp = client.get(f"{API_PREFIX}/users/")
        assert resp.status_code == status.HTTP_200_OK
        assert isinstance(resp.json(), list)

    def test_create_user(self, client, db_session):
        su = make_superuser(db_session)
        client.app.dependency_overrides[deps.get_current_active_superuser] = lambda: su

        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
            "is_active": True,
            "is_superuser": False,
        }
        resp = client.post(f"{API_PREFIX}/users/", json=payload)
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["username"] == payload["username"]
        assert data["email"] == payload["email"]
        assert "id" in data

    def test_me_and_get_by_id_and_update(self, client, db_session):
        su = make_superuser(db_session)
        other = make_user(db_session, username="alice", email="alice@example.com")

        client.app.dependency_overrides[deps.get_current_active_user] = lambda: su
        client.app.dependency_overrides[deps.get_current_active_superuser] = lambda: su

        # /me returns current user
        resp = client.get(f"{API_PREFIX}/users/me")
        assert resp.status_code == status.HTTP_200_OK
        me = resp.json()
        assert me["username"] == su.username

        # get by id (as superuser)
        resp = client.get(f"{API_PREFIX}/users/{other.id}")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["username"] == other.username

        # update other as superuser
        payload = {"username": "alice_2"}
        resp = client.put(f"{API_PREFIX}/users/{other.id}", json=payload)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["username"] == "alice_2"

        # Non-superuser trying to read another user should fail
        client.app.dependency_overrides[deps.get_current_active_user] = lambda: other
        resp = client.get(f"{API_PREFIX}/users/{su.id}")
        # Endpoint returns 400 for insufficient privileges
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

        # Get non-existent by id -> returns None => should be 200 with null? Endpoint returns object directly; if None, FastAPI returns null
        # We instead test update on missing -> 404
        resp = client.put(f"{API_PREFIX}/users/999999", json={"username": "valid_name"})
        assert resp.status_code == status.HTTP_404_NOT_FOUND
