import pytest
from fastapi import status

from app.api import deps
from app.core.config import settings
from app.models.user import User
from app.models.models import Role, Profession, EliteSpecialization, Composition

API_PREFIX = settings.API_V1_STR


def make_user(db_session, username="u1", email="u1@example.com", is_superuser=False):
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


def seed_role_prof(db_session):
    r = Role(name="DPS")
    p1 = Profession(name="Warrior")
    p2 = Profession(name="Guardian")
    db_session.add_all([r, p1, p2])
    db_session.commit()
    db_session.refresh(r)
    db_session.refresh(p1)
    db_session.refresh(p2)
    return r, p1, p2


@pytest.mark.usefixtures("client")
class TestCompositionsEdges:
    def test_member_validation_branches(self, client, db_session):
        su = make_user(db_session, username="admin", email="admin@example.com", is_superuser=True)
        client.app.dependency_overrides[deps.get_current_active_user] = lambda: su
        client.app.dependency_overrides[deps.get_current_active_superuser] = lambda: su

        r, p1, p2 = seed_role_prof(db_session)
        # elite spec for p1 only
        elite = EliteSpecialization(name="Berserker", profession_id=p1.id)
        db_session.add(elite)
        db_session.commit()
        db_session.refresh(elite)

        # role not found -> 404
        payload = {
            "name": "C1",
            "description": "d",
            "squad_size": 5,
            "is_public": True,
            "members": [
                {
                    "user_id": su.id,
                    "role_id": 99999,
                    "profession_id": p1.id,
                    "elite_specialization_id": None,
                    "role_type": "dps",
                    "notes": None,
                    "is_commander": False,
                    "is_secondary_commander": False,
                    "custom_build_url": None,
                    "priority": 1,
                }
            ],
        }
        resp = client.post(f"{API_PREFIX}/compositions/", json=payload)
        assert resp.status_code == status.HTTP_404_NOT_FOUND

        # profession not found -> 404
        payload["members"][0]["role_id"] = r.id
        payload["members"][0]["profession_id"] = 99999
        resp = client.post(f"{API_PREFIX}/compositions/", json=payload)
        assert resp.status_code == status.HTTP_404_NOT_FOUND

        # elite not found -> 404
        payload["members"][0]["profession_id"] = p1.id
        payload["members"][0]["elite_specialization_id"] = 99999
        resp = client.post(f"{API_PREFIX}/compositions/", json=payload)
        assert resp.status_code == status.HTTP_404_NOT_FOUND

        # elite-profession mismatch -> 400
        payload["members"][0]["elite_specialization_id"] = elite.id
        payload["members"][0]["profession_id"] = p2.id  # mismatch
        resp = client.post(f"{API_PREFIX}/compositions/", json=payload)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_filter_and_permissions(self, client, db_session):
        owner = make_user(db_session, username="owner", email="owner@example.com", is_superuser=False)
        other = make_user(db_session, username="other", email="other@example.com", is_superuser=False)
        su = make_user(db_session, username="admin2", email="admin2@example.com", is_superuser=True)

        client.app.dependency_overrides[deps.get_current_active_user] = lambda: su

        # create one public and one private composition
        c_public = Composition(name="Pub", description="d", squad_size=5, is_public=True, created_by=owner.id)
        c_private = Composition(name="Priv", description="d", squad_size=5, is_public=False, created_by=owner.id)
        db_session.add_all([c_public, c_private])
        db_session.commit()
        db_session.refresh(c_public)
        db_session.refresh(c_private)

        # list with is_public filter
        resp = client.get(f"{API_PREFIX}/compositions/?is_public=true")
        assert resp.status_code == status.HTTP_200_OK
        names = [c["name"] for c in resp.json()]
        assert "Pub" in names and "Priv" not in names

        # reading private as non-owner, non-superuser -> 403
        client.app.dependency_overrides[deps.get_current_active_user] = lambda: other
        resp = client.get(f"{API_PREFIX}/compositions/{c_private.id}")
        assert resp.status_code == status.HTTP_403_FORBIDDEN

        # update not found
        client.app.dependency_overrides[deps.get_current_active_user] = lambda: su
        resp = client.put(f"{API_PREFIX}/compositions/999999", json={"name": "xx"})
        assert resp.status_code == status.HTTP_404_NOT_FOUND

        # update permission denied for non-owner
        client.app.dependency_overrides[deps.get_current_active_user] = lambda: other
        resp = client.put(f"{API_PREFIX}/compositions/{c_private.id}", json={"name": "xx"})
        assert resp.status_code == status.HTTP_403_FORBIDDEN

        # delete not found
        client.app.dependency_overrides[deps.get_current_active_user] = lambda: su
        resp = client.delete(f"{API_PREFIX}/compositions/999999")
        assert resp.status_code == status.HTTP_404_NOT_FOUND

        # delete forbidden for non-owner
        client.app.dependency_overrides[deps.get_current_active_user] = lambda: other
        resp = client.delete(f"{API_PREFIX}/compositions/{c_private.id}")
        assert resp.status_code == status.HTTP_403_FORBIDDEN
