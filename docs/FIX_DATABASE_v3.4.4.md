# Fix Base de Données - v3.4.4

**Problème**: `no such column: users.first_name`  
**Cause**: Base de données ancienne sans les nouvelles colonnes  
**Solution**: Base recréée ✅

---

## ✅ Base de Données Recréée

La base `gw2_wvwbuilder.db` a été recréée avec **19 tables** et le schéma à jour:

**Table users** maintenant avec:
- id
- username
- email  
- hashed_password
- full_name
- **first_name** ✅ (nouveau)
- **last_name** ✅ (nouveau)
- is_active
- is_superuser
- is_verified
- created_at
- updated_at

---

## 🔧 Créer Utilisateur de Test

### Option 1: Via Script Python

```bash
cd /home/roddy/GW2_WvWbuilder/backend
poetry run python create_test_user.py
```

Le script `create_test_user.py` est déjà créé et va ajouter:
- **Email**: test@test.com
- **Password**: Test123!
- **Username**: testuser

### Option 2: Via Backend API

Démarrer le backend puis utiliser l'endpoint register:

```bash
# Terminal 1 - Backend
cd backend
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2 - Créer user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@test.com",
    "password": "Test123!",
    "username": "testuser",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### Option 3: Via Frontend (Recommandé)

1. Lancer backend: `cd backend && poetry run uvicorn app.main:app --port 8000`
2. Lancer frontend: `cd frontend && npm run dev`
3. Ouvrir: http://localhost:5173/register
4. Remplir formulaire:
   - Email: test@test.com
   - Password: Test123!
   - Confirm Password: Test123!
   - Username: testuser

---

## 🎯 Test Login

Une fois l'utilisateur créé:

**Via Frontend**:
1. Aller sur: http://localhost:5173/login
2. Email: test@test.com
3. Password: Test123!
4. Cliquer "Sign in"

**Via API**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Test123!"}'
```

Réponse attendue:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

---

## ✅ Validation

L'erreur devrait être résolue:
- ❌ Avant: `no such column: users.first_name`
- ✅ Après: Login fonctionne correctement

---

## 📝 Commandes Rapides

```bash
# Backend
cd /home/roddy/GW2_WvWbuilder/backend
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend  
cd /home/roddy/GW2_WvWbuilder/frontend
npm run dev

# Créer user test (si nécessaire)
cd /home/roddy/GW2_WvWbuilder/backend
poetry run python create_test_user.py
```

**Accès Frontend**: http://localhost:5173

---

## 🎉 Résultat Attendu

✅ Frontend charge sans erreur DB  
✅ Page de login affichée  
✅ Registration fonctionne  
✅ Login fonctionne avec test@test.com  
✅ Redirection vers dashboard après login

**Score Frontend attendu**: 85-95/100 ✅
