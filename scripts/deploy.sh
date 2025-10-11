#!/bin/bash

# Script de déploiement local pour GW2 WvW Builder
# Utilisation: ./deploy.sh [staging|production] [options]

set -e  # Arrêter le script en cas d'erreur

# Configuration par défaut
ENV=""
CONFIG_FILE=""
SSH_KEY=""
SSH_USER=""
SSH_HOST=""
TARGET_DIR=""
WORKERS=4
THREADS=2
TIMEOUT=120
DATABASE_URL=""
REDIS_URL=""
SECRET_KEY=""
DEBUG="False"

# Charger la configuration depuis un fichier
load_config() {
    if [ -f "$1" ]; then
        echo "Chargement de la configuration depuis $1"
        source "$1"
    else
        echo "Erreur: Fichier de configuration $1 introuvable"
        exit 1
    fi
}

# Afficher l'aide
show_help() {
    echo "Utilisation: $0 [environnement] [options]"
    echo "Environnements:"
    echo "  staging     Déploiement sur l'environnement de staging"
    echo "  production  Déploiement sur l'environnement de production"
    echo "Options:"
    echo "  -c, --config FILE    Fichier de configuration à utiliser"
    echo "  -h, --help           Afficher cette aide"
    exit 0
}

# Traiter les arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        staging|production)
            ENV="$1"
            shift
            ;;
        -c|--config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            ;;
        *)
            echo "Option inconnue: $1"
            show_help
            ;;
    esac
done

# Vérifier qu'un environnement a été spécifié
if [ -z "$ENV" ]; then
    echo "Erreur: Aucun environnement spécifié"
    show_help
    exit 1
fi

# Charger la configuration
if [ -z "$CONFIG_FILE" ]; then
    CONFIG_FILE="deploy.$ENV.conf"
fi

load_config "$CONFIG_FILE"

# Vérifier les variables requises
for var in SSH_KEY SSH_USER SSH_HOST TARGET_DIR DATABASE_URL REDIS_URL SECRET_KEY; do
    if [ -z "${!var}" ]; then
        echo "Erreur: La variable $var n'est pas définie dans $CONFIG_FILE"
        exit 1
    done
done

echo "Démarrage du déploiement sur l'environnement $ENV..."

# Créer un répertoire temporaire
TMP_DIR="/tmp/gw2-wvwbuilder-deploy-$(date +%s)"
mkdir -p "$TMP_DIR"

# Copier les fichiers nécessaires
cp -r . "$TMP_DIR/"

# Créer le fichier .env
cat > "$TMP_DIR/backend/.env" <<EOF
ENVIRONMENT=$ENV
DATABASE_URL=$DATABASE_URL
REDIS_URL=$REDIS_URL
SECRET_KEY=$SECRET_KEY
DEBUG=$DEBUG
DATABASE_POOL_SIZE=$WORKERS
DATABASE_MAX_OVERFLOW=$((WORKERS / 2))
EOF

# Se connecter en SSH et déployer
ssh -i "$SSH_KEY" "$SSH_USER@$SSH_HOST" << EOF
    # Créer le répertoire de déploiement s'il n'existe pas
    mkdir -p "$TARGET_DIR"
    
    # Arrêter les services si nécessaire
    if [ -f "$TARGET_DIR/docker-compose.yml" ]; then
        cd "$TARGET_DIR"
        docker-compose down
    fi

    # Copier les fichiers
    rsync -avz --delete "$TMP_DIR/" "$TARGET_DIR/"

    # Démarrer les services
    cd "$TARGET_DIR"
    docker-compose up -d --build

    # Exécuter les migrations
    docker-compose exec backend alembic upgrade head
EOF

# Nettoyer
rm -rf "$TMP_DIR"

echo "Déploiement terminé avec succès sur $ENV !"
echo "URL: https://$SSH_HOST"
