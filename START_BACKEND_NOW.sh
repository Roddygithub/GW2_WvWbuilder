#!/bin/bash

echo "========================================="
echo "🚀 DÉMARRAGE DU BACKEND"
echo "========================================="
echo ""

# Aller dans le dossier backend
cd /home/roddy/GW2_WvWbuilder/backend

# Démarrer le backend
echo "Démarrage de uvicorn..."
echo ""
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
