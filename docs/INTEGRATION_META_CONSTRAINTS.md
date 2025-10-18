# Intégration des Contraintes Méta dans le Solver

**Date**: 2025-10-17 16:45  
**Version**: v3.7.3

---

## 📋 Fichiers Créés

### 1. `/backend/app/core/optimizer/meta_constraints.py`
Module Python contenant les contraintes méta pour les 3 modes WvW.

**Fonctions principales**:
- `get_mode_constraints(mode, squad_size)`: Retourne contraintes/targets/weights
- `get_zerg_constraints(squad_size)`: Contraintes Zerg (25-50 joueurs)
- `get_havoc_constraints(squad_size)`: Contraintes Havoc (10-20 joueurs)
- `get_roaming_constraints(squad_size)`: Contraintes Roaming (1-5 joueurs)
- `apply_meta_constraints(model, x, g, ...)`: Applique les contraintes au modèle CP-SAT
- `get_meta_description(mode, squad_size)`: Description lisible

### 2. `/docs/WVW_META_CONSTRAINTS.md`
Documentation complète des contraintes méta basées sur la communauté WvW.

---

## 🔧 Intégration dans le Solver

### Étape 1: Importer le Module

Dans `/backend/app/core/optimizer/solver_cp_sat_streaming.py`:

```python
from app.core.optimizer.meta_constraints import (
    apply_meta_constraints,
    get_meta_description,
)
```

### Étape 2: Appliquer les Contraintes

Après la création des variables `x`, `g`, `z`, ajouter:

```python
# Apply meta-based constraints (after line ~90)
mode = "zerg"  # ou "havoc" ou "roaming" selon req.mode
targets_meta, weights_meta = apply_meta_constraints(
    model=model,
    x=x,
    g=g,
    players=players,
    builds=builds,
    build_index=build_index,
    group_count=group_count,
    mode=mode,
    squad_size=n,
)

# Override targets and weights with meta values
if req.targets:
    # Merge user targets with meta targets
    targets = {**targets_meta, **req.targets}
else:
    targets = targets_meta

if req.weights:
    # Merge user weights with meta weights
    weights = {**weights_meta, **req.weights}
else:
    weights = weights_meta
```

### Étape 3: Ajouter le Mode dans le Schema

Dans `/backend/app/schemas/optimization.py`:

```python
class OptimizationRequest(BaseModel):
    players: List[PlayerInput]
    builds: List[BuildInput]
    mode: Literal["wvw", "pve"] = "wvw"
    wvw_mode: Optional[Literal["zerg", "havoc", "roaming"]] = "zerg"  # NEW
    squad_size: int
    time_limit_ms: Optional[int] = 2000
    targets: Optional[OptimizationTargets] = None
    weights: Optional[OptimizationWeights] = None
    # ...
```

### Étape 4: Mettre à Jour le Frontend

Dans `/frontend/src/api/optimize.ts`:

```typescript
export type OptimizationRequest = {
  players: OptimizationPlayer[];
  builds: OptimizationBuild[];
  mode: "wvw";
  wvw_mode?: "zerg" | "havoc" | "roaming";  // NEW
  squad_size: number;
  time_limit_ms?: number;
  targets?: OptimizationTargets;
  weights?: OptimizationWeights;
};
```

Dans `/frontend/src/pages/OptimizePage.tsx`:

```typescript
const [wvwMode, setWvwMode] = useState<"zerg" | "havoc" | "roaming">("zerg");

// Dans onStart():
const req: ApiOptimizationRequest = {
  // ...
  mode: "wvw",
  wvw_mode: wvwMode,  // NEW
  // ...
};

// UI pour sélectionner le mode:
<Select value={wvwMode} onValueChange={setWvwMode}>
  <SelectTrigger>
    <SelectValue />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="zerg">Zerg (25-50 joueurs)</SelectItem>
    <SelectItem value="havoc">Havoc (10-20 joueurs)</SelectItem>
    <SelectItem value="roaming">Roaming (1-5 joueurs)</SelectItem>
  </SelectContent>
</Select>
```

---

## 📊 Exemple d'Utilisation

### Avant (Sans Contraintes Méta)
```python
# Résultat: 15 Firebrands (pas de diversité)
result = solve_cp_sat_streaming(req, callback)
```

### Après (Avec Contraintes Méta)
```python
# Mode Zerg (15 joueurs)
req.wvw_mode = "zerg"
result = solve_cp_sat_streaming(req, callback)

# Résultat attendu:
# - 3 Firebrands (20%)
# - 2 Scrappers (13%)
# - 2 Heralds (13%)
# - 1 Tempest (7%)
# - 2 Scourges (13%)
# - 5 DPS (33%)
```

---

## 🧪 Tests

### Test 1: Zerg 50 Joueurs

```python
from app.core.optimizer.meta_constraints import get_mode_constraints

meta = get_mode_constraints("zerg", 50)

# Vérifier les contraintes
assert meta["build_constraints"]["Firebrand"]["min"] == 8
assert meta["build_constraints"]["Firebrand"]["max"] == 12
assert meta["targets"]["quickness_uptime"] == 0.95
assert meta["weights"]["stability"] == 1.0
```

### Test 2: Havoc 15 Joueurs

```python
meta = get_mode_constraints("havoc", 15)

assert meta["build_constraints"]["Firebrand"]["min"] == 2
assert meta["build_constraints"]["Firebrand"]["max"] == 4
assert meta["targets"]["quickness_uptime"] == 0.90
assert meta["weights"]["dps"] == 0.80  # Plus important en Havoc
```

### Test 3: Roaming 5 Joueurs

```python
meta = get_mode_constraints("roaming", 5)

assert meta["build_constraints"]["_max_same_build"] == 2
assert meta["targets"]["quickness_uptime"] == 0.50  # Personnel
assert meta["weights"]["dps"] == 1.0  # Priorité maximale
```

---

## 📈 Bénéfices

### Avant
- ❌ 15 Firebrands (composition inutile)
- ❌ Pas de diversité
- ❌ Targets trop basses (50% quickness)
- ❌ Pas de contraintes sur les builds

### Après
- ✅ Composition équilibrée (20% FB, 12% Scrapper, etc.)
- ✅ Diversité forcée par contraintes hard
- ✅ Targets réalistes (95% quickness en Zerg)
- ✅ Contraintes par subgroup (1 FB minimum)
- ✅ 3 modes adaptés (Zerg, Havoc, Roaming)

---

## 🎯 Prochaines Étapes

### Court Terme
1. ✅ Créer `meta_constraints.py`
2. ✅ Documenter les contraintes (`WVW_META_CONSTRAINTS.md`)
3. ⏸️ Intégrer dans `solver_cp_sat_streaming.py`
4. ⏸️ Ajouter `wvw_mode` dans le schema
5. ⏸️ Mettre à jour le frontend (sélecteur de mode)

### Moyen Terme
1. Tests unitaires pour `meta_constraints.py`
2. Tests d'intégration avec le solver
3. UI pour visualiser les contraintes actives
4. Presets personnalisables ("Zerg Défensif", "Havoc Agressif")

### Long Terme
1. Machine learning pour ajuster les contraintes
2. Analyse post-optimization: "Pourquoi ce build ?"
3. Suggestions: "Ajouter 1 Scrapper pour +20% resist"
4. Historique: comparer plusieurs compositions

---

## 📚 Documentation

- **`WVW_META_CONSTRAINTS.md`**: Contraintes détaillées par mode
- **`FIX_15_FIREBRANDS.md`**: Explication du problème initial
- **`INTEGRATION_META_CONSTRAINTS.md`**: Ce document

---

## 🎉 Conclusion

Les contraintes méta sont maintenant **documentées et implémentées**. L'intégration dans le solver nécessite quelques modifications mineures dans `solver_cp_sat_streaming.py` et le frontend.

**Prochaine étape**: Intégrer `apply_meta_constraints()` dans le solver et tester avec différents modes.

---

**Auteur**: Cascade AI  
**Date**: 2025-10-17 16:45  
**Version**: v3.7.3
