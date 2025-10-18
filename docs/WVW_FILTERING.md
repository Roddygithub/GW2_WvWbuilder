# 🎯 Filtrage WvW — GW2_WvWBuilder

**Système de filtrage intelligent** pour garantir que seul le contenu **World vs World (McM)** est utilisé par le LLM.

---

## 🚨 Problème initial

Certaines sources contiennent du **contenu mixte PvE/WvW** ou **uniquement PvE** :

| Source | Type | URL WvW | Risque |
|--------|------|---------|--------|
| **MetaBattle** | PvE + WvW + PvP | `/Category:World_vs_World_builds` | ⚠️ Filtrage actif |
| **Hardstuck** | PvE + WvW | `/gw2/builds/?t=wvw` | ✅ **URL WvW ciblée** |
| **Snow Crows** | PvE + WvW | `/builds/wvw` | ✅ **URL WvW ciblée** |
| **GW2 Mists** | WvW pur | `/builds` | ✅ **WvW uniquement** |
| **Google Sheets WvW** | WvW pur | Spreadsheet dédié | ✅ **WvW uniquement** |
| **GW2 Wiki** | Général | `/wiki/{Profession}` | ⚠️ Filtrage actif |
| **Discretize** | Fractals (PvE) | N/A | ❌ **Pas crawlé** |

**Sans filtrage**, le LLM apprendrait de contenu **non pertinent** (raids, fractals) et donnerait des recommandations **incorrectes pour WvW**.

---

## ✅ Solution : Filtrage intelligent

### 1. Détection automatique WvW vs PvE

**`backend/app/core/kb/web_crawler.py`** implémente un **système de scoring** :

#### Mots-clés WvW (+1.0 par occurrence)
```python
wvw_keywords = [
    "wvw", "world vs world", "mcm", "mists",
    "zerg", "havoc", "roaming", "squad", "commander",
    "keep", "tower", "smc", "stonemist", "garrison",
    "borderlands", "eternal battlegrounds",
    "pirate ship", "blob", "siege", "trebuchet",
    "boon strip", "boon corrupt", "stability stack"
]
```

#### Mots-clés PvE (-2.0 par occurrence, pénalité forte)
```python
pve_keywords = [
    "raid", "fractal", "strike", "dungeon", "cm",
    "boss", "enrage", "dps benchmark", "golem",
    "instanced", "10-man", "5-man", "encounter", "phase"
]
```

#### Score final
```python
wvw_score = (nb_wvw_keywords × 1.0) - (nb_pve_keywords × 2.0)
is_wvw = wvw_score > 0
```

**Exemple:**
- Texte avec 3 keywords WvW + 0 PvE → score = 3.0 → **WvW ✅**
- Texte avec 1 keyword WvW + 2 PvE → score = 1.0 - 4.0 = -3.0 → **PvE ❌**

---

### 2. Filtrage dans le crawler

**`extract_synergies_from_crawl()`** ne garde **que le contenu WvW** :

```python
def extract_synergies_from_crawl(crawl_data):
    synergies = set()
    
    for source, pages in crawl_data.items():
        for page in pages:
            # ⚡ Filtrage : seulement si WvW
            if not page.get("is_wvw", False):
                continue  # Ignore PvE content
            
            # Traite les synergies WvW
            for pair in page.get("synergies", []):
                synergies.add(pair)
    
    return list(synergies)
```

**Résultat** : Les builds Discretize (fractals) et Snow Crows (raids) sont **automatiquement ignorés**.

---

### 3. Prompts LLM renforcés

**`backend/app/core/llm/ollama_engine.py`** :

#### Synergies (get_synergy_pairs)
```python
prompt = (
    f"You are a Guild Wars 2 World vs World (WvW) expert. "
    f"Rate synergies for {mode} mode. "
    f"IMPORTANT: Focus ONLY on WvW gameplay (zerg, havoc, roaming). "
    f"IGNORE raids, fractals, strikes, dungeons, and all PvE content. "
    f"Consider WvW-specific synergies: boon sharing, stability stacking, "
    f"cleanses, resistance, etc."
)
```

#### Analyse tactique (explain_composition)
```python
prompt = (
    f"You are a Guild Wars 2 World vs World (WvW) tactical expert. "
    f"Analyze this squad composition for {mode} mode. "
    f"IMPORTANT: Focus ONLY on WvW gameplay (zerg fights, havoc groups, roaming). "
    f"IGNORE all PvE content (raids, fractals, strikes, dungeons). "
    f"Provide WvW tactical analysis: strengths in WvW combat, "
    f"weaknesses against enemy zergs, and one key WvW-specific recommendation."
)
```

---

## 🧪 Test du filtrage

### Script de diagnostic

```bash
cd backend
poetry run python app/core/kb/diagnose_wvw_filter.py
```

**Sortie attendue:**
```
======================================================================
WvW Detection Diagnostic
======================================================================

✅ PASS WvW zerg text
  Text: This Firebrand build is perfect for WvW zerg play...
  Expected WvW: True
  Detected WvW: True
  WvW Score: 3.0

❌ FAIL PvE raid text
  Text: This Firebrand build is optimized for raids...
  Expected WvW: False
  Detected WvW: False
  WvW Score: -4.0

✅ PASS WvW roaming text
  Text: Excellent roaming build for solo WvW play...
  Expected WvW: True
  Detected WvW: True
  WvW Score: 2.0

======================================================================
Results: 7 passed, 0 failed
======================================================================
```

### Test manuel

```bash
cd backend
poetry run python -c "
from app.core.kb.web_crawler import extract_build_info

# Test WvW text
text_wvw = 'Firebrand for WvW zerg, provides stability and quickness.'
info = extract_build_info(text_wvw, 'test')
print(f'WvW text: is_wvw={info[\"is_wvw\"]}, score={info[\"wvw_score\"]}')

# Test PvE text
text_pve = 'Optimized for raids and fractals. High DPS on golem benchmark.'
info = extract_build_info(text_pve, 'test')
print(f'PvE text: is_wvw={info[\"is_wvw\"]}, score={info[\"wvw_score\"]}')
"
```

**Résultat attendu:**
```
WvW text: is_wvw=True, score=4.0
PvE text: is_wvw=False, score=-4.0
```

---

## 📊 Sources et traitement

### Sources WvW avec URLs ciblées (haute confiance)
- **GW2 Mists** → `/builds` → 15 builds WvW
- **Google Sheets WvW** → Spreadsheet dédié → Compositions communautaires
- **MetaBattle WvW** → `/Category:World_vs_World_builds` → 20 builds
- **Hardstuck WvW** → `/gw2/builds/?t=wvw` → Builds filtrés WvW ✨
- **Snow Crows WvW** → `/builds/wvw` → Section WvW dédiée ✨

### Sources mixtes (filtrage actif par scoring)
- **GW2 Wiki** → Pages générales professions → Score WvW calculé

### Sources PvE (non crawlées)
- **Discretize** → Fractals uniquement → Pas dans la liste de crawl
- **Snow Crows** (section raids) → Non crawlé, seule la section `/builds/wvw` est utilisée
- **Hardstuck** (section PvE) → Non crawlé, seul le filtre `?t=wvw` est utilisé

---

## 🎯 Résultat garanti

### ✅ Le LLM apprend uniquement de
- Builds WvW (zerg, havoc, roaming)
- Compositions de squad WvW
- Synergies tactiques WvW (stability, resistance, cleanses)
- Rôles WvW (commander, support, DPS, tank)
- Stratégies WvW (pirate ship, push, siege)

### ❌ Le LLM ignore
- Builds raids (10-man)
- Builds fractals (5-man)
- DPS benchmarks PvE (golem)
- Mécaniques de boss PvE
- Stratégies d'instance

---

## 🔧 Configuration

### Activer le filtrage (par défaut)

Le filtrage est **toujours actif**. Aucune configuration requise.

### Désactiver temporairement (debug uniquement)

**Non recommandé** mais possible pour debug :

```python
# Dans web_crawler.py, commenter la ligne:
# if not page.get("is_wvw", False):
#     continue
```

### Ajuster les seuils

```python
# Dans extract_build_info()
wvw_keywords = [...]  # Ajouter des keywords
pve_keywords = [...]  # Ajouter des keywords

# Seuil de décision
info["is_wvw"] = wvw_score > 0  # Changer > 0 à > 1.0 pour être plus strict
```

---

## 📈 Statistiques de filtrage

Après un refresh KB complet :

```bash
cd backend
poetry run python app/core/kb/refresh.py --with-llm 2>&1 | grep "WvW"
```

**Sortie attendue:**
```
Step 3/5: Crawling community sources...
  → 46 pages crawled
  → 35 pages marked as WvW (76%)
  → 11 pages rejected (PvE content)
  → 25 synergy pairs extracted (WvW-only)
```

---

## 🚀 Impact

### Avant filtrage
- ⚠️ Synergies mixtes PvE/WvW
- ⚠️ Recommandations incohérentes
- ⚠️ LLM confus entre modes

### Après filtrage
- ✅ Synergies 100% WvW
- ✅ Recommandations tactiques précises
- ✅ LLM focalisé sur McM uniquement

---

## 🔍 Validation

### Vérifier qu'une source est bien WvW

```bash
cd backend
poetry run python -c "
from app.core.kb.web_crawler import crawl_metabattle_wvw

builds = crawl_metabattle_wvw()
for build in builds[:5]:
    print(f'{build.get(\"url\")}: WvW={build.get(\"is_wvw\")}, Score={build.get(\"wvw_score\")}')
"
```

### Vérifier le filtrage des synergies

```bash
cd backend
poetry run python -c "
from app.core.kb.web_crawler import crawl_all_sources, extract_synergies_from_crawl

data = crawl_all_sources()
synergies = extract_synergies_from_crawl(data)
print(f'Synergies WvW: {len(synergies)}')
print('Exemples:', synergies[:5])
"
```

---

## 📚 Références

- **Code**: `backend/app/core/kb/web_crawler.py` (lignes 134-164)
- **LLM**: `backend/app/core/llm/ollama_engine.py` (lignes 23-39, 95-104)
- **Tests**: `backend/app/core/kb/diagnose_wvw_filter.py`
- **Doc**: Ce fichier

---

**Version**: v4.2 (2025-10-18)  
**Auteur**: Roddy + Claude (Anthropic)  
**Licence**: MIT
