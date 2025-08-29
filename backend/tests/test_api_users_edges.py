import pytest
from fastapi import status

from app.api import deps
from app.core.config import settings
from app.models.user import User

API_PREFIX = settings.API_V1_STR


def make_user(db_session, username="john", email="john@example.com", is_superuser=False):
    u = User(
        email=email,
        username=username,
        hashed_password="hashed",
        is_active=True,
        is_superuser=is_superuser,
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


@pytest.mark.usefixtures("client")
class TestUsersEdges:
    def test_read_user_by_id_self_branch(self, client, db_session):
        u = make_user(db_session)
        client.app.dependency_overrides[deps.get_current_active_user] = lambda: u

        resp = client.get(f"{API_PREFIX}/users/{u.id}")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["id"] == u.id
