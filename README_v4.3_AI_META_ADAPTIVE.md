# 🤖 README v4.3 — AI Meta Adaptive System

**GW2_WvWBuilder** Version 4.3.0 (2025-10-18)

---

## 🎯 Qu'est-ce que v4.3 ?

Un **système d'IA autonome** qui surveille les patch notes Guild Wars 2 et **ajuste automatiquement** :
- ⚖️ Les **poids** des spécialisations (Firebrand, Scrapper, etc.)
- 🔗 La **matrice de synergies** entre specs
- 📈 L'**historique** complet des changements de méta

**Résultat** : L'optimiseur s'adapte automatiquement aux patchs ArenaNet sans intervention manuelle.

---

## ✨ Nouveautés

### 1. Surveillance Automatique des Patch Notes

Le système crawle automatiquement :
- 📰 **GW2 Wiki** (Game Updates, Balance Updates)
- 🗣️ **Forum officiel** (Release Notes)
- 🔥 **Reddit** r/Guildwars2 (discussions)

Et détecte :
- 📉 **Nerfs** : `reduced|decreased|removed|nerfed`
- 📈 **Buffs** : `increased|improved|buffed|enhanced`
- 🔄 **Reworks** : `reworked|changed|updated|adjusted`

### 2. Analyse Intelligente avec Mistral AI

Chaque changement est analysé par **Mistral 7B** :
```
Input: "Firebrand quickness duration reduced by 15%"

LLM Output:
{
  "weight_delta": -0.15,
  "synergy_impact": "medium",
  "affected_roles": ["support"],
  "reasoning": "Reduces support value in zerg play"
}
```

### 3. Ajustement Automatique des Poids

Le système ajuste les poids dynamiquement :
```
Firebrand: 1.00 → 0.85 (après nerf)
Mechanist: 1.00 → 1.12 (après buff)
```

Les poids sont persistés dans `backend/app/var/meta_weights.json`

### 4. API REST Complète

8 nouveaux endpoints pour le frontend :
```bash
GET  /api/v1/meta/weights           # Poids actuels
GET  /api/v1/meta/synergies         # Matrice synergies
GET  /api/v1/meta/history           # Historique
GET  /api/v1/meta/stats             # Statistiques
GET  /api/v1/meta/changes/recent    # Patch notes récents
POST /api/v1/meta/scan              # Trigger manuel
POST /api/v1/meta/reset             # Reset à 1.0
POST /api/v1/meta/rollback/{ts}     # Rollback
```

---

## 🚀 Quick Start

### 1. Tester le système (dry-run)

```bash
cd backend
poetry run python app/ai/adaptive_meta_runner.py --with-llm --dry-run
```

**Sortie attendue** :
```
======================================================================
Adaptive Meta System v4.3
======================================================================
Step 1/4: Monitoring patch notes from all sources...
  → 5 changes detected

Step 2/4: Analyzing balance changes...
  → LLM engine (Mistral) activated
  → Firebrand: nerf → weight Δ=-0.15
  → Scrapper: buff → weight Δ=+0.10

Step 3/4: Updating specialization weights...
  → DRY RUN: No changes will be saved

Step 4/4: Recalculating synergy matrix...
  → DRY RUN: Synergies not saved

======================================================================
Adaptive Meta System Complete
======================================================================
Changes detected: 5
Analyses generated: 5
Weights adjusted: 2 (dry-run)
```

### 2. Exécution réelle (sauvegarde)

```bash
cd backend
poetry run python app/ai/adaptive_meta_runner.py --with-llm
```

Les fichiers sont créés :
- `backend/app/var/meta_weights.json`
- `backend/app/var/meta_history.json`
- `backend/app/var/synergy_matrix.json`

### 3. Consulter les poids

```bash
cat backend/app/var/meta_weights.json | jq
```

**Sortie** :
```json
{
  "firebrand": 0.85,
  "scrapper": 1.10,
  "herald": 1.00,
  "tempest": 1.05,
  ...
}
```

### 4. Tester l'API

```bash
# Démarrer le backend
cd backend
poetry run uvicorn app.main:app --reload

# Tester les endpoints
curl http://localhost:8000/api/v1/meta/stats | jq
curl http://localhost:8000/api/v1/meta/weights | jq
curl http://localhost:8000/api/v1/meta/history?limit=10 | jq
```

---

## 📅 Automatisation (Cron)

### Setup Cron (tous les 12h)

```bash
# Éditer crontab
crontab -e

# Ajouter cette ligne (3h et 15h chaque jour)
0 3,15 * * * cd /home/user/GW2_WvWbuilder/backend && poetry run python app/ai/adaptive_meta_runner.py --with-llm >> /var/log/gw2_adaptive_meta.log 2>&1
```

**Résultat** : Le système scan automatiquement les patch notes 2 fois par jour.

---

## 📊 Visualisation (Frontend à implémenter)

### Dashboard recommandé

**Composant** : `frontend/src/pages/MetaEvolutionPage.tsx`

**Fonctionnalités** :
- 📈 **Graphe temporel** : Évolution des poids dans le temps
- 🔥 **Heatmap** : Matrice de synergies visuelle
- 🏷️ **Badges** : 📉 nerf / 📈 buff sur specs récentes
- 📜 **Timeline** : Historique des ajustements
- 🏆 **Classement** : Top/Bottom specs par poids

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
import { useQuery } from '@tanstack/react-query';
import { LineChart } from 'recharts';

export function MetaEvolutionPage() {
  const { data: weights } = useQuery(['meta-weights'], getWeights);
  const { data: history } = useQuery(['meta-history'], () => getHistory(100));

  return (
    <div>
      <h1>Meta Evolution 🤖</h1>
      
      {/* Graphe évolution */}
      <LineChart
        data={history.map(h => ({
          timestamp: new Date(h.timestamp).toLocaleDateString(),
          ...h.adjustments.reduce((acc, adj) => ({
            ...acc,
            [adj.spec]: adj.new_weight
          }), {})
        }))}
        width={800}
        height={400}
      />
      
      {/* Liste poids actuels */}
      <div>
        {weights.map(w => (
          <div key={w.spec}>
            {w.spec}: {w.weight.toFixed(2)}
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 🧪 Tests

### Test patch monitor

```bash
cd backend
poetry run python -c "
from app.ai.patch_monitor import monitor_all_sources
changes = monitor_all_sources()
print(f'Changes: {len(changes)}')
for c in changes[:3]:
    print(f'  {c[\"spec\"]}: {c[\"change_type\"]}')
"
```

### Test meta analyzer

```bash
poetry run python -c "
from app.ai.meta_analyzer import analyze_all_changes
from app.ai.patch_monitor import monitor_all_sources

changes = monitor_all_sources()
analyses = analyze_all_changes(changes[:5], llm_engine=None)
for a in analyses:
    print(f'{a[\"spec\"]}: Δ={a[\"weight_delta\"]}')
"
```

### Test weights updater

```bash
poetry run python -c "
from app.ai.meta_weights_updater import MetaWeightsUpdater

updater = MetaWeightsUpdater()
print(f'Firebrand weight: {updater.get_weight(\"firebrand\")}')
print(f'Total specs: {len(updater.get_weights())}')
print(f'History entries: {len(updater.get_history())}')
"
```

---

## 📚 Documentation

- **Guide complet** : `docs/AI_META_ADAPTIVE_SYSTEM_v4.3.md`
- **Changelog** : `CHANGELOG.md` (section v4.3.0)
- **API Swagger** : http://localhost:8000/docs (après démarrage backend)

---

## 🔧 Architecture

```
┌─────────────────────────────────────────────────────────┐
│               AI Meta Adaptive System v4.3              │
└─────────────────────────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
    ┌──────▼──────┐ ┌─────▼─────┐ ┌──────▼──────┐
    │   Patch     │ │   Meta    │ │   Weights   │
    │  Monitor    │ │  Analyzer │ │   Updater   │
    │ (GW2 Wiki,  │ │ (Mistral  │ │  (Storage   │
    │  Forum,     │ │   LLM +   │ │   + History)│
    │  Reddit)    │ │ Heuristic)│ │             │
    └─────────────┘ └───────────┘ └─────────────┘
           │               │               │
           └───────────────┼───────────────┘
                           │
                    ┌──────▼──────┐
                    │   API REST  │
                    │  (FastAPI)  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Frontend   │
                    │ (Dashboard) │
                    └─────────────┘
```

---

## 🎯 Scénarios d'Utilisation

### Scénario 1 : Nerf Firebrand

**Patch note détecté** :
> "Firebrand: Reduced quickness duration by 15% on all tome skills"

**Ce qui se passe** :
1. `patch_monitor` détecte le changement
2. `meta_analyzer` (Mistral) analyse :
   ```
   weight_delta: -0.15
   synergy_impact: medium
   reasoning: "Significantly impacts zerg support role"
   ```
3. `meta_weights_updater` ajuste :
   - Firebrand: 1.00 → 0.85
   - Synergy FB-Scrapper: 0.95 → 0.90
4. **Optimizer** recommande désormais moins de Firebrands

### Scénario 2 : Buff Mechanist

**Patch note détecté** :
> "Mechanist: Increased barrier output by 20%"

**Ce qui se passe** :
1. Détection automatique
2. Analyse LLM : `weight_delta: +0.12`
3. Mechanist: 1.00 → 1.12
4. **Optimizer** booste Mechanist dans compositions

---

## ⚠️ Important

### Dépendances

Le système nécessite :
- ✅ Mistral (Ollama) pour analyse intelligente (optionnel, fallback heuristique)
- ✅ Accès internet pour crawl patch notes
- ✅ Python 3.10+
- ✅ FastAPI backend démarré

### Sécurité

- **Rate limiting** : 1s entre requêtes externes
- **Timeout** : 15s max par page
- **Validation** : Poids clampés [0.1, 2.0], synergies [0.0, 1.0]
- **Rollback** : Retour arrière sûr à n'importe quel timestamp
- **Graceful degradation** : Fonctionne même si LLM down ou sources unavailable

---

## 🚀 Prochaines Étapes

### Backend ✅
- [x] Patch monitor
- [x] Meta analyzer (LLM + heuristic)
- [x] Weights updater
- [x] API REST complète
- [x] Documentation

### Frontend ⏳
- [ ] Dashboard Meta Evolution
- [ ] Graphe temporel poids
- [ ] Heatmap synergies
- [ ] Timeline historique
- [ ] Badges nerf/buff

### Tests ⏳
- [ ] Unit tests (patch_monitor, meta_analyzer, meta_weights_updater)
- [ ] Integration tests (API)
- [ ] E2E tests (frontend)

### DevOps ⏳
- [ ] Monitoring Prometheus
- [ ] Webhook Discord notifications
- [ ] CI/CD intégration

---

## 📞 Support

**Questions ?** Consulter :
- `docs/AI_META_ADAPTIVE_SYSTEM_v4.3.md` (guide complet)
- `CHANGELOG.md` (détails v4.3)
- API Swagger : http://localhost:8000/docs

**Logs** :
```bash
# Logs du runner
tail -f /var/log/gw2_adaptive_meta.log

# Logs du backend
cd backend
poetry run uvicorn app.main:app --reload --log-level debug
```

---

**Version** : v4.3.0 (2025-10-18)  
**Auteur** : Roddy + Claude (Anthropic)  
**Licence** : MIT

---

🎉 **Félicitations !** Le système AI Meta Adaptive est maintenant opérationnel !

**Prochaine action recommandée** :
```bash
cd backend
poetry run python app/ai/adaptive_meta_runner.py --with-llm --dry-run
```
