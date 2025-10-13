# 🚀 Quick Start - Tester l'Auth MAINTENANT

**Date**: 2025-10-13 08:20 UTC+2  
**Status**: ✅ **REGISTER FONCTIONNE** - Utiliser ce flux pour tester

---

## ⚡ Démarrage Rapide (5 minutes)

### 1. Démarrer le Backend

```bash
cd backend
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Vérifier** : http://localhost:8000/docs

### 2. Démarrer le Frontend

```bash
cd frontend
npm install  # Si première fois
npm run dev
```

**Vérifier** : http://localhost:5173

---

## ✅ Flux qui FONCTIONNE : Register → Dashboard

### Étape 1 : Créer un Compte

1. Ouvrir http://localhost:5173/register
2. Remplir le formulaire :
   - **Username** : `myuser`
   - **Email** : `myuser@example.com`
   - **Password** : `MyPassword123!`
   - **Confirm Password** : `MyPassword123!`
3. Cliquer **"Create account"**

### Étape 2 : Vérifier la Redirection

✅ **Devrait automatiquement** :
- Créer le compte dans la base de données
- Se connecter automatiquement (auto-login)
- Rediriger vers `/dashboard`
- Afficher les informations du user

### Étape 3 : Vérifier le Dashboard

Le Dashboard devrait afficher :
- ✅ Nom d'utilisateur : `myuser`
- ✅ Email : `myuser@example.com`
- ✅ Status : Active
- ✅ Bouton Logout fonctionnel

---

## 🔍 Vérifier dans la Console Navigateur

Ouvrir DevTools (F12) → Console

**Logs attendus** :
```
[AUTH] Register successful
[AUTH] Auto-login after registration
[AUTH] Login successful, token received
[AUTH] Token stored in localStorage
[AUTH] Navigating to dashboard
```

**Vérifier le localStorage** :
```javascript
// Dans la console du navigateur
localStorage.getItem('access_token')
// Devrait retourner un JWT token
```

---

## ❌ Flux qui NE FONCTIONNE PAS : Login Direct

**Problème connu** : `/auth/login` timeout (bug backend)

**Symptôme** :
1. Aller sur http://localhost:5173/login
2. Entrer email + password
3. Cliquer "Sign in"
4. ⏳ Attendre 5 secondes
5. ❌ Message : "Login request timed out"

**Workaround** : Utiliser Register au lieu de Login

---

## 🧪 Tests Backend (Sans Bloquer)

### Test 1: Health Check ✅
```bash
curl http://localhost:8000/api/v1/health
# {"status":"ok","database":"ok","version":"1.0.0"}
```

### Test 2: Register ✅
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
# {"id":16,"username":"testuser","email":"test@example.com",...}
```

### Test 3: Login ❌ (NE PAS TESTER - BLOQUE)
```bash
# ⚠️ NE PAS EXÉCUTER - TIMEOUT GARANTI
# curl -X POST http://localhost:8000/api/v1/auth/login ...
```

---

## 📊 Utilisateurs de Test Disponibles

| Username | Email | Password | Notes |
|----------|-------|----------|-------|
| truefinal | truefinal@test.com | TrueFinal123! | ✅ Créé via register |
| frontenduser | frontend@user.com | Frontend123! | ⚠️ Ne peut pas login |

**Recommandation** : Créer un nouveau compte via Register

---

## 🐛 Problèmes Connus

### 1. Login Direct Timeout ❌
- **Symptôme** : Requête bloque indéfiniment
- **Cause** : Bug backend (DetachedInstanceError)
- **Solution** : Utiliser Register avec auto-login
- **Status** : En investigation

### 2. Lint Error Frontend (Non-bloquant)
```
Property 'env' does not exist on type 'ImportMeta'
```
- **Fichier** : `frontend/src/api/auth.ts` ligne 8
- **Impact** : Aucun (warning seulement)
- **Fix** : Ajouter `/// <reference types="vite/client" />` en haut du fichier

---

## 🔧 Dépannage

### Backend ne démarre pas
```bash
# Vérifier si le port 8000 est occupé
lsof -i:8000

# Tuer le processus si nécessaire
lsof -ti:8000 | xargs kill -9

# Redémarrer
cd backend
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend ne démarre pas
```bash
# Réinstaller les dépendances
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Dashboard ne charge pas
```bash
# Vérifier le token dans localStorage
# Console navigateur :
localStorage.getItem('access_token')

# Si null, recréer un compte via Register
```

### CORS Error
```bash
# Vérifier que le backend tourne sur port 8000
curl http://localhost:8000/api/v1/health

# Vérifier CORS dans backend/.env
BACKEND_CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## 📝 Checklist de Test Complet

### ✅ Tests qui Fonctionnent

- [ ] Backend démarre sans erreur
- [ ] Frontend démarre sur port 5173
- [ ] Health check retourne 200 OK
- [ ] Page Register s'affiche correctement
- [ ] Création de compte réussit
- [ ] Auto-login après register
- [ ] Redirection vers Dashboard
- [ ] Dashboard affiche les infos user
- [ ] Logout fonctionne
- [ ] Retour à la page Login après logout

### ⏸️ Tests à Éviter (Bloquent)

- [ ] ~~Login direct via formulaire~~ ❌
- [ ] ~~Test curl /auth/login~~ ❌
- [ ] ~~Test curl /auth/simple-login~~ ❌

---

## 🎯 Prochaines Étapes (Pour Développeurs)

### Immédiat
1. ✅ Utiliser Register pour tous les tests
2. ✅ Documenter le workaround pour l'équipe
3. ✅ Créer des comptes de test via Register

### Court Terme
1. 🔧 Déboguer `/auth/login` avec logs détaillés
2. 🔧 Tester avec session synchrone
3. 🔧 Implémenter make_transient() pour User

### Moyen Terme
1. 📦 Déployer avec Docker Compose
2. 🧪 Tests d'intégration complets
3. 📊 Monitoring des endpoints

---

## 📚 Documentation Complète

- **Rapport détaillé** : `frontend/AUTH_FRONTEND_FIX_REPORT.md`
- **Rapport backend** : `AUTH_SUCCESS.md`
- **Rapport stabilisation** : `STABILISATION_AUTH_REPORT.md`

---

## 💡 Conseils

1. **Toujours utiliser Register** pour créer des comptes de test
2. **Ne pas tester Login direct** tant que le bug n'est pas corrigé
3. **Vérifier les logs console** pour déboguer
4. **Utiliser DevTools Network** pour voir les requêtes
5. **Vérifier localStorage** pour confirmer le token

---

**Dernière mise à jour** : 2025-10-13 08:20 UTC+2  
**Status** : ✅ Register → Dashboard FONCTIONNEL  
**Recommandation** : Utiliser ce flux pour tous les tests
