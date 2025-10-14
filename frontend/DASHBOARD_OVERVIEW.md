# Dashboard Overview

## 📊 Fonctionnalités Implémentées

### 1. **Architecture & State Management**
- ✅ **Zustand** pour la gestion d'état globale (authentification)
- ✅ **React Query** pour le cache et la synchronisation des données API
- ✅ **Protected Routes** avec redirection automatique vers login
- ✅ Persistance de l'état d'authentification dans localStorage

### 2. **Composants Réutilisables**

#### `ProtectedRoute.tsx`
Wrapper pour sécuriser les routes nécessitant une authentification.
```tsx
<Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
```

#### `StatCard.tsx`
Carte de statistique réutilisable avec:
- Icône personnalisable (Lucide React)
- Valeur principale
- Sous-titre optionnel
- Indicateur de tendance (optionnel)

#### `ActivityFeed.tsx`
Flux d'activités récentes avec:
- Support de différents types d'activités (composition, build, team, tag)
- Formatage intelligent des timestamps
- État vide avec message approprié
- Icônes colorées par type d'activité

### 3. **Dashboard Principal** (`Dashboard.tsx`)

#### Sections:
1. **Header**
   - Titre de l'application
   - Message de bienvenue personnalisé
   - Bouton de déconnexion

2. **Statistiques (Overview)**
   - Nombre total de compositions
   - Nombre total de builds
   - Nombre total d'équipes
   - Activité récente (30 derniers jours)

3. **Informations Utilisateur**
   - Username
   - Email
   - Nom complet (si disponible)
   - Statut du compte (actif/inactif)
   - Badge admin (si superuser)

4. **Actions Rapides**
   - Gestion des tags
   - Squad Builder
   - Compositions

5. **Activité Récente**
   - Flux des 5 dernières activités
   - Timestamps formatés intelligemment

6. **Statut Système**
   - État de connexion au backend
   - État de l'authentification
   - Disponibilité des APIs

### 4. **API Endpoints Backend**

#### `/api/v1/dashboard/stats`
Retourne les statistiques de l'utilisateur:
```json
{
  "total_compositions": 0,
  "total_builds": 0,
  "total_teams": 0,
  "recent_activity_count": 0
}
```

#### `/api/v1/dashboard/activities?limit=10`
Retourne les activités récentes:
```json
[
  {
    "id": "comp-1",
    "type": "composition",
    "title": "Created composition: My Squad",
    "description": "WvW composition for zerg",
    "timestamp": "2025-10-13T14:00:00"
  }
]
```

## 🎨 Design System

### Couleurs
- **Background**: Gradient slate-900 → purple-900 → slate-900
- **Cards**: slate-800/50 avec backdrop-blur
- **Primary**: purple-600
- **Success**: green-400
- **Warning**: yellow-400
- **Error**: red-400

### Icônes (Lucide React)
- **Compositions**: `Layers`
- **Builds**: `FileText`
- **Teams**: `Users`
- **Activity**: `TrendingUp`
- **Tags**: `Tag`
- **Clock**: `Clock`

### Responsive
- Mobile-first design
- Grid adaptatif: 1 col (mobile) → 2 cols (tablet) → 4 cols (desktop)

## 🔐 Sécurité

### Protected Routes
Toutes les routes protégées utilisent le composant `ProtectedRoute`:
- Vérifie l'authentification avant le rendu
- Redirige vers `/login` si non authentifié
- Préserve l'URL de destination pour redirection post-login

### Token Management
- Stockage sécurisé dans localStorage
- Refresh automatique via React Query
- Déconnexion automatique si token expiré

## 🚀 Utilisation

### Démarrage
```bash
# Backend
cd backend
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend
cd frontend
npm run dev
```

### Accès
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Credentials de test
```
Username: frontend@user.com
Password: Frontend123!
```

## 📦 Dépendances

### Frontend
- `react` & `react-dom`: Framework UI
- `react-router-dom`: Routing
- `zustand`: State management
- `@tanstack/react-query`: Data fetching & caching
- `lucide-react`: Icônes
- `tailwindcss`: Styling

### Backend
- `fastapi`: Framework API
- `sqlalchemy`: ORM
- `pydantic`: Validation
- `python-jose`: JWT

## 🔄 Flow d'Authentification

```
1. User → Login Page
2. Submit credentials → POST /api/v1/auth/login
3. Receive access_token
4. Store token in localStorage
5. Redirect to /dashboard
6. Dashboard loads user data → GET /api/v1/users/me
7. Dashboard loads stats → GET /api/v1/dashboard/stats
8. Dashboard loads activities → GET /api/v1/dashboard/activities
```

## 🧪 Tests

### Test Manuel
1. Login avec credentials de test
2. Vérifier affichage des statistiques
3. Vérifier les actions rapides (liens fonctionnels)
4. Vérifier le flux d'activités
5. Tester la déconnexion
6. Vérifier la redirection vers login

### Points de Validation
- ✅ Login réussi → Dashboard affiché
- ✅ Stats chargées depuis l'API
- ✅ User info affichée correctement
- ✅ Logout → Retour au login
- ✅ Accès direct à /dashboard sans auth → Redirect login
- ✅ Responsive sur mobile/tablet/desktop

## 📝 Prochaines Étapes

### Court Terme
- [ ] Ajouter des graphiques (recharts) pour les statistiques
- [ ] Implémenter le filtrage des activités par type
- [ ] Ajouter des notifications toast pour les actions
- [ ] Créer des tests unitaires pour les composants

### Moyen Terme
- [ ] Implémenter le Squad Builder complet
- [ ] Ajouter la gestion des compositions
- [ ] Créer un système de favoris
- [ ] Implémenter le partage de compositions

### Long Terme
- [ ] Intégration GW2 API pour les données en temps réel
- [ ] Système de recommandations de builds
- [ ] Mode collaboratif multi-utilisateurs
- [ ] Export/Import de compositions

## 🐛 Debugging

### Backend Logs
```bash
cd backend
poetry run uvicorn app.main:app --reload --log-level debug
```

### Frontend Dev Tools
- React DevTools pour l'état des composants
- Network tab pour les appels API
- Console pour les erreurs JavaScript

### Common Issues
1. **401 Unauthorized**: Token expiré → Reconnexion
2. **CORS errors**: Vérifier VITE_API_BASE_URL dans .env
3. **Stats not loading**: Vérifier que le backend est démarré
4. **Blank dashboard**: Vérifier la console pour erreurs React

## 📚 Ressources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Query Docs](https://tanstack.com/query/latest)
- [Zustand Docs](https://docs.pmnd.rs/zustand/getting-started/introduction)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Lucide Icons](https://lucide.dev/)
