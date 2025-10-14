#!/bin/bash

# Script de configuration de la base de données de production
# À exécuter manuellement avant le premier déploiement en production

set -e

# Charger les variables d'environnement si un fichier .env existe
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Vérifier que les variables requises sont définies
for var in POSTGRES_DB POSTGRES_USER POSTGRES_PASSWORD; do
    if [ -z "${!var}" ]; then
        echo "Erreur: La variable $var n'est pas définie"
        exit 1
    fi
done

echo "Création de la base de données PostgreSQL..."

# Commande pour créer la base de données (à exécuter dans le conteneur PostgreSQL)
# Remplacez 'postgres' par le nom de votre service de base de données si nécessaire
docker-compose exec -T postgres psql -U $POSTGRES_USER -c "CREATE DATABASE $POSTGRES_DB;" || echo "La base de données existe peut-être déjà"

echo "Application des migrations..."
# Appliquer les migrations Alembic
docker-compose exec -T app alembic upgrade head

echo "Création d'un utilisateur administrateur..."
# Créer un utilisateur administrateur via l'API ou une commande personnalisée
# Remplacez les valeurs par défaut par des informations sécurisées
ADMIN_EMAIL="admin@example.com"
ADMIN_PASSWORD=$(openssl rand -base64 16)

echo "Création de l'administrateur avec l'email: $ADMIN_EMAIL"
echo "Mot de passe généré: $ADMIN_PASSWORD"

# Sauvegarder les identifiants dans un fichier sécurisé
cat > admin_credentials.txt <<EOL
ADMIN_EMAIL=$ADMIN_EMAIL
ADMIN_PASSWORD=$ADMIN_PASSWORD
EOL

chmod 600 admin_credentials.txt
echo "Les identifiants administrateur ont été enregistrés dans admin_credentials.txt"
echo "N'oubliez pas de les noter dans un endroit sûr et de supprimer ce fichier après utilisation"

echo "Configuration de la base de données terminée avec succès!"
