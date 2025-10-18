# 🤖 AI Meta Adaptive System — GW2_WvWBuilder v4.3

**Système d'intelligence artificielle adaptative** pour ajustement automatique des poids et synergies basé sur les patch notes Guild Wars 2.

---

## 🎯 Vision

Le système v4.3 transforme GW2_WvWBuilder en un **outil autonome et évolutif** capable de :
- 📰 **Surveiller** automatiquement les patch notes GW2
- 🧠 **Analyser** les changements d'équilibrage avec Mistral AI
- ⚖️ **Ajuster** dynamiquement les poids des spécialisations
- 🔗 **Recalculer** la matrice de synergies
- 📈 **Tracker** l'évolution du méta dans le temps

**Résultat** : Un optimiseur qui s'adapte automatiquement aux patchs ArenaNet sans intervention manuelle.

---

## 📦 Architecture

### Modules

```
backend/app/ai/
├── __init__.py                  # Module exports
├── patch_monitor.py             # Surveillance patch notes
├── meta_analyzer.py             # Analyse LLM des changements
├── meta_weights_updater.py      # Gestion des poids dynamiques
└── adaptive_meta_runner.py      # Orchestrateur principal (CLI)

backend/app/api/api_v1/endpoints/
└── meta_evolution.py            # API REST pour frontend

backend/app/var/
├── meta_weights.json            # Poids actuels des specs
├── meta_history.json            # Historique complet des ajustements
└── synergy_matrix.json          # Matrice de synergies dynamique
```

---

## 🌐 1. Patch Monitor

**Fichier** : `backend/app/ai/patch_monitor.py`

### Fonctionnalités

- **Surveillance multi-sources** :
  - GW2 Wiki (Game Updates, Balance Updates)
  - Forum officiel GW2 (Release Notes)
  - Reddit r/Guildwars2 (discussions patch)

- **Détection automatique** :
  - Nerfs : `reduced|decreased|removed|nerfed|lowered|weakened`
  - Buffs : `increased|improved|buffed|enhanced|strengthened`
  - Reworks : `reworked|changed|updated|adjusted|modified`

- **Extraction intelligente** :
  - Spécialisation affectée
  - Type de changement (nerf/buff/rework)
  - Magnitude (ex: "15%", "2 seconds")
  - Impact textuel (context)

### Exemple de sortie

```json
{
  "date": "2025-10-18",
  "spec": "Firebrand",
  "change_type": "nerf",
  "impact": "Quickness duration reduced by 15% on tome skills",
  "magnitude": "15%",
  "source": "gw2wiki"
}
```

### Utilisation

```python
from app.ai.patch_monitor import monitor_all_sources, filter_recent_changes

# Surveiller toutes les sources
all_changes = monitor_all_sources()

# Filtrer sur les 30 derniers jours
recent = filter_recent_changes(all_changes, days=30)
```

---

## 🧠 2. Meta Analyzer

**Fichier** : `backend/app/ai/meta_analyzer.py`

### Analyse LLM (Mistral)

Le système utilise **Mistral 7B** pour analyser l'impact des changements :

**Prompt** :
```
You are a Guild Wars 2 World vs World (WvW) meta analyst.
Analyze this balance change:

Specialization: Firebrand
Change Type: nerf
Details: Quickness duration reduced by 15% on tome skills
Magnitude: 15%

Provide a JSON response with:
1. weight_delta: float between -0.3 and +0.3 (how much to adjust spec weight)
2. synergy_impact: 'low', 'medium', or 'high'
3. affected_roles: list of affected WvW roles
4. reasoning: brief explanation (2-3 sentences)
```

**Réponse LLM** :
```json
{
  "weight_delta": -0.15,
  "synergy_impact": "medium",
  "affected_roles": ["support"],
  "reasoning": "Quickness nerf significantly reduces Firebrand's support value in zerg play. This affects synergy with power DPS specs that rely on quickness uptime."
}
```

### Fallback Heuristique

Si le LLM est indisponible :
- **Nerf** : weight_delta = -0.10
- **Buff** : weight_delta = +0.10
- **Rework** : weight_delta = 0.0 (neutral)

### Recalcul des Synergies

```python
def recalculate_synergies(analyses, current_synergies, llm_engine):
    # Détecte specs avec changements high/medium impact
    # Demande au LLM quelles synergies ajuster
    # Applique les nouveaux scores
    # Retourne matrice mise à jour
```

---

## ⚖️ 3. Meta Weights Updater

**Fichier** : `backend/app/ai/meta_weights_updater.py`

### Classe MetaWeightsUpdater

```python
updater = MetaWeightsUpdater(data_dir="app/var")

# Appliquer des ajustements
updated_weights = updater.apply_weight_adjustments(analyses)

# Mettre à jour les synergies
updater.apply_synergy_updates(new_synergies)

# Obtenir le poids actuel
weight = updater.get_weight("Firebrand")  # → 0.85

# Rollback à un timestamp
updater.rollback_to_timestamp("2025-10-17T10:00:00")

# Reset à 1.0
updater.reset_to_defaults()
```

### Persistence

**`meta_weights.json`** :
```json
{
  "firebrand": 0.85,
  "scrapper": 1.10,
  "herald": 1.00,
  ...
}
```

**`meta_history.json`** :
```json
[
  {
    "timestamp": "2025-10-18T10:30:00",
    "adjustments": [
      {
        "spec": "firebrand",
        "old_weight": 1.00,
        "new_weight": 0.85,
        "delta": -0.15,
        "change_type": "nerf",
        "reasoning": "Quickness nerf reduces support value"
      }
    ],
    "source": "patch_analysis"
  }
]
```

**`synergy_matrix.json`** :
```json
{
  "firebrand-scrapper": 0.90,
  "firebrand-herald": 0.85,
  "scrapper-tempest": 0.88,
  ...
}
```

### Contraintes

- **Poids clampés** : [0.1, 2.0] pour stabilité
- **Historique complet** : Toutes modifications tracées
- **Rollback sûr** : Retour à n'importe quel timestamp

---

## 🔄 4. Adaptive Meta Runner

**Fichier** : `backend/app/ai/adaptive_meta_runner.py`

### CLI Script

```bash
cd backend
poetry run python app/ai/adaptive_meta_runner.py [--with-llm] [--dry-run]
```

**Options** :
- `--with-llm` : Active analyse Mistral (sinon heuristique)
- `--dry-run` : Mode test sans sauvegarde

### Cycle complet

```
Step 1/4: Monitoring patch notes from all sources...
  → 12 changes detected (5 recent)

Step 2/4: Analyzing balance changes...
  → LLM engine (Mistral) activated
  → Firebrand: nerf → weight Δ=-0.15
  → Scrapper: buff → weight Δ=+0.10

Step 3/4: Updating specialization weights...
  → Weights updated: 27 specs

Step 4/4: Recalculating synergy matrix...
  → Synergies updated: 35 pairs

Adaptive Meta System Complete
  Changes detected: 5
  Analyses generated: 5
  Weights adjusted: 2
  Synergies updated: 35
```

### Cron Setup (recommandé : 12h)

```bash
# Ajouter au crontab
crontab -e

# Exécuter tous les jours à 3h et 15h
0 3,15 * * * cd /home/user/GW2_WvWbuilder/backend && poetry run python app/ai/adaptive_meta_runner.py --with-llm >> /var/log/gw2_adaptive_meta.log 2>&1
```

---

## 🌐 5. Meta Evolution API

**Fichier** : `backend/app/api/api_v1/endpoints/meta_evolution.py`

### Endpoints

#### GET `/api/v1/meta/weights`

Obtenir les poids actuels de toutes les specs.

**Réponse** :
```json
[
  {"spec": "scrapper", "weight": 1.10},
  {"spec": "firebrand", "weight": 0.85},
  ...
]
```

#### GET `/api/v1/meta/weights/{spec}`

Poids d'une spec spécifique.

**Exemple** : `/api/v1/meta/weights/firebrand`

#### GET `/api/v1/meta/synergies?min_score=0.7&limit=20`

Matrice de synergies filtrée.

**Réponse** :
```json
[
  {"spec1": "firebrand", "spec2": "scrapper", "score": 0.90},
  {"spec1": "herald", "spec2": "tempest", "score": 0.85},
  ...
]
```

#### GET `/api/v1/meta/history?limit=50`

Historique des ajustements.

**Réponse** :
```json
[
  {
    "timestamp": "2025-10-18T10:30:00",
    "adjustments": [...],
    "source": "patch_analysis"
  }
]
```

#### GET `/api/v1/meta/stats`

Statistiques du méta.

**Réponse** :
```json
{
  "total_specs": 27,
  "total_synergies": 45,
  "history_entries": 12,
  "last_update": "2025-10-18T10:30:00",
  "avg_weight": 1.02,
  "top_specs": [...],
  "bottom_specs": [...]
}
```

#### GET `/api/v1/meta/changes/recent?days=30`

Patch changes récents.

#### POST `/api/v1/meta/scan`

Déclencheur manuel du scan (développement).

```json
{
  "with_llm": true
}
```

#### POST `/api/v1/meta/reset`

Reset tous les poids à 1.0.

#### POST `/api/v1/meta/rollback/{timestamp}`

Rollback à un timestamp spécifique.

---

## 📈 6. Frontend Integration

### Dashboard "Meta Evolution"

**Composant recommandé** : `frontend/src/pages/MetaEvolutionPage.tsx`

**Fonctionnalités** :
- **Graphe temporel** : Évolution des poids dans le temps
- **Heatmap synergies** : Matrice visuelle des synergies
- **Badges changements** : 📉 nerf / 📈 buff sur specs récentes
- **Historique** : Timeline des ajustements
- **Top/Bottom specs** : Classement par poids

**Exemple d'intégration** :
```typescript
// src/api/metaEvolution.ts
export async function getWeights() {
  const response = await fetch('/api/v1/meta/weights');
  return response.json();
}

export async function getHistory(limit = 50) {
  const response = await fetch(`/api/v1/meta/history?limit=${limit}`);
  return response.json();
}

// MetaEvolutionPage.tsx
const { data: weights } = useQuery('meta-weights', getWeights);
const { data: history } = useQuery('meta-history', () => getHistory(100));

<LineChart
  data={history.map(h => ({
    timestamp: h.timestamp,
    ...h.adjustments.reduce((acc, adj) => ({
      ...acc,
      [adj.spec]: adj.new_weight
    }), {})
  }))}
/>
```

---

## 🧪 Tests

### Test manuel

```bash
cd backend

# Dry-run (pas de sauvegarde)
poetry run python app/ai/adaptive_meta_runner.py --with-llm --dry-run

# Vérifier les poids
cat app/var/meta_weights.json | jq '.firebrand'

# Vérifier l'historique
cat app/var/meta_history.json | jq '.[-1]'

# Test API
curl http://localhost:8000/api/v1/meta/stats | jq
```

### Tests unitaires (à créer)

```bash
cd backend
poetry run pytest tests/test_patch_monitor.py -v
poetry run pytest tests/test_meta_analyzer.py -v
poetry run pytest tests/test_meta_weights_updater.py -v
```

---

## ⚙️ Configuration

### Variables d'environnement

```bash
# .env
LLM_ENGINE=ollama
LLM_MODEL=mistral:7b
LLM_ENDPOINT=http://localhost:11434

# Optionnel
ADAPTIVE_META_SCAN_INTERVAL=12h  # Pour cron
ADAPTIVE_META_RECENT_DAYS=30     # Filtre changements récents
```

---

## 📊 Exemples de Scénarios

### Scénario 1 : Nerf Firebrand

**Patch note détecté** :
> "Firebrand: Reduced quickness duration by 15% on all tome skills"

**Analyse LLM** :
- weight_delta: -0.15
- synergy_impact: medium
- affected_roles: [support]
- reasoning: "Significantly impacts zerg support role"

**Ajustement automatique** :
- Firebrand: 1.00 → 0.85
- Synergy Firebrand-Scrapper: 0.95 → 0.90
- Synergy Firebrand-Herald: 0.90 → 0.85

**Impact optimizer** :
- Moins de Firebrands recommandés dans compositions
- Poids vers autres supports (Scrapper, Herald)

### Scénario 2 : Buff Mechanist

**Patch note détecté** :
> "Mechanist: Increased barrier output by 20%"

**Analyse LLM** :
- weight_delta: +0.12
- synergy_impact: low
- affected_roles: [support, sustain]
- reasoning: "Improves squad sustain in prolonged fights"

**Ajustement automatique** :
- Mechanist: 1.00 → 1.12

---

## 🔐 Sécurité et Fiabilité

### Rate Limiting

- 1 seconde entre requêtes aux sources externes
- Timeout 15s par page
- Retry logic avec backoff exponentiel

### Validation

- Poids clampés [0.1, 2.0]
- Synergies [0.0, 1.0]
- Rollback sûr via timestamps

### Graceful Degradation

- LLM indisponible → Fallback heuristique
- Source externe down → Skip avec log
- Parse error → Continue avec autres sources

---

## 🚀 Prochaines Étapes

### Court terme
- [ ] Tests unitaires complets
- [ ] Frontend dashboard Meta Evolution
- [ ] Monitoring Prometheus (scan success/failure)
- [ ] Webhook Discord pour notifications

### Long terme
- [ ] ML model pour prédiction de méta
- [ ] Analyse historique de méta shifts
- [ ] API publique pour communauté
- [ ] Integration avec simulateur de combat

---

**Version** : v4.3.0 (2025-10-18)  
**Auteur** : Roddy + Claude (Anthropic)  
**Licence** : MIT
