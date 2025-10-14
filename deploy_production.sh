#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Déploiement One-Shot GW2 WvW Builder - $(date)"

# --- 1️⃣ Start Backend ---
echo "🔹 Démarrage du backend..."
cd backend
poetry install --no-interaction
poetry run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!
sleep 5  # Attendre que le backend soit opérationnel

# Vérifier health
echo "🔹 Vérification du backend..."
curl -s http://127.0.0.1:8000/api/v1/health | grep -q '"status":"ok"' && echo "✅ Backend OK" || (echo "❌ Backend KO" && exit 1)

# --- 2️⃣ Build Frontend ---
echo "🔹 Build frontend..."
cd ../frontend
npm install --legacy-peer-deps
npm run build
echo "✅ Build frontend terminé"

# --- 3️⃣ Lancer Tests E2E ---
echo "🔹 Exécution des tests E2E..."
npm run e2e:headless
TEST_STATUS=$?

if [ $TEST_STATUS -eq 0 ]; then
    echo "✅ Tous les tests E2E ont réussi"
else
    echo "⚠️ Certains tests E2E ont échoué"
fi

# --- 4️⃣ Rapport final ---
echo "🔹 Génération rapport final..."
PASSING=$(npm run e2e:headless -- --reporter json | grep -o '"pass":true' | wc -l)
TOTAL=$(npm run e2e:headless -- --reporter json | grep -o '"pass":true\|"pass":false' | wc -l)
echo "📊 Tests E2E: $PASSING / $TOTAL passants"

# --- 5️⃣ Fin et nettoyage ---
echo "🔹 Arrêt du backend..."
kill $BACKEND_PID
echo "🏁 Déploiement terminé - $(date)"

