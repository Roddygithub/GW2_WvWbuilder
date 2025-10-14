# 🚀 Guide de Démarrage Rapide - Infrastructure Production

Ce guide vous permet de mettre en place l'infrastructure production en quelques minutes.

---

## ⚡ Installation Rapide (5 minutes)

### Étape 1: Scripts de Base

```bash
cd /home/roddy/GW2_WvWbuilder

# Rendre scripts exécutables
chmod +x scripts/*.sh
chmod +x scripts/systemd/*.service
chmod +x scripts/load_testing/*.py
```

### Étape 2: Backup Automatique

```bash
# Installer cron job (weekly backup)
bash scripts/install_cron.sh

# Test backup manuel
bash scripts/backup_database.sh

# Vérifier
cat backups/backup.log
```

### Étape 3: Aliases Monitoring

```bash
# Ajouter aliases au ~/.bashrc
cat >> ~/.bashrc << 'EOF'

# GW2 WvW Builder Aliases
alias gw2-logs='~/GW2_WvWbuilder/scripts/monitor_logs.sh'
alias gw2-logs-errors='~/GW2_WvWbuilder/scripts/monitor_logs.sh -e'
alias gw2-backup='~/GW2_WvWbuilder/scripts/backup_database.sh'
EOF

# Recharger bashrc
source ~/.bashrc

# Tester
gw2-logs -n 20
```

### Étape 4: Service systemd (Optionnel, requires sudo)

```bash
# Copier service
sudo cp scripts/systemd/gw2-backend.service /etc/systemd/system/

# Activer et démarrer
sudo systemctl daemon-reload
sudo systemctl enable gw2-backend
sudo systemctl start gw2-backend

# Vérifier
systemctl status gw2-backend
```

### Étape 5: Nginx (Optionnel, requires sudo + domain)

```bash
# Installer Nginx
sudo apt install nginx

# Copier config
sudo cp scripts/nginx/gw2-wvwbuilder.conf /etc/nginx/sites-available/

# ⚠️ IMPORTANT: Éditer le fichier et changer:
# - server_name (votre domaine)
# - ssl_certificate paths
sudo nano /etc/nginx/sites-available/gw2-wvwbuilder.conf

# Activer site
sudo ln -s /etc/nginx/sites-available/gw2-wvwbuilder.conf /etc/nginx/sites-enabled/

# Tester config
sudo nginx -t

# Recharger
sudo systemctl reload nginx
```

### Étape 6: SSL/HTTPS (Optionnel, requires domain)

```bash
# Installer Certbot
sudo apt install certbot python3-certbot-nginx

# Obtenir certificat
sudo certbot --nginx -d votre-domaine.com

# Vérifier auto-renewal
sudo certbot renew --dry-run
```

---

## 📋 Commandes Essentielles

### Monitoring

```bash
# Logs temps réel (colorés)
gw2-logs

# Seulement erreurs
gw2-logs -e

# Dernières 100 lignes
gw2-logs -n 100

# Nettoyer logs anciens
gw2-logs -c
```

### Backup

```bash
# Backup manuel
gw2-backup

# Voir logs backup
cat backups/backup.log

# Restaurer backup
cp backups/gw2_wvwbuilder.db.backup backend/gw2_wvwbuilder.db
```

### Service (si systemd installé)

```bash
# Status
sudo systemctl status gw2-backend

# Démarrer
sudo systemctl start gw2-backend

# Arrêter
sudo systemctl stop gw2-backend

# Redémarrer
sudo systemctl restart gw2-backend

# Logs
sudo journalctl -u gw2-backend -f
```

### Tests

```bash
# Health check
curl http://127.0.0.1:8000/api/v1/health

# Load testing
cd scripts/load_testing
pip install httpx rich
python load_test.py
```

---

## 🔧 Configuration Par Défaut

### Backup

- **Fréquence:** Hebdomadaire (Dimanche 2:00 AM)
- **Stratégie:** 1 backup (écrase l'ancien)
- **Location:** `backups/gw2_wvwbuilder.db.backup`

### Logs

- **Backend:** `backend.log` (INFO level)
- **Rotation:** 14 jours
- **Monitoring:** Scripts colorisés

### Service

- **Auto-restart:** Oui
- **Boot startup:** Oui (si enabled)
- **Workers:** 2
- **Memory limit:** 1GB

### Nginx

- **HTTP:** Redirect → HTTPS
- **HTTPS:** Port 443
- **Backend proxy:** 127.0.0.1:8000
- **Static files:** frontend/dist/

---

## ✅ Checklist Installation

### Basique (sans sudo)

- [x] Scripts exécutables
- [x] Backup script configured
- [x] Cron job installé
- [x] Aliases monitoring ajoutés
- [x] Test backup manuel

### Avancé (avec sudo)

- [ ] systemd service installé
- [ ] Nginx installé et configuré
- [ ] SSL/HTTPS configuré
- [ ] Log rotation configuré
- [ ] Monitoring actif

### CI/CD

- [x] GitHub Actions workflow configuré
- [ ] Secrets GitHub configurés
- [ ] Deploy keys ajoutées

---

## 🚨 Troubleshooting Rapide

### Backend ne démarre pas

```bash
# Vérifier logs
gw2-logs -e

# Tester manuellement
cd backend
poetry run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Backup échoue

```bash
# Permissions
chmod +x scripts/backup_database.sh

# Test manuel
bash scripts/backup_database.sh

# Voir erreurs
cat backups/backup.log
```

### Monitoring ne marche pas

```bash
# Recharger aliases
source ~/.bashrc

# Vérifier fichier log existe
ls -lh backend.log

# Test direct
bash scripts/monitor_logs.sh -n 10
```

---

## 📖 Documentation Complète

Pour plus de détails, voir:
- **INFRASTRUCTURE.md** - Documentation complète
- **DEPLOYMENT_FINAL_REPORT.md** - Rapport déploiement
- **FINALIZATION_DEBUG_REPORT.md** - Rapport optimisation

---

## 💡 Conseils

1. **Commencez petit:** Installez backup et monitoring d'abord
2. **Testez toujours:** Vérifiez chaque composant après installation
3. **Logs sont vos amis:** `gw2-logs` est votre meilleur outil
4. **Backup régulier:** Vérifiez les backups chaque semaine
5. **Monitoring actif:** Surveillez les logs quotidiennement

---

**Version:** 1.0.0  
**Date:** 15 octobre 2025  
**Support:** Voir INFRASTRUCTURE.md
