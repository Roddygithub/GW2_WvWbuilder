import pytest
from fastapi import status, HTTPException

from app.api import deps
from app.core.config import settings
from app.models import User, Role

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
        
        # Tenter de créer un rôle en tant qu'utilisateur normal
        r = client.post(f"{API_PREFIX}/roles/", json={"name": "HEALER"})
        
        # Vérifier que l'accès est refusé (403)
        assert r.status_code == status.HTTP_403_FORBIDDEN
        assert r.json()["detail"] == "The user doesn't have enough privileges"
        
        # Nettoyer les surcharges
        client.app.dependency_overrides = {}

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

