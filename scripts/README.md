# 📁 Scripts Infrastructure - GW2 WvW Builder

Ce dossier contient tous les scripts d'infrastructure production.

---

## 📋 Structure

```
scripts/
├── backup_database.sh          # Backup automatique DB (weekly)
├── monitor_logs.sh             # Monitoring logs temps réel
├── setup_infrastructure.sh     # Installation infrastructure complète
├── install_cron.sh             # Installation cron job backup
├── deploy_production_final.sh  # Déploiement production one-shot
├── systemd/
│   └── gw2-backend.service    # Service systemd backend
├── nginx/
│   └── gw2-wvwbuilder.conf    # Configuration Nginx reverse proxy
└── load_testing/
    └── load_test.py            # Tests de charge API
```

---

## 🛠️ Scripts Principaux

### 1. backup_database.sh

**Purpose:** Backup automatique hebdomadaire de la base de données

**Usage:**
```bash
# Manuel
./backup_database.sh

# Automatique via cron (Dimanche 2:00 AM)
# Installé via install_cron.sh
```

**Fonctionnalités:**
- ✅ Backup SQLite avec vérification intégrité
- ✅ Écrase l'ancien backup (1 seul fichier)
- ✅ Logs détaillés
- ✅ Cleanup logs anciens (30 jours)

**Output:**
- Backup: `backups/gw2_wvwbuilder.db.backup`
- Logs: `backups/backup.log`

---

### 2. monitor_logs.sh

**Purpose:** Monitoring logs backend en temps réel avec colorisation

**Usage:**
```bash
# Tous les logs
./monitor_logs.sh

# Seulement erreurs
./monitor_logs.sh -e

# Seulement warnings
./monitor_logs.sh -w

# Dernières N lignes
./monitor_logs.sh -n 100

# Nettoyer logs anciens
./monitor_logs.sh -c
```

**Fonctionnalités:**
- ✅ Colorisation automatique (ERROR=rouge, INFO=vert, etc.)
- ✅ Filtrage par niveau (ERROR, WARNING, INFO)
- ✅ Follow mode (-f)
- ✅ Tail mode (-n)

**Aliases:**
```bash
gw2-logs          # Tous logs
gw2-logs-errors   # Erreurs seulement
```

---

### 3. setup_infrastructure.sh

**Purpose:** Installation complète infrastructure production

**Usage:**
```bash
# Installation utilisateur (backup, monitoring)
./setup_infrastructure.sh

# Installation système (systemd, nginx) - requires sudo
sudo ./setup_infrastructure.sh --system
```

**Actions:**
1. ✅ Configure backup script
2. ✅ Installe cron job
3. ⚙️ Installe systemd service (si --system)
4. ⚙️ Configure Nginx (si --system)
5. ⚙️ Setup log rotation (si --system)
6. ✅ Ajoute aliases monitoring

---

### 4. install_cron.sh

**Purpose:** Installation cron job pour backup hebdomadaire

**Usage:**
```bash
./install_cron.sh
```

**Cron Schedule:**
```cron
0 2 * * 0 /path/to/backup_database.sh >> /path/to/backups/cron.log 2>&1
```

**Vérification:**
```bash
crontab -l | grep backup_database
```

---

### 5. deploy_production_final.sh

**Purpose:** Déploiement production one-shot complet

**Usage:**
```bash
./deploy_production_final.sh
```

**Actions:**
1. ✅ Pre-deployment checks (git, poetry, npm)
2. ✅ Stop services (8000, 5173)
3. ✅ Install dependencies
4. ✅ Database migrations
5. ✅ Build frontend
6. ✅ Start backend
7. ✅ Health check
8. ✅ Seed test user

**Output:**
- Backend PID: `backend.pid`
- Logs: `deployment_YYYYMMDD_HHMMSS.log`
- Info: `deployment_info.txt`

---

## 📂 Sous-Dossiers

### systemd/

**Fichier:** `gw2-backend.service`

**Installation:**
```bash
sudo cp systemd/gw2-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gw2-backend
sudo systemctl start gw2-backend
```

**Commandes:**
```bash
systemctl status gw2-backend
sudo systemctl restart gw2-backend
sudo journalctl -u gw2-backend -f
```

---

### nginx/

**Fichier:** `gw2-wvwbuilder.conf`

**Installation:**
```bash
sudo cp nginx/gw2-wvwbuilder.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/gw2-wvwbuilder.conf /etc/nginx/sites-enabled/

# ⚠️ IMPORTANT: Edit file and change domain name!
sudo nano /etc/nginx/sites-available/gw2-wvwbuilder.conf

sudo nginx -t
sudo systemctl reload nginx
```

**Configuration:**
- HTTP → HTTPS redirect
- Reverse proxy backend (127.0.0.1:8000)
- Static files frontend (dist/)
- SSL/TLS avec Let's Encrypt
- Security headers
- Gzip compression

---

### load_testing/

**Fichier:** `load_test.py`

**Installation:**
```bash
pip install httpx rich
```

**Usage:**
```bash
cd load_testing
python load_test.py
```

**Tests:**
- Health check (100 req, 20 concurrent)
- Dashboard stats (50 req, 10 concurrent)
- Recent activities (50 req, 10 concurrent)
- User profile (50 req, 10 concurrent)

**Métriques:**
- Success rate
- Avg/Min/Max/P95 response time
- Requests per second

---

## 🔧 Configuration

### Variables Environnement

```bash
# Backend
PROJECT_ROOT="/home/roddy/GW2_WvWbuilder"
DB_PATH="$PROJECT_ROOT/backend/gw2_wvwbuilder.db"
BACKUP_DIR="$PROJECT_ROOT/backups"
LOG_FILE="$PROJECT_ROOT/backend.log"
```

### Permissions

```bash
# Rendre tous scripts exécutables
chmod +x scripts/*.sh
chmod +x scripts/load_testing/*.py
```

---

## 📊 Logs

### Locations

| Script | Log Location |
|--------|--------------|
| backup_database.sh | `backups/backup.log` |
| Cron backup | `backups/cron.log` |
| deploy_production_final.sh | `deployment_YYYYMMDD_HHMMSS.log` |
| Backend service | `backend.log` |

### Nettoyage

```bash
# Nettoyer logs >7 jours
./monitor_logs.sh -c

# Nettoyer manuellement
find . -name "*.log" -mtime +7 -delete
```

---

## ✅ Checklist Utilisation

### Première Installation

- [x] Rendre scripts exécutables: `chmod +x scripts/*.sh`
- [x] Installer cron: `./install_cron.sh`
- [x] Ajouter aliases: Editer `~/.bashrc`
- [x] Test backup: `./backup_database.sh`
- [x] Test monitoring: `./monitor_logs.sh -n 10`

### Quotidien

- [ ] Check logs: `gw2-logs -e`
- [ ] Check backend: `systemctl status gw2-backend`

### Hebdomadaire

- [ ] Vérifier backup: `cat backups/backup.log`
- [ ] Run load test: `python load_testing/load_test.py`

### Mensuel

- [ ] Update dependencies
- [ ] Security audit
- [ ] Review logs size

---

## 🚨 Troubleshooting

### Script Permission Denied

```bash
chmod +x scripts/<script_name>.sh
```

### Cron Not Working

```bash
# Vérifier cron installé
which crontab

# Installer cron
sudo apt install cron

# Vérifier cron job
crontab -l
```

### Backup Fails

```bash
# Vérifier DB existe
ls -lh backend/gw2_wvwbuilder.db

# Vérifier permissions
chmod 644 backend/gw2_wvwbuilder.db

# Run avec debug
bash -x scripts/backup_database.sh
```

### Monitoring No Output

```bash
# Vérifier log file existe
ls -lh backend.log

# Créer si manquant
touch backend.log

# Permissions
chmod 644 backend.log
```

---

## 📖 Documentation

Pour plus d'informations:
- **INFRASTRUCTURE.md** - Documentation complète infrastructure
- **QUICK_START_INFRASTRUCTURE.md** - Guide démarrage rapide
- **DEPLOYMENT_FINAL_REPORT.md** - Rapport déploiement

---

**Maintenu par:** DevOps Team  
**Version:** 1.0.0  
**Date:** 15 octobre 2025
