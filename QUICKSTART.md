# 🚀 Quick Start Guide - GW2 WvW Builder

## Démarrage Rapide (5 minutes)

### 1. Backend
```bash
cd /home/roddy/GW2_WvWbuilder/backend
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend (nouveau terminal)
```bash
cd /home/roddy/GW2_WvWbuilder/frontend
npm run dev
```

### 3. Accès
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 4. Login
```
Username: frontend@user.com
Password: Frontend123!
```

---

## ✨ Nouveau Dashboard

### Fonctionnalités disponibles:
- ✅ **Statistiques en temps réel**
  - Compositions créées
  - Builds créés
  - Teams gérées
  - Activité récente (30 jours)

- ✅ **Flux d'activités**
  - Dernières compositions
  - Derniers builds
  - Dernières teams
  - Timestamps intelligents

- ✅ **Actions rapides**
  - Gestion des tags
  - Squad Builder
  - Compositions

- ✅ **Sécurité**
  - Routes protégées
  - JWT authentication
  - Auto-redirect si non connecté

---

## 🧪 Test Rapide

### Backend
```bash
cd backend
poetry run python -c "
import requests
r = requests.post('http://localhost:8000/api/v1/auth/login',
                  data={'username':'frontend@user.com','password':'Frontend123!'})
print('Login:', r.status_code)
access = r.json()['access_token']
r = requests.get('http://localhost:8000/api/v1/dashboard/stats',
                 headers={'Authorization': f'Bearer {access}'})
print('Stats:', r.status_code, r.json())
"
```

### Frontend
1. Ouvrir http://localhost:5173
2. Login avec credentials
3. Vérifier affichage du dashboard
4. Tester logout

---

## 📚 Documentation Complète

- **Dashboard Overview**: `frontend/DASHBOARD_OVERVIEW.md`
- **Fix Report**: `DASHBOARD_FIX_REPORT.md`
- **API Docs**: http://localhost:8000/docs

---

## 🐛 Troubleshooting

### Backend ne démarre pas
```bash
cd backend
poetry install
poetry run alembic upgrade head
```

### Frontend ne démarre pas
```bash
cd frontend
npm install
```

### 401 Unauthorized
- Vérifier que le backend est démarré
- Vérifier les credentials
- Effacer localStorage et re-login

### CORS errors
- Vérifier `VITE_API_BASE_URL` dans `frontend/.env`
- Devrait être: `http://localhost:8000`

---

## 🎯 Prochaines Étapes

1. **Créer des données de test**
   - Compositions
   - Builds
   - Teams

2. **Explorer les fonctionnalités**
   - Tags Manager
   - Squad Builder (en développement)
   - Compositions

3. **Contribuer**
   - Voir `DASHBOARD_OVERVIEW.md` pour les prochaines features
   - Branch: `develop`

---

**Bon développement! 🚀**
