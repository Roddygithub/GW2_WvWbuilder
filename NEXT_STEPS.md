# 🚀 Prochaines Étapes - Plan d'Exécution

**Date:** 14 octobre 2025
**Statut:** develop @ c9d56be  
**Basé sur:** AUDIT_COMPLETE_REPORT.md

---

## ⚡ ACTIONS IMMÉDIATES (Aujourd'hui)

### 1. 🔐 CRITIQUE - Sécuriser les Clés JWT (15 minutes)

**Pourquoi:** Clés secrètes exposées dans le repo = risque de sécurité majeur

**Actions:**
```bash
cd /home/roddy/GW2_WvWbuilder/backend

# Générer 3 nouvelles clés fortes
echo "Nouvelles clés:"
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))"
python3 -c "import secrets; print('JWT_REFRESH_SECRET_KEY=' + secrets.token_hex(32))"
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
```

**Ensuite:**
1. Copier ces 3 clés
2. Ouvrir `backend/.env`
3. Remplacer les lignes 12, 13 et 20 avec les nouvelles clés
4. Sauvegarder

**Vérifier que .env est ignoré:**
```bash
cd /home/roddy/GW2_WvWbuilder
git check-ignore backend/.env

# Si aucune sortie (pas ignoré), ajouter:
echo "backend/.env" >> .gitignore
git add .gitignore
git commit -m "security: ensure .env files are ignored"
```

**⚠️ IMPORTANT:** Si `.env` a déjà été commité, il faut nettoyer l'historique Git:
```bash
# Supprimer de l'historique (ATTENTION: opération dangereuse)
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch backend/.env' \
  --prune-empty --tag-name-filter cat -- --all

# Puis force push (si repo distant)
git push origin --force --all
```

---

### 2. 🔧 URGENT - Fixer les Erreurs TypeScript (20 minutes)

**Pourquoi:** Le build frontend échoue actuellement

**Étape A - Installer les types manquants:**
```bash
cd /home/roddy/GW2_WvWbuilder/frontend

# Installer @types/jest pour les tests
npm install --save-dev @types/jest

# Vérifier
npm run build 2>&1 | grep "error TS"
```

**Étape B - Décider du sort de Storybook:**

**Option 1 - Garder Storybook (si utilisé):**
```bash
npm install --save-dev @storybook/react-vite storybook
```

**Option 2 - Supprimer Storybook (si non utilisé):**
```bash
rm -rf src/stories/
rm -rf .storybook/
npm uninstall @storybook/react @storybook/react-vite storybook
```

**Étape C - Fixer asChild prop:**
```bash
# Mettre à jour Radix UI
npm update @radix-ui/react-slot
```

**Étape D - Vérifier le build:**
```bash
npm run build

# Devrait afficher: "Build completed successfully"
```

**Commit:**
```bash
git add package.json package-lock.json
git commit -m "fix: resolve TypeScript compilation errors"
```

---

### 3. ✅ Test de Validation (10 minutes)

**Vérifier que tout fonctionne:**

```bash
# Terminal 1 - Backend
cd /home/roddy/GW2_WvWbuilder/backend
poetry run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2 - Tests E2E (après 5 secondes)
cd /home/roddy/GW2_WvWbuilder/frontend
npm run e2e:headless

# Résultat attendu: 79.1% passing (34/43)
```

---

## 📅 CETTE SEMAINE (15-20 Oct)

### 4. 🧹 Nettoyer la Configuration (30 minutes)

**A. Consolider les fichiers .env:**
```bash
cd /home/roddy/GW2_WvWbuilder/backend

# Supprimer les doublons
rm .env.dev .env.development  # Obsolètes
rm .env.example.new  # Ancien template

# Garder seulement:
# - .env (développement local)
# - .env.example (template pour nouveaux devs)
# - .env.test (tests automatisés)
# - .env.production (déploiement prod)

# Vérifier .gitignore couvre tout
cat .gitignore | grep "\.env"
```

**B. Mettre à jour CORS dans .env:**
```bash
# Éditer backend/.env ligne 31
# Remplacer:
BACKEND_CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:8000

# Par:
BACKEND_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000
```

**Commit:**
```bash
git add backend/.env.example
git commit -m "chore: consolidate .env files and update CORS config"
```

### 5. 🐍 Migrer pyproject.toml vers PEP 621 (45 minutes)

**Backup:**
```bash
cd /home/roddy/GW2_WvWbuilder/backend
cp pyproject.toml pyproject.toml.backup
```

**Éditer pyproject.toml:**
```toml
# Ajouter en haut du fichier (avant [tool.poetry])
[project]
name = "gw2-wvwbuilder-backend"
version = "1.0.0"
description = "GW2 WvW Builder API - FastAPI backend for Guild Wars 2 WvW build management"
authors = [
    {name = "Roddy", email = "roddy@example.com"}
]
readme = "README.md"
requires-python = ">=3.11,<4.0"
license = {text = "MIT"}

[project.urls]
Homepage = "https://github.com/Roddygithub/GW2_WvWbuilder"
Repository = "https://github.com/Roddygithub/GW2_WvWbuilder.git"

# Garder [tool.poetry] pour la gestion des dépendances
[tool.poetry]
# Poetry continuera à gérer les dépendances ici
```

**Tester:**
```bash
poetry check
poetry lock --no-update
poetry install
```

**Commit:**
```bash
git add pyproject.toml
git commit -m "chore: migrate pyproject.toml to PEP 621 standard"
```

### 6. 📊 Améliorer la Couverture de Tests (2 heures)

**Créer les fichiers de test manquants:**

```bash
cd /home/roddy/GW2_WvWbuilder/backend

# Créer la structure
mkdir -p tests/unit/services
touch tests/unit/services/__init__.py
touch tests/unit/services/test_gw2_api.py
touch tests/unit/services/test_webhook_service.py
touch tests/unit/test_worker.py
```

**Exemple - tests/unit/services/test_gw2_api.py:**
```python
"""Tests for GW2 API service."""
import pytest
from unittest.mock import AsyncMock, patch
from app.services.gw2_api import GW2APIService

@pytest.mark.asyncio
async def test_get_items_success():
    """Test successful item retrieval."""
    service = GW2APIService()
    
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {"id": 12345, "name": "Test Item"}
        mock_get.return_value.__aenter__.return_value = mock_response
        
        result = await service.get_item(12345)
        
        assert result["id"] == 12345
        assert result["name"] == "Test Item"

@pytest.mark.asyncio
async def test_get_items_not_found():
    """Test item not found handling."""
    service = GW2APIService()
    
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_get.return_value.__aenter__.return_value = mock_response
        
        with pytest.raises(Exception):
            await service.get_item(99999)
```

**Exécuter et vérifier:**
```bash
poetry run pytest tests/unit/services/ -v --cov=app/services
```

**Commit:**
```bash
git add tests/unit/services/
git commit -m "test: add unit tests for GW2 API and webhook services"
```

---

## 🗓️ SEMAINE PROCHAINE (21-27 Oct)

### 7. 🔐 Implémenter Registration Backend (3 heures)

**Créer le endpoint:**
```bash
cd /home/roddy/GW2_WvWbuilder/backend
# Éditer app/api/api_v1/endpoints/auth.py
```

**Ajouter:**
```python
@router.post("/register", response_model=schemas.Token, status_code=status.HTTP_201_CREATED)
async def register(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    user_in: schemas.UserCreate,
) -> Any:
    """
    Register a new user.
    """
    # Vérifier si l'email existe déjà
    user = await crud.user.get_by_email_async(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists in the system",
        )
    
    # Créer l'utilisateur
    user = await crud.user.create_async(db, obj_in=user_in)
    
    # Générer les tokens
    access_token = security.create_access_token(user.id)
    refresh_token = security.create_refresh_token(user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
```

**Tester:**
```bash
# Lancer le backend
poetry run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Dans un autre terminal
curl -X POST http://127.0.0.1:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"newuser@test.com","password":"Test123!","full_name":"New User"}'
```

**Commit:**
```bash
git add app/api/api_v1/endpoints/auth.py
git commit -m "feat: implement user registration endpoint"
```

### 8. ✅ Validation Client-Side Frontend (2 heures)

**Éditer frontend/src/pages/Register.tsx:**
```typescript
import { z } from 'zod';

// Schéma de validation
const registerSchema = z.object({
  email: z.string().email("Invalid email format"),
  password: z.string()
    .min(8, "Password must be at least 8 characters")
    .regex(/[A-Z]/, "Password must contain uppercase letter")
    .regex(/[0-9]/, "Password must contain number")
    .regex(/[!@#$%^&*]/, "Password must contain special character"),
  confirmPassword: z.string(),
  fullName: z.string().min(2, "Name must be at least 2 characters"),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords do not match",
  path: ["confirmPassword"],
});

// Dans le composant
const {
  register,
  handleSubmit,
  formState: { errors },
} = useForm<RegisterFormData>({
  resolver: zodResolver(registerSchema),
});
```

**Tester:**
```bash
cd frontend
npm run dev

# Ouvrir http://localhost:5173/register
# Tester la validation
```

**Commit:**
```bash
git add src/pages/Register.tsx
git commit -m "feat: add client-side validation for registration"
```

### 9. 🧪 Relancer les Tests E2E (30 minutes)

```bash
cd /home/roddy/GW2_WvWbuilder/frontend
npm run e2e:headless

# Résultat attendu après registration:
# - Tests passing: 40/43 (93%)
# - Seuls 3 échecs restants (edge cases)
```

**Si > 90% passing:**
```bash
git add cypress/
git commit -m "test: update E2E tests after registration implementation"
```

---

## 🔮 MOYEN TERME (Nov)

### 10. 📦 Mise à Jour des Dépendances (4 heures)

**Phase 1 - Updates mineures:**
```bash
cd frontend
npm update
npm audit fix
npm run build
npm run test
```

**Phase 2 - React 19:**
```bash
npm install react@19 react-dom@19
npm run build
npm run e2e:headless
# Si échec: rollback et investiguer
```

**Phase 3 - Cypress 15:**
```bash
npm install cypress@15
npm run e2e:headless
```

**Phase 4 - ESLint 9:**
```bash
npm install eslint@9 @typescript-eslint/eslint-plugin@8
npm run lint
```

### 11. 📚 Documentation (2 heures)

**Créer/Mettre à jour:**
- `DEPLOYMENT.md` - Guide de déploiement
- `CONTRIBUTING.md` - Guide pour contributeurs
- `API_DOCUMENTATION.md` - Documentation API complète
- `ARCHITECTURE.md` - Diagrammes et explications

---

## 📊 INDICATEURS DE SUCCÈS

### Métriques à Suivre

**Cette Semaine:**
- [ ] Clés JWT sécurisées (✅/❌)
- [ ] Build frontend sans erreurs (✅/❌)
- [ ] Tests E2E: 79% → ??? %
- [ ] Fichiers .env consolidés (✅/❌)

**Semaine Prochaine:**
- [ ] Endpoint /register implémenté (✅/❌)
- [ ] Validation client-side active (✅/❌)
- [ ] Tests E2E: ??? → >90%
- [ ] Coverage backend: 28% → 35%

**Fin du Mois:**
- [ ] Dépendances à jour (✅/❌)
- [ ] Tests E2E: >93%
- [ ] Coverage backend: >40%
- [ ] Documentation complète (✅/❌)

---

## 🎯 CHECKLIST QUOTIDIENNE

### Avant de Commencer le Travail
- [ ] `git pull origin develop`
- [ ] Backend démarré et health check OK
- [ ] Frontend build sans erreurs
- [ ] Environnement virtuel activé

### Pendant le Travail
- [ ] Tests passent avant chaque commit
- [ ] Messages de commit descriptifs
- [ ] Code review (si équipe)
- [ ] Documentation à jour

### Avant de Finir
- [ ] `git push origin develop`
- [ ] CI/CD vert
- [ ] CHANGELOG mis à jour (si applicable)
- [ ] Tests E2E vérifiés

---

## 🆘 EN CAS DE PROBLÈME

### Backend ne démarre pas
```bash
cd backend
poetry install
poetry run alembic upgrade head
rm gw2_wvwbuilder.db  # En dernier recours
```

### Frontend ne build pas
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Tests E2E échouent tous
```bash
# Vérifier le backend
curl http://127.0.0.1:8000/api/v1/health

# Vérifier le test user
cd backend
poetry run python scripts/seed_test_user.py

# Nettoyer Cypress
cd frontend
rm -rf cypress/screenshots cypress/videos
npx cypress cache clear
npm run e2e:headless
```

### Git conflicts
```bash
git stash
git pull --rebase origin develop
git stash pop
# Résoudre les conflits
git add .
git rebase --continue
```

---

## 📞 RESSOURCES

**Documentation:**
- Audit complet: `AUDIT_COMPLETE_REPORT.md`
- Tests E2E: `E2E_FINAL_SUCCESS.md`
- Sécurité: `SECURITY.md`
- Tests: `TESTING.md`

**Scripts Utiles:**
- Check backend: `./CHECK_BACKEND.sh`
- Seed data: `backend/scripts/seed_test_user.py`
- Fix test user: `backend/scripts/fix_test_user.py`

**Commandes Rapides:**
```bash
# Backend
alias be-start="cd backend && poetry run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
alias be-test="cd backend && poetry run pytest"
alias be-cov="cd backend && poetry run pytest --cov=app --cov-report=html"

# Frontend
alias fe-dev="cd frontend && npm run dev"
alias fe-build="cd frontend && npm run build"
alias fe-test="cd frontend && npm run e2e:headless"
alias fe-lint="cd frontend && npm run lint"

# Git
alias gs="git status"
alias gp="git pull"
alias gc="git commit -m"
alias gps="git push"
```

---

**Créé par:** Cascade AI  
**Date:** 14 octobre 2025, 23:50  
**Basé sur:** AUDIT_COMPLETE_REPORT.md  
**Pour:** Projet GW2 WvW Builder
