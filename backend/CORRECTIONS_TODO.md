# 🔧 Liste des Corrections à Appliquer - GW2_WvWbuilder

**Date de création**: 11 Octobre 2025  
**Dernière mise à jour**: 11 Octobre 2025

---

## ✅ Corrections Appliquées

### 1. Correction de la syntaxe dans factories.py
- **Fichier**: `tests/helpers/factories.py`
- **Problème**: Docstring mal formée (`""` au lieu de `"""`)
- **Ligne**: 228
- **Status**: ✅ CORRIGÉ
- **Commit**: À faire

### 2. Correction des imports dans factories.py
- **Fichier**: `tests/helpers/factories.py`
- **Problème**: Import des schémas depuis `app.models` au lieu de `app.schemas`
- **Lignes**: 15-20
- **Status**: ✅ CORRIGÉ
- **Commit**: À faire

### 3. Correction des imports dans tests/__init__.py
- **Fichier**: `tests/__init__.py`
- **Problème**: Import depuis `.factories` au lieu de `.helpers.factories`
- **Lignes**: 18-30
- **Status**: ✅ CORRIGÉ
- **Commit**: À faire

### 4. Correction de la configuration du moteur de test
- **Fichier**: `tests/unit/conftest.py`
- **Problème**: `StaticPool` ne supporte pas `max_overflow` et `pool_size`
- **Lignes**: 63-79
- **Status**: ✅ CORRIGÉ
- **Commit**: À faire

### 5. Correction des dépendances dans conftest.py
- **Fichier**: `tests/unit/conftest.py`
- **Problème**: Import de `get_db` au lieu de `get_async_db`
- **Ligne**: 187
- **Status**: ✅ CORRIGÉ
- **Commit**: À faire

---

## 🔴 Corrections Critiques à Appliquer

### 6. Sécuriser les clés secrètes
- **Fichiers**: 
  - `app/core/config.py`
  - `.env.example`
  - `.env` (à créer)
- **Problème**: Clés secrètes codées en dur
- **Action**:
  ```python
  # Dans app/core/config.py
  SECRET_KEY: str = os.getenv("SECRET_KEY")
  JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
  JWT_REFRESH_SECRET_KEY: str = os.getenv("JWT_REFRESH_SECRET_KEY")
  
  # Validation
  if not SECRET_KEY or SECRET_KEY == "supersecretkeyfordevelopmentonly":
      if ENVIRONMENT == "production":
          raise ValueError("SECRET_KEY must be set in production")
  ```
- **Status**: ⏳ À FAIRE
- **Priorité**: CRITIQUE
- **Temps estimé**: 30 minutes

### 7. Implémenter le rollback automatique des tests
- **Fichiers**:
  - `tests/conftest.py`
  - `tests/unit/conftest.py`
- **Problème**: Isolation incomplète entre les tests
- **Action**:
  ```python
  @pytest_asyncio.fixture(scope="function")
  async def db_session(engine):
      """Create a clean database session with automatic rollback."""
      connection = await engine.connect()
      transaction = await connection.begin()
      
      session = async_sessionmaker(
          bind=connection,
          expire_on_commit=False,
          autoflush=False,
          class_=AsyncSession
      )()
      
      try:
          yield session
      finally:
          await session.close()
          await transaction.rollback()
          await connection.close()
  ```
- **Status**: ⏳ À FAIRE
- **Priorité**: CRITIQUE
- **Temps estimé**: 1 heure

### 8. Corriger la configuration asyncio dans pytest
- **Fichier**: `pytest.ini`
- **Problème**: `asyncio_default_fixture_loop_scope` non défini
- **Action**:
  ```ini
  [pytest]
  asyncio_default_fixture_loop_scope = function
  ```
- **Status**: ⏳ À FAIRE
- **Priorité**: CRITIQUE
- **Temps estimé**: 5 minutes

---

## 🟠 Corrections Haute Priorité

### 9. Augmenter la couverture de code
- **Modules cibles**:
  - `app/core/security.py`: 0% → 90%
  - `app/crud/build.py`: 0% → 80%
  - `app/services/webhook_service.py`: 26% → 85%
  - `app/core/gw2/client.py`: 24% → 80%
- **Action**: Ajouter des tests unitaires complets
- **Status**: ⏳ À FAIRE
- **Priorité**: HAUTE
- **Temps estimé**: 1 jour

### 10. Implémenter la rotation des clés JWT
- **Fichiers**:
  - `app/core/key_rotation_service.py` (existe déjà)
  - `app/core/security.py`
  - `app/core/tasks/key_rotation_task.py`
- **Action**:
  1. Intégrer le service de rotation dans l'authentification
  2. Planifier la rotation automatique
  3. Tester la validation avec anciennes clés
- **Status**: ⏳ À FAIRE
- **Priorité**: HAUTE
- **Temps estimé**: 4 heures

### 11. Ajouter des tests d'intégration
- **Répertoire**: `tests/integration/`
- **Tests à ajouter**:
  - Flux d'authentification complet
  - Création et gestion de builds
  - Création et gestion de compositions
  - Gestion des équipes
  - Webhooks
- **Status**: ⏳ À FAIRE
- **Priorité**: HAUTE
- **Temps estimé**: 1 jour

### 12. Protéger les endpoints critiques
- **Fichiers**: 
  - `app/api/api_v1/endpoints/*.py`
  - `app/core/limiter.py`
- **Action**:
  1. Auditer tous les endpoints
  2. Ajouter rate limiting global
  3. Vérifier les permissions
  4. Documenter les endpoints publics vs privés
- **Status**: ⏳ À FAIRE
- **Priorité**: HAUTE
- **Temps estimé**: 3 heures

---

## 🟡 Corrections Moyenne Priorité

### 13. Standardiser les réponses API
- **Fichiers**: `app/api/api_v1/endpoints/*.py`
- **Action**:
  ```python
  # Créer un schéma de réponse standard
  class APIResponse(BaseModel):
      success: bool
      data: Optional[Any] = None
      error: Optional[str] = None
      message: Optional[str] = None
  ```
- **Status**: ⏳ À FAIRE
- **Priorité**: MOYENNE
- **Temps estimé**: 2 heures

### 14. Optimiser le pipeline CI/CD
- **Fichier**: `.github/workflows/ci-cd.yml`
- **Action**:
  1. Paralléliser les tests par module
  2. Améliorer le cache des dépendances
  3. Ajouter des jobs de déploiement automatique
- **Status**: ⏳ À FAIRE
- **Priorité**: MOYENNE
- **Temps estimé**: 2 heures

### 15. Supprimer la duplication de structure
- **Répertoires**:
  - `app/api/api_v1/` (à garder)
  - `app/api/v1/` (à supprimer)
- **Action**: Supprimer `app/api/v1/` et mettre à jour les imports
- **Status**: ⏳ À FAIRE
- **Priorité**: MOYENNE
- **Temps estimé**: 30 minutes

### 16. Améliorer la documentation
- **Fichiers à créer/mettre à jour**:
  - `README.md`
  - `CONTRIBUTING.md`
  - `ARCHITECTURE.md`
  - `API_DOCUMENTATION.md`
- **Status**: ⏳ À FAIRE
- **Priorité**: MOYENNE
- **Temps estimé**: 3 heures

---

## 🟢 Corrections Basse Priorité

### 17. Réduire la complexité du code
- **Fichiers**: À identifier avec radon ou pylint
- **Action**: Refactoriser les fonctions > 50 lignes
- **Status**: ⏳ À FAIRE
- **Priorité**: BASSE
- **Temps estimé**: 1 jour

### 18. Nettoyer le code mort
- **Fichiers**:
  - `app/models/models.py.bak`
  - Autres fichiers `.bak`
- **Action**: Supprimer tous les fichiers de backup
- **Status**: ⏳ À FAIRE
- **Priorité**: BASSE
- **Temps estimé**: 15 minutes

### 19. Épingler les versions des dépendances
- **Fichier**: `pyproject.toml`
- **Action**: Remplacer `^` par `==` pour les versions
- **Status**: ⏳ À FAIRE
- **Priorité**: BASSE
- **Temps estimé**: 30 minutes

---

## 📊 Statistiques

### Corrections Appliquées
- ✅ Total: 5/19 (26%)
- ✅ Critiques: 2/4 (50%)
- ⏳ Haute priorité: 0/4 (0%)
- ⏳ Moyenne priorité: 0/4 (0%)
- ⏳ Basse priorité: 0/3 (0%)

### Temps Estimé Total
- ⏳ Corrections critiques restantes: 1.5 heures
- ⏳ Haute priorité: 2.5 jours
- ⏳ Moyenne priorité: 7.5 heures
- ⏳ Basse priorité: 1.75 jours

**Total estimé**: 3-4 jours de travail

---

## 🎯 Plan d'Exécution Recommandé

### Phase 1: Stabilisation (Jour 1 - Matin)
1. ✅ Corriger les imports et la syntaxe
2. ⏳ Sécuriser les clés secrètes
3. ⏳ Implémenter le rollback automatique
4. ⏳ Corriger la configuration asyncio

### Phase 2: Tests (Jour 1 - Après-midi + Jour 2)
5. ⏳ Augmenter la couverture de code à 90%
6. ⏳ Ajouter des tests d'intégration

### Phase 3: Sécurité (Jour 3 - Matin)
7. ⏳ Implémenter la rotation des clés JWT
8. ⏳ Protéger les endpoints critiques

### Phase 4: Optimisation (Jour 3 - Après-midi)
9. ⏳ Standardiser les réponses API
10. ⏳ Optimiser le pipeline CI/CD

### Phase 5: Nettoyage (Jour 4)
11. ⏳ Supprimer la duplication
12. ⏳ Améliorer la documentation
13. ⏳ Nettoyer le code mort

---

**Document maintenu par**: SWE-1  
**Dernière révision**: 11 Octobre 2025
