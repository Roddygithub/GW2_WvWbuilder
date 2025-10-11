# ⚡ Guide de Démarrage Rapide - Corrections Critiques

**Temps estimé**: 2 heures  
**Objectif**: Stabiliser le backend et faire passer tous les tests

---

## 🎯 Étape 1: Sécuriser les Clés Secrètes (30 min)

### 1.1 Générer des clés fortes

```bash
# Générer 3 clés secrètes fortes
echo "SECRET_KEY=$(openssl rand -hex 32)"
echo "JWT_SECRET_KEY=$(openssl rand -hex 32)"
echo "JWT_REFRESH_SECRET_KEY=$(openssl rand -hex 32)"
```

### 1.2 Créer le fichier .env

```bash
cd /home/roddy/GW2_WvWbuilder/backend
cp .env.example .env
```

### 1.3 Éditer .env avec les clés générées

```bash
nano .env
```

Ajouter :
```env
# Security - IMPORTANT: Remplacer par les clés générées ci-dessus
SECRET_KEY=<votre_clé_générée_1>
JWT_SECRET_KEY=<votre_clé_générée_2>
JWT_REFRESH_SECRET_KEY=<votre_clé_générée_3>

# Database
DATABASE_URL=sqlite+aiosqlite:///./gw2_wvwbuilder.db
TEST_DATABASE_URL=sqlite+aiosqlite:///:memory:

# Environment
ENVIRONMENT=development
DEBUG=True
TESTING=False

# JWT Configuration
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_MINUTES=1440

# CORS
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Cache
CACHE_ENABLED=false
REDIS_URL=
```

### 1.4 Mettre à jour .env.example

```bash
nano .env.example
```

Ajouter un commentaire :
```env
# Security - IMPORTANT: Generate strong keys with: openssl rand -hex 32
SECRET_KEY=your-secret-key-here-CHANGE-THIS
JWT_SECRET_KEY=your-jwt-secret-key-here-CHANGE-THIS
JWT_REFRESH_SECRET_KEY=your-jwt-refresh-secret-key-here-CHANGE-THIS
```

### 1.5 Ajouter validation dans config.py

```bash
nano app/core/config.py
```

Ajouter après la classe Settings :
```python
# Validation des clés secrètes
def validate_secret_keys(self) -> None:
    """Valide que les clés secrètes sont définies et sécurisées."""
    if self.ENVIRONMENT == "production":
        if not self.SECRET_KEY or self.SECRET_KEY == "supersecretkeyfordevelopmentonly":
            raise ValueError("SECRET_KEY must be set to a strong value in production")
        if not self.JWT_SECRET_KEY or self.JWT_SECRET_KEY == "supersecretjwtkey":
            raise ValueError("JWT_SECRET_KEY must be set to a strong value in production")
        if len(self.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
```

---

## 🎯 Étape 2: Corriger la Configuration Asyncio (5 min)

### 2.1 Mettre à jour pytest.ini

```bash
nano pytest.ini
```

Ajouter après `asyncio_mode = auto` :
```ini
asyncio_default_fixture_loop_scope = function
```

Le fichier devrait ressembler à :
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
python_classes = Test*

addopts = 
    -v 
    --tb=short
    --strict-markers
    --strict-config
    -p no:warnings
    -p no:cacheprovider
    --asyncio-mode=auto
    --import-mode=importlib
    --cov=app
    --cov-report=term-missing
    --cov-report=xml
    --cov-fail-under=80

# Configuration pour asyncio
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
```

---

## 🎯 Étape 3: Implémenter le Rollback Automatique (1 heure)

### 3.1 Mettre à jour tests/conftest.py

```bash
nano tests/conftest.py
```

Remplacer la fixture `db_session` par :
```python
@pytest_asyncio.fixture(scope="function")
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a clean database session for testing with automatic rollback.
    
    This fixture provides a new database session for each test function and ensures
    that all changes are rolled back after the test completes, maintaining test isolation.
    """
    # Create a new connection
    connection = await engine.connect()
    
    # Start a new transaction
    transaction = await connection.begin()
    
    # Create a session factory bound to this connection
    async_session_factory = async_sessionmaker(
        bind=connection,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
        class_=AsyncSession
    )
    
    # Create the session
    session = async_session_factory()
    
    # Enable foreign key constraints for SQLite
    if "sqlite" in str(connection.engine.url):
        await connection.execute(text("PRAGMA foreign_keys=ON"))
    
    try:
        yield session
    except Exception as e:
        # Rollback on error
        await session.rollback()
        raise
    finally:
        # Always close the session and rollback the transaction
        await session.close()
        if transaction.is_active:
            await transaction.rollback()
        await connection.close()
```

### 3.2 Mettre à jour tests/unit/conftest.py

Appliquer la même modification pour la fixture `db_session` dans ce fichier.

---

## 🎯 Étape 4: Vérifier les Corrections (30 min)

### 4.1 Exécuter les tests unitaires

```bash
cd /home/roddy/GW2_WvWbuilder/backend
pytest tests/unit/ -v --tb=short
```

### 4.2 Vérifier la couverture

```bash
pytest tests/unit/ --cov=app --cov-report=term --cov-report=html
```

### 4.3 Ouvrir le rapport de couverture

```bash
# Le rapport HTML est généré dans htmlcov/
# Ouvrir htmlcov/index.html dans un navigateur
```

### 4.4 Vérifier les tests d'intégration

```bash
pytest tests/integration/ -v --tb=short
```

### 4.5 Exécuter tous les tests

```bash
pytest tests/ -v --tb=short --cov=app --cov-report=term
```

---

## 🎯 Étape 5: Commit des Corrections (10 min)

### 5.1 Vérifier les changements

```bash
git status
git diff
```

### 5.2 Commit des corrections

```bash
git add tests/helpers/factories.py
git add tests/__init__.py
git add tests/unit/conftest.py
git add tests/conftest.py
git add pytest.ini
git add .env.example
git add app/core/config.py

git commit -m "fix: Apply critical corrections from audit

- Fix docstring syntax in factories.py
- Fix imports in factories.py (schemas from app.schemas)
- Fix imports in tests/__init__.py
- Fix test engine configuration (remove invalid StaticPool params)
- Fix dependencies in conftest.py (use get_async_db)
- Add asyncio_default_fixture_loop_scope to pytest.ini
- Implement automatic rollback in test fixtures
- Secure secret keys (move to .env)
- Add secret key validation

Resolves: Critical issues from audit report
Coverage: 29% → Target: 90%
"
```

---

## ✅ Checklist de Validation

Après avoir appliqué toutes les corrections, vérifier :

- [ ] Le fichier `.env` existe et contient des clés fortes
- [ ] `pytest.ini` contient `asyncio_default_fixture_loop_scope = function`
- [ ] Les fixtures `db_session` implémentent le rollback automatique
- [ ] Tous les tests unitaires passent : `pytest tests/unit/ -v`
- [ ] La couverture est calculée : `pytest --cov=app`
- [ ] Aucun warning pytest critique
- [ ] Le commit est fait avec un message descriptif

---

## 🐛 Dépannage

### Problème : Tests échouent avec "PendingRollbackError"

**Solution** : Vérifier que la fixture `db_session` implémente bien le rollback automatique dans le `finally`.

### Problème : "Event loop is closed"

**Solution** : Vérifier que `asyncio_default_fixture_loop_scope = function` est dans `pytest.ini`.

### Problème : "SECRET_KEY not set"

**Solution** : Vérifier que le fichier `.env` existe et contient `SECRET_KEY=...`.

### Problème : Couverture toujours à 29%

**Solution** : C'est normal à ce stade. Les étapes suivantes (Jour 2-3) augmenteront la couverture.

---

## 📊 Résultats Attendus

Après ces corrections :
- ✅ Tests stables (pas de PendingRollbackError)
- ✅ Clés secrètes sécurisées
- ✅ Configuration asyncio correcte
- ✅ Isolation complète entre les tests
- ⏳ Couverture : 29% (à augmenter dans les prochaines étapes)

---

## 🚀 Prochaines Étapes

Une fois ces corrections appliquées, passer à :
1. **Jour 2** : Augmenter la couverture de code (voir CORRECTIONS_TODO.md)
2. **Jour 3** : Implémenter la rotation des clés JWT
3. **Jour 4** : Optimiser le CI/CD et la documentation

---

**Temps total estimé** : 2 heures  
**Difficulté** : Moyenne  
**Impact** : Critique (bloque la suite du développement)

---

**Guide créé le** : 11 Octobre 2025  
**Par** : SWE-1 (Ingénieur Backend Senior)
