# 🧬 GW2_WvWBuilder v4.1 — IA Évolutive

**Système d'apprentissage automatique périodique** pour enrichir continuellement la Base de Connaissances (KB) depuis les sources publiques Guild Wars 2.

---

## 🎯 Concept

L'IA Mistral (via Ollama) devient **vraiment intelligente** en :
1. **Ingérant** automatiquement les données GW2 (API officielle + Wiki + communauté)
2. **Analysant** les synergies, rôles et méta builds
3. **Enrichissant** la KB avec des relations vectorielles
4. **S'adaptant** aux patchs et évolutions de méta

---

## 🔄 Cycle d'apprentissage (24h)

```
┌─────────────────────────────────────────────────────────┐
│  3:00 AM — Auto-Refresh KB                              │
├─────────────────────────────────────────────────────────┤
│  1. Ingest GW2 API (skills, traits, professions)       │
│  2. Ingest GW2 Wiki (boons, roles, notes)              │
│  3. Crawl community sources (MetaBattle, Hardstuck...)  │
│  4. Enrich synergies via Mistral 7B (LLM)              │
│  5. Save updated KB → app/var/kb.json                   │
│  6. (Optional) Restart backend                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🌐 Sources d'apprentissage

### Officielles (ArenaNet)
- **API GW2**: https://api.guildwars2.com/v2/
  - `/skills`, `/traits`, `/professions`, `/specializations`, `/itemstats`
- **Wiki GW2**: https://wiki.guildwars2.com/
  - Pages professions, skills, builds WvW

### Communautaires
- **MetaBattle**: https://metabattle.com/wiki/Category:World_vs_World_builds
- **Hardstuck WvW**: https://hardstuck.gg/gw2/builds/?t=wvw (Filtre WvW)
- **Snow Crows WvW**: https://snowcrows.com/builds/wvw (Section WvW dédiée)
- **GW2 Mists**: https://gw2mists.com/builds (Builds WvW compétitifs)
- **Google Sheets WvW**: https://docs.google.com/spreadsheets/d/1wPCpLzT-wNbU4Zukvc0pG20UgSvxr8zzBJZEwI38HqU (Compositions communautaires)
- **Discretize**: https://discretize.eu/ (Fractals - non crawlé)
- **Reddit**: r/Guildwars2
- **Forum officiel**: https://en-forum.guildwars2.com/

---

## 🚀 Installation

### 1. Activer les variables d'environnement

Le fichier `.env` a été créé automatiquement avec :

```bash
LLM_ENGINE=ollama
LLM_MODEL=mistral:7b
LLM_ENDPOINT=http://localhost:11434
LLM_WEB_SOURCES=1
LLM_WEB_SOURCES_URLS=https://wiki.guildwars2.com,https://metabattle.com,https://hardstuck.gg/gw2/builds/?t=wvw,https://snowcrows.com/builds/wvw,https://gw2mists.com,https://docs.google.com/spreadsheets/d/1wPCpLzT-wNbU4Zukvc0pG20UgSvxr8zzBJZEwI38HqU
```

### 2. Installer la tâche cron (auto-refresh quotidien)

```bash
./setup_cron.sh
```

**Ce script:**
- ✅ Configure un cron job quotidien (3:00 AM)
- ✅ Lance `refresh.py --with-llm --auto`
- ✅ Logs dans `kb_refresh.log`

### 3. Tester le refresh manuellement

```bash
cd backend
poetry run python app/core/kb/refresh.py --with-llm
```

**Sortie attendue:**
```
============================================================
KB Refresh Cycle Started
============================================================
Step 1/5: Ingesting GW2 API data...
  → 500 skills
  → 500 traits
  → 27 specializations
Step 2/5: Ingesting GW2 Wiki data...
  → 5 mode priorities
  → 12 spec notes
Step 3/5: Crawling community sources...
  → 35 pages crawled
  → 18 synergy pairs extracted
Step 4/5: Building KB from aggregated data...
  → 12 build templates in KB
Step 5/5: Enriching synergies with LLM (Mistral)...
  → 24 LLM-enriched synergy pairs
Saving KB to disk...
  → KB saved to app/var/kb.json
============================================================
KB Refresh Cycle Complete
============================================================
```

### 4. Relancer le système avec les nouvelles données

```bash
./stop_all.sh
./start_all.sh
```

---

## 📊 Modules créés

### 1. **`backend/app/core/kb/web_crawler.py`**

**Fonctionnalités:**
- `fetch_page()`: récupère HTML avec User-Agent éducatif
- `extract_build_info()`: extrait professions, spés, boons, rôles, synergies
- `crawl_metabattle_wvw()`: crawl MetaBattle WvW builds (max 20)
- `crawl_hardstuck_wvw()`: crawl Hardstuck builds
- `crawl_gw2_wiki_professions()`: crawl pages professions Wiki
- `crawl_gw2mists()`: crawl GW2 Mists builds (max 15)
- `crawl_google_sheets_wvw()`: crawl Google Sheets WvW communautaire (HTML export)
- `crawl_all_sources()`: orchestrateur principal
- `extract_synergies_from_crawl()`: extrait paires de synergies

**Sources actives:**
- MetaBattle (20 builds max) - `/Category:World_vs_World_builds`
- Hardstuck WvW (filtre t=wvw) - `/gw2/builds/?t=wvw` ✨
- Snow Crows WvW (section dédiée) - `/builds/wvw` ✨
- GW2 Wiki (9 professions)
- GW2 Mists (15 builds max) - `/builds`
- Google Sheets WvW (compositions communautaires)

**Rate limiting:** 0.5s entre chaque page (respectueux)

### 2. **`backend/app/core/kb/refresh.py`**

**Script CLI pour refresh KB:**

```bash
python app/core/kb/refresh.py [--with-llm] [--auto]
```

**Options:**
- `--with-llm`: enrichit synergies via Mistral (Ollama)
- `--auto`: mode cron (logs + optionnel restart backend)

**Cycle complet:**
1. Ingest GW2 API
2. Ingest Wiki
3. Crawl web sources (si `LLM_WEB_SOURCES=1`)
4. Build KB
5. Enrich LLM (si `--with-llm`)
6. Save KB

### 3. **`setup_cron.sh`**

**Script d'installation cron:**
- Ajoute tâche quotidienne (3:00 AM)
- Logs dans `kb_refresh.log`
- Commande: `poetry run python app/core/kb/refresh.py --with-llm --auto`

### 4. **`.env` / `.env.example`**

**Configuration centralisée:**
- LLM (Ollama/Mistral)
- Web sources (URLs, enable/disable)
- Database, API, CORS, Logging

---

## 🧪 Tests

### Test manuel du crawler

```bash
cd backend
poetry run python -c "
from app.core.kb.web_crawler import crawl_all_sources
data = crawl_all_sources()
for source, pages in data.items():
    print(f'{source}: {len(pages)} pages')
print(f'Total: {sum(len(v) for v in data.values())} pages')
"
```

**Résultat attendu:**
```
metabattle: 20 pages
hardstuck: 1 pages
snowcrows: 1 pages
gw2wiki: 9 pages
gw2mists: 15 pages
google_sheets: 1 pages
Total: 47 pages
```

### Test manuel du refresh

```bash
cd backend
poetry run python app/core/kb/refresh.py --with-llm
```

### Vérifier le cron

```bash
crontab -l | grep GW2_WvWbuilder
```

### Voir les logs du refresh

```bash
tail -f kb_refresh.log
```

---

## 🔧 Configuration avancée

### Désactiver le web crawling

```bash
# Dans .env
LLM_WEB_SOURCES=0
```

### Changer la fréquence du cron

```bash
# Éditer le cron
crontab -e

# Exemples:
# Toutes les 6h: 0 */6 * * *
# Toutes les heures: 0 * * * *
# Hebdomadaire (dimanche 3h): 0 3 * * 0
```

### Ajouter des sources web

```bash
# Dans .env
LLM_WEB_SOURCES_URLS=https://wiki.guildwars2.com,https://metabattle.com,https://hardstuck.gg,https://gw2mists.com,https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID,https://your-custom-source.com
```

**Sources actuellement supportées:**
- Wiki GW2 (professions)
- MetaBattle (builds WvW)
- **Hardstuck WvW** (filtre `?t=wvw`) ✨
- **Snow Crows WvW** (section `/builds/wvw`) ✨
- **GW2 Mists** (builds compétitifs)
- **Google Sheets** (compositions communautaires)

### Changer le modèle LLM

```bash
# Dans .env
LLM_MODEL=mistral:latest
# ou
LLM_MODEL=llama2:13b
```

---

## 📈 Évolution de la KB

### Structure KB enrichie

```json
{
  "builds": [
    {
      "id": 200,
      "profession": "Guardian",
      "specialization": "Firebrand",
      "capability": {
        "quickness": 0.95,
        "stability": 0.85,
        "...": "..."
      }
    }
  ],
  "meta": {
    "mode": "wvw",
    "source": "gw2_api_ingestion",
    "web_synergies": [
      {"pair": ["firebrand", "scrapper"], "source": "web_crawl"}
    ],
    "llm_synergies": [
      {"pair": ["firebrand", "scrapper"], "score": 0.92, "source": "llm"}
    ]
  }
}
```

### Versioning

La KB est versionnée automatiquement :
- Timestamp de dernière mise à jour
- Hash des données sources
- Détection de changements post-patch

---

## 🐛 Dépannage

### Le cron ne se lance pas

```bash
# Vérifier le cron
crontab -l

# Vérifier les logs système
grep CRON /var/log/syslog

# Tester manuellement
cd backend && poetry run python app/core/kb/refresh.py --with-llm
```

### Le crawler échoue

```bash
# Vérifier la connectivité
curl -I https://metabattle.com

# Vérifier les logs
tail -f kb_refresh.log

# Tester le crawler isolément
cd backend
poetry run python -c "from app.core.kb.web_crawler import crawl_metabattle_wvw; print(crawl_metabattle_wvw())"
```

### Mistral ne répond pas

```bash
# Vérifier Ollama
ollama list
ollama ps

# Tester Mistral
ollama run mistral:7b "Test"

# Vérifier l'endpoint
curl http://localhost:11434/api/tags
```

### KB corrompue

```bash
# Backup de la KB
cp backend/app/var/kb.json backend/app/var/kb.json.backup

# Forcer un refresh complet
cd backend
poetry run python app/core/kb/refresh.py --with-llm

# Restaurer le backup si nécessaire
cp backend/app/var/kb.json.backup backend/app/var/kb.json
```

---

## 📊 Métriques d'apprentissage

### Indicateurs de qualité KB

- **Couverture**: % de spécialisations avec données complètes
- **Fraîcheur**: temps depuis dernier refresh
- **Synergies**: nombre de paires découvertes (web + LLM)
- **Précision**: validation contre méta connue

### Logs de progression

```bash
# Voir l'historique des refresh
tail -100 kb_refresh.log

# Compter les synergies
cd backend
poetry run python -c "
from app.core.kb.store import load_kb
kb = load_kb()
web = len(kb.meta.get('web_synergies', []))
llm = len(kb.meta.get('llm_synergies', []))
print(f'Web: {web}, LLM: {llm}, Total: {web+llm}')
"
```

---

## 🎯 Résultat attendu

Après quelques cycles (3-7 jours), l'IA aura :

✅ **Mappé** toutes les spécialisations WvW avec données complètes  
✅ **Découvert** 50-100 synergies tactiques (web + LLM)  
✅ **Adapté** les poids/targets selon les patchs récents  
✅ **Enrichi** les rapports IA avec contexte méta actuel  
✅ **Optimisé** les compositions sans intervention humaine

**L'IA devient autonome et s'améliore continuellement.**

---

## 📚 Ressources

- **Ollama**: https://ollama.com/
- **Mistral AI**: https://mistral.ai/
- **GW2 API**: https://wiki.guildwars2.com/wiki/API:Main
- **MetaBattle**: https://metabattle.com/
- **Hardstuck**: https://hardstuck.gg/

---

**Version**: v4.1 (2025-10-18)  
**License**: MIT  
**Auteur**: Roddy + Claude (Anthropic)
