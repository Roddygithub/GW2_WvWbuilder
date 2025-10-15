# 🎯 Builder V2 - Refonte complète McM/PvE

## ✅ Status: **OPÉRATIONNEL**

La refonte complète du Builder est terminée avec support McM et PvE, flux utilisateur optimisé, et moteur automatique pour les rôles/spécialisations.

---

## 📦 Modifications apportées

### 1. **Configurations PvE** (3 nouveaux fichiers)

#### `backend/config/optimizer/pve_openworld.yml`
- **Mode**: Open World (1-5 joueurs)
- **Emphasis**: Damage (35%), Survivability (25%), Mobility (15%)
- **Boons**: Might 70%, Fury 70%, Swiftness 80%
- **Rôles**: Majorité DPS (4/5), pas de healer dédié

#### `backend/config/optimizer/pve_fractale.yml`
- **Mode**: Fractales (5 joueurs)
- **Emphasis**: Damage (30%), Boon Uptime (25%), CC (15%)
- **Boons**: Might/Fury/Quickness/Alacrity 95% (permanent)
- **Rôles**: 1 Healer/Quickness, 1 Alacrity, 3 DPS

#### `backend/config/optimizer/pve_raid.yml`
- **Mode**: Raids/Strikes (10 joueurs)
- **Emphasis**: Damage (30%), Boon Uptime (25%), Healing (15%)
- **Boons**: Might/Fury/Quickness/Alacrity 100% (permanent)
- **Rôles**: 2 Healers, 2 Boon Supports, 6 DPS
- **Structure**: 2 sous-groupes de 5

### 2. **Backend - Schéma API** (`backend/app/schemas/composition.py`)

**Nouveau schéma de requête:**
```python
class CompositionOptimizationRequest(BaseModel):
    squad_size: int  # 1-50 joueurs
    game_type: str  # "wvw" ou "pve"
    game_mode: str  # "zerg", "roaming", "guild_raid", "openworld", "fractale", "raid"
    fixed_professions: Optional[List[int]]  # IDs des professions fixes (optionnel)
    # preferred_roles: DEPRECATED - rôles auto-optimisés
    # optimization_goals: DEPRECATED - goals auto-déterminés par mode
```

**Changements clés:**
- ✅ `game_type` + `game_mode` remplacent l'ancien `game_mode` unique
- ✅ `fixed_professions` remplace `fixed_roles` (moteur choisit rôles/specs)
- ✅ `preferred_roles` et `optimization_goals` sont maintenant auto-déterminés

### 3. **Backend - Engine** (`backend/app/core/optimizer/engine.py`)

**Modifications:**
```python
class OptimizerEngine:
    def __init__(self, game_type: str = "wvw", game_mode: str = "zerg"):
        # Map game_type + game_mode to config file
        if game_type == "pve":
            config_name = f"pve_{game_mode}"
        else:
            config_name = f"wvw_{game_mode}"
        self.config = self._load_config(config_name)
```

**Logique de sélection:**
- Si `fixed_professions` fourni → filtre le catalogue sur ces professions
- Sinon → utilise tout le catalogue
- Le moteur choisit automatiquement les rôles et spécialisations optimales selon le config du mode

### 4. **Backend - Endpoints** (`backend/app/api/api_v1/endpoints/builder.py`)

#### Nouveau endpoint `/builder/modes`
```json
{
  "game_types": {
    "wvw": {
      "name": "World vs World (McM)",
      "modes": [
        {"id": "zerg", "name": "Zerg (30-50)", ...},
        {"id": "roaming", "name": "Roaming (2-10)", ...},
        {"id": "guild_raid", "name": "Guild Raid (15-30)", ...}
      ]
    },
    "pve": {
      "name": "Player vs Environment (PvE)",
      "modes": [
        {"id": "openworld", "name": "Open World (1-5)", ...},
        {"id": "fractale", "name": "Fractales (5)", ...},
        {"id": "raid", "name": "Raids/Strikes (10)", ...}
      ]
    }
  }
}
```

#### Nouveau endpoint `/builder/professions`
```json
{
  "professions": [
    {"id": 1, "name": "Guardian", "color": "blue"},
    {"id": 2, "name": "Revenant", "color": "red"},
    ...
  ]
}
```

### 5. **Frontend - Builder V2** (`frontend/src/pages/BuilderV2.tsx`)

**Nouveau flux utilisateur (600+ lignes):**

#### Étape 1: Nombre de joueurs
- Input numérique 1-50
- Simple et direct

#### Étape 2: Type de jeu et mode
- **Sélection Game Type**: 2 boutons (McM / PvE)
- **Sélection Mode**: Menu déroulant dynamique selon le type
  - McM → Zerg, Roaming, Guild Raid
  - PvE → Open World, Fractales, Raids/Strikes
- Affichage description + emphasis du mode

#### Étape 3: Classes (optionnel)
- **Checkbox**: "Je veux choisir les classes"
- Si coché → Grille de 9 professions sélectionnables
- Si non coché → Moteur choisit automatiquement
- **Important**: Le moteur choisit TOUJOURS les rôles et spécialisations

#### Résultats
- Score global
- Boon coverage
- Métriques (healing, damage, survivability, CC)
- Distribution des rôles (auto-optimisée)
- Liste complète des membres avec professions/élites/rôles

### 6. **Frontend - Types** (`frontend/src/api/builder.ts`)

```typescript
export interface CompositionOptimizationRequest {
  squad_size: number;
  game_type: string;  // "wvw" ou "pve"
  game_mode: string;  // sous-mode spécifique
  fixed_professions?: number[];  // IDs professions fixes
}
```

### 7. **Routing** (`frontend/src/App.tsx`)

```
/builder → BuilderV2Page (nouvelle version)
/builder/v1 → BuilderOptimizerPage (ancienne version)
/builder/legacy → BuilderPage (version originale)
```

---

## 🎨 Aperçu visuel du nouveau flux

```
┌─────────────────────────────────────────────────────────────┐
│        🎯 Optimiseur de Composition GW2                     │
│    McM & PvE - Rôles et spécialisations auto-optimisés     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Étape 1: Nombre de joueurs                                  │
│ ┌──────────────────┐                                        │
│ │ Squad Size: 10   │                                        │
│ └──────────────────┘                                        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Étape 2: Type de jeu et mode                                │
│                                                             │
│ Type de jeu:                                                │
│ ┌──────────┐  ┌──────────┐                                 │
│ │ 🛡️ McM   │  │ ⚔️ PvE   │                                 │
│ │ (WvW)    │  │          │                                 │
│ └──────────┘  └──────────┘                                 │
│                                                             │
│ Mode de jeu:                                                │
│ ┌────────────────────────────────────┐                     │
│ │ Zerg (30-50 players)              ▼│                     │
│ └────────────────────────────────────┘                     │
│                                                             │
│ ℹ️ Large-scale fights with emphasis on boon coverage       │
│    Tags: boon_uptime, healing, survivability               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Étape 3: Classes (optionnel)                                │
│                                                             │
│ ☐ Je veux choisir les classes                              │
│                                                             │
│ Le moteur choisira automatiquement les rôles et            │
│ spécialisations optimales                                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│          ✨ Optimiser la composition →                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Pour tester

### 1. Redémarrer le backend

```bash
# Arrêter le backend actuel
pkill -f uvicorn

# Relancer
cd backend
poetry run uvicorn app.main:app --reload
```

### 2. Vérifier que le frontend tourne

```bash
# Si besoin de relancer
cd frontend
npm run dev
```

### 3. Tester le nouveau flux

1. **Ouvrir** http://localhost:5173/builder
2. **Étape 1**: Choisir 10 joueurs
3. **Étape 2**: 
   - Cliquer sur "McM"
   - Sélectionner "Zerg" dans le menu
4. **Étape 3**: Laisser décoché (moteur choisit tout)
5. **Cliquer** "Optimiser la composition"
6. **Voir**:
   - Score global
   - Boon coverage
   - Distribution des rôles (auto-optimisée)
   - Liste des 10 membres avec professions/élites/rôles

### 4. Tester avec classes fixes

1. **Étape 3**: Cocher "Je veux choisir les classes"
2. **Sélectionner**: Guardian, Revenant, Necromancer
3. **Optimiser**: Le moteur utilisera uniquement ces 3 professions
4. **Résultat**: Composition avec seulement Guardian/Revenant/Necro, mais rôles/specs optimisés

### 5. Tester PvE

1. **Étape 2**: Cliquer sur "PvE"
2. **Sélectionner**: "Fractales (5 joueurs)"
3. **Squad Size**: Ajuster à 5
4. **Optimiser**: Voir composition PvE optimisée (1 healer, 1 alac, 3 DPS)

---

## 📊 Exemples de requêtes/réponses

### Requête McM Zerg (10 joueurs, auto)
```json
{
  "squad_size": 10,
  "game_type": "wvw",
  "game_mode": "zerg",
  "fixed_professions": null
}
```

### Requête PvE Fractale (5 joueurs, classes fixes)
```json
{
  "squad_size": 5,
  "game_type": "pve",
  "game_mode": "fractale",
  "fixed_professions": [1, 6, 4]  // Guardian, Engineer, Warrior
}
```

### Réponse
```json
{
  "composition": {
    "name": "Optimized PVE FRACTALE Composition",
    "squad_size": 5,
    "game_mode": "pve_fractale",
    "members": [
      {
        "id": 1,
        "profession_name": "Guardian",
        "elite_specialization_name": "Firebrand",
        "role_type": "healer",
        "is_commander": true
      },
      {
        "id": 2,
        "profession_name": "Engineer",
        "elite_specialization_name": "Mechanist",
        "role_type": "boon_support",
        "is_commander": false
      },
      // ... 3 DPS
    ]
  },
  "score": 0.92,
  "role_distribution": {
    "healer": 1,
    "boon_support": 1,
    "dps": 3
  },
  "boon_coverage": {
    "might": 0.95,
    "quickness": 0.95,
    "alacrity": 0.95,
    ...
  }
}
```

---

## ✅ Fonctionnalités implémentées

### Flux utilisateur
- ✅ Étape 1: Squad size (1-50)
- ✅ Étape 2: Game type (McM/PvE) + Mode (6 modes au total)
- ✅ Étape 3: Classes fixes optionnelles (checkbox + sélection)
- ✅ Bouton optimiser avec loader
- ✅ Affichage résultats complets

### Backend
- ✅ 6 configs de modes (3 McM + 3 PvE)
- ✅ Engine adapté pour game_type + game_mode
- ✅ Support fixed_professions (moteur choisit rôles/specs)
- ✅ Endpoints `/modes` et `/professions`
- ✅ Génération membres avec professions/élites/rôles

### Frontend
- ✅ UI moderne et fluide (Framer Motion)
- ✅ Sélection game type (2 boutons)
- ✅ Sélection mode dynamique (menu déroulant)
- ✅ Sélection professions (grille 3×3)
- ✅ Affichage résultats avec membres détaillés
- ✅ Responsive design

### Automatisation
- ✅ Rôles auto-optimisés par le moteur
- ✅ Spécialisations auto-optimisées par le moteur
- ✅ Goals auto-déterminés par le mode
- ✅ Pondérations auto-chargées depuis config

---

## 🎯 Différences avec l'ancienne version

### Avant (Builder V1)
- Utilisateur choisissait: squad size, mode, **rôles**, goals
- 1 seul type de jeu (McM)
- 3 modes (zerg, roaming, guild_raid)
- Rôles manuels (healer: 3, dps: 9, etc.)

### Maintenant (Builder V2)
- Utilisateur choisit: squad size, **game type**, mode, **classes (opt.)**
- 2 types de jeu (McM + PvE)
- 6 modes (3 McM + 3 PvE)
- **Rôles et spécialisations auto-optimisés**
- Classes fixes optionnelles (moteur choisit le reste)

---

## 📝 Prochaines étapes

### Tests
- [ ] Tests backend pour PvE modes
- [ ] Tests E2E Cypress pour nouveau flux
- [ ] Tests de charge (100+ req/s)

### Améliorations
- [ ] Enrichir catalogue de builds (10 → 30+)
- [ ] Cache Redis pour requêtes similaires
- [ ] Sauvegarder compositions optimisées
- [ ] Export/Import compositions

### Documentation
- [ ] Mettre à jour BUILDER_UI_COMPLETE.md
- [ ] Screenshots du nouveau flux
- [ ] Vidéo de démonstration

---

## ✅ Checklist de validation

- [x] Configs PvE créées (openworld, fractale, raid)
- [x] Engine adapté pour game_type + game_mode
- [x] Schéma API mis à jour (game_type, fixed_professions)
- [x] Endpoints `/modes` et `/professions` créés
- [x] Builder V2 UI complète (600+ lignes)
- [x] Routing mis à jour (/builder → V2)
- [x] Types TypeScript alignés
- [x] Flux utilisateur optimisé (3 étapes)
- [x] Rôles/specs auto-optimisés
- [x] Support McM et PvE

---

## 🎉 Conclusion

La refonte complète du Builder est **opérationnelle** avec:

✅ **Support McM et PvE**: 6 modes au total (3+3)
✅ **Flux optimisé**: 3 étapes simples et intuitives
✅ **Automatisation**: Rôles et spécialisations auto-optimisés
✅ **Flexibilité**: Classes fixes optionnelles
✅ **UI moderne**: Animations, responsive, feedback utilisateur
✅ **Backend robuste**: Configs par mode, engine adaptatif

**Le système fonctionne maintenant exactement comme demandé**: l'utilisateur choisit le nombre de joueurs, le type de jeu, le mode, et optionnellement les classes. Le moteur fait le reste automatiquement! 🚀
