import pytest
from fastapi import status

from app.api import deps
from app.core.config import settings
from app.models.user import User
from app.models.models import Role

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


def make_user(db_session, username="bob", email="bob@example.com"):
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
class TestRolesAPI:
    def test_list_and_create_role(self, client, db_session):
        su = make_superuser(db_session)
        client.app.dependency_overrides[deps.get_current_active_superuser] = lambda: su
        client.app.dependency_overrides[deps.get_current_active_user] = lambda: su

        # list initially
        r = client.get(f"{API_PREFIX}/roles/")
        assert r.status_code == status.HTTP_200_OK
        assert isinstance(r.json(), list)

        # create
        r = client.post(f"{API_PREFIX}/roles/", json={"name": "DPS"})
        assert r.status_code == status.HTTP_200_OK
        role = r.json()
        assert role["name"] == "DPS"

        # duplicate -> 400
        r = client.post(f"{API_PREFIX}/roles/", json={"name": "DPS"})
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_forbidden_for_non_superuser(self, client, db_session):
        user = make_user(db_session)
        # Override only get_current_user so the superuser check runs and fails
        client.app.dependency_overrides[deps.get_current_user] = lambda: user

        r = client.post(f"{API_PREFIX}/roles/", json={"name": "HEALER"})
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_get_update_delete_role(self, client, db_session):
        su = make_superuser(db_session)
        client.app.dependency_overrides[deps.get_current_active_superuser] = lambda: su
        client.app.dependency_overrides[deps.get_current_active_user] = lambda: su

        # create one
        r = client.post(f"{API_PREFIX}/roles/", json={"name": "SUPPORT"})
        assert r.status_code == status.HTTP_200_OK
        rid = r.json()["id"]

        # get by id
        r = client.get(f"{API_PREFIX}/roles/{rid}")
        assert r.status_code == status.HTTP_200_OK
        assert r.json()["name"] == "SUPPORT"

        # update
        r = client.put(f"{API_PREFIX}/roles/{rid}", json={"name": "HYBRID"})
        assert r.status_code == status.HTTP_200_OK
        assert r.json()["name"] == "HYBRID"

        # update missing -> 404
        r = client.put(f"{API_PREFIX}/roles/999999", json={"name": "XX"})
        assert r.status_code == status.HTTP_404_NOT_FOUND

        # delete
        r = client.delete(f"{API_PREFIX}/roles/{rid}")
        assert r.status_code == status.HTTP_200_OK

        # get deleted -> 404
        r = client.get(f"{API_PREFIX}/roles/{rid}")
        assert r.status_code == status.HTTP_404_NOT_FOUND

