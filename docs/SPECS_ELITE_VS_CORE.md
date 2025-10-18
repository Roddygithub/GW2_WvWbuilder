# 🎯 Spécialisations Elite vs Core — GW2_WvWBuilder

**Documentation complète** sur la distinction entre **spécialisations de base (core)** et **spécialisations d'élite (elite)** dans le système.

---

## 📊 Vue d'ensemble

### Statistiques

| Type | Nombre par profession | Total | Exemple |
|------|----------------------|-------|---------|
| **Core** | 5 | 45 | Radiance, Valor, Strength |
| **Elite** | 3 | 27 | Firebrand, Scrapper, Herald |
| **Total** | 8 | 72 | - |

### Professions

Guild Wars 2 compte **9 professions** :
- Guardian
- Warrior
- Engineer
- Ranger
- Thief
- Elementalist
- Mesmer
- Necromancer
- Revenant

---

## 🔥 Spécialisations d'élite

### Définition

Les **spécialisations d'élite** remplacent entièrement une spécialisation de base et changent :
- ✅ Mécaniques de profession (ex: tomes pour Firebrand)
- ✅ Armes disponibles (ex: bouclier pour Scrapper)
- ✅ Skills 7-0 (utilitaires et élite)
- ✅ Esthétique et animations

### Liste complète par expansion

#### Heart of Thorns (HoT) — 2015

| Profession | Elite Spec | Rôle principal WvW |
|-----------|-----------|-------------------|
| Guardian | **Dragonhunter** | DPS Power |
| Warrior | **Berserker** | DPS Power |
| Engineer | **Scrapper** | Support/Sustain |
| Ranger | **Druid** | Heal/Support |
| Thief | **Daredevil** | DPS/Mobilité |
| Elementalist | **Tempest** | Heal/Auras |
| Mesmer | **Chronomancer** | Support (historique) |
| Necromancer | **Reaper** | DPS Power |
| Revenant | **Herald** | Support/DPS |

#### Path of Fire (PoF) — 2017

| Profession | Elite Spec | Rôle principal WvW |
|-----------|-----------|-------------------|
| Guardian | **Firebrand** | Support (top tier) |
| Warrior | **Spellbreaker** | Boon Strip |
| Engineer | **Holosmith** | DPS Power/Burst |
| Ranger | **Soulbeast** | DPS Power |
| Thief | **Deadeye** | DPS Sniper |
| Elementalist | **Weaver** | DPS Power |
| Mesmer | **Mirage** | DPS Conditions |
| Necromancer | **Scourge** | DPS Conditions/Barrier |
| Revenant | **Renegade** | DPS/Support |

#### End of Dragons (EoD) — 2022

| Profession | Elite Spec | Rôle principal WvW |
|-----------|-----------|-------------------|
| Guardian | **Willbender** | DPS/Mobilité |
| Warrior | **Bladesworn** | DPS Burst |
| Engineer | **Mechanist** | DPS/Support |
| Ranger | **Untamed** | DPS Hybride |
| Thief | **Specter** | Support/Heal |
| Elementalist | **Catalyst** | DPS/Support |
| Mesmer | **Virtuoso** | DPS Power |
| Necromancer | **Harbinger** | DPS Conditions |
| Revenant | **Vindicator** | DPS Hybride |

---

## ⚙️ Spécialisations Core

### Définition

Les **spécialisations de base (core)** sont disponibles dès le niveau 80 sans extension. Elles modifient :
- ✅ Stats (power, precision, condition damage, etc.)
- ✅ Traits mineurs et majeurs
- ✅ Synergies avec armes et compétences existantes

### Liste complète par profession

#### Guardian
- **Radiance** (power damage)
- **Valor** (defense/sustain)
- **Honor** (heal/support)
- **Virtues** (virtues boost)
- **Zeal** (symbols/burns)

#### Warrior
- **Strength** (power/berserker)
- **Arms** (bleeds/crit)
- **Defense** (tank/sustain)
- **Tactics** (banners/support)
- **Discipline** (burst/adrenaline)

#### Engineer
- **Explosives** (bombs/grenades)
- **Firearms** (direct damage)
- **Inventions** (defense/healing)
- **Alchemy** (elixirs/conditions)
- **Tools** (gadgets/utility)

#### Ranger
- **Marksmanship** (power ranged)
- **Skirmishing** (flanking/crit)
- **Wilderness Survival** (survival/conditions)
- **Nature Magic** (spirits/regen)
- **Beastmastery** (pet synergy)

#### Thief
- **Deadly Arts** (poison/conditions)
- **Critical Strikes** (crit/ferocity)
- **Shadow Arts** (stealth/sustain)
- **Acrobatics** (dodge/mobility)
- **Trickery** (initiative/utility)

#### Elementalist
- **Fire** (power damage/burns)
- **Air** (lightning/mobility)
- **Earth** (defense/bleeds)
- **Water** (heal/support)
- **Arcane** (attunements/boons)

#### Mesmer
- **Domination** (power/burst)
- **Dueling** (sword/precision)
- **Chaos** (conditions/defense)
- **Inspiration** (heal/support)
- **Illusions** (clones/phantasms)

#### Necromancer
- **Spite** (power/vulnerability)
- **Curses** (conditions/torment)
- **Death Magic** (minions/defense)
- **Blood Magic** (heal/vampirism)
- **Soul Reaping** (life force/death shroud)

#### Revenant
- **Corruption** (conditions/torment)
- **Retribution** (retaliation/damage)
- **Salvation** (heal/support)
- **Invocation** (legends/energy)
- **Devastation** (power/ferocity)

---

## 🧬 Implémentation dans le système

### Schéma de données

```python
class BuildTemplateKB(BaseModel):
    id: int
    profession: str
    specialization: str
    is_elite: bool  # True = elite, False = core
    capability: CapabilityVector
```

### Module de référence

**`backend/app/core/kb/specs_reference.py`** :

```python
from app.core.kb.specs_reference import (
    get_all_elite_specs,      # Liste des 27 specs elite
    get_all_core_specs,       # Liste des 45 specs core
    is_elite_spec,            # Vérifie si spec est elite
    get_profession_for_spec,  # Profession pour une spec
    get_expansion_for_elite,  # Expansion (HoT/PoF/EoD)
    get_specs_by_profession,  # Toutes specs d'une profession
    get_wvw_meta_specs,       # Specs méta WvW
)
```

### Exemples d'utilisation

#### Vérifier si une spec est elite

```python
from app.core.kb.specs_reference import is_elite_spec

is_elite_spec("Firebrand")  # → True
is_elite_spec("Radiance")   # → False
```

#### Obtenir la profession d'une spec

```python
from app.core.kb.specs_reference import get_profession_for_spec

get_profession_for_spec("Firebrand")  # → "Guardian"
get_profession_for_spec("Scrapper")   # → "Engineer"
get_profession_for_spec("Radiance")   # → "Guardian"
```

#### Obtenir l'expansion d'une spec elite

```python
from app.core.kb.specs_reference import get_expansion_for_elite

get_expansion_for_elite("Firebrand")    # → "PoF"
get_expansion_for_elite("Scrapper")     # → "HoT"
get_expansion_for_elite("Mechanist")    # → "EoD"
get_expansion_for_elite("Radiance")     # → "" (core spec)
```

#### Obtenir toutes les specs d'une profession

```python
from app.core.kb.specs_reference import get_specs_by_profession

# Toutes (core + elite)
get_specs_by_profession("Guardian")
# → ["Radiance", "Valor", "Honor", "Virtues", "Zeal", 
#    "Dragonhunter", "Firebrand", "Willbender"]

# Elite uniquement
get_specs_by_profession("Guardian", include_core=False)
# → ["Dragonhunter", "Firebrand", "Willbender"]

# Core uniquement
get_specs_by_profession("Guardian", include_elite=False)
# → ["Radiance", "Valor", "Honor", "Virtues", "Zeal"]
```

#### Obtenir les specs méta WvW

```python
from app.core.kb.specs_reference import get_wvw_meta_specs

# Elite uniquement (méta actuel)
get_wvw_meta_specs(elite_only=True)
# → ["Firebrand", "Scrapper", "Mechanist", "Herald", 
#    "Tempest", "Scourge", "Reaper", ...]

# Toutes (elite + core meta)
get_wvw_meta_specs()
```

---

## 🎯 Distinction dans la KB

### Ingestion API GW2

L'API GW2 fournit le champ **`elite`** :

```json
{
  "id": 62,
  "name": "Firebrand",
  "profession": "Guardian",
  "elite": true,
  "major_traits": [2075, 2101, 2159],
  "minor_traits": [2086, 2105, 2179]
}
```

### Stockage KB

**`backend/app/var/kb.json`** :

```json
{
  "builds": [
    {
      "id": 200,
      "profession": "Guardian",
      "specialization": "Firebrand",
      "is_elite": true,
      "capability": {
        "quickness": 0.95,
        "stability": 0.85,
        "...": "..."
      }
    },
    {
      "id": 250,
      "profession": "Guardian",
      "specialization": "Radiance",
      "is_elite": false,
      "capability": {
        "dps": 0.75,
        "sustain": 0.40,
        "...": "..."
      }
    }
  ]
}
```

### Refresh KB

Le script `refresh.py` extrait automatiquement **`is_elite`** depuis l'API :

```python
# backend/app/core/kb/builder.py
spec_is_elite: Dict[str, bool] = {}
for spec in gw2_data.get("specializations", []):
    spec_name = spec["name"].lower()
    spec_is_elite[spec_name] = spec.get("elite", False)
```

---

## 🧪 Tests

### Lancer les tests

```bash
cd backend
poetry run pytest tests/test_specs_reference.py -v
```

### Résultats attendus

```
test_specs_reference.py::test_total_specs_count ✓
test_specs_reference.py::test_is_elite_spec ✓
test_specs_reference.py::test_get_profession_for_spec ✓
test_specs_reference.py::test_get_expansion_for_elite ✓
test_specs_reference.py::test_get_specs_by_profession ✓
test_specs_reference.py::test_wvw_meta_specs ✓
test_specs_reference.py::test_elite_specs_uniqueness ✓
test_specs_reference.py::test_all_professions_have_specs ✓
test_specs_reference.py::test_known_wvw_specs ✓

========== 9 passed in 0.12s ==========
```

---

## 🚀 Impact sur l'optimisation

### Pénalités de doublons

Le solver peut appliquer des **pénalités différentes** selon le type de spec :

```python
# Elite specs (plus spécialisées)
if build.is_elite:
    dup_penalty_group = 0.25  # Pénalité forte
else:
    dup_penalty_group = 0.15  # Pénalité modérée (core plus flexible)
```

### Diversité

Le solver peut **récompenser la diversité** en priorisant les builds elite :

```python
if build.is_elite and build.specialization not in seen_specs:
    diversity_bonus += 0.05  # Bonus pour spec elite unique
```

### Méta WvW

Le solver peut **prioriser les specs méta** :

```python
from app.core.kb.specs_reference import get_wvw_meta_specs

meta_specs = get_wvw_meta_specs(elite_only=True)
if build.specialization in meta_specs:
    meta_bonus += 0.10  # Bonus méta WvW
```

---

## 📈 Statistiques actuelles

### Specs WvW par type

| Type | Méta | Viable | Situationnel |
|------|------|--------|--------------|
| **Elite** | 13 | 10 | 4 |
| **Core** | 2 | 3 | 40 |

### Top 5 specs WvW (elite)

1. **Firebrand** (Guardian) — Support top tier
2. **Scrapper** (Engineer) — Support/Sustain
3. **Herald** (Revenant) — Support/DPS
4. **Tempest** (Elementalist) — Heal/Auras
5. **Scourge** (Necromancer) — Conditions/Barrier

---

## 🔄 Évolution future

### Prochaines extensions

ArenaNet ajoutera probablement de **nouvelles specs elite** dans les futures extensions :
- 4ème spec elite par profession
- Méta WvW en constante évolution
- Adaptation automatique via KB refresh

### Veille méta

Le système crawle automatiquement :
- MetaBattle (builds communautaires)
- Hardstuck (guides compétitifs)
- GW2 Wiki (patchs officiels)

Le **refresh KB quotidien** assure une mise à jour continue de **`is_elite`** et des capacités.

---

## 📚 Ressources

- **API GW2 Specializations**: https://api.guildwars2.com/v2/specializations
- **Wiki GW2 Elite Specs**: https://wiki.guildwars2.com/wiki/Elite_specialization
- **MetaBattle WvW**: https://metabattle.com/wiki/Category:World_vs_World_builds
- **Hardstuck WvW**: https://hardstuck.gg/gw2/builds/

---

**Version**: v4.1 (2025-10-18)  
**Auteur**: Roddy + Claude (Anthropic)  
**Licence**: MIT
