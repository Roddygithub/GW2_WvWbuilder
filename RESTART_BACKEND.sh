#!/bin/bash

echo "========================================="
echo "🔄 REDÉMARRAGE DU BACKEND"
echo "========================================="
echo ""

# Tuer tous les processus uvicorn
echo "1. Arrêt des processus uvicorn existants..."
pkill -9 -f "uvicorn app.main:app" 2>/dev/null
sleep 2

# Vérifier que le port est libre
if lsof -i:8000 >/dev/null 2>&1; then
    echo "   ⚠️  Port 8000 encore occupé, force kill..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    sleep 2
fi

echo "   ✅ Processus arrêtés"
echo ""

# Aller dans le dossier backend
cd /home/roddy/GW2_WvWbuilder/backend

# Démarrer le backend
echo "2. Démarrage du nouveau backend..."
echo "   (avec le code corrigé pour /users/me)"
echo ""
echo "========================================="
echo ""

poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
