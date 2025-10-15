#!/bin/bash

# Script de nettoyage urgent du projet GW2_WvWbuilder
# À exécuter APRÈS avoir lu PROJECT_AUDIT_COMPLETE.md

set -e

echo "🎯 Nettoyage urgent du projet GW2_WvWbuilder"
echo "=============================================="
echo ""

# Vérifier qu'on est dans le bon répertoire
if [ ! -f "PROJECT_AUDIT_COMPLETE.md" ]; then
    echo "❌ Erreur: Ce script doit être exécuté depuis la racine du projet"
    exit 1
fi

# 1. Créer dossier archive pour docs
echo "📁 Création du dossier docs/archive..."
mkdir -p docs/archive

# 2. Archiver rapports de phases
echo "📦 Archivage des rapports de phases..."
mv PHASE_*.md docs/archive/ 2>/dev/null || true
mv AUDIT_*.md docs/archive/ 2>/dev/null || true
mv FINAL_*.md docs/archive/ 2>/dev/null || true
mv FINALIZATION_*.md docs/archive/ 2>/dev/null || true

# 3. Archiver rapports frontend/backend
echo "📦 Archivage des rapports frontend/backend..."
mv FRONTEND_*.md docs/archive/ 2>/dev/null || true
mv BACKEND_*.md docs/archive/ 2>/dev/null || true
mv E2E_*.md docs/archive/ 2>/dev/null || true
mv DEPLOYMENT_*.md docs/archive/ 2>/dev/null || true

# 4. Supprimer rapports obsolètes
echo "🗑️  Suppression des rapports obsolètes..."
rm -f AUTH_SUCCESS.md
rm -f DASHBOARD_FIX_REPORT.md
rm -f DASHBOARD_REDESIGN_SUMMARY.md
rm -f EXECUTIVE_FINAL_REPORT.md
rm -f FULL_STACK_READY.md
rm -f GITHUB_UPDATE_REPORT.md
rm -f GW2_API_DIAGNOSTIC_REPORT.md
rm -f IMPLEMENTATION_SUMMARY.md
rm -f INSTRUCTIONS_REDEMARRAGE.md
rm -f LIVE_FEATURES_UPDATE.md
rm -f LOGIN_FIX_SUCCESS.md
rm -f MISSION_COMPLETE.md
rm -f STATUS.md
rm -f TEST_FRONTEND_NOW.md
rm -f NEXT_STEPS.md
rm -f RELEASE_NOTES.md

# 5. Nettoyer backend
echo "🧹 Nettoyage du backend..."
cd backend

# Supprimer logs de tests
rm -f test_output*.log
rm -f deployment_*.log
rm -f test_errors.txt
rm -f test_jwt.log
rm -f test_refresh_token.log

# Supprimer fichiers temporaires
rm -f file.tmp
rm -f *.bak

# Supprimer .env multiples (garder .env, .env.example, .env.test)
echo "⚠️  Nettoyage des fichiers .env (vérifiez manuellement)"
echo "   Gardés: .env, .env.example, .env.test"
echo "   À supprimer manuellement si non utilisés: .env.dev, .env.development, .env.secure, .env.example.new"

cd ..

# 6. Lister fichiers non commités importants
echo ""
echo "📋 Fichiers critiques non commités (À COMMIT ER):"
echo "================================================"
git status --short | grep -E "^\?\?" | grep -E "(optimizer|Builder|composition)" || true

echo ""
echo "✅ Nettoyage terminé!"
echo ""
echo "🔴 ACTIONS MANUELLES REQUISES:"
echo "1. Vérifier docs/archive/ et supprimer si OK"
echo "2. Commit les fichiers optimizer/builder:"
echo "   git add backend/app/core/optimizer/"
echo "   git add backend/config/optimizer/"
echo "   git add backend/app/api/api_v1/endpoints/builder.py"
echo "   git add frontend/src/pages/BuilderV2.tsx"
echo "   git add frontend/src/components/CompositionMembersList.tsx"
echo "   git commit -m 'feat(optimizer): implement McM/PvE optimization engine with Builder V2'"
echo "3. Vérifier et supprimer .env inutiles dans backend/"
echo "4. Vérifier keys.json (contient des secrets réels?)"
echo "5. Supprimer pages Builder redondantes:"
echo "   rm frontend/src/pages/builder.tsx"
echo "   rm frontend/src/pages/BuilderOptimizer.tsx"
echo ""
echo "📊 Statistiques:"
find docs/archive -type f | wc -l | xargs echo "   Fichiers archivés:"
echo "   Documentation racine restante:"
ls -1 *.md 2>/dev/null | wc -l
echo ""
