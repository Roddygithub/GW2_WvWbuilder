# Guide de Test Frontend - GW2_WvWbuilder v3.4.4

**Date**: 2025-10-17 00:42 UTC+2  
**Backend**: ✅ Lancé sur port 8000  
**Frontend**: À lancer sur port 5173  
**Objectif**: Validation complète interface utilisateur

---

## 🚀 Lancement

### Backend (Déjà lancé)
```bash
# Terminal 1
cd /home/roddy/GW2_WvWbuilder/backend
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
# PID: 129557 ✅
```

### Frontend (À lancer)
```bash
# Terminal 2
cd /home/roddy/GW2_WvWbuilder/frontend
npm run dev
```

**Accès**: http://localhost:5173

---

## 📋 Checklist de Test

### 1. Démarrage et Accueil (5 min)

#### ✅ Vérifications Initiales
- [ ] Page d'accueil charge sans erreur
- [ ] Aucune erreur console (F12)
- [ ] Logo et branding affichés
- [ ] Thème (clair/sombre) fonctionne
- [ ] Layout responsive (mobile/desktop)

#### ✅ Composants Visibles
- [ ] **Header**: Navigation principale
- [ ] **Sidebar**: Menu latéral
- [ ] **Footer**: Informations site
- [ ] **Buttons**: Styles cohérents
- [ ] **Icons**: Lucide React chargés

**Score attendu**: 100% - Tous les composants s'affichent

---

### 2. Navigation (5 min)

#### ✅ Routes Principales

| Page | URL | Attendu |
|------|-----|---------|
| Accueil | `/` | Dashboard/Home |
| Dashboard | `/dashboard` | Stats & overview |
| Builder | `/builder` | Build creator V2 |
| Compositions | `/compositions` | Liste compositions |
| Tags | `/tags` | Gestion tags |
| About | `/about` | Informations projet |
| Login | `/login` | Authentification |
| Register | `/register` | Inscription |

**Tests**:
- [ ] Chaque lien fonctionne
- [ ] Pas d'erreurs 404
- [ ] Navigation fluide
- [ ] Breadcrumbs corrects
- [ ] Active link styling

**Score attendu**: 100% - Toutes les routes fonctionnelles

---

### 3. Dashboard (10 min)

#### ✅ Composants Dashboard
- [ ] **StatCards**: Métriques affichées
  - Total builds
  - Total compositions
  - Active teams
  - Recent activity
- [ ] **ActivityFeed**: Dernières actions
- [ ] **QuickActions**: Boutons rapides
- [ ] **Charts**: Graphiques (Recharts)

#### ✅ Données API
```bash
# Test manuel API
curl http://localhost:8000/api/v1/health
# Attendu: {"status":"ok","database":"ok"}
```

- [ ] Dashboard charge données depuis API
- [ ] Loading states affichés
- [ ] Erreurs API gérées gracieusement

**Score attendu**: 90% - Dashboard fonctionnel (données vides OK)

---

### 4. Builder V2 (15 min)

**Page**: `/builder`

#### ✅ Formulaire Build

**Champs**:
- [ ] **Name**: Input texte (3-100 chars)
- [ ] **Description**: Textarea (max 1000 chars)
- [ ] **Game Mode**: Select (WvW, PvP, PvE)
- [ ] **Profession**: Select GW2
- [ ] **Elite Spec**: Select conditionnelle
- [ ] **Team Size**: Number (1-50)
- [ ] **Public/Private**: Toggle

#### ✅ Validation
- [ ] Champs requis validés
- [ ] Longueur min/max respectée
- [ ] Messages d'erreur clairs
- [ ] Formulaire bloque si invalide

#### ✅ Actions
- [ ] **Save Build**: POST /api/v1/builds/
- [ ] **Cancel**: Reset formulaire
- [ ] **Preview**: Affiche aperçu

**Test API**:
```javascript
// Devrait appeler
POST http://localhost:8000/api/v1/builds/
Headers: { "Content-Type": "application/json" }
Body: {
  "name": "Test Build",
  "game_mode": "wvw",
  "team_size": 5,
  "is_public": true
}
// Attendu: 201 Created ou 401 Unauthorized
```

**Score attendu**: 85% - Formulaire fonctionne (auth manquante OK)

---

### 5. Compositions (15 min)

**Page**: `/compositions`

#### ✅ Liste Compositions
- [ ] Tableau/Cards affichés
- [ ] Colonnes: Name, Mode, Team Size, Status
- [ ] Pagination fonctionnelle
- [ ] Filtres applicables
- [ ] Recherche texte

#### ✅ Actions CRUD
- [ ] **Create**: Bouton "New Composition"
- [ ] **Read**: Click composition → détails
- [ ] **Update**: Bouton "Edit"
- [ ] **Delete**: Bouton "Delete" + confirmation

#### ✅ Détails Composition
**Page**: `/compositions/:id`

- [ ] **Header**: Nom, mode, statut
- [ ] **Members List**: Roles et builds
- [ ] **Stats**: Synergies, boons
- [ ] **Actions**: Edit, Delete, Share

#### ✅ Création Composition
**Page**: `/compositions/create`

- [ ] **Form fields**: Name, mode, description
- [ ] **Team builder**: Ajouter membres
- [ ] **Role assignment**: Support, DPS, Healer
- [ ] **Validation**: Champs requis
- [ ] **Submit**: POST /api/v1/compositions/

**Test API**:
```bash
# Liste
GET http://localhost:8000/api/v1/compositions/

# Détails
GET http://localhost:8000/api/v1/compositions/1

# Créer
POST http://localhost:8000/api/v1/compositions/
```

**Score attendu**: 90% - CRUD complet (données vides OK)

---

### 6. Authentication (10 min)

#### ✅ Login Page
**Page**: `/login`

- [ ] **Email**: Input email
- [ ] **Password**: Input password (masqué)
- [ ] **Remember me**: Checkbox
- [ ] **Submit**: POST /api/v1/auth/login
- [ ] **Forgot password**: Lien
- [ ] **Register link**: Vers /register

**Test**:
```javascript
POST http://localhost:8000/api/v1/auth/login
Body: { "email": "test@test.com", "password": "test123" }
// Attendu: 200 OK + token ou 401 Unauthorized
```

- [ ] Erreurs affichées (bad credentials)
- [ ] Success → redirect dashboard
- [ ] Token stocké (localStorage/cookie)

#### ✅ Register Page
**Page**: `/register`

- [ ] **Email**: Input email
- [ ] **Username**: Input texte
- [ ] **Password**: Input password
- [ ] **Confirm Password**: Match validation
- [ ] **Terms**: Checkbox
- [ ] **Submit**: POST /api/v1/auth/register

**Validation**:
- [ ] Email format
- [ ] Password strength (8+ chars, 1 upper, 1 lower, 1 digit, 1 special)
- [ ] Passwords match
- [ ] Terms accepted

**Score attendu**: 95% - Auth flow complet

---

### 7. Tags Manager (5 min)

**Page**: `/tags`

#### ✅ Fonctionnalités
- [ ] **Liste tags**: Affichée
- [ ] **Create tag**: Modal/form
- [ ] **Edit tag**: Inline edit
- [ ] **Delete tag**: Confirmation
- [ ] **Assign to builds**: Bulk actions

**API**:
```bash
GET http://localhost:8000/api/v1/tags/
POST http://localhost:8000/api/v1/tags/
```

**Score attendu**: 80% - Gestion tags fonctionnelle

---

### 8. API Integration (10 min)

#### ✅ Professions GW2
```bash
# Backend devrait exposer
GET http://localhost:8000/api/v1/professions/
# Attendu: [
#   {"id": 1, "name": "Guardian", ...},
#   {"id": 2, "name": "Warrior", ...}
# ]
```

- [ ] Frontend charge professions depuis API
- [ ] Dropdown affiche toutes les professions
- [ ] Icons GW2 affichés

#### ✅ Elite Specializations
```bash
GET http://localhost:8000/api/v1/elite-specializations/
```

- [ ] Chargées depuis API
- [ ] Filtrées par profession
- [ ] Affichées dans builder

#### ✅ External GW2 API
```bash
# Si intégré
GET https://api.guildwars2.com/v2/professions
```

- [ ] Données GW2 officielles chargées
- [ ] Cache en place
- [ ] Fallback si API down

**Score attendu**: 85% - API bien intégrée

---

### 9. UI/UX Components (10 min)

#### ✅ UI Library (shadcn/ui)
- [ ] **Buttons**: Primary, Secondary, Destructive
- [ ] **Inputs**: Text, Number, Select, Textarea
- [ ] **Dialogs**: Modals fonctionnels
- [ ] **Toast/Sonner**: Notifications
- [ ] **Dropdown menus**: Interactions OK
- [ ] **Cards**: Layout cohérent
- [ ] **Badges**: Status/tags affichés

#### ✅ States
- [ ] **Loading**: Skeletons/spinners
- [ ] **Empty**: EmptyState component
- [ ] **Error**: ErrorState component
- [ ] **Success**: Messages confirmation

#### ✅ Thème
- [ ] **Light mode**: Tout lisible
- [ ] **Dark mode**: Tout lisible
- [ ] **Toggle**: Fonctionne instantanément
- [ ] **Persistance**: Sauvegardé localStorage

**Score attendu**: 100% - UI polished

---

### 10. Performance & Qualité (10 min)

#### ✅ Performance
- [ ] **Page load**: <2s
- [ ] **Route change**: <500ms
- [ ] **API calls**: <1s
- [ ] **Animations**: Fluides 60fps

#### ✅ Console (F12)
- [ ] **Aucune erreur** JS
- [ ] **Aucun warning** React
- [ ] **Aucune erreur** réseau 500
- [ ] Warnings mineurs OK (401 auth)

#### ✅ Network (F12)
```
Vérifier:
- API calls vers localhost:8000
- CORS headers présents
- Réponses JSON valides
- Status codes corrects
```

#### ✅ Responsive
- [ ] **Desktop**: Layout optimal
- [ ] **Tablet**: Adapté
- [ ] **Mobile**: Utilisable
- [ ] **Breakpoints**: TailwindCSS

**Score attendu**: 90% - Performance bonne

---

## 📊 Grille de Notation

| Catégorie | Points | Critères |
|-----------|--------|----------|
| **Démarrage** | 10 | Page charge sans erreur |
| **Navigation** | 10 | Toutes routes fonctionnelles |
| **Dashboard** | 10 | Components et données |
| **Builder** | 15 | Formulaire complet et validé |
| **Compositions** | 15 | CRUD fonctionnel |
| **Authentication** | 15 | Login/Register complets |
| **Tags** | 5 | Gestion basique OK |
| **API Integration** | 10 | Backend calls OK |
| **UI/UX** | 10 | Components polished |
| **Performance** | 10 | Rapide et sans erreurs |
| **TOTAL** | **100** | |

### Seuils
- **90-100**: ✅ Excellent - Production ready
- **75-89**: ✅ Bon - Quelques ajustements
- **60-74**: ⚠️ Acceptable - Corrections nécessaires
- **<60**: ❌ Insuffisant - Travail majeur requis

---

## 🐛 Erreurs Communes à Vérifier

### API Connection
```
❌ Erreur: Failed to fetch
   Cause: Backend pas lancé ou CORS
   Fix: Vérifier backend port 8000 et CORS localhost:5173
```

### Authentication
```
❌ Erreur: 401 Unauthorized
   Cause: Token manquant ou invalide
   Attendu: Normal si pas connecté
   Fix: Login avant de tester endpoints protégés
```

### Empty Data
```
⚠️ Warning: No data to display
   Cause: Database vide
   Attendu: Normal sur fresh install
   Fix: Créer données de test via formulaires
```

### TypeScript Errors
```
❌ Erreur: Type 'X' is not assignable to type 'Y'
   Cause: Types mal définis
   Fix: Vérifier interfaces TypeScript
```

---

## 🎯 Tests Prioritaires

### Must Have (Bloquants)
1. ✅ Page d'accueil charge
2. ✅ Navigation fonctionne
3. ✅ Formulaires validés
4. ✅ API backend connectée
5. ✅ Pas d'erreurs console critiques

### Should Have (Importants)
6. ✅ Authentication complète
7. ✅ CRUD compositions fonctionne
8. ✅ Builder V2 utilisable
9. ✅ UI responsive
10. ✅ Thème dark/light

### Nice to Have (Bonus)
11. ⏸️ Animations polies
12. ⏸️ Tooltips informatifs
13. ⏸️ Keyboard shortcuts
14. ⏸️ Accessibility (ARIA)
15. ⏸️ PWA features

---

## 📸 Screenshots Recommandés

Capturer pour documentation:
1. **Dashboard**: Vue d'ensemble
2. **Builder V2**: Formulaire build
3. **Compositions**: Liste et détails
4. **Login**: Page auth
5. **Dark mode**: Thème sombre
6. **Mobile**: Layout responsive
7. **Errors**: Gestion erreurs

Dossier: `docs/screenshots/v3.4.4/`

---

## ✅ Checklist Finale

### Avant de Valider
- [ ] Backend lancé et stable
- [ ] Frontend lance sans erreur
- [ ] Tous les tests prioritaires passés
- [ ] Score ≥75/100
- [ ] Aucun blocker critique
- [ ] Documentation à jour

### Après Validation
- [ ] Screenshots capturés
- [ ] Bugs documentés
- [ ] Score calculé
- [ ] Rapport final généré
- [ ] Commit changements

---

## 📝 Notes de Test

**Template** pour documenter:
```markdown
### Test: [Nom du test]
- Date: 2025-10-17
- Testeur: [Votre nom]
- Browser: Chrome/Firefox/Safari
- Résultat: ✅ Pass / ❌ Fail / ⚠️ Warning
- Score: X/Y
- Notes: [Observations]
- Bugs: [Si applicable]
```

---

## 🎉 Validation Réussie Si...

✅ **Frontend** = 90+ points:
- Application lance sans erreur
- Navigation fluide
- Formulaires fonctionnels
- API intégrée
- UI polished

✅ **Global** (Backend 100% + Frontend 90%+):
- **Score: 95/100** ✅ **PRODUCTION READY**

---

**Guide créé**: 2025-10-17 00:42 UTC+2  
**Version**: v3.4.4  
**Backend**: ✅ Port 8000  
**Frontend**: À tester Port 5173
