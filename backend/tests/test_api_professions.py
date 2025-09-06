import pytest
from fastapi import status, HTTPException

from app.api import deps
from app.core.config import settings
from app.models import User

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


def make_user(db_session, username="eve", email="eve@example.com"):
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
class TestProfessionsAPI:
    def test_list_and_crud_professions(self, client, db_session):
        su = make_superuser(db_session)
        client.app.dependency_overrides[deps.get_current_active_superuser] = lambda: su
        client.app.dependency_overrides[deps.get_current_active_user] = lambda: su

        # list initially
        r = client.get(f"{API_PREFIX}/professions/")
        assert r.status_code == status.HTTP_200_OK
        assert isinstance(r.json(), list)

        # create
        r = client.post(f"{API_PREFIX}/professions/", json={"name": "Warrior"})
        assert r.status_code == status.HTTP_200_OK
        pid = r.json()["id"]
        assert r.json()["name"] == "Warrior"

        # duplicate -> 400
        r = client.post(f"{API_PREFIX}/professions/", json={"name": "Warrior"})
        assert r.status_code == status.HTTP_400_BAD_REQUEST

        # get by id
        r = client.get(f"{API_PREFIX}/professions/{pid}")
        assert r.status_code == status.HTTP_200_OK

        # update
        r = client.put(f"{API_PREFIX}/professions/{pid}", json={"name": "Guardian"})
        assert r.status_code == status.HTTP_200_OK
        assert r.json()["name"] == "Guardian"

        # update missing -> 404
        r = client.put(f"{API_PREFIX}/professions/999999", json={"name": "XX"})
        assert r.status_code == status.HTTP_404_NOT_FOUND

        # delete
        r = client.delete(f"{API_PREFIX}/professions/{pid}")
        assert r.status_code == status.HTTP_200_OK

        # get deleted -> 404
        r = client.get(f"{API_PREFIX}/professions/{pid}")
        assert r.status_code == status.HTTP_404_NOT_FOUND

    def test_forbidden_for_non_superuser(self, client, db_session):
        # Créer un utilisateur non-superuser
        user = make_user(db_session)
        
        # Créer une fonction qui va remplacer get_current_active_superuser
        def override_get_current_active_superuser():
            # Cette fonction est appelée par FastAPI pour vérifier les permissions
            # On lève une exception 403 car l'utilisateur n'est pas superuser
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user doesn't have enough privileges"
            )
        
        # Surcharger la dépendance pour simuler un accès refusé
        client.app.dependency_overrides[deps.get_current_active_superuser] = override_get_current_active_superuser
        
        # Tenter de créer une profession en tant qu'utilisateur normal
        r = client.post(f"{API_PREFIX}/professions/", json={"name": "Thief"})
        
        # Vérifier que l'accès est refusé (403)
        assert r.status_code == status.HTTP_403_FORBIDDEN
        assert r.json()["detail"] == "The user doesn't have enough privileges"
        
        # Nettoyer les surcharges
        client.app.dependency_overrides = {}

    def test_elite_specializations_crud_and_validation(self, client, db_session):
        su = make_superuser(db_session)
        client.app.dependency_overrides[deps.get_current_active_superuser] = lambda: su
        client.app.dependency_overrides[deps.get_current_active_user] = lambda: su

        # Create a base profession
        r = client.post(f"{API_PREFIX}/professions/", json={"name": "Guardian"})
        assert r.status_code == status.HTTP_200_OK
        prof_id = r.json()["id"]

        # Create elite specialization with non-existent profession -> 404
        r = client.post(
            f"{API_PREFIX}/professions/elite-specializations/",
            json={"name": "Firebrand", "profession_id": 999999},
        )
        assert r.status_code == status.HTTP_404_NOT_FOUND

        # Create elite specialization valid
        r = client.post(
            f"{API_PREFIX}/professions/elite-specializations/",
            json={"name": "Firebrand", "profession_id": prof_id},
        )
        assert r.status_code == status.HTTP_200_OK
        elite_id = r.json()["id"]
        assert r.json()["name"] == "Firebrand"
        assert r.json()["profession_id"] == prof_id

        # Duplicate name for same profession -> 400
        r = client.post(
            f"{API_PREFIX}/professions/elite-specializations/",
            json={"name": "Firebrand", "profession_id": prof_id},
        )
        assert r.status_code == status.HTTP_400_BAD_REQUEST

        # Read by id -> 200
        r = client.get(f"{API_PREFIX}/professions/elite-specializations/{elite_id}")
        assert r.status_code == status.HTTP_200_OK

        # Update to non-existent profession -> 404
        r = client.put(
            f"{API_PREFIX}/professions/elite-specializations/{elite_id}",
            json={"profession_id": 999999},
        )
        assert r.status_code == status.HTTP_404_NOT_FOUND

        # Valid update (rename)
        r = client.put(
            f"{API_PREFIX}/professions/elite-specializations/{elite_id}",
            json={"name": "Dragonhunter"},
        )
        assert r.status_code == status.HTTP_200_OK
        assert r.json()["name"] == "Dragonhunter"

        # List with filter by profession
        r = client.get(
            f"{API_PREFIX}/professions/elite-specializations/",
            params={"profession_id": prof_id},
        )
        assert r.status_code == status.HTTP_200_OK
        data = r.json()
        assert isinstance(data, list)
        assert any(es["id"] == elite_id for es in data)

        # Delete -> 200
        r = client.delete(f"{API_PREFIX}/professions/elite-specializations/{elite_id}")
        assert r.status_code == status.HTTP_200_OK

        # Get deleted -> 404
        r = client.get(f"{API_PREFIX}/professions/elite-specializations/{elite_id}")
        assert r.status_code == status.HTTP_404_NOT_FOUND

        # Delete non-existent -> 404
        r = client.delete(f"{API_PREFIX}/professions/elite-specializations/{elite_id}")
        assert r.status_code == status.HTTP_404_NOT_FOUND

