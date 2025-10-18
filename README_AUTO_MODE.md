# 🎮 GW2_WvWBuilder v4.0 — IA Tactique McM Autonome

**Auto Mode (Soft-Only)** + **LLM Ollama/Mistral** pour compositions de squads optimales sans quotas durs.

---

## 🚀 Démarrage rapide

### 1. Lancer tout automatiquement

```bash
./start_all.sh
```

**Ce script lance:**
- ✅ Backend FastAPI (port 8000)
- ✅ Frontend React/Vite (port 5173)
- ✅ Ollama/Mistral 7B (si installé)

### 2. Accéder à l'application

- **Frontend**: http://localhost:5173
- **Optimize**: http://localhost:5173/optimize
- **API Docs**: http://localhost:8000/docs

### 3. Arrêter tout

```bash
./stop_all.sh
```

---

## 🧠 Philosophie Auto Mode (Soft-Only)

### ❌ Ce que l'IA ne fait PAS
- Pas de quotas durs par profession (ex: "8-12 Firebrands obligatoires")
- Pas de contraintes min/max rigides par spécialisation
- Pas de composition imposée

### ✅ Ce que l'IA fait
- **Saturation de boons** par groupe (caps utiles: quickness, stability, etc.)
- **Pénalités douces** pour doublons (groupe + global)
- **Récompense de diversité** par spécialisation unique
- **Bonus de synergies** tactiques (paires: Firebrand+Scrapper, Herald+Tempest, etc.)
- **Adaptation continue** via Base de Connaissances (KB) depuis API GW2

### 🎯 Résultat
Le solver propose **plusieurs solutions valides**, ajustées selon les pondérations configurables (sliders UI).

---

## 🔧 Configuration LLM (Ollama)

### Installation Ollama (optionnel)

```bash
# Installer Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Télécharger Mistral 7B
ollama pull mistral:7b
```

### Variables d'environnement

```bash
export LLM_ENGINE=ollama
export LLM_MODEL=mistral:7b
export LLM_ENDPOINT=http://localhost:11434
```

### Usage LLM

1. **Synergies adaptatives**: découverte automatique de combos optimaux
2. **Rapport IA**: analyse tactique riche ("Pourquoi cette compo ?")
3. **Fallback**: heuristiques par défaut si LLM indisponible

---

## 📊 Modes WvW disponibles

| Mode | Taille | Priorités | Cas d'usage |
|------|--------|-----------|-------------|
| **Zerg** | 25-50 | Stability, Quickness, Resistance | Batailles de masse, sièges |
| **Havoc** | 10-20 | Quickness, Stability, DPS | Harcèlement, objectifs secondaires |
| **Roaming** | 1-5 | DPS, Sustain, Mobility | Duels, petits groupes |
| **Defense** | 15-30 | Stability, Protection, Sustain | Défense de structures |
| **Gank** | 5-15 | Burst DPS, Quickness, Might | Embuscades, burst |

---

## 🎛️ Paramètres Soft-Only (sliders UI)

### Pénalités de doublons
- **`dup_penalty_group`** (0.0-1.0): pénalité par doublon dans un groupe
- **`dup_penalty_global`** (0.0-1.0): pénalité par doublon dans le squad

### Diversité
- **`diversity_reward`** (0.0-1.0): récompense par spécialisation unique

### Synergies
- **`synergy`** (0.0-1.0): poids des synergies tactiques

### Presets par mode

**Zerg** (défaut):
```json
{
  "quickness": 1.0,
  "stability": 1.0,
  "resistance": 0.95,
  "dup_penalty_group": 0.25,
  "diversity_reward": 0.04,
  "synergy": 0.06
}
```

**Havoc**:
```json
{
  "quickness": 1.0,
  "stability": 1.0,
  "dps": 0.8,
  "dup_penalty_group": 0.2,
  "diversity_reward": 0.05,
  "synergy": 0.05
}
```

**Roaming**:
```json
{
  "dps": 1.0,
  "sustain": 0.95,
  "quickness": 0.4,
  "dup_penalty_group": 0.3,
  "diversity_reward": 0.06,
  "synergy": 0.04
}
```

---

## 📦 Base de Connaissances (KB)

### Ingestion automatique

La KB se construit depuis:
- **API GW2 officielle**: professions, spécialisations, skills, traits, items
- **Wiki GW2**: priorités boons, rôles, notes par spé

### Refresh KB

```bash
# Manuel
cd backend
poetry run python -c "from app.core.kb.builder import refresh_kb; refresh_kb('wvw')"

# Automatique (planifié)
# → Tâche CRON hebdomadaire ou CI/CD post-patch
```

### Versioning

La KB est versionnée (`backend/app/var/kb.json`) pour détecter les changements post-patch.

---

## 🧪 Tests

### Backend

```bash
cd backend
poetry install
poetry run pytest tests/
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173/optimize
```

### E2E

```bash
# Lancer tout
./start_all.sh

# Tester l'endpoint optimize
curl -X POST http://localhost:8000/api/v1/optimize \
  -H "Content-Type: application/json" \
  -d @tests/fixtures/optimize_15players.json

# Arrêter
./stop_all.sh
```

---

## 📚 Documentation complète

- **Solver Design**: `docs/solver_design.md` (à créer)
- **Architecture**: `docs/architecture.md` (à créer)
- **LLM Integration**: `docs/llm_integration.md` (à créer)
- **KB Refresh**: `docs/kb_refresh.md` (à créer)

---

## 🐛 Dépannage

### Backend ne démarre pas

```bash
# Vérifier les logs
tail -f backend.log

# Vérifier le port
lsof -i :8000

# Nettoyer et relancer
./stop_all.sh
./start_all.sh
```

### Frontend ne démarre pas

```bash
# Vérifier les logs
tail -f frontend.log

# Réinstaller les dépendances
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Ollama ne répond pas

```bash
# Vérifier Ollama
ollama list

# Redémarrer Ollama
pkill ollama
ollama serve &

# Télécharger le modèle
ollama pull mistral:7b
```

### KB vide ou incomplète

```bash
# Forcer le refresh
cd backend
poetry run python -c "from app.core.kb.builder import refresh_kb; refresh_kb('wvw')"
```

---

## 🎯 Résultat attendu

Le solver propose des **compositions équilibrées et optimales** sans intervention humaine:

✅ **Diversité de spécialisations** (pas de 15 Firebrands)  
✅ **Couverture boons adaptée** au mode (Zerg: 95% quick, Roaming: 50% quick)  
✅ **Synergies tactiques** (Firebrand+Scrapper, Herald+Tempest, etc.)  
✅ **Adaptation post-patch** via refresh KB  
✅ **Explications IA riches** (LLM Ollama + Mistral)

**L'IA ne doit pas imposer de quotas, mais favoriser la diversité, la complémentarité et la robustesse.**

---

## 📈 Roadmap

- [x] Solver Auto (Soft-Only)
- [x] KB ingestion (GW2 API + Wiki)
- [x] LLM integration (Ollama + Mistral)
- [x] Services (presets, reporter)
- [ ] Frontend sliders + mode selector
- [ ] Heatmaps synergies + viz boons
- [ ] Tests (unit, property, integration, perf)
- [ ] Docs complètes
- [ ] CI/CD + refresh KB planifié

---

## 📞 Support

- **Issues**: https://github.com/Roddygithub/GW2_WvWbuilder/issues
- **Wiki**: https://github.com/Roddygithub/GW2_WvWbuilder/wiki

---

**Version**: v4.0 (2025-10-17)  
**License**: MIT  
**Auteur**: Roddy + Claude (Anthropic)
