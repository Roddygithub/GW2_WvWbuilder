# 🔥 GW2Optimizer - Nouveau Frontend

**Version**: 1.0 Alpha  
**Date**: 2025-10-18  
**Status**: 🚧 Développement Actif (36% complété)

---

## 🎯 Vue d'Ensemble

Refonte complète du frontend **GW2_WvWbuilder** en **GW2Optimizer** avec:
- ✅ Interface moderne aux couleurs Guild Wars 2
- ✅ ChatBox pour interagir avec Mistral 7B
- ✅ Affichage compositions optimales via cards interactives
- ⏳ Dashboard Meta Evolution (à venir)
- ⏳ BuildSelector mini-interface (créé, à intégrer)

---

## 📂 Structure des Fichiers Créés

```
frontend/
├── tailwind.config.gw2.js       ✅ Config Tailwind GW2
├── src/
│   ├── styles/
│   │   └── gw2-theme.css        ✅ Styles globaux GW2
│   ├── types/
│   │   └── gw2optimizer.ts      ✅ Types TypeScript complets
│   ├── components/
│   │   ├── layout/
│   │   │   └── Header.tsx       ✅ Header avec logo + Mistral
│   │   ├── chat/
│   │   │   └── ChatBox.tsx      ✅ Interface chat interactive
│   │   ├── squad/
│   │   │   └── SquadCard.tsx    ✅ Affichage compositions
│   │   └── builds/
│   │       └── BuildSelector.tsx ✅ Modal sélection builds
│   ├── pages/
│   │   └── HomePage.tsx         ✅ Page principale
│   └── api/
│       └── gw2optimizer.ts      ✅ Client API
```

**Total**: 11 fichiers créés + 3 documents

---

## 🎨 Charte Graphique

### Couleurs
```css
--gw2-red: #b02c2c        /* Primaire - Boutons, accents */
--gw2-gold: #d4af37       /* Secondaire - Highlights, badges */
--gw2-dark: #1f1f1f       /* Fond principal */
--gw2-cardBg: #2c2c2c     /* Fond cards */
--gw2-border: #3a3a3a     /* Bordures */
--success: #4caf50        /* Buffs */
--warning: #ff9800        /* Warnings */
--danger: #f44336         /* Nerfs */
```

### Classes Utilitaires
```css
gw2-card              /* Card de base */
gw2-card-hover        /* Card avec hover effect or */
gw2-button-primary    /* Bouton rouge GW2 */
gw2-button-secondary  /* Bouton gris */
gw2-badge-buff        /* Badge vert (buffs) */
gw2-badge-nerf        /* Badge rouge (nerfs) */
gw2-input             /* Input stylisé */
gw2-gradient-text     /* Texte gradient rouge-or */
```

---

## ⚙️ Installation

### 1. Copier la Config Tailwind

```bash
cd frontend
cp tailwind.config.gw2.js tailwind.config.js
```

### 2. Installer Dépendances

```bash
npm install lucide-react
# lucide-react déjà installé normalement
```

### 3. Importer les Styles GW2

**Fichier**: `src/main.tsx`

```typescript
import './styles/gw2-theme.css';
import './index.css';
```

### 4. Ajouter la Route HomePage

**Fichier**: `src/App.tsx`

```typescript
import HomePage from './pages/HomePage';

// Dans le router
<Route path="/" element={<HomePage />} />
// Ou remplacer la route existante
```

---

## 🚀 Lancement

```bash
# Terminal 1 - Backend
cd backend
poetry run uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

**URL**: http://localhost:5173

---

## 🧪 Tests Manuels

### ✅ Test 1: Affichage de Base
1. Ouvrir http://localhost:5173
2. Vérifier Header visible (logo + "Empowered by Ollama")
3. Vérifier ChatBox à gauche
4. Vérifier zone "Aucune composition" à droite
5. Vérifier couleurs GW2 (rouge, or, gris sombre)

### ✅ Test 2: Chat Interaction
1. Taper dans le chat: "Composition pour 15 joueurs zerg"
2. Appuyer Entrée ou cliquer Envoyer
3. Vérifier message utilisateur affiché à droite
4. Vérifier loading indicator (3 dots animés)
5. Observer réponse AI (si backend répond)

### ✅ Test 3: Affichage Composition
1. Si composition générée, vérifier SquadCard affiché
2. Vérifier stats (Weight, Synergy, Players)
3. Vérifier liste builds avec icônes
4. Vérifier badges buffs/nerfs si présents
5. Vérifier hover effect (bordure or)

### ⏳ Test 4: BuildSelector (Modal)
1. Ouvrir BuildSelector (à intégrer dans HomePage)
2. Vérifier liste de 6 builds mock
3. Tester filtres (Profession, Role, Synergy)
4. Tester search bar
5. Cliquer "Select" → Modal se ferme

---

## 🔧 Backend Requis

### Endpoint à Créer

**Fichier**: `backend/app/api/api_v1/endpoints/compositions.py` (nouveau)

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db

router = APIRouter()

@router.post("/generate")
async def generate_composition(
    prompt: str,
    squad_size: int = 15,
    mode: str | None = None,
    db: Session = Depends(get_db)
):
    """
    Génère composition via prompt.
    TODO: Parser prompt avec LLM Mistral
    TODO: Appeler optimizer
    TODO: Formater en Squad pour frontend
    """
    # Pour l'instant, retourner mock data
    return {
        "squads": [{
            "id": "squad-1",
            "name": "Squad Alpha",
            "builds": [
                {"id": "1", "profession": "Guardian", "specialization": "Firebrand", "role": "Support", "count": 3, "weight": 0.85},
                {"id": "2", "profession": "Engineer", "specialization": "Scrapper", "role": "Support", "count": 2, "weight": 1.1},
            ],
            "weight": 0.95,
            "synergy": 0.87,
            "buffs": ["Quickness +15%", "Stability +20%"],
            "nerfs": [],
            "timestamp": "2025-10-18T12:00:00",
            "mode": mode or "zerg",
            "squad_size": squad_size,
        }],
        "meta": {
            "total_players": squad_size,
            "avg_weight": 0.95,
            "avg_synergy": 0.87,
        }
    }
```

**Fichier**: `backend/app/api/api_v1/api.py`

```python
from app.api.api_v1.endpoints import compositions

# Ajouter
api_router.include_router(
    compositions.router,
    prefix="/compositions",
    tags=["compositions"]
)
```

---

## 📋 Composants Détaillés

### Header
- Logo Flame rouge
- Titre "GW2Optimizer" gradient
- Mention "Empowered by Ollama with Mistral 7B"
- Sticky top, backdrop blur

### ChatBox
- Messages utilisateur (droite, gris)
- Messages AI (gauche, bordure or)
- Loading indicator animé
- Auto-scroll
- Input validation

### SquadCard
- Stats grid (Weight, Synergy, Players)
- Liste builds avec icônes professions
- Badges buffs (vert) / nerfs (rouge)
- Mode badge (zerg/havoc/roaming)
- Hover effect bordure or

### HomePage
- Layout 2 colonnes responsive
- ChatBox + Squads display
- Error handling avec alert
- Loading overlay
- Parsing prompt intelligent (taille, mode)

### BuildSelector
- Modal avec backdrop
- Search bar
- Filtres (Profession, Role, Synergy)
- Liste builds scrollable
- BuildCard cliquable
- Mock data (6 builds)

---

## 🎯 Fonctionnalités Implémentées

### ✅ Complétées
- [x] Charte graphique GW2
- [x] Header avec branding
- [x] ChatBox interactive
- [x] SquadCard display
- [x] HomePage layout
- [x] API client
- [x] BuildSelector modal
- [x] Types TypeScript complets
- [x] Styles globaux GW2
- [x] Animations (shimmer, pulse)

### ⏳ En Cours
- [ ] Intégration backend
- [ ] Meta Evolution page
- [ ] Tests unitaires
- [ ] Responsive mobile

### 📅 À Faire
- [ ] E2E tests
- [ ] Documentation Storybook
- [ ] Optimisation bundle
- [ ] Déploiement

---

## 🐛 Problèmes Connus

### 1. Endpoint Compositions 404
**Cause**: Endpoint `/api/v1/compositions/generate` pas encore créé backend

**Solution**: Créer endpoint (voir section Backend Requis)

### 2. Types Import Errors
**Cause**: Path alias `@/` peut ne pas être configuré

**Solution**: Vérifier `tsconfig.json`
```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### 3. Styles Non Appliqués
**Cause**: `gw2-theme.css` pas importé

**Solution**: Importer dans `main.tsx`

---

## 📚 Documentation

### Fichiers Créés
1. **GW2OPTIMIZER_SPECS_v1.0.md** - Spécifications complètes
2. **GW2OPTIMIZER_IMPLEMENTATION_STATUS.md** - État implémentation
3. **NEXT_STEPS_GW2OPTIMIZER.md** - Prochaines actions
4. **README_GW2OPTIMIZER.md** - Ce fichier

### Wireframes
- HomePage: ChatBox + Squads
- MetaEvolution: Graphs + Heatmap + Timeline
- BuildSelector: Modal avec filtres

---

## 🚀 Prochaines Étapes

### Court Terme (Aujourd'hui)
1. Créer endpoint backend `/api/v1/compositions/generate`
2. Tester HomePage avec backend
3. Corriger bugs éventuels

### Moyen Terme (Cette Semaine)
4. Implémenter MetaEvolutionPage
5. Intégrer BuildSelector dans HomePage
6. Ajouter tests unitaires

### Long Terme (Semaine Prochaine)
7. Tests E2E complets
8. Documentation Storybook
9. Optimisation performance
10. Déploiement production

---

## 💡 Exemples d'Utilisation

### Utiliser un Composant

```typescript
import { SquadCard } from '@/components/squad/SquadCard';
import { Squad } from '@/types/gw2optimizer';

const squad: Squad = {
  id: 'squad-1',
  name: 'Squad Alpha',
  builds: [...],
  weight: 0.95,
  synergy: 0.87,
  buffs: ['Quickness +15%'],
  nerfs: [],
  timestamp: new Date().toISOString(),
  mode: 'zerg',
  squad_size: 15,
};

<SquadCard squad={squad} onSelect={(id) => console.log(id)} />
```

### Appeler l'API

```typescript
import { generateComposition } from '@/api/gw2optimizer';

const result = await generateComposition(
  "Composition optimale pour 15 joueurs en mode zerg",
  15,
  'zerg'
);

console.log(result.squads);
```

---

## 🎨 Captures d'Écran (Conceptuelles)

### HomePage
```
┌─────────────────────────────────────────────────┐
│ 🔥 GW2Optimizer    Empowered by Ollama Mistral │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────┐  ┌──────────────────────────┐│
│  │   ChatBox    │  │   SquadCard 1            ││
│  │              │  │   Weight: 95%            ││
│  │ Messages...  │  │   Synergy: 87%           ││
│  │              │  │   15 joueurs             ││
│  │ [Input...]   │  │                          ││
│  └──────────────┘  │   🛡️ Firebrand x3        ││
│                    │   📈 Scrapper x2         ││
│                    │   ⚔️ Herald x2            ││
│                    └──────────────────────────┘│
│                                                  │
└─────────────────────────────────────────────────┘
```

---

## ✅ Checklist Validation

### Configuration
- [ ] `tailwind.config.gw2.js` copié
- [ ] `gw2-theme.css` importé
- [ ] Route HomePage ajoutée
- [ ] Dépendances installées

### Backend
- [ ] Endpoint `/compositions/generate` créé
- [ ] Router ajouté dans `api.py`
- [ ] Backend répond correctement

### Frontend
- [ ] Page s'affiche sans erreur
- [ ] Styles GW2 appliqués
- [ ] Chat fonctionnel
- [ ] Pas d'erreurs console

### Tests
- [ ] Chat envoie messages
- [ ] Backend retourne composition
- [ ] SquadCard s'affiche
- [ ] BuildSelector fonctionne

---

## 📞 Support

### Erreurs Fréquentes

**Erreur**: `Cannot find module '@/types/gw2optimizer'`
```bash
# Vérifier tsconfig.json paths
# Redémarrer npm run dev
```

**Erreur**: `POST /api/v1/compositions/generate 404`
```bash
# Créer endpoint backend
# Vérifier router dans api.py
```

**Erreur**: Styles non appliqués
```typescript
// main.tsx - Ordre important
import './styles/gw2-theme.css';
import './index.css';
```

---

## 🎯 Objectif Final

**Frontend GW2Optimizer 100% fonctionnel** avec:
- ✅ Interface moderne GW2
- ✅ Chat Mistral 7B
- ✅ Compositions optimales
- ⏳ Meta Evolution dashboard
- ⏳ BuildSelector intégré
- ⏳ Tests complets
- ⏳ Documentation exhaustive

**Status Actuel**: 36% (Fondations solides)  
**ETA Complétion**: 3-5 jours

---

**Prêt à coder ?** 🔥 Commencez par tester HomePage !
