# ✅ Fix Appliqué: 15 Firebrands → Composition Diversifiée

**Date**: 2025-10-17 13:05  
**Problème**: Solver proposait 15 Firebrands au lieu de diversifier

---

## 🐛 Le Problème

Tu as lancé l'optimisation et obtenu **15 Firebrands** dans le même groupe. Complètement inutile !

**Cause**: Pas de targets/weights spécifiés → le solver utilisait les valeurs par défaut ultra-basses (quickness 50%, stability 0 sources).

Avec des cibles aussi basses, **1 seul Firebrand suffit** pour tout satisfaire. Pas de raison de diversifier !

---

## ✅ Solution Appliquée

J'ai ajouté des **targets et weights réalistes** pour WvW :

```typescript
targets: {
  quickness_uptime: 0.9,      // 90% quickness (critique)
  alacrity_uptime: 0.7,        // 70% alacrity
  resistance_uptime: 0.8,      // 80% resistance (vs conditions)
  protection_uptime: 0.6,      // 60% protection
  stability_sources: 2,        // 2 sources de stability par groupe
}

weights: {
  quickness: 1.0,              // Priorité maximale
  stability: 1.0,              // Critique en WvW
  resistance: 0.9,             // Très important
  alacrity: 0.8,
  protection: 0.7,
  dps: 0.6,
  sustain: 0.5,
  might: 0.5,
  fury: 0.4,
}
```

---

## 🎯 Pourquoi Ça Marche

Avec ces contraintes, le solver est **forcé de diversifier** :

- **Quickness 90%**: Nécessite Herald + Firebrand (1 seul ne suffit plus)
- **Resistance 80%**: Nécessite Scrapper + Tempest + Scourge
- **Stability 2 sources**: Force Firebrand + Scrapper
- **Protection 60%**: Nécessite Herald + Firebrand + Scrapper

**Résultat**: Composition équilibrée avec 6 builds différents !

---

## 📊 Composition Attendue (Après Fix)

### Chaque groupe (5 joueurs) devrait avoir :
- 1x Firebrand (quickness, stability, protection)
- 1x Scrapper (stability, resistance, quickness)
- 1x Herald (quickness, might, fury, protection)
- 1x Tempest/Scourge (resistance, healing/barrier)
- 1x Mechanist (alacrity, might)

### Coverage attendue :
- ✅ Quickness: 90%+
- ✅ Alacrity: 70%+
- ✅ Stability: 2+ sources
- ✅ Resistance: 80%+
- ✅ Protection: 60%+
- ✅ Might: 70%+

---

## 🔧 Fichiers Modifiés

1. **`frontend/src/api/optimize.ts`**
   - Ajout types `OptimizationTargets` et `OptimizationWeights`

2. **`frontend/src/pages/OptimizePage.tsx`**
   - Ajout targets/weights réalistes dans la requête

---

## 🎮 Comment Tester

1. **Recharger la page**: http://localhost:5173/optimize
2. **Cliquer**: "Lancer l'optimisation"
3. **Observer**: 
   - Builds diversifiés (pas que des Firebrands)
   - 3 groupes de 5 joueurs
   - Coverage équilibrée
   - Pas de warnings

---

## 📚 Documentation

Voir **`docs/FIX_15_FIREBRANDS.md`** pour l'explication complète.

---

**Fix appliqué**: ✅  
**Prêt à tester**: ✅  
**Recharge la page et relance l'optimisation !** 🚀
