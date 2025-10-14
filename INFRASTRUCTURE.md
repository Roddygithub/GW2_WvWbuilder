# 🏗️ Infrastructure Production - GW2 WvW Builder

**Version:** 1.0.0  
**Date:** 15 octobre 2025  
**Responsable:** DevOps Team

---

## 📋 Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture](#architecture)
3. [Backup Automatique](#backup-automatique)
4. [Monitoring](#monitoring)
5. [Service systemd](#service-systemd)
6. [Reverse Proxy Nginx](#reverse-proxy-nginx)
7. [SSL/HTTPS](#ssl-https)
8. [CI/CD Pipeline](#cicd-pipeline)
9. [Load Testing](#load-testing)
10. [Sécurité](#sécurité)
11. [Maintenance](#maintenance)
12. [Troubleshooting](#troubleshooting)

---

## 🎯 Vue d'ensemble

### Composants Infrastructure

| Composant | Description | Status |
|-----------|-------------|--------|
| **Backend** | FastAPI + Uvicorn (Python 3.11) | ✅ Production |
| **Frontend** | React + Vite (Node 20) | ✅ Production |
| **Database** | SQLite (gw2_wvwbuilder.db) | ✅ Production |
| **Reverse Proxy** | Nginx | ✅ Configured |
| **SSL** | Let's Encrypt | ⏳ À configurer |
| **Service Manager** | systemd | ✅ Configured |
| **Backup** | Cron weekly | ✅ Active |
| **Monitoring** | Logs + Scripts | ✅ Active |
| **CI/CD** | GitHub Actions | ✅ Configured |

---

## 🏛️ Architecture

### Architecture Production

```
                     Internet
                        |
                     [DNS]
                        |
                    [Nginx] :443 (HTTPS)
                        |
            +-----------+-----------+
            |                       |
    [Static Files]          [Backend API]
    /var/www/dist           127.0.0.1:8000
    (Frontend)              (FastAPI)
                                |
                           [Database]
                        SQLite (.db)
                                |
                          [Backups]
                     Weekly @ 2:00 AM
```

### Flux de Requêtes

```
Client → Nginx:443 (HTTPS)
  ├─→ / (Frontend) → Static files (dist/)
  └─→ /api/* → Backend proxy → FastAPI:8000 → Database
```

---

## 💾 Backup Automatique

### Configuration Backup

**Script:** `/scripts/backup_database.sh`  
**Fréquence:** Hebdomadaire (Dimanche 2:00 AM)  
**Stratégie:** 1 seul backup (écrase l'ancien)

### Fonctionnalités

- ✅ Backup automatique via cron
- ✅ Vérification intégrité (SQLite PRAGMA)
- ✅ Logs détaillés
- ✅ Écrasement ancien backup
- ✅ Cleanup logs anciens (30 jours)

### Usage

```bash
# Backup manuel
./scripts/backup_database.sh

# Vérifier cron
crontab -l | grep backup

# Voir logs backup
cat backups/backup.log

# Restaurer backup
cp backups/gw2_wvwbuilder.db.backup backend/gw2_wvwbuilder.db
```

### Cron Configuration

```cron
# Weekly backup - Every Sunday at 2:00 AM
0 2 * * 0 /home/roddy/GW2_WvWbuilder/scripts/backup_database.sh >> /home/roddy/GW2_WvWbuilder/backups/cron.log 2>&1
```

### Structure Backups

```
backups/
├── gw2_wvwbuilder.db.backup  # Latest backup (overwritten weekly)
├── backup.log                # Backup execution logs
└── cron.log                  # Cron execution logs
```

---

## 📊 Monitoring

### Scripts Monitoring

**Script principal:** `/scripts/monitor_logs.sh`

### Commandes Disponibles

```bash
# Monitoring temps réel
gw2-logs                    # Tous les logs colorés
gw2-logs -e                 # Seulement erreurs
gw2-logs -w                 # Seulement warnings
gw2-logs -i                 # Seulement info
gw2-logs -n 100             # Dernières 100 lignes

# Nettoyage logs
gw2-logs -c                 # Nettoyer logs >7 jours
```

### Colorisation Logs

| Type | Couleur |
|------|---------|
| ERROR/CRITICAL | 🔴 Rouge |
| WARNING | 🟡 Jaune |
| INFO | 🟢 Vert |
| DEBUG | 🔵 Cyan |
| HTTP 2xx | 🟢 Vert |
| HTTP 4xx/5xx | 🔴 Rouge |

### Logs Backend

**Location:** `/home/roddy/GW2_WvWbuilder/backend.log`

**Niveau:** INFO (aiosqlite optimisé)

**Rotation:** 14 jours (via logrotate)

### Commandes Monitoring

```bash
# Status service
gw2-status

# Logs systemd
sudo journalctl -u gw2-backend -f

# Logs nginx
sudo tail -f /var/log/nginx/gw2-builder-access.log
sudo tail -f /var/log/nginx/gw2-builder-error.log

# Process backend
ps aux | grep uvicorn

# Ports actifs
sudo lsof -i :8000
sudo lsof -i :443
```

---

## ⚙️ Service systemd

### Configuration Service

**Fichier:** `/etc/systemd/system/gw2-backend.service`

**Fonctionnalités:**
- ✅ Auto-restart en cas de crash
- ✅ Démarrage automatique au boot
- ✅ Limites ressources (1GB RAM, 200% CPU)
- ✅ Security hardening
- ✅ Logs intégrés

### Commandes systemd

```bash
# Démarrer service
sudo systemctl start gw2-backend

# Arrêter service
sudo systemctl stop gw2-backend

# Redémarrer service
sudo systemctl restart gw2-backend

# Recharger config
sudo systemctl daemon-reload

# Activer au boot
sudo systemctl enable gw2-backend

# Désactiver au boot
sudo systemctl disable gw2-backend

# Status service
systemctl status gw2-backend

# Logs temps réel
sudo journalctl -u gw2-backend -f

# Logs dernières 100 lignes
sudo journalctl -u gw2-backend -n 100
```

### Configuration Service

```ini
[Unit]
Description=GW2 WvW Builder Backend Service
After=network.target

[Service]
Type=simple
User=roddy
WorkingDirectory=/home/roddy/GW2_WvWbuilder/backend
ExecStart=/usr/bin/env poetry run uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2

# Auto-restart
Restart=always
RestartSec=10

# Resource limits
MemoryMax=1G
CPUQuota=200%

[Install]
WantedBy=multi-user.target
```

---

## 🌐 Reverse Proxy Nginx

### Configuration Nginx

**Fichier:** `/etc/nginx/sites-available/gw2-wvwbuilder.conf`

### Fonctionnalités

- ✅ HTTPS redirect (80 → 443)
- ✅ SSL/TLS configuration
- ✅ Security headers
- ✅ Gzip compression
- ✅ Static files caching
- ✅ Backend proxy
- ✅ WebSocket support

### Routes

| Route | Destination | Description |
|-------|-------------|-------------|
| `/` | Static files | Frontend SPA |
| `/api/*` | 127.0.0.1:8000 | Backend API |
| `/docs` | 127.0.0.1:8000/docs | Swagger UI |
| `/health` | 127.0.0.1:8000/api/v1/health | Health check |

### Commandes Nginx

```bash
# Tester configuration
sudo nginx -t

# Recharger configuration
sudo systemctl reload nginx

# Redémarrer Nginx
sudo systemctl restart nginx

# Status Nginx
systemctl status nginx

# Logs accès
sudo tail -f /var/log/nginx/gw2-builder-access.log

# Logs erreurs
sudo tail -f /var/log/nginx/gw2-builder-error.log
```

### Configuration Importante

**À modifier dans le fichier:**
```nginx
server_name gw2builder.example.com;  # ← CHANGER
ssl_certificate /etc/letsencrypt/live/gw2builder.example.com/fullchain.pem;  # ← CHANGER
ssl_certificate_key /etc/letsencrypt/live/gw2builder.example.com/privkey.pem;  # ← CHANGER
```

---

## 🔒 SSL/HTTPS

### Installation Certbot

```bash
# Installer certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Obtenir certificat SSL
sudo certbot --nginx -d votre-domaine.com

# Renouvellement automatique (cron)
sudo certbot renew --dry-run
```

### Configuration SSL

**Protocoles:** TLSv1.2, TLSv1.3  
**Ciphers:** HIGH:!aNULL:!MD5

### Security Headers

```nginx
Strict-Transport-Security: max-age=31536000
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
```

### Renouvellement Automatique

Certbot configure automatiquement un cron:
```cron
0 0,12 * * * certbot renew --quiet
```

### Vérifier Certificat

```bash
# Status certificat
sudo certbot certificates

# Test renouvellement
sudo certbot renew --dry-run

# Forcer renouvellement
sudo certbot renew --force-renewal
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

**Fichier:** `.github/workflows/production-deploy.yml`

### Pipeline Stages

```
┌─────────────┐
│  Push main  │
└──────┬──────┘
       │
       ├─────────────────────────────┐
       │                             │
┌──────▼─────────┐           ┌──────▼────────┐
│ Backend Tests  │           │ Frontend Tests│
│ - Unit tests   │           │ - Lint        │
│ - Linting      │           │ - Type check  │
│ - Security     │           │ - Build       │
└──────┬─────────┘           └──────┬────────┘
       │                             │
       └─────────────┬───────────────┘
                     │
              ┌──────▼──────┐
              │  E2E Tests  │
              │ - Cypress   │
              └──────┬──────┘
                     │
              ┌──────▼─────────┐
              │ Security Audit │
              │ - Trivy        │
              │ - NPM audit    │
              └──────┬─────────┘
                     │
              ┌──────▼──────────┐
              │ Build & Tag     │
              │ - Create version│
              └──────┬──────────┘
                     │
              ┌──────▼──────────┐
              │    Deploy       │
              │ (Manual Approval)│
              └─────────────────┘
```

### Jobs Pipeline

| Job | Description | Durée estimée |
|-----|-------------|---------------|
| **test-backend** | Tests unitaires Python | ~2 min |
| **test-frontend** | Build + lint frontend | ~1 min |
| **test-e2e** | Tests Cypress E2E | ~2 min |
| **security-audit** | Scan vulnérabilités | ~1 min |
| **build-and-tag** | Version tagging | <1 min |
| **deploy-production** | Déploiement prod | Variable |

### Triggers

- ✅ Push sur `main`
- ✅ Manuel (workflow_dispatch)

### Secrets Requis

```yaml
secrets:
  SSH_PRIVATE_KEY: <clé SSH déploiement>
  # Autres secrets si nécessaire
```

### Déploiement Manuel

```bash
# Via GitHub UI
Actions → Production Deployment → Run workflow → main

# Ou via API
gh workflow run production-deploy.yml
```

---

## ⚡ Load Testing

### Script Load Testing

**Fichier:** `/scripts/load_testing/load_test.py`

### Fonctionnalités

- ✅ Tests concurrents asynchrones
- ✅ Statistiques détaillées (avg, min, max, p95)
- ✅ Affichage coloré (Rich)
- ✅ Support authentification JWT
- ✅ Tests multiples endpoints

### Usage

```bash
# Installation dépendances
pip install httpx rich

# Exécuter tests
cd scripts/load_testing
python load_test.py
```

### Endpoints Testés

| Endpoint | Requêtes | Concurrent | Auth |
|----------|----------|------------|------|
| `/api/v1/health` | 100 | 20 | Non |
| `/api/v1/dashboard/stats` | 50 | 10 | Oui |
| `/api/v1/dashboard/activities` | 50 | 10 | Oui |
| `/api/v1/users/me` | 50 | 10 | Oui |

### Métriques

- **Total requests:** Nombre total requêtes
- **Errors:** Nombre d'erreurs
- **Success rate:** % de succès
- **Avg time:** Temps moyen réponse (ms)
- **P95 time:** 95e percentile (ms)
- **Requests/sec:** Throughput

### Critères Succès

- ✅ Success rate ≥ 95%: PASS
- ⚠️ Success rate ≥ 90%: WARNING
- ❌ Success rate < 90%: FAIL

### Exemple Résultats

```
═══════════════════════════════════════════════
              LOAD TEST RESULTS
═══════════════════════════════════════════════

Endpoint              Total  Errors  Success%  Avg(ms)  P95(ms)  Req/s
────────────────────────────────────────────────────────────────────
Health Check           100      0     100.0%    12.34    18.56   45.2
Dashboard Stats         50      0     100.0%    45.67    67.89   22.1
Recent Activities       50      0     100.0%    38.12    55.23   26.3
User Profile            50      0     100.0%    23.45    34.56   35.8

Overall Success Rate: 100.00%
✅ LOAD TEST PASSED
```

---

## 🔐 Sécurité

### Vérifications Sécurité

#### 1. Vulnérabilités NPM

```bash
cd frontend
npm audit

# Fix automatique
npm audit fix
```

**Status actuel:** ✅ 0 vulnérabilités

#### 2. Vulnérabilités Python

```bash
cd backend
poetry run safety check
```

#### 3. Secrets & Keys

```bash
# JWT keys dans .env (gitignored)
grep -r "SECRET_KEY" backend/.env

# Vérifier .gitignore
cat .gitignore | grep .env
```

**✅ Confirmé:** JWT keys jamais exposées

#### 4. HTTPS

- ✅ Redirect HTTP → HTTPS
- ✅ HSTS header
- ✅ TLS 1.2/1.3 seulement

#### 5. Headers Sécurité

```nginx
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Referrer-Policy: no-referrer-when-downgrade
```

#### 6. Password Hashing

- ✅ Bcrypt avec 12 rounds
- ✅ Salt automatique
- ✅ Jamais de plaintext passwords

#### 7. Authentication

- ✅ JWT tokens sécurisés
- ✅ Token expiration (access + refresh)
- ✅ 401 auto-redirect /login
- ✅ Protected routes enforcement

### Audit Sécurité

```bash
# Scan Trivy (containers)
trivy fs .

# Scan bandit (Python)
cd backend
poetry run bandit -r app/

# Scan ESLint (JavaScript)
cd frontend
npm run lint
```

---

## 🛠️ Maintenance

### Tâches Quotidiennes

```bash
# 1. Check backend status
gw2-status

# 2. Monitor logs
gw2-logs -e  # Vérifier erreurs

# 3. Check disk space
df -h

# 4. Check memory
free -h
```

### Tâches Hebdomadaires

```bash
# 1. Vérifier backups
ls -lh backups/
cat backups/backup.log

# 2. Update dependencies
cd backend && poetry update
cd frontend && npm update

# 3. Security audit
npm audit
poetry run safety check

# 4. Check logs size
du -sh backend.log
```

### Tâches Mensuelles

```bash
# 1. Renouveler SSL
sudo certbot renew

# 2. Review monitoring
gw2-logs -c  # Clean old logs

# 3. Database vacuum
cd backend
poetry run python -c "import sqlite3; conn = sqlite3.connect('gw2_wvwbuilder.db'); conn.execute('VACUUM'); conn.close()"

# 4. Performance review
python scripts/load_testing/load_test.py
```

### Updates Système

```bash
# Update OS
sudo apt update && sudo apt upgrade -y

# Update Nginx
sudo apt install --only-upgrade nginx

# Update Certbot
sudo apt install --only-upgrade certbot
```

---

## 🚨 Troubleshooting

### Backend Ne Démarre Pas

**Symptômes:** Service failed, port 8000 non accessible

**Solutions:**

```bash
# 1. Vérifier logs
sudo journalctl -u gw2-backend -n 50

# 2. Vérifier port
sudo lsof -i :8000

# 3. Tester manuellement
cd backend
poetry run uvicorn app.main:app --host 127.0.0.1 --port 8000

# 4. Vérifier permissions
ls -la backend/gw2_wvwbuilder.db

# 5. Restart service
sudo systemctl restart gw2-backend
```

### Nginx Erreurs

**Symptômes:** 502 Bad Gateway, 504 Timeout

**Solutions:**

```bash
# 1. Test config
sudo nginx -t

# 2. Check backend
curl http://127.0.0.1:8000/api/v1/health

# 3. Logs nginx
sudo tail -50 /var/log/nginx/gw2-builder-error.log

# 4. Restart nginx
sudo systemctl restart nginx

# 5. Check permissions
sudo chown -R roddy:roddy /home/roddy/GW2_WvWbuilder/frontend/dist
```

### SSL Problèmes

**Symptômes:** HTTPS non accessible, certificat expiré

**Solutions:**

```bash
# 1. Vérifier certificat
sudo certbot certificates

# 2. Renouveler
sudo certbot renew --force-renewal

# 3. Restart nginx
sudo systemctl restart nginx

# 4. Check logs
sudo tail -50 /var/log/letsencrypt/letsencrypt.log
```

### Database Corruption

**Symptômes:** SQLite errors, integrity check failed

**Solutions:**

```bash
# 1. Check integrity
cd backend
sqlite3 gw2_wvwbuilder.db "PRAGMA integrity_check;"

# 2. Restore backup
cp ../backups/gw2_wvwbuilder.db.backup gw2_wvwbuilder.db

# 3. Restart backend
sudo systemctl restart gw2-backend

# 4. Create fresh backup
cd ..
./scripts/backup_database.sh
```

### Tests E2E Échouent

**Symptômes:** E2E tests failing in CI/CD

**Solutions:**

```bash
# 1. Run locally
cd frontend
npm run e2e:headless

# 2. Check backend running
curl http://127.0.0.1:8000/api/v1/health

# 3. Check test user
cd backend
poetry run python scripts/fix_test_user.py

# 4. Clear cache
rm -rf frontend/node_modules/.cache

# 5. Rebuild
npm run build
```

### Performance Dégradée

**Symptômes:** Slow responses, high CPU/memory

**Solutions:**

```bash
# 1. Check resources
top
htop
free -h
df -h

# 2. Check logs
gw2-logs -e

# 3. Restart backend
sudo systemctl restart gw2-backend

# 4. Run load test
python scripts/load_testing/load_test.py

# 5. Database vacuum
cd backend
sqlite3 gw2_wvwbuilder.db "VACUUM;"
```

---

## 📞 Support & Contacts

### Logs Importants

| Log | Location |
|-----|----------|
| Backend | `/home/roddy/GW2_WvWbuilder/backend.log` |
| Systemd | `journalctl -u gw2-backend` |
| Nginx Access | `/var/log/nginx/gw2-builder-access.log` |
| Nginx Error | `/var/log/nginx/gw2-builder-error.log` |
| Backup | `/home/roddy/GW2_WvWbuilder/backups/backup.log` |
| Cron | `/home/roddy/GW2_WvWbuilder/backups/cron.log` |

### Commandes Rapides

```bash
# Status global
gw2-status && systemctl status nginx

# Restart tout
sudo systemctl restart gw2-backend nginx

# Backup manuel
gw2-backup

# Monitoring live
gw2-logs

# Health check
curl http://127.0.0.1:8000/api/v1/health
```

### Checklist Problème

1. ✅ Backend running? `gw2-status`
2. ✅ Nginx running? `systemctl status nginx`
3. ✅ Database accessible? `ls -lh backend/gw2_wvwbuilder.db`
4. ✅ Logs propres? `gw2-logs -e`
5. ✅ Disk space? `df -h`
6. ✅ Memory OK? `free -h`

---

**Documentation maintenue par:** DevOps Team  
**Dernière mise à jour:** 15 octobre 2025  
**Version:** 1.0.0
