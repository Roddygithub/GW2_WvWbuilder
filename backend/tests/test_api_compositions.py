import pytest
from fastapi import status

from app.api import deps
from app.core.config import settings
from app.models import User, Role, Profession

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


def seed_refs(db_session):
    r = Role(name="DPS")
    p = Profession(name="Warrior")
    db_session.add_all([r, p])
    db_session.commit()
    return r, p


@pytest.mark.usefixtures("client")
class TestCompositionsAPI:
    def test_crud_composition(self, client, db_session):
        su = make_superuser(db_session)
        client.app.dependency_overrides[deps.get_current_active_user] = lambda: su
        client.app.dependency_overrides[deps.get_current_active_superuser] = lambda: su
        role, prof = seed_refs(db_session)

        # create with minimal valid payload
        payload = {
            "name": "Test Squad",
            "description": "desc",
            "squad_size": 10,
            "is_public": True,
            "tags": [],
        }
        r = client.post(f"{API_PREFIX}/compositions/", json=payload)
        assert r.status_code == status.HTTP_201_CREATED
        comp = r.json()
        cid = comp["id"]
        assert comp["name"] == payload["name"]

        # list
        r = client.get(f"{API_PREFIX}/compositions/")
        assert r.status_code == status.HTTP_200_OK
        assert isinstance(r.json(), list)

        # get by id
        r = client.get(f"{API_PREFIX}/compositions/{cid}")
        assert r.status_code == status.HTTP_200_OK

        # update basic fields
        r = client.put(f"{API_PREFIX}/compositions/{cid}", json={"name": "Updated Squad"})
        assert r.status_code == status.HTTP_200_OK
        assert r.json()["name"] == "Updated Squad"

        # replace members including validation
        members = [
            {
                "user_id": su.id,
                "role_id": role.id,
                "profession_id": prof.id,
                "elite_specialization_id": None,
                "role_type": "healer",
                "notes": "n",
                "is_commander": False,
                "is_secondary_commander": False,
                "custom_build_url": None,
                "priority": 1,
            }
        ]
        r = client.put(f"{API_PREFIX}/compositions/{cid}", json={"members": members})
        assert r.status_code == status.HTTP_200_OK
        assert isinstance(r.json()["members"], list)
        assert len(r.json()["members"]) == 1

        # delete
        r = client.delete(f"{API_PREFIX}/compositions/{cid}")
        assert r.status_code == status.HTTP_200_OK

        # get deleted -> 404
        r = client.get(f"{API_PREFIX}/compositions/{cid}")
        assert r.status_code == status.HTTP_404_NOT_FOUND

    def test_member_validation_404s(self, client, db_session):
        su = make_superuser(db_session)
        client.app.dependency_overrides[deps.get_current_active_user] = lambda: su
        client.app.dependency_overrides[deps.get_current_active_superuser] = lambda: su
        # no refs seeded, use invalid ids
        payload = {
            "name": "Bad Squad",
            "description": "desc",
            "squad_size": 5,
            "is_public": True,
            "members": [
                {
                    "user_id": 9999,
                    "role_id": 1,
                    "profession_id": 1,
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
        r = client.post(f"{API_PREFIX}/compositions/", json=payload)
        assert r.status_code == status.HTTP_404_NOT_FOUND

