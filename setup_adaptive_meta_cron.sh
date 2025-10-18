#!/bin/bash
# Setup Adaptive Meta Cron — GW2_WvWBuilder v4.3
# Installe un cron job pour exécuter le système adaptatif toutes les 12h

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
LOG_DIR="/var/log"
LOG_FILE="$LOG_DIR/gw2_adaptive_meta.log"

echo "=========================================="
echo "Setup Adaptive Meta Cron v4.3"
echo "=========================================="
echo ""

# Vérifier si poetry est installé
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry n'est pas installé. Installez-le d'abord :"
    echo "   curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Vérifier si le répertoire backend existe
if [ ! -d "$BACKEND_DIR" ]; then
    echo "❌ Répertoire backend introuvable : $BACKEND_DIR"
    exit 1
fi

# Créer le fichier de log s'il n'existe pas
if [ ! -f "$LOG_FILE" ]; then
    echo "📝 Création du fichier de log : $LOG_FILE"
    sudo touch "$LOG_FILE"
    sudo chown $USER:$USER "$LOG_FILE"
fi

# Définir la ligne cron
CRON_CMD="0 3,15 * * * cd $BACKEND_DIR && poetry run python app/ai/adaptive_meta_runner.py --with-llm >> $LOG_FILE 2>&1"

# Vérifier si le cron existe déjà
if crontab -l 2>/dev/null | grep -q "adaptive_meta_runner.py"; then
    echo "⚠️  Un cron job existe déjà pour adaptive_meta_runner.py"
    echo ""
    echo "Voulez-vous le remplacer ? (y/n)"
    read -r response
    if [ "$response" != "y" ]; then
        echo "❌ Installation annulée"
        exit 0
    fi
    
    # Supprimer l'ancien cron
    crontab -l | grep -v "adaptive_meta_runner.py" | crontab -
    echo "✅ Ancien cron supprimé"
fi

# Ajouter le nouveau cron
(crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -

echo ""
echo "=========================================="
echo "✅ Cron installé avec succès !"
echo "=========================================="
echo ""
echo "Configuration :"
echo "  Fréquence : Tous les jours à 3h et 15h"
echo "  Script    : $BACKEND_DIR/app/ai/adaptive_meta_runner.py"
echo "  Log       : $LOG_FILE"
echo "  Mode      : --with-llm (LLM Mistral activé)"
echo ""
echo "Commandes utiles :"
echo "  Voir le cron     : crontab -l"
echo "  Voir les logs    : tail -f $LOG_FILE"
echo "  Retirer le cron  : crontab -e (supprimer la ligne)"
echo "  Test manuel      : cd $BACKEND_DIR && poetry run python app/ai/adaptive_meta_runner.py --with-llm --dry-run"
echo ""
echo "=========================================="
