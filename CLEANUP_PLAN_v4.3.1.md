# 🧹 Plan de Nettoyage GW2_WvWBuilder v4.3.1

**Date**: 2025-10-18 | **Status**: POUR VALIDATION

---

## 📊 Analyse Actuelle

**Problèmes Identifiés**:
- 50+ fichiers MD obsolètes (rapports CI/CD, tests temporaires)
- Tests en doublon (archive_duplicates/)
- Fichiers backend doublons (cache.py/caching.py, deps.py×3, crud doublons)
- Logs/PIDs versionnés (.log, .pid, .db.backup)
- Scripts temporaires (test_*.py, test_*.sh)
- 5+ README différents

---

## 🗑️ FICHIERS À SUPPRIMER

### Racine (53 fichiers)

**Rapports CI/CD (14)**: CI_*.md, GITHUB_*.md, github_setup.sh
**Rapports Projet (10)**: BUILDER_*.md, PHASE3_*.md, PROJECT_*.md, SETUP_*.md
**Infrastructure (8)**: INFRASTRUCTURE*.md, RAPPORT_*.md, SECURISATION*.md
**README Redondants (4)**: README.old.md, README_AUTO_MODE.md, README_EVOLUTIONARY_AI.md
**Guides Multiples (5)**: QUICKSTART.md, QUICK_START*.md, LIRE_MOI_TESTS.md
**Scripts Temp (8)**: CHECK_*.sh, CLEANUP_URGENT.sh, RESTART_*.sh, test_*.py/sh
**Logs/PIDs (12+)**: *.log, *.pid, auth_test_result.txt, deployment_*.log
**Backups (3)**: *.db.backup, test.db
**Divers (4)**: Prompt_Windsurf.txt, app/, backups/, logs/, reports/

### Backend Doublons

**Core (5)**: cache.py, logging.py, deps.py, api/deps.py, config.py (racine)
**CRUD (6+)**: build.py, elite_specialization.py, profession.py, tag.py, team.py, user.py

### Tests

**Archive**: archive_duplicates/ (tout)
**Obsolètes**: helpers.py, test_example.py, test_smoke.py, tests/gw2_wvwbuilder.db

---

## ♻️ REFACTORING

### 1. Consolidation Dependencies
Fusionner `app/api/dependencies.py` + `app/api/deps.py` + `app/core/deps.py`  
→ Garder uniquement `app/api/dependencies.py`

### 2. Consolidation Logging
Fusionner `app/core/logging.py` → `app/core/logging_config.py`

### 3. Consolidation CRUD
Supprimer `app/crud/*.py`, garder `app/crud/crud_*.py`

### 4. Amélioration Gestion Erreurs
```python
# app/core/exceptions.py
class GW2WvWBuilderException(Exception):
    """Base exception."""
    pass

class MetaAnalysisError(GW2WvWBuilderException):
    """Erreur analyse méta."""
    pass
```

### 5. Optimisation I/O JSON
```python
# app/ai/meta_weights_updater.py
def _load_json(file_path: Path, default: Any = None) -> Any:
    """Charge JSON avec gestion erreurs robuste."""
    # Implémentation améliorée

def _save_json(file_path: Path, data: Any, backup: bool = True) -> None:
    """Sauvegarde JSON avec backup et écriture atomique."""
    # Implémentation améliorée
```

---

## 📝 DOCUMENTATION CIBLE

```
Racine:
├── README.md (fusionné, complet)
├── CHANGELOG.md ✅
├── CONTRIBUTING.md ✅
├── LICENSE ✅
├── TESTING.md
├── DEPLOYMENT.md
├── SECURITY.md ✅

docs/:
├── ARCHITECTURE.md
├── AI_META_ADAPTIVE_SYSTEM_v4.3.md ✅
├── v4.3.1_RSS_FORUM_INTEGRATION.md ✅
├── API_REFERENCE.md
└── DEVELOPMENT.md

frontend/:
└── SETUP_META_DASHBOARD.md ✅
```

---

## 🚀 SCRIPT AUTOMATIQUE

```bash
#!/bin/bash
# cleanup_v4.3.1.sh

set -e

echo "🧹 GW2_WvWbuilder Cleanup v4.3.1"

# 1. Backup
git add -A
git commit -m "Pre-cleanup snapshot" || true
git tag "pre-cleanup-$(date +%Y%m%d-%H%M%S)"

# 2. Supprimer fichiers obsolètes
rm -f CI_*.md BUILDER_*.md PHASE*.md PROJECT_*.md
rm -f QUICK*.md RAPPORT_*.md README.old.md README_AUTO*.md
rm -f *.log *.pid *.db.backup test.db test_*.py test_*.sh
rm -f CHECK_*.sh CLEANUP_URGENT.sh RESTART_*.sh
rm -rf app/ backups/ logs/ reports/

# 3. Backend doublons
cd backend
rm -f app/core/cache.py app/core/logging.py app/core/deps.py
rm -f app/api/deps.py app/config.py
rm -f app/crud/{build,elite_specialization,profession,tag,team,user}.py
rm -rf tests/archive_duplicates/
rm -f tests/{helpers,test_example,test_smoke}.py tests/gw2_wvwbuilder.db
cd ..

# 4. Format & Lint
cd backend
poetry run black app/
poetry run flake8 app/ --max-line-length=100
cd ..

# 5. Tests
cd backend
poetry run pytest tests/ -v --cov=app
cd ..

echo "✅ Cleanup complete!"
```

---

## ✅ CHECKLIST VALIDATION

### Avant
- [ ] Backup Git créé
- [ ] Tests passent (36/36)
- [ ] Backend démarre
- [ ] Frontend démarre

### Après
- [ ] Tests passent
- [ ] Aucun import cassé
- [ ] Backend/Frontend démarrent
- [ ] Dashboard fonctionne
- [ ] Coverage ≥ 22%

### Code Quality
- [ ] Black formatting
- [ ] Flake8 compliant
- [ ] Docstrings ajoutées
- [ ] Gestion erreurs robuste

---

## 📊 RÉSULTAT ATTENDU

**Avant**: ~350 files | **Après**: ~150 files  
**Réduction**: -57% fichiers, -90% MD obsolètes

**Metrics**:
- ✅ Coverage > 25%
- ✅ Code formatté (Black)
- ✅ Linting OK (Flake8)
- ✅ Docs complètes

---

**Prêt pour exécution**: ✅ OUI | ❌ NON (à valider)
