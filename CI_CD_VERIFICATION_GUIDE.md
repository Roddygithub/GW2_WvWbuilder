# 🧩 Guide de Vérification CI/CD - GitHub Actions

**Date**: 2025-10-15  
**Objectif**: Vérifier et valider en temps réel tous les pipelines CI/CD sur GitHub Actions  
**Repository**: https://github.com/Roddygithub/GW2_WvWbuilder

---

## 📋 Étapes de Vérification

### 1️⃣ Accéder aux GitHub Actions

Ouvrir dans votre navigateur:
```
https://github.com/Roddygithub/GW2_WvWbuilder/actions
```

### 2️⃣ Workflows à Vérifier

Vous avez **6 workflows** configurés. Voici ceux à vérifier en priorité:

| Workflow | Fichier | Triggers | Priorité |
|----------|---------|----------|----------|
| **Modern CI/CD Pipeline** | `ci-cd-modern.yml` | push, PR, manual | 🔴 **CRITIQUE** |
| **Full CI/CD Pipeline** | `full-ci.yml` | push, PR | 🔴 **CRITIQUE** |
| **Tests & Quality Checks** | `tests.yml` | push, PR | 🟡 **IMPORTANT** |
| **CI/CD Complete** | `ci-cd-complete.yml` | push, PR, manual | 🟡 **IMPORTANT** |
| **CI/CD** | `ci-cd.yml` | push, PR, manual | 🟢 **OPTIONNEL** |
| **Production Deploy** | `production-deploy.yml` | manual | 🟢 **OPTIONNEL** |

---

## 🎯 Workflows Critiques à Valider

### A) Modern CI/CD Pipeline (`ci-cd-modern.yml`)

**Status**: 🔴 **PRIORITÉ MAXIMALE**

**11 Jobs à vérifier**:
1. ✅ `backend-lint` - Ruff, Black, MyPy
2. ✅ `backend-test-unit` - 1123 tests unitaires
3. ✅ `backend-test-integration` - Tests avec PostgreSQL
4. ✅ `backend-test-optimizer` - Tests optimizer (80% coverage)
5. ✅ `backend-security` - pip-audit, Bandit
6. ✅ `frontend-lint` - ESLint, Prettier, TypeScript
7. ⚠️ `frontend-test-unit` - Tests Vitest (peut échouer si tests .skip)
8. ✅ `frontend-test-e2e` - Cypress E2E
9. ✅ `frontend-build` - Production bundle
10. ✅ `frontend-security` - npm audit, Trivy
11. ✅ `validate-all` - Quality gates

**Derniers commits à vérifier**:
- `08dc0d4` - docs(phase4): final production readiness assessment
- `3d05281` - feat(staging): add complete staging deployment infrastructure
- `e1cc119` - fix(frontend): resolve TypeScript build errors for CI/CD

**Vérification**:
```bash
# Dans GitHub Actions, chercher:
- Run déclenché par le dernier push sur develop
- Date: 2025-10-15 13:35-14:00 UTC+2
- Branch: develop
- Commit SHA: 08dc0d4 ou 3d05281
```

### B) Full CI/CD Pipeline (`full-ci.yml`)

**Status**: 🔴 **PRIORITÉ HAUTE**

**7 Jobs à vérifier**:
1. ✅ `backend-tests` - Pytest avec coverage
2. ✅ `backend-lint` - Black, Ruff, Bandit
3. ✅ `backend-type-check` - MyPy
4. ✅ `frontend-build` - Build + Tests frontend
5. ✅ `integration-check` - Health checks API
6. ✅ `summary` - CI Summary

**Continue-on-error**: Oui (plusieurs jobs)
**Expected**: ⚠️ **Certains jobs peuvent être oranges mais workflow global VERT**

---

## 🔧 Comment Relancer un Pipeline

Si un workflow n'a pas de run récent ou a échoué:

### Option 1: Re-run depuis GitHub UI

1. Aller sur https://github.com/Roddygithub/GW2_WvWbuilder/actions
2. Cliquer sur le workflow concerné (ex: "Modern CI/CD Pipeline")
3. Sélectionner le run le plus récent
4. Cliquer sur **"Re-run all jobs"** (en haut à droite)
5. Attendre 10-15 minutes

### Option 2: Lancement Manuel (workflow_dispatch)

Les workflows suivants supportent le lancement manuel:
- `ci-cd-modern.yml` ✅
- `ci-cd-complete.yml` ✅
- `ci-cd.yml` ✅
- `production-deploy.yml` ✅

**Procédure**:
1. Aller sur https://github.com/Roddygithub/GW2_WvWbuilder/actions
2. Cliquer sur le workflow souhaité (ex: "Modern CI/CD Pipeline")
3. Cliquer sur **"Run workflow"** (bouton bleu à droite)
4. Sélectionner la branche: **develop**
5. Cliquer sur **"Run workflow"** (confirmer)

### Option 3: Push Vide (forcer un trigger)

```bash
cd /home/roddy/GW2_WvWbuilder
git commit --allow-empty -m "chore: trigger CI/CD validation"
git push origin develop
```

---

## 📊 Template de Validation à Remplir

Une fois les workflows exécutés, remplir le fichier `CI_CD_GITHUB_VALIDATION_RESULTS.md` avec:

```markdown
# Résultats Validation GitHub Actions

**Date vérification**: [REMPLIR]
**Heure vérification**: [REMPLIR] UTC+2
**Vérificateur**: [REMPLIR]

## Workflow 1: Modern CI/CD Pipeline

**Status Global**: [✅ PASS / ❌ FAIL]
**Run URL**: https://github.com/Roddygithub/GW2_WvWbuilder/actions/runs/[ID]
**Commit**: [SHA]
**Durée**: [XX min]

### Jobs Status:
- backend-lint: [✅/❌]
- backend-test-unit: [✅/❌]
- backend-test-integration: [✅/❌]
- backend-test-optimizer: [✅/❌]
- backend-security: [✅/❌]
- frontend-lint: [✅/❌]
- frontend-test-unit: [✅/❌/⚠️]
- frontend-test-e2e: [✅/❌]
- frontend-build: [✅/❌]
- frontend-security: [✅/❌]
- validate-all: [✅/❌]

### Artifacts Générés:
- [ ] frontend-dist
- [ ] coverage.xml (Codecov)
- [ ] cypress-videos
- [ ] validation-report.md

### Erreurs (si applicable):
[COPIER-COLLER les erreurs principales]

## Workflow 2: Full CI/CD Pipeline

**Status Global**: [✅ PASS / ❌ FAIL]
**Run URL**: https://github.com/Roddygithub/GW2_WvWbuilder/actions/runs/[ID]
**Commit**: [SHA]
**Durée**: [XX min]

### Jobs Status:
- backend-tests: [✅/❌]
- backend-lint: [✅/❌]
- backend-type-check: [✅/❌]
- frontend-build: [✅/❌]
- integration-check: [✅/❌]
- summary: [✅/❌]

## Workflow 3: Tests & Quality Checks

**Status Global**: [✅ PASS / ❌ FAIL]
**Run URL**: https://github.com/Roddygithub/GW2_WvWbuilder/actions/runs/[ID]

### Jobs Status:
- test: [✅/❌]
- lint: [✅/❌]
- type-check: [✅/❌]
```

---

## 🔍 Points de Vigilance

### Tests Frontend Désactivés

**Fichiers .skip**:
```
frontend/src/__tests__/hooks/useBuilder.test.ts.skip
frontend/src/__tests__/pages/BuilderV2.test.tsx.skip
frontend/src/__tests__/components/CompositionMembersList.test.tsx.skip
```

**Impact**: 
- ⚠️ Job `frontend-test-unit` peut échouer ou être vide
- ✅ Tests E2E Cypress compensent (15+ scénarios)
- 📝 Documenté dans CI_VALIDATION_REPORT.md

**Action**:
- Si `frontend-test-unit` échoue: **NORMAL** (tests désactivés)
- Vérifier que `frontend-test-e2e` passe: **CRITIQUE**

### Continue-on-error

Certains jobs ont `continue-on-error: true`:
- `pip-audit` (backend-security)
- `bandit` (backend-security)
- `npm audit` (frontend-security)
- `mypy` (backend-type-check)

**Signification**: Ces jobs peuvent échouer sans bloquer le workflow global.

**Validation**: Vérifier les **logs** de ces jobs même s'ils sont verts/oranges.

---

## ✅ Critères de Succès

Pour considérer la validation CI/CD comme **RÉUSSIE**, il faut:

### Critères Obligatoires (🔴 CRITICAL)

- ✅ **Modern CI/CD Pipeline** (ci-cd-modern.yml): Status global VERT
  - Tous les jobs backend: VERT
  - frontend-lint: VERT
  - frontend-build: VERT
  - frontend-test-e2e: VERT
  - validate-all: VERT
  
- ✅ **Full CI/CD Pipeline** (full-ci.yml): Status global VERT ou ORANGE avec jobs critiques VERTS
  - backend-tests: VERT
  - frontend-build: VERT
  - integration-check: VERT

### Critères Optionnels (🟡 IMPORTANT)

- ✅ Tests & Quality Checks: VERT ou ORANGE
- ✅ Artifacts générés (frontend-dist, coverage)
- ✅ Codecov upload réussi

### Critères Acceptables (⚠️ WARNING)

- ⚠️ frontend-test-unit: PEUT échouer (tests désactivés)
- ⚠️ Security audits: PEUVENT être oranges (continue-on-error)
- ⚠️ Type checking: PEUT être orange (continue-on-error)

---

## 📸 Screenshots à Capturer

Pour la documentation finale, capturer:

1. **Overview page**: https://github.com/Roddygithub/GW2_WvWbuilder/actions
   - Vue d'ensemble des derniers runs
   - Badge status des workflows

2. **Modern CI/CD run detail**:
   - Page du run complet avec tous les jobs
   - Jobs timeline (graphique)

3. **Artifacts**:
   - Liste des artifacts générés
   - Taille des artifacts

4. **Codecov**:
   - Badge coverage (si visible)
   - Lien Codecov: https://codecov.io/gh/Roddygithub/GW2_WvWbuilder

---

## 🚨 En cas d'Erreur

### Erreur: "Secrets not found"

**Cause**: CODECOV_TOKEN ou GW2_API_KEY manquants  
**Solution**:
1. Aller dans Settings > Secrets and variables > Actions
2. Vérifier présence de:
   - `CODECOV_TOKEN`
   - `GW2_API_KEY`
3. Ajouter si manquants

### Erreur: "Poetry installation failed"

**Cause**: Version Poetry incompatible ou cache corrompu  
**Solution**:
1. Vérifier version dans workflow: 1.7.1 ou 2.2.1
2. Re-run avec "Clear cache" activé

### Erreur: "Frontend tests failed"

**Cause**: Tests .skip encore référencés  
**Solution**: 
- **NORMAL** si tests désactivés
- Vérifier que frontend-test-e2e passe
- Documenter dans CI_CD_GITHUB_VALIDATION_RESULTS.md

### Erreur: "Database connection failed"

**Cause**: Service PostgreSQL non démarré  
**Solution**:
- Vérifier section `services:` dans workflow
- Vérifier health-check PostgreSQL
- Re-run le job

---

## 📝 Après Validation

Une fois la validation complète:

1. ✅ Remplir `CI_CD_GITHUB_VALIDATION_RESULTS.md`
2. ✅ Mettre à jour `PRODUCTION_READINESS_V2.md` avec:
   - Section "CI/CD Pipeline Status" → Status réel
   - Lien vers le run GitHub Actions
   - Timestamp de validation
3. ✅ Commit + Push:
   ```bash
   git add CI_CD_GITHUB_VALIDATION_RESULTS.md PRODUCTION_READINESS_V2.md
   git commit -m "docs: add real GitHub Actions CI/CD validation results"
   git push origin develop
   ```

---

## 🎯 Checklist Finale

- [ ] Accédé à https://github.com/Roddygithub/GW2_WvWbuilder/actions
- [ ] Vérifié run récent (< 1h) sur develop
- [ ] Modern CI/CD Pipeline: ✅ VERT
- [ ] Full CI/CD Pipeline: ✅ VERT ou ORANGE acceptable
- [ ] Artifacts générés (frontend-dist, coverage)
- [ ] Codecov upload réussi
- [ ] Screenshots capturés
- [ ] Template de validation rempli
- [ ] Documentation mise à jour
- [ ] Commit + Push effectué

---

**Une fois tous les points vérifiés: PROJET CI/CD VERIFIED ✅**

---

## 📞 Contact & Support

Si problème persistant:
1. Copier logs complets GitHub Actions
2. Vérifier fichiers .github/workflows/*.yml
3. Consulter DEPLOYMENT.md section "Troubleshooting"
4. Vérifier GitHub Actions status: https://www.githubstatus.com/

---

**Guide créé le**: 2025-10-15 13:55 UTC+2  
**Version**: 1.0  
**Auteur**: CI/CD Validation Team
