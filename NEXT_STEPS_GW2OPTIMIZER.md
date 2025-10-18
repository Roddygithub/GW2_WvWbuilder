# 🚀 GW2Optimizer - Prochaines Étapes

**Date**: 2025-10-18  
**Status**: ✅ Fondations Créées - Prêt pour Tests

---

## ✅ Ce Qui Est Déjà Fait (36%)

### Configuration & Architecture
- ✅ **Tailwind GW2** configuré (couleurs, animations, classes custom)
- ✅ **Types TypeScript** complets (Squad, ChatMessage, MetaData, etc.)
- ✅ **Styles globaux** GW2 (scrollbar, badges, boutons)
- ✅ **Structure dossiers** définie

### Composants Créés (4)
- ✅ **Header** - Logo + "Empowered by Ollama with Mistral 7B"
- ✅ **ChatBox** - Interface chat complète avec animations
- ✅ **SquadCard** - Affichage compositions avec badges buffs/nerfs
- ✅ **HomePage** - Page principale avec chat + squads

### API Client
- ✅ **gw2optimizer.ts** - Client API complet

### Documentation
- ✅ **Spécifications** complètes (wireframes, architecture)
- ✅ **Status implémentation** détaillé

---

## 🔧 Actions Immédiates Requises

### 1. Intégrer le Nouveau Frontend dans App.tsx

**Fichier**: `frontend/src/App.tsx`

```typescript
// Remplacer ou ajouter la route HomePage
import HomePage from './pages/HomePage';

// Dans le router
<Route path="/" element={<HomePage />} />
```

### 2. Importer les Styles GW2

**Fichier**: `frontend/src/main.tsx` ou `frontend/src/App.tsx`

```typescript
import './styles/gw2-theme.css';
```

### 3. Utiliser la Nouvelle Config Tailwind

**Commande**:
```bash
cd frontend
cp tailwind.config.gw2.js tailwind.config.js
```

### 4. Créer l'Endpoint Backend Compositions

**Fichier**: `backend/app/api/api_v1/endpoints/compositions.py` (nouveau)

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.optimization import OptimizationRequest
from app.api.api_v1.endpoints.optimizer import optimize

router = APIRouter()

@router.post("/generate")
async def generate_composition(
    prompt: str,
    squad_size: int = 15,
    mode: str | None = None,
    db: Session = Depends(get_db)
):
    """
    Génère une composition via prompt text.
    Wrapper autour de /optimize pour interface chat.
    """
    # Parser le prompt (simple pour commencer)
    request = OptimizationRequest(
        squad_size=squad_size,
        wvw_mode=mode or "zerg",
        # Autres params par défaut
    )
    
    # Appeler optimizer existant
    result = await optimize(request, db)
    
    # Transformer en format Squad pour frontend
    squads = [{
        "id": "squad-1",
        "name": f"Squad Alpha",
        "builds": [...],  # À formater depuis result
        "weight": result.score / 100,
        "synergy": 0.85,  # À calculer
        "buffs": [],
        "nerfs": [],
        "timestamp": datetime.now().isoformat(),
        "mode": mode,
        "squad_size": squad_size,
    }]
    
    return {
        "squads": squads,
        "meta": {
            "total_players": squad_size,
            "avg_weight": result.score / 100,
            "avg_synergy": 0.85,
        }
    }
```

**Fichier**: `backend/app/api/api_v1/api.py`

```python
from app.api.api_v1.endpoints import compositions

# Ajouter le router
api_router.include_router(
    compositions.router,
    prefix="/compositions",
    tags=["compositions"]
)
```

### 5. Installer Dépendances Manquantes (si nécessaire)

```bash
cd frontend
npm install lucide-react  # Icônes (si pas déjà installé)
```

### 6. Tester l'Interface

```bash
# Terminal 1 - Backend
cd backend
poetry run uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

**Accès**: http://localhost:5173

---

## 🧪 Tests à Effectuer

### Test 1: Affichage Page
- [ ] HomePage s'affiche correctement
- [ ] Header visible avec logo et mention Mistral
- [ ] ChatBox visible à gauche
- [ ] Placeholder "Aucune composition" à droite

### Test 2: Styles GW2
- [ ] Couleurs GW2 appliquées (rouge #b02c2c, or #d4af37)
- [ ] Scrollbar personnalisée
- [ ] Cards avec bordures et hover effects
- [ ] Badges colorés (vert/rouge/orange)

### Test 3: Chat Interaction
- [ ] Taper un message dans le chat
- [ ] Message utilisateur affiché à droite
- [ ] Loading indicator visible
- [ ] Message AI affiché à gauche (ou erreur)

### Test 4: Backend Integration
- [ ] Endpoint `/api/v1/compositions/generate` répond
- [ ] Composition générée affichée dans SquadCard
- [ ] Builds listés avec icônes professions
- [ ] Stats (weight, synergy) visibles

---

## 🐛 Problèmes Potentiels & Solutions

### Problème 1: Endpoint 404
**Symptôme**: `POST /api/v1/compositions/generate → 404`

**Solution**:
```bash
# Vérifier que le router est bien ajouté
curl http://localhost:8000/docs
# Chercher "compositions" dans Swagger
```

### Problème 2: Types TypeScript Errors
**Symptôme**: Erreurs d'import types

**Solution**:
```bash
cd frontend
npm run build  # Vérifier erreurs compilation
```

### Problème 3: Styles Non Appliqués
**Symptôme**: Interface sans couleurs GW2

**Solution**:
```typescript
// Vérifier import dans main.tsx
import './styles/gw2-theme.css';
import './index.css';  // Après gw2-theme pour override
```

### Problème 4: CORS Errors
**Symptôme**: Requêtes bloquées dans console

**Solution**:
```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📋 Checklist Avant de Continuer

### Configuration
- [ ] `tailwind.config.gw2.js` → `tailwind.config.js`
- [ ] `gw2-theme.css` importé dans `main.tsx`
- [ ] Route `HomePage` ajoutée dans `App.tsx`

### Backend
- [ ] Endpoint `/api/v1/compositions/generate` créé
- [ ] Router compositions ajouté dans `api.py`
- [ ] Backend redémarré

### Frontend
- [ ] Dependencies installées (`lucide-react`)
- [ ] `npm run dev` fonctionne sans erreur
- [ ] Page accessible sur http://localhost:5173

### Tests
- [ ] HomePage s'affiche
- [ ] Chat fonctionne (input + send)
- [ ] Styles GW2 appliqués
- [ ] Pas d'erreurs console

---

## 🎯 Objectif de Cette Session

**Obtenir une HomePage fonctionnelle avec**:
1. ✅ Chat qui accepte des messages
2. ✅ Appel backend qui génère composition
3. ✅ Affichage composition dans SquadCard
4. ✅ Styles GW2 appliqués partout

**Temps Estimé**: 30-60 minutes

---

## 🚀 Commandes Rapides

```bash
# Setup complet
cd frontend
cp tailwind.config.gw2.js tailwind.config.js
npm install lucide-react
npm run dev

# Dans un autre terminal
cd backend
poetry run uvicorn app.main:app --reload

# Ouvrir navigateur
open http://localhost:5173
```

---

## 📞 Si Besoin d'Aide

### Erreur Backend
```bash
# Voir logs backend
cd backend
poetry run uvicorn app.main:app --reload --log-level debug
```

### Erreur Frontend
```bash
# Voir erreurs compilation
cd frontend
npm run build
```

### Vérifier API
```bash
# Test endpoint directement
curl -X POST http://localhost:8000/api/v1/compositions/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Compo 15 joueurs", "squad_size": 15, "mode": "zerg"}'
```

---

**Prêt à Tester ?** 🎮

Commencez par les 6 actions immédiates, puis testez l'interface !
