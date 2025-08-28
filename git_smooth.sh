#!/bin/bash

# ===============================
# Script Git pour GW2_WvWbuilder
# Gestion main et develop
# ===============================

echo "📂 Vérification du dépôt Git..."
git status >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Ce dossier n'est pas un dépôt Git."
    exit 1
fi

# Branche actuelle
current_branch=$(git branch --show-current)
echo "🌿 Branche actuelle : $current_branch"

# Vérifie si la branche develop existe, sinon la crée
if ! git show-ref --verify --quiet refs/heads/develop; then
    echo "🆕 Création de la branche 'develop'..."
    git checkout -b develop
    git push -u origin develop
    git checkout "$current_branch"
fi

# Menu principal
echo "Que voulez-vous faire ?"
echo "1) Pousser les changements vers develop"
echo "2) Fusionner develop dans main"
echo "3) Status rapide"
echo "4) Quitter"
read -p "Choix [1-4]: " choice

case "$choice" in
    1)
        echo "🚀 Pousser les changements vers develop..."
        git checkout develop
        git pull origin develop --rebase
        git add .
        read -p "Message du commit : " commit_msg
        git commit -m "$commit_msg"
        git push origin develop
        ;;
    2)
        echo "🔀 Fusionner develop dans main..."
        git checkout main
        git pull origin main --rebase
        git merge develop -m "Fusion automatique de develop dans main"
        if [ $? -ne 0 ]; then
            echo "⚠️ Conflits détectés dans les fichiers suivants :"
            git status --short | grep '^UU'
            echo "Résolvez-les puis faites 'git add <fichier>' et 'git commit'"
            exit 1
        fi
        git push origin main
        ;;
    3)
        echo "ℹ️ Status rapide du dépôt"
        git status
        ;;
    4)
        echo "👋 Sortie du script"
        exit 0
        ;;
    *)
        echo "❌ Choix invalide"
        exit 1
        ;;
esac
