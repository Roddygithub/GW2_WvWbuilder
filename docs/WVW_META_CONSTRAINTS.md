# Contraintes Méta WvW pour OR-Tools

**Date**: 2025-10-17 16:30  
**Source**: MetaBattle, GuildJen, Hardstuck, Reddit WvW Community

---

## 📊 Modes de Jeu WvW

### 1. **Zerg / Large Scale** (25-50 joueurs)
Combat en grande escouade, objectifs de siège, batailles de masse.

### 2. **Havoc / Small Scale** (10-15 joueurs)
Petits groupes mobiles, harcèlement, capture d'objectifs secondaires.

### 3. **Roaming** (1-5 joueurs)
Solo ou petit groupe, duels, mobilité maximale.

---

## 🎯 Mode 1: Zerg / Large Scale (25-50 joueurs)

### Composition Méta (Squad de 50)

#### **Support Backbone (20-25% du squad)**
Ces builds sont **essentiels** et doivent être présents dans chaque subgroup (5 joueurs).

| Build | Rôle | Quantité (50p) | Par Subgroup | Priorité |
|-------|------|----------------|--------------|----------|
| **Firebrand** | Stability, Quickness, Aegis | **10** (20%) | **2** | ⭐⭐⭐⭐⭐ |
| **Scrapper** | Resistance, Stability, Healing | **5-8** (10-16%) | **1** | ⭐⭐⭐⭐⭐ |
| **Herald** | Might, Fury, Protection, Quickness | **5** (10%) | **1** | ⭐⭐⭐⭐ |
| **Tempest** | Healing, Auras, Cleanse | **3-5** (6-10%) | **0-1** | ⭐⭐⭐⭐ |

**Total Support**: 23-28 joueurs (46-56%)

#### **DPS / Flex (50-54% du squad)**
Builds de dégâts ou hybrides, flexibles selon la stratégie.

| Build | Rôle | Quantité (50p) | Priorité |
|-------|------|----------------|----------|
| **Scourge** (DPS/Support) | Conditions, Barrier, Boon Corrupt | **5-8** | ⭐⭐⭐⭐ |
| **Reaper** | Power DPS, Sustain | **3-5** | ⭐⭐⭐ |
| **Weaver** | Power DPS, Burst | **3-5** | ⭐⭐⭐ |
| **Holosmith** | Power DPS, Mobility | **2-4** | ⭐⭐⭐ |
| **Berserker** | Power DPS, CC | **2-4** | ⭐⭐⭐ |
| **Mirage** | Condition DPS, Evasion | **2-3** | ⭐⭐ |
| **Vindicator** | Hybrid DPS/Support | **2-3** | ⭐⭐ |

**Total DPS**: 22-27 joueurs (44-54%)

---

### Contraintes OR-Tools (Zerg 50 joueurs)

#### **Contraintes Hard (AddExactlyOne / AddAtLeast / AddAtMost)**

```python
# 1. FIREBRAND - Backbone critique
# Minimum 8, Optimal 10, Maximum 12
solver.Add(sum(x[i, build_firebrand] for i in players) >= 8)
solver.Add(sum(x[i, build_firebrand] for i in players) <= 12)

# 2. SCRAPPER - Backbone critique
# Minimum 5, Optimal 6-8, Maximum 10
solver.Add(sum(x[i, build_scrapper] for i in players) >= 5)
solver.Add(sum(x[i, build_scrapper] for i in players) <= 10)

# 3. HERALD - Might/Fury essentiel
# Minimum 4, Optimal 5, Maximum 7
solver.Add(sum(x[i, build_herald] for i in players) >= 4)
solver.Add(sum(x[i, build_herald] for i in players) <= 7)

# 4. TEMPEST - Healing/Cleanse
# Minimum 2, Optimal 3-5, Maximum 6
solver.Add(sum(x[i, build_tempest] for i in players) >= 2)
solver.Add(sum(x[i, build_tempest] for i in players) <= 6)

# 5. SCOURGE - Flex DPS/Support
# Minimum 3, Optimal 5-8, Maximum 10
solver.Add(sum(x[i, build_scourge] for i in players) >= 3)
solver.Add(sum(x[i, build_scourge] for i in players) <= 10)

# 6. Distribution par subgroup (5 joueurs max)
for group_id in groups:
    solver.Add(sum(g[i, group_id] for i in players) <= 5)
    
    # Chaque subgroup doit avoir au moins 1 Firebrand
    solver.Add(sum(x[i, build_firebrand] * g[i, group_id] for i in players) >= 1)
    
    # Chaque subgroup doit avoir au moins 1 Scrapper OU 1 Tempest
    solver.Add(sum((x[i, build_scrapper] + x[i, build_tempest]) * g[i, group_id] for i in players) >= 1)
```

#### **Targets Boons (Soft Constraints)**

```python
targets = {
    "quickness_uptime": 0.95,      # 95% (critique, Firebrand + Herald)
    "alacrity_uptime": 0.70,        # 70% (utile mais pas critique)
    "resistance_uptime": 0.85,      # 85% (Scrapper + Tempest + Scourge)
    "protection_uptime": 0.70,      # 70% (Herald + Firebrand)
    "stability_sources": 3,         # 3 sources minimum (Firebrand + Scrapper + Herald)
    "might_stacks": 20,             # 20 stacks (Herald + Tempest)
    "fury_uptime": 0.80,            # 80% (Herald)
}
```

#### **Weights Objectif**

```python
weights = {
    "quickness": 1.0,      # Priorité maximale
    "stability": 1.0,      # Critique en Zerg
    "resistance": 0.95,    # Très important (conditions)
    "might": 0.85,         # Important (DPS)
    "fury": 0.80,          # Important (crit)
    "protection": 0.75,    # Mitigation
    "alacrity": 0.70,      # Utile mais pas critique
    "dps": 0.60,           # Modéré
    "sustain": 0.55,       # Modéré
}
```

---

## 🎯 Mode 2: Havoc / Small Scale (10-15 joueurs)

### Composition Méta (Squad de 15)

#### **Support Core (40-50%)**

| Build | Quantité (15p) | Par Subgroup | Priorité |
|-------|----------------|--------------|----------|
| **Firebrand** | **3** (20%) | **1** | ⭐⭐⭐⭐⭐ |
| **Scrapper** | **2** (13%) | **0-1** | ⭐⭐⭐⭐ |
| **Herald** | **2** (13%) | **0-1** | ⭐⭐⭐⭐ |
| **Tempest** | **1** (7%) | **0-1** | ⭐⭐⭐ |

**Total Support**: 6-8 joueurs (40-53%)

#### **DPS / Flex (47-60%)**

| Build | Quantité (15p) | Priorité |
|-------|----------------|----------|
| **Scourge** | **2-3** | ⭐⭐⭐⭐ |
| **Reaper** | **1-2** | ⭐⭐⭐ |
| **Weaver** | **1-2** | ⭐⭐⭐ |
| **Holosmith** | **1** | ⭐⭐ |
| **Berserker** | **1** | ⭐⭐ |

**Total DPS**: 7-9 joueurs (47-60%)

---

### Contraintes OR-Tools (Havoc 15 joueurs)

#### **Contraintes Hard**

```python
# 1. FIREBRAND - Minimum 2, Optimal 3, Maximum 4
solver.Add(sum(x[i, build_firebrand] for i in players) >= 2)
solver.Add(sum(x[i, build_firebrand] for i in players) <= 4)

# 2. SCRAPPER - Minimum 1, Optimal 2, Maximum 3
solver.Add(sum(x[i, build_scrapper] for i in players) >= 1)
solver.Add(sum(x[i, build_scrapper] for i in players) <= 3)

# 3. HERALD - Minimum 1, Optimal 2, Maximum 3
solver.Add(sum(x[i, build_herald] for i in players) >= 1)
solver.Add(sum(x[i, build_herald] for i in players) <= 3)

# 4. TEMPEST - Minimum 0, Optimal 1, Maximum 2
solver.Add(sum(x[i, build_tempest] for i in players) <= 2)

# 5. SCOURGE - Minimum 1, Optimal 2-3, Maximum 4
solver.Add(sum(x[i, build_scourge] for i in players) >= 1)
solver.Add(sum(x[i, build_scourge] for i in players) <= 4)

# 6. Distribution par subgroup (5 joueurs max)
for group_id in groups:
    solver.Add(sum(g[i, group_id] for i in players) <= 5)
    
    # Chaque subgroup doit avoir au moins 1 Firebrand
    solver.Add(sum(x[i, build_firebrand] * g[i, group_id] for i in players) >= 1)
```

#### **Targets Boons**

```python
targets = {
    "quickness_uptime": 0.90,      # 90%
    "alacrity_uptime": 0.60,        # 60% (moins critique)
    "resistance_uptime": 0.80,      # 80%
    "protection_uptime": 0.65,      # 65%
    "stability_sources": 2,         # 2 sources minimum
    "might_stacks": 18,             # 18 stacks
    "fury_uptime": 0.75,            # 75%
}
```

#### **Weights Objectif**

```python
weights = {
    "quickness": 1.0,
    "stability": 1.0,
    "resistance": 0.90,
    "dps": 0.80,           # Plus important en Havoc
    "might": 0.75,
    "fury": 0.70,
    "protection": 0.65,
    "sustain": 0.60,
    "alacrity": 0.55,      # Moins critique
}
```

---

## 🎯 Mode 3: Roaming (1-5 joueurs)

### Composition Méta (Groupe de 5)

#### **Builds Autosuffisants**
En roaming, chaque build doit être **autosuffisant** (sustain, mobility, burst).

| Build | Quantité (5p) | Priorité |
|-------|---------------|----------|
| **Willbender** (Celestial) | **1** | ⭐⭐⭐⭐⭐ |
| **Scrapper** (Celestial) | **1** | ⭐⭐⭐⭐ |
| **Herald** (Power) | **1** | ⭐⭐⭐⭐ |
| **Scourge** (Condition) | **1** | ⭐⭐⭐⭐ |
| **Weaver** (Fresh Air) | **1** | ⭐⭐⭐ |

**Alternatives**: Reaper, Berserker, Mirage, Virtuoso, Daredevil, Harbinger

---

### Contraintes OR-Tools (Roaming 5 joueurs)

#### **Contraintes Hard**

```python
# 1. Pas de contraintes strictes sur les builds
# Chaque build doit être viable en solo

# 2. Diversité recommandée (pas plus de 2 builds identiques)
for build in builds:
    solver.Add(sum(x[i, build] for i in players) <= 2)

# 3. Au moins 1 build avec sustain élevé (Scrapper, Tempest, Druid)
solver.Add(sum(x[i, build_scrapper] + x[i, build_tempest] + x[i, build_druid] for i in players) >= 1)

# 4. Au moins 1 build avec burst élevé (Weaver, Willbender, Berserker)
solver.Add(sum(x[i, build_weaver] + x[i, build_willbender] + x[i, build_berserker] for i in players) >= 1)
```

#### **Targets Boons** (Moins critiques)

```python
targets = {
    "quickness_uptime": 0.50,      # 50% (personnel)
    "alacrity_uptime": 0.30,        # 30% (personnel)
    "resistance_uptime": 0.60,      # 60%
    "protection_uptime": 0.50,      # 50%
    "stability_sources": 1,         # 1 source minimum
    "might_stacks": 15,             # 15 stacks
    "fury_uptime": 0.70,            # 70%
}
```

#### **Weights Objectif**

```python
weights = {
    "dps": 1.0,            # Priorité maximale (burst)
    "sustain": 0.95,       # Très important (survie)
    "mobility": 0.90,      # Très important (kiting)
    "stability": 0.80,
    "resistance": 0.75,
    "might": 0.60,
    "fury": 0.60,
    "quickness": 0.40,     # Moins critique
    "alacrity": 0.30,      # Moins critique
}
```

---

## 📊 Tableau Récapitulatif

### Contraintes par Mode

| Mode | Squad Size | Firebrand | Scrapper | Herald | Tempest | Scourge | DPS |
|------|------------|-----------|----------|--------|---------|---------|-----|
| **Zerg** | 50 | 8-12 (20%) | 5-10 (12%) | 4-7 (10%) | 2-6 (8%) | 3-10 (12%) | 22-27 (48%) |
| **Havoc** | 15 | 2-4 (20%) | 1-3 (13%) | 1-3 (13%) | 0-2 (7%) | 1-4 (13%) | 7-9 (53%) |
| **Roaming** | 5 | 0-1 (10%) | 0-1 (20%) | 0-1 (20%) | 0-1 (10%) | 0-1 (20%) | 3-4 (70%) |

### Targets par Mode

| Boon | Zerg | Havoc | Roaming |
|------|------|-------|---------|
| **Quickness** | 95% | 90% | 50% |
| **Alacrity** | 70% | 60% | 30% |
| **Resistance** | 85% | 80% | 60% |
| **Protection** | 70% | 65% | 50% |
| **Stability** | 3 sources | 2 sources | 1 source |
| **Might** | 20 stacks | 18 stacks | 15 stacks |
| **Fury** | 80% | 75% | 70% |

### Weights par Mode

| Métrique | Zerg | Havoc | Roaming |
|----------|------|-------|---------|
| **Quickness** | 1.0 | 1.0 | 0.4 |
| **Stability** | 1.0 | 1.0 | 0.8 |
| **Resistance** | 0.95 | 0.90 | 0.75 |
| **Might** | 0.85 | 0.75 | 0.6 |
| **Fury** | 0.80 | 0.70 | 0.6 |
| **Protection** | 0.75 | 0.65 | 0.5 |
| **Alacrity** | 0.70 | 0.55 | 0.3 |
| **DPS** | 0.60 | 0.80 | 1.0 |
| **Sustain** | 0.55 | 0.60 | 0.95 |

---

## 🔧 Implémentation dans le Solver

### Exemple: Mode Zerg (50 joueurs)

```python
def apply_zerg_constraints(solver, players, builds, groups):
    """
    Applique les contraintes méta pour le mode Zerg (50 joueurs).
    """
    # Build IDs (à adapter selon votre base de données)
    FIREBRAND_ID = 101
    SCRAPPER_ID = 102
    HERALD_ID = 103
    TEMPEST_ID = 104
    SCOURGE_ID = 105
    
    # 1. Contraintes Firebrand (8-12)
    firebrand_count = sum(x[i, FIREBRAND_ID] for i in players)
    solver.Add(firebrand_count >= 8)
    solver.Add(firebrand_count <= 12)
    
    # 2. Contraintes Scrapper (5-10)
    scrapper_count = sum(x[i, SCRAPPER_ID] for i in players)
    solver.Add(scrapper_count >= 5)
    solver.Add(scrapper_count <= 10)
    
    # 3. Contraintes Herald (4-7)
    herald_count = sum(x[i, HERALD_ID] for i in players)
    solver.Add(herald_count >= 4)
    solver.Add(herald_count <= 7)
    
    # 4. Contraintes Tempest (2-6)
    tempest_count = sum(x[i, TEMPEST_ID] for i in players)
    solver.Add(tempest_count >= 2)
    solver.Add(tempest_count <= 6)
    
    # 5. Contraintes Scourge (3-10)
    scourge_count = sum(x[i, SCOURGE_ID] for i in players)
    solver.Add(scourge_count >= 3)
    solver.Add(scourge_count <= 10)
    
    # 6. Distribution par subgroup
    for group_id in groups:
        # Max 5 joueurs par groupe
        solver.Add(sum(g[i, group_id] for i in players) <= 5)
        
        # Au moins 1 Firebrand par groupe
        solver.Add(sum(x[i, FIREBRAND_ID] * g[i, group_id] for i in players) >= 1)
        
        # Au moins 1 Scrapper OU Tempest par groupe
        solver.Add(sum((x[i, SCRAPPER_ID] + x[i, TEMPEST_ID]) * g[i, group_id] for i in players) >= 1)
    
    # 7. Targets et Weights
    targets = {
        "quickness_uptime": 0.95,
        "alacrity_uptime": 0.70,
        "resistance_uptime": 0.85,
        "protection_uptime": 0.70,
        "stability_sources": 3,
        "might_stacks": 20,
        "fury_uptime": 0.80,
    }
    
    weights = {
        "quickness": 1.0,
        "stability": 1.0,
        "resistance": 0.95,
        "might": 0.85,
        "fury": 0.80,
        "protection": 0.75,
        "alacrity": 0.70,
        "dps": 0.60,
        "sustain": 0.55,
    }
    
    return targets, weights
```

---

## 📚 Sources

1. **MetaBattle**: https://metabattle.com/wiki/WvW
   - Builds Zerg: Meta, Great, Good tiers
   - Builds Roaming: Meta builds par profession

2. **GuildJen**: https://guildjen.com/gw2-wvw-zerg-builds/
   - Support builds: Firebrand, Scrapper, Tempest, etc.
   - DPS builds: Holosmith, Berserker, Scourge, etc.

3. **Hardstuck**: https://hardstuck.gg/gw2/guides/events/squads-and-commanding/
   - Squad composition guide
   - Boon distribution par subgroup

4. **Reddit WvW Community**:
   - r/Guildwars2 discussions sur les comps
   - Retours d'expérience de commanders

---

## 🎉 Conclusion

Ces contraintes sont basées sur les **méta actuelles** (2025) et les **retours de la communauté WvW**. Elles permettent de paramétrer OR-Tools avec des contraintes réalistes qui reflètent les compositions utilisées par les guildes compétitives.

**Recommandation**: Utiliser le **mode Zerg** par défaut, avec possibilité de basculer vers **Havoc** ou **Roaming** via l'UI.

---

**Auteur**: Cascade AI  
**Date**: 2025-10-17 16:30  
**Version**: v3.7.3
