# 📈 Guide pour Augmenter la Couverture de Tests à 80%+

## 🎯 Objectif
Passer de ~30% à ≥80% de couverture de code

---

## 📊 Analyse Actuelle

### Commande pour Identifier les Modules Non Couverts
```bash
cd /home/roddy/GW2_WvWbuilder/backend

# Générer le rapport de couverture
poetry run pytest tests/unit/ --cov=app --cov-report=term-missing --cov-report=html

# Voir les modules avec faible couverture
poetry run coverage report --skip-empty | grep -E "^app/" | sort -k4 -n

# Ouvrir le rapport HTML
xdg-open htmlcov/index.html
```

---

## 🔍 Modules Prioritaires à Tester

### 1. **app/api/endpoints/** (Endpoints API)

#### Fichiers à Tester
- `app/api/api_v1/endpoints/auth.py`
- `app/api/api_v1/endpoints/users.py`
- `app/api/api_v1/endpoints/builds.py`
- `app/api/api_v1/endpoints/compositions.py`
- `app/api/api_v1/endpoints/teams.py`

#### Template de Test d'Endpoint
```python
# tests/unit/api/test_auth_endpoints.py
import pytest
from httpx import AsyncClient
from fastapi import status

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    """Test successful login."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "TestPassword123!"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with invalid credentials."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@example.com", "password": "wrong"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_login_missing_fields(client: AsyncClient):
    """Test login with missing fields."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
```

#### Cas à Tester pour Chaque Endpoint
- ✅ Succès (200/201)
- ✅ Non authentifié (401)
- ✅ Interdit (403)
- ✅ Non trouvé (404)
- ✅ Validation échouée (422)
- ✅ Erreur serveur (500)

---

### 2. **app/crud/** (Opérations CRUD)

#### Fichiers à Tester
- `app/crud/crud_user.py`
- `app/crud/crud_role.py`
- `app/crud/crud_composition.py`
- `app/crud/crud_team.py`

#### Template de Test CRUD
```python
# tests/unit/crud/test_crud_user.py
import pytest
from sqlalchemy.orm import Session
from app.crud.crud_user import user_crud
from app.schemas.user import UserCreate, UserUpdate

def test_create_user(db: Session):
    """Test creating a user."""
    user_in = UserCreate(
        email="test@example.com",
        username="testuser",
        password="TestPassword123!"
    )
    user = user_crud.create(db, obj_in=user_in)
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.id is not None

def test_get_user(db: Session, test_user):
    """Test getting a user by ID."""
    user = user_crud.get(db, id=test_user.id)
    assert user is not None
    assert user.id == test_user.id
    assert user.email == test_user.email

def test_get_user_not_found(db: Session):
    """Test getting a non-existent user."""
    user = user_crud.get(db, id=99999)
    assert user is None

def test_get_multi_users(db: Session, test_users):
    """Test getting multiple users."""
    users = user_crud.get_multi(db, skip=0, limit=10)
    assert len(users) >= len(test_users)

def test_update_user(db: Session, test_user):
    """Test updating a user."""
    user_update = UserUpdate(username="updated_username")
    updated_user = user_crud.update(db, db_obj=test_user, obj_in=user_update)
    assert updated_user.username == "updated_username"

def test_delete_user(db: Session, test_user):
    """Test deleting a user."""
    user_crud.remove(db, id=test_user.id)
    deleted_user = user_crud.get(db, id=test_user.id)
    assert deleted_user is None
```

#### Opérations CRUD à Tester
- ✅ `create()` - Création
- ✅ `get()` - Lecture par ID
- ✅ `get_multi()` - Lecture multiple
- ✅ `update()` - Mise à jour
- ✅ `remove()` - Suppression
- ✅ Méthodes spécifiques (ex: `get_by_email()`)

---

### 3. **app/services/** (Services Métier)

#### Fichiers à Tester
- `app/services/auth_service.py`
- `app/services/build_service.py`
- `app/services/composition_service.py`

#### Template de Test de Service
```python
# tests/unit/services/test_auth_service.py
import pytest
from app.services.auth_service import AuthService
from app.core.security import verify_password

@pytest.mark.asyncio
async def test_authenticate_user_success(db, test_user):
    """Test successful authentication."""
    service = AuthService(db)
    user = await service.authenticate(
        email=test_user.email,
        password="TestPassword123!"
    )
    assert user is not None
    assert user.id == test_user.id

@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(db, test_user):
    """Test authentication with wrong password."""
    service = AuthService(db)
    user = await service.authenticate(
        email=test_user.email,
        password="WrongPassword"
    )
    assert user is None

@pytest.mark.asyncio
async def test_register_user(db):
    """Test user registration."""
    service = AuthService(db)
    user = await service.register(
        email="newuser@example.com",
        username="newuser",
        password="TestPassword123!"
    )
    assert user is not None
    assert user.email == "newuser@example.com"
    assert verify_password("TestPassword123!", user.hashed_password)
```

---

### 4. **app/core/** (Modules Core)

#### Fichiers à Tester
- `app/core/config.py` - Configuration
- `app/core/cache.py` - Cache Redis
- `app/core/limiter.py` - Rate limiting

#### Template de Test Core
```python
# tests/unit/core/test_config.py
import pytest
from app.core.config import Settings

def test_settings_default_values():
    """Test default settings values."""
    settings = Settings()
    assert settings.PROJECT_NAME == "GW2 WvW Builder"
    assert settings.API_V1_STR == "/api/v1"
    assert settings.ENVIRONMENT in ["development", "testing", "production"]

def test_settings_from_env(monkeypatch):
    """Test settings from environment variables."""
    monkeypatch.setenv("PROJECT_NAME", "Custom Name")
    monkeypatch.setenv("DEBUG", "true")
    settings = Settings()
    assert settings.PROJECT_NAME == "Custom Name"
    assert settings.DEBUG is True

# tests/unit/core/test_cache.py
import pytest
from app.core.cache import cache

@pytest.mark.asyncio
async def test_cache_set_get(mock_redis):
    """Test cache set and get."""
    await cache.set("test_key", "test_value", ttl=60)
    value = await cache.get("test_key")
    assert value == "test_value"

@pytest.mark.asyncio
async def test_cache_delete(mock_redis):
    """Test cache delete."""
    await cache.set("test_key", "test_value")
    await cache.delete("test_key")
    value = await cache.get("test_key")
    assert value is None
```

---

### 5. **app/models/** (Modèles SQLAlchemy)

#### Fichiers à Tester
- `app/models/user.py`
- `app/models/build.py`
- `app/models/composition.py`
- `app/models/team.py`

#### Template de Test de Modèle
```python
# tests/unit/models/test_user_model.py
import pytest
from app.models.user import User

def test_user_creation():
    """Test user model creation."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password"
    )
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.is_active is True
    assert user.is_superuser is False

def test_user_repr():
    """Test user string representation."""
    user = User(email="test@example.com", username="testuser")
    assert "testuser" in repr(user)

def test_user_relationships(db, test_user, test_build):
    """Test user relationships."""
    db.add(test_build)
    db.commit()
    db.refresh(test_user)
    assert len(test_user.builds) > 0
    assert test_build in test_user.builds
```

---

## 🛠️ Outils et Techniques

### 1. Fixtures Réutilisables

Créer des fixtures dans `tests/conftest.py`:

```python
@pytest.fixture
def test_user(db: Session):
    """Create a test user."""
    from app.models.user import User
    from app.core.security import get_password_hash
    
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("TestPassword123!"),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_users(db: Session):
    """Create multiple test users."""
    users = []
    for i in range(5):
        user = User(
            email=f"user{i}@example.com",
            username=f"user{i}",
            hashed_password=get_password_hash("TestPassword123!")
        )
        db.add(user)
        users.append(user)
    db.commit()
    return users

@pytest.fixture
def authenticated_client(client: AsyncClient, test_user):
    """Create an authenticated client."""
    from app.core.security import create_access_token
    
    token = create_access_token({"sub": test_user.email, "user_id": test_user.id})
    client.headers["Authorization"] = f"Bearer {token}"
    return client
```

### 2. Mocks pour Dépendances Externes

```python
# tests/conftest.py
@pytest.fixture
def mock_redis(monkeypatch):
    """Mock Redis client."""
    class MockRedis:
        def __init__(self):
            self.data = {}
        
        async def get(self, key):
            return self.data.get(key)
        
        async def set(self, key, value, ex=None):
            self.data[key] = value
        
        async def delete(self, key):
            self.data.pop(key, None)
    
    mock = MockRedis()
    monkeypatch.setattr("app.core.cache.redis_client", mock)
    return mock

@pytest.fixture
def mock_email_service(monkeypatch):
    """Mock email service."""
    sent_emails = []
    
    async def mock_send_email(to, subject, body):
        sent_emails.append({"to": to, "subject": subject, "body": body})
    
    monkeypatch.setattr("app.services.email_service.send_email", mock_send_email)
    return sent_emails
```

### 3. Parameterized Tests

```python
@pytest.mark.parametrize("email,password,expected_status", [
    ("valid@example.com", "ValidPass123!", 200),
    ("invalid@example.com", "short", 422),
    ("", "ValidPass123!", 422),
    ("valid@example.com", "", 422),
])
@pytest.mark.asyncio
async def test_login_various_inputs(client, email, password, expected_status):
    """Test login with various inputs."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password}
    )
    assert response.status_code == expected_status
```

---

## 📋 Plan d'Action

### Semaine 1: Fondations (30% → 50%)
- [ ] Tests CRUD pour User, Role, Permission
- [ ] Tests endpoints Auth (login, register, refresh)
- [ ] Tests core (config, security, cache)

### Semaine 2: Fonctionnalités (50% → 70%)
- [ ] Tests CRUD pour Build, Composition, Team
- [ ] Tests endpoints Builds, Compositions
- [ ] Tests services métier

### Semaine 3: Complétion (70% → 80%+)
- [ ] Tests edge cases
- [ ] Tests d'erreur
- [ ] Tests d'intégration
- [ ] Refactoring et optimisation

---

## 🎯 Checklist par Module

### Pour Chaque Module à Tester

- [ ] **Happy path**: Cas nominal fonctionne
- [ ] **Edge cases**: Limites et cas limites
- [ ] **Error cases**: Gestion d'erreurs
- [ ] **Validation**: Validation des données
- [ ] **Permissions**: Contrôle d'accès
- [ ] **Database**: Transactions et rollback
- [ ] **Async**: Comportement asynchrone correct

---

## 📊 Suivi de Progression

### Commande de Suivi
```bash
# Générer rapport et afficher progression
poetry run pytest tests/unit/ --cov=app --cov-report=term | tee coverage_report.txt

# Extraire le pourcentage
grep "TOTAL" coverage_report.txt
```

### Tableau de Bord
```bash
# Créer un dashboard simple
cat > coverage_dashboard.sh << 'EOF'
#!/bin/bash
echo "╔════════════════════════════════════════╗"
echo "║     📊 COVERAGE DASHBOARD             ║"
echo "╚════════════════════════════════════════╝"
poetry run coverage report --skip-empty | grep -E "^(app/|TOTAL)"
echo ""
echo "Objectif: 80%"
EOF
chmod +x coverage_dashboard.sh
```

---

## ✅ Résultat Attendu

```
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║           🎯 OBJECTIF: COUVERTURE ≥80%                     ║
║                                                            ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  Phase 1: Fondations        ✅ 30% → 50%                   ║
║  Phase 2: Fonctionnalités   🔄 50% → 70%                   ║
║  Phase 3: Complétion        ⏳ 70% → 80%+                  ║
║                                                            ║
║  STATUT: EN COURS 🚀                                       ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

---

**Commencer maintenant**: `./fix_all_tests.sh` puis suivre ce guide !
