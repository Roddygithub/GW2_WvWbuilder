import logging
import sys
import pytest
from fastapi import status

from app.api import deps
from app.api.api_v1.endpoints import professions as prof_ep
from app.api.api_v1.endpoints import roles as roles_ep
from app.api.api_v1.endpoints import users as users_ep
from app.core.config import settings
from app.models.models import User, Role, Profession, EliteSpecialization
from app import crud

API_PREFIX = settings.API_V1_STR


# ---------- Models __repr__ coverage ----------

def test_model_reprs(db_session):
    u = User(email="r@e.co", username="r", hashed_password="h")
    r = Role(name="role")
    p = Profession(name="Prof")
    es = EliteSpecialization(name="Spec", profession=p)
    db_session.add_all([u, r, p, es])
    db_session.commit()

    assert "<User" in repr(u)
    assert "<Role" in repr(r)
    assert "<Profession" in repr(p)
    # Ensure relationship is present in __repr__ for EliteSpecialization
    assert "Spec (Prof)" in repr(es)

def test_composition_repr():
    from app.models.models import Composition
    c = Composition(name="Zerg Squad")
    assert "<Composition Zerg Squad>" == repr(c)


# ---------- deps coverage ----------

def test_get_current_active_user_inactive_raises():
    user = type("U", (), {"is_active": False})()
    with pytest.raises(Exception) as ex:
        deps.get_current_active_user(current_user=user)
    assert "Inactive user" in str(ex.value)

def test_get_current_active_superuser_paths():
    su = type("U", (), {"is_superuser": True})()
    assert deps.get_current_active_superuser(current_user=su) is su
    non_su = type("U", (), {"is_superuser": False})()
    with pytest.raises(Exception):
        deps.get_current_active_superuser(current_user=non_su)

def test_get_current_user_404_and_403(monkeypatch):
    class DummySession:
        def __init__(self):
            self.closed = False
        def close(self):
            self.closed = True
    
    # Use dummy SessionLocal
    monkeypatch.setattr(deps, "SessionLocal", lambda: DummySession())

    # 403 branch: invalid token format
    with pytest.raises(Exception) as ex1:
        deps.get_current_user(db=None, token="invalid_token")
    assert "Could not validate credentials" in str(ex1.value)

    # 403 branch: raise jwt.JWTError inside try
    class DummyJWT:
        class JWTError(Exception):
            pass
        
        @staticmethod
        def decode(*args, **kwargs):
            raise DummyJWT.JWTError("bad token")
    
    monkeypatch.setattr(deps, "jwt", DummyJWT)
    
    with pytest.raises(Exception) as ex2:
        deps.get_current_user(db=None, token="token")
    assert "Could not validate credentials" in str(ex2.value)

def test_get_current_user_success_path(monkeypatch):
    # Ensure line 38 (return user) is hit
    class DummyUser:
        pass
    du = DummyUser()
    class DummySession:
        def close(self):
            pass
    monkeypatch.setattr(deps, "SessionLocal", lambda: DummySession())
    monkeypatch.setattr(crud.user, "get", lambda db, id: du)
    # Also bypass token extraction by passing a dummy string (oauth2 handled by Depends in real app)
    got = deps.get_current_user(db=DummySession(), token="x")
    assert got is du

def test_get_db_finally_closes(monkeypatch):
    # Cover lines 16-20: creation and finally close
    calls = {"closed": False}
    class DummySession:
        def close(self):
            calls["closed"] = True
    monkeypatch.setattr(deps, "SessionLocal", lambda: DummySession())
    gen = deps.get_db()
    db = next(gen)
    assert isinstance(db, DummySession)
    with pytest.raises(StopIteration):
        next(gen)
    assert calls["closed"] is True

def test_get_current_active_user_happy_path():
    # Cover line 52: return current_user
    u = type("U", (), {"is_active": True})()
    assert deps.get_current_active_user(current_user=u) is u


# ---------- endpoints tiny edges ----------
@pytest.mark.usefixtures("client")
class TestTinyEdges:
    def test_roles_delete_not_found(self, client):
        # superuser override
        su = User(email="su@example.com", username="su", hashed_password="x", is_superuser=True)
        client.app.dependency_overrides[deps.get_current_active_superuser] = lambda: su
        resp = client.delete(f"{API_PREFIX}/roles/999999")
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_professions_delete_not_found(self, client):
        su = User(email="su2@example.com", username="su2", hashed_password="x", is_superuser=True)
        client.app.dependency_overrides[deps.get_current_active_superuser] = lambda: su
        resp = client.delete(f"{API_PREFIX}/professions/999999")
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_elite_specs_update_not_found(self, client, db_session):
        su = User(email="su3@example.com", username="su3", hashed_password="x", is_superuser=True)
        client.app.dependency_overrides[deps.get_current_active_superuser] = lambda: su
        # non-existent elite spec
        resp = client.put(f"{API_PREFIX}/professions/elite-specializations/999999", json={"name": "New"})
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_users_create_duplicate_email(self, client, db_session):
        su = User(email="admin@example.com", username="admin", hashed_password="x", is_superuser=True)
        client.app.dependency_overrides[deps.get_current_active_superuser] = lambda: su
        payload = {"email": "dup@example.com", "username": "dup", "password": "password123"}
        resp1 = client.post(f"{API_PREFIX}/users/", json=payload)
        assert resp1.status_code == status.HTTP_200_OK
        # duplicate by email should hit 400 branch
        resp2 = client.post(f"{API_PREFIX}/users/", json=payload)
        assert resp2.status_code == status.HTTP_400_BAD_REQUEST

    def test_users_update_me_path(self, client, db_session):
        u = User(email="me@example.com", username="me", hashed_password="x", is_active=True)
        db_session.add(u)
        db_session.commit()
        db_session.refresh(u)
        # act as this user
        client.app.dependency_overrides[deps.get_current_active_user] = lambda: u
        resp = client.put(f"{API_PREFIX}/users/me", json={"username": "me2"})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["username"] == "me2"


# ---------- logging exception hook ----------

def test_logging_exception_hook(monkeypatch):
    import app.core.logging_config as logging_config
    from app.core.logging_config import setup_logging

    records = {"critical": []}
    class DummyLogger:
        def info(self, *a, **k):
            pass
        def critical(self, *a, **k):
            records["critical"].append((a, k))
    # Patch getLogger only for our module logger name to avoid breaking pytest logging
    original_getLogger = logging.getLogger
    def selective_getLogger(name=None):
        if name == logging_config.__name__:
            return DummyLogger()
        return original_getLogger(name)
    monkeypatch.setattr(logging, "getLogger", selective_getLogger)

    setup_logging()

    # KeyboardInterrupt path (should call default and return)
    sys.excepthook(KeyboardInterrupt, KeyboardInterrupt(), None)

    # Critical log path
    sys.excepthook(ValueError, ValueError("boom"), None)
    assert records["critical"], "Expected critical to be logged"
