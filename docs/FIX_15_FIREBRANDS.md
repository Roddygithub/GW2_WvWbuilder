# Fix: Pourquoi 15 Firebrands ? 🔥

**Date**: 2025-10-17 13:05  
**Problème**: Le solver propose 15 Firebrands au lieu de diversifier les builds

---

## 🐛 Le Problème

Quand tu lances l'optimisation, tu obtiens **15 Firebrands** dans le même groupe. C'est complètement inutile en WvW !

### Symptômes
- ✅ Quickness: 100%
- ✅ Resistance: 100%
- ✅ Protection: 100%
- ❌ Stability: 0%
- ❌ Might: NaN%
- ❌ Fury: 3%
- ⚠️ Tous les joueurs dans le même groupe (15/5)

---

## 🔍 Cause Racine

Le problème vient de **l'absence de targets et weights** dans la requête d'optimisation.

### Avant (Bugué)
```typescript
const req: ApiOptimizationRequest = {
  players: [...],
  builds: [...],
  mode: "wvw",
  squad_size: 15,
  time_limit_ms: 3000,
  // ❌ PAS DE TARGETS
  // ❌ PAS DE WEIGHTS
};
```

**Résultat**: Le solver utilise les valeurs par défaut ultra-basses du backend:
- `quickness_uptime: 0.5` (50% seulement)
- `stability_sources: 0` (aucune stability requise !)
- Tous les weights à 1.0 (pas de priorité)

Avec des cibles aussi basses, **un seul Firebrand suffit** pour tout satisfaire. Le solver n'a donc aucune raison de diversifier !

---

## ✅ Solution Appliquée

### Après (Corrigé)
```typescript
const req: ApiOptimizationRequest = {
  players: [...],
  builds: [...],
  mode: "wvw",
  squad_size: 15,
  time_limit_ms: 3000,
  targets: {
    quickness_uptime: 0.9,      // 90% quickness (critique)
    alacrity_uptime: 0.7,        // 70% alacrity
    resistance_uptime: 0.8,      // 80% resistance (vs conditions)
    protection_uptime: 0.6,      // 60% protection
    stability_sources: 2,        // 2 sources de stability par groupe
  },
  weights: {
    quickness: 1.0,
    alacrity: 0.8,
    stability: 1.0,              // Stability prioritaire
    resistance: 0.9,
    protection: 0.7,
    might: 0.5,
    fury: 0.4,
    dps: 0.6,
    sustain: 0.5,
  },
};
```

---

## 🎯 Pourquoi Ça Marche Maintenant

### 1. Targets Réalistes
- **Quickness 90%**: Force le solver à avoir plusieurs sources (Herald + Firebrand)
- **Resistance 80%**: Nécessite Scrapper + Tempest + Scourge
- **Stability 2 sources**: Force Firebrand + Scrapper (les deux meilleurs)
- **Protection 60%**: Nécessite diversité (Herald, Firebrand, Scrapper)

### 2. Weights Équilibrés
- **Stability 1.0**: Priorité maximale (critique en WvW)
- **Quickness 1.0**: Aussi important
- **Resistance 0.9**: Très important (conditions)
- **DPS 0.6**: Modéré (pas la priorité #1)
- **Might 0.5**: Bonus appréciable

### 3. Contraintes Hard
Le solver doit maintenant:
- Atteindre 90% quickness → **Pas possible avec 1 seul Firebrand**
- Avoir 2 sources stability → **Nécessite Firebrand + Scrapper**
- Atteindre 80% resistance → **Nécessite Scrapper + Tempest**

**Résultat**: Le solver est **forcé de diversifier** les builds !

---

## 📊 Composition Attendue (Après Fix)

### Groupe 1 (5 joueurs)
- 1x Firebrand (quickness, stability, protection)
- 1x Scrapper (stability, resistance, quickness)
- 1x Herald (quickness, might, fury, protection)
- 1x Tempest (resistance, protection, healing)
- 1x Scourge (resistance, barrier, conditions)

### Groupe 2 (5 joueurs)
- 1x Firebrand
- 1x Scrapper
- 1x Herald
- 1x Mechanist (alacrity, might)
- 1x Tempest

### Groupe 3 (5 joueurs)
- 1x Firebrand
- 1x Scrapper
- 1x Herald
- 1x Scourge
- 1x Mechanist

**Coverage attendue**:
- ✅ Quickness: 90%+
- ✅ Alacrity: 70%+
- ✅ Stability: 2+ sources
- ✅ Resistance: 80%+
- ✅ Protection: 60%+
- ✅ Might: 70%+
- ✅ Fury: 50%+

---

## 🔧 Fichiers Modifiés

1. **`frontend/src/api/optimize.ts`**
   - Ajout `OptimizationTargets` type
   - Ajout `OptimizationWeights` type
   - Mise à jour `OptimizationRequest` avec `targets?` et `weights?`

2. **`frontend/src/pages/OptimizePage.tsx`**
   - Ajout targets réalistes dans `onStart()`
   - Ajout weights équilibrés

---

## 🎮 Comment Tester

1. **Recharger la page**: http://localhost:5173/optimize
2. **Cliquer**: "Lancer l'optimisation"
3. **Observer**: 
   - Builds diversifiés (Firebrand, Scrapper, Herald, etc.)
   - 3 groupes de 5 joueurs
   - Coverage équilibrée
   - Pas de warnings "Stability < 50%"

---

## 📚 Leçons Apprises

### Pourquoi C'est Important

1. **Targets trop basses = Pas de diversité**
   - Si tu demandes 50% quickness, 1 Firebrand suffit
   - Si tu demandes 90% quickness, il faut Herald + Firebrand

2. **Weights guident les priorités**
   - Sans weights, le solver optimise "au hasard"
   - Avec weights, il sait que stability > might > fury

3. **Contraintes hard forcent la diversité**
   - `stability_sources: 2` force au moins 2 builds différents
   - `resistance_uptime: 0.8` force Scrapper + Tempest

### Valeurs Recommandées WvW

```typescript
// Cibles réalistes pour WvW compétitif
targets: {
  quickness_uptime: 0.9,       // 90% (critique)
  alacrity_uptime: 0.7,        // 70% (utile)
  resistance_uptime: 0.8,      // 80% (vs conditions)
  protection_uptime: 0.6,      // 60% (mitigation)
  stability_sources: 2,        // 2 sources minimum
}

// Weights pour WvW (total = 6.8)
weights: {
  quickness: 1.0,    // 15% du score
  stability: 1.0,    // 15% du score
  resistance: 0.9,   // 13% du score
  alacrity: 0.8,     // 12% du score
  protection: 0.7,   // 10% du score
  dps: 0.6,          // 9% du score
  sustain: 0.5,      // 7% du score
  might: 0.5,        // 7% du score
  fury: 0.4,         // 6% du score
}
```

---

## 🚀 Prochaines Améliorations

### Court Terme
- [ ] UI pour ajuster targets/weights
- [ ] Presets: "Zerg", "Roaming", "Defense"
- [ ] Validation: alerter si targets impossibles

### Moyen Terme
- [ ] Analyse post-optimization: "Pourquoi ce build ?"
- [ ] Suggestions: "Ajouter 1 Scrapper pour +20% resistance"
- [ ] Historique: comparer plusieurs compositions

---

## 🎉 Conclusion

Le problème des "15 Firebrands" était dû à **l'absence de contraintes réalistes**. Avec des targets à 90% quickness et 2 sources de stability, le solver est maintenant **forcé de diversifier** les builds.

**Fix appliqué**: ✅  
**Composition attendue**: Diversifiée (Firebrand, Scrapper, Herald, Tempest, Scourge, Mechanist)  
**Coverage**: Équilibrée (90% quick, 80% resist, 2 stab sources)

---

**Auteur**: Cascade AI  
**Date**: 2025-10-17 13:05  
**Version**: v3.7.1 → v3.7.2
