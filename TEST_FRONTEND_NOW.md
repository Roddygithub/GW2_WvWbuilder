# 🚀 TEST FRONTEND - Guide Rapide

**Date**: 2025-10-13 09:35 UTC+2  
**Status**: ✅ Backend prêt, frontend à tester

---

## ⚡ Démarrage (2 minutes)

### Terminal 1 - Backend

```bash
cd /home/roddy/GW2_WvWbuilder/backend
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Vérifier** : http://localhost:8000/docs

### Terminal 2 - Frontend

```bash
cd /home/roddy/GW2_WvWbuilder/frontend
npm run dev
```

**Vérifier** : http://localhost:5173

---

## ✅ Test 1: Login Direct (NOUVEAU - FONCTIONNE !)

### Étapes

1. Ouvrir http://localhost:5173/login
2. Entrer :
   - **Username** : `frontend@user.com`
   - **Password** : `Frontend123!`
3. Cliquer **"Sign in"**

### Résultat Attendu

✅ Redirection vers `/dashboard`  
✅ Dashboard affiche :
- Username: `frontenduser`
- Email: `frontend@user.com`
- Status: Active

### Si ça ne fonctionne pas

**Ouvrir DevTools (F12) → Console**

Logs attendus :
```
[AUTH] Login attempt: { username: "frontend@user.com", ... }
[AUTH] Sending login request...
[AUTH] Response received: 200 OK
[AUTH] Login successful, token received
[AUTH] Token stored in localStorage
```

Si erreur :
- Vérifier que le backend tourne (http://localhost:8000/health)
- Vérifier CORS dans backend/.env
- Vérifier les logs backend

---

## ✅ Test 2: Register puis Login

### Étapes

1. Ouvrir http://localhost:5173/register
2. Créer un compte :
   - **Username** : `testuser`
   - **Email** : `test@example.com`
   - **Password** : `TestPass123!`
   - **Confirm** : `TestPass123!`
3. Cliquer **"Create account"**
4. ✅ Devrait auto-login et rediriger vers `/dashboard`
5. Cliquer **"Logout"**
6. Aller sur http://localhost:5173/login
7. Se reconnecter avec :
   - **Username** : `test@example.com`
   - **Password** : `TestPass123!`
8. ✅ Devrait rediriger vers `/dashboard`

---

## ✅ Test 3: Gestion des Erreurs

### Test 3a: Mauvais mot de passe

1. Aller sur http://localhost:5173/login
2. Entrer :
   - **Username** : `frontend@user.com`
   - **Password** : `WrongPassword`
3. Cliquer **"Sign in"**
4. ✅ Devrait afficher : "Incorrect email or password"

### Test 3b: Utilisateur inexistant

1. Aller sur http://localhost:5173/login
2. Entrer :
   - **Username** : `notexist@test.com`
   - **Password** : `AnyPassword`
3. Cliquer **"Sign in"**
4. ✅ Devrait afficher : "Incorrect email or password"

---

## 🔍 Vérifications Techniques

### Vérifier le Token dans localStorage

**Console navigateur** :
```javascript
localStorage.getItem('access_token')
// Devrait retourner un long string JWT
```

### Vérifier le Backend

```bash
# Health check
curl http://localhost:8000/api/v1/health
# {"status":"ok","database":"ok","version":"1.0.0"}

# Test login direct
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=frontend@user.com&password=Frontend123!"
# Devrait retourner un token JWT
```

---

## 📊 Checklist Complète

### Backend
- [ ] Backend démarre sans erreur
- [ ] http://localhost:8000/health retourne 200
- [ ] http://localhost:8000/docs accessible
- [ ] POST /auth/login retourne token JWT
- [ ] POST /auth/register crée un user

### Frontend
- [ ] Frontend démarre sur port 5173
- [ ] Page /login s'affiche correctement
- [ ] Page /register s'affiche correctement
- [ ] Page /dashboard s'affiche correctement

### Flux Login
- [ ] Login avec user valide → Dashboard
- [ ] Dashboard affiche username et email
- [ ] Token stocké dans localStorage
- [ ] Logout fonctionne
- [ ] Mauvais password → Message d'erreur
- [ ] User inexistant → Message d'erreur

### Flux Register
- [ ] Register crée un compte
- [ ] Auto-login après register
- [ ] Redirection vers Dashboard
- [ ] Logout puis re-login fonctionne

---

## 🐛 Dépannage

### Problème: "Failed to fetch"

**Cause** : Backend ne tourne pas ou CORS mal configuré

**Solution** :
1. Vérifier backend : `curl http://localhost:8000/health`
2. Vérifier CORS dans `backend/.env` :
   ```
   BACKEND_CORS_ORIGINS=http://localhost:5173,http://localhost:3000
   ```
3. Redémarrer le backend

### Problème: "Login request timed out"

**Cause** : Ancien code backend (avant le fix)

**Solution** :
1. Vérifier que le backend a bien rechargé :
   ```bash
   tail -f /tmp/backend.log | grep "Reloading"
   ```
2. Ou redémarrer complètement :
   ```bash
   pkill -9 -f uvicorn
   cd backend
   poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Problème: Dashboard ne charge pas

**Cause** : Token invalide ou endpoint /users/me ne fonctionne pas

**Solution temporaire** :
1. Le Dashboard devrait quand même s'afficher avec les infos du store
2. Si problème, vérifier le store Zustand :
   ```javascript
   // Console navigateur
   JSON.parse(localStorage.getItem('auth-storage'))
   ```

### Problème: CORS Error

**Erreur console** : "Access to fetch at 'http://localhost:8000' from origin 'http://localhost:5173' has been blocked by CORS"

**Solution** :
1. Vérifier `backend/.env` :
   ```
   BACKEND_CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:8000
   ```
2. Redémarrer le backend

---

## 📝 Utilisateurs de Test

| Username | Email | Password | Notes |
|----------|-------|----------|-------|
| frontenduser | frontend@user.com | Frontend123! | ✅ Testé backend |
| truefinal | truefinal@test.com | TrueFinal123! | ✅ Testé backend |
| shelltest | shelltest@example.com | TestPass123! | Disponible |

---

## 🎯 Résultat Attendu Final

Après tous les tests, tu devrais avoir :

✅ **Login fonctionne** : Connexion via formulaire  
✅ **Register fonctionne** : Création de compte + auto-login  
✅ **Dashboard accessible** : Affiche les infos user  
✅ **Logout fonctionne** : Déconnexion propre  
✅ **Gestion erreurs** : Messages clairs pour les erreurs  
✅ **Token persistant** : Reste connecté après refresh page

---

## 📚 Documentation Complète

- **LOGIN_FIX_SUCCESS.md** : Détails techniques de la correction
- **QUICK_START_AUTH.md** : Guide utilisateur complet
- **frontend/AUTH_FRONTEND_FIX_REPORT.md** : Rapport technique frontend
- **AUTH_SUCCESS.md** : Succès backend register

---

## 💡 Prochaines Étapes

Si tout fonctionne :
1. ✅ Marquer le ticket comme résolu
2. ✅ Documenter pour l'équipe
3. ✅ Créer des tests d'intégration
4. ✅ Déployer en staging

Si problèmes :
1. Vérifier les logs backend et frontend
2. Consulter la section Dépannage
3. Vérifier que le code est à jour (git pull)

---

**Dernière mise à jour** : 2025-10-13 09:35 UTC+2  
**Status** : ✅ Prêt à tester  
**Temps estimé** : 10 minutes pour tous les tests
