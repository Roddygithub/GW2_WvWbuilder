#!/bin/bash
# Nettoyage Final v4.3.1 - Caches, Logs, Temporaires
# Date: 2025-10-18

set -e

echo "🧹 Nettoyage Final v4.3.1"
echo "============================"
echo ""

# Confirmation
read -p "⚠️  Supprimer caches, logs et fichiers temporaires ? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Annulé"
    exit 1
fi

# Backup Git
echo "💾 Création backup Git..."
git add -A
git commit -m "backup: avant nettoyage final v4.3.1" || true
TAG="pre-cleanup-final-$(date +%Y%m%d-%H%M%S)"
git tag "$TAG"
echo "✅ Backup créé: $TAG"
echo ""

# Calcul espace avant
echo "📊 Calcul espace disque..."
BEFORE=$(du -sh . 2>/dev/null | awk '{print $1}')
echo "Espace AVANT: $BEFORE"
echo ""

echo "🗑️  Suppression fichiers temporaires..."
echo ""

# 1. __pycache__
echo "  → __pycache__ (1259+ dossiers)..."
PYCACHE_COUNT=$(find . -type d -name "__pycache__" 2>/dev/null | wc -l)
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
echo "    ✅ $PYCACHE_COUNT dossiers supprimés"

# 2. venv/ dupliqué
if [ -d "venv/" ]; then
    echo "  → venv/ dupliqué (garder .venv/)..."
    du -sh venv/ 2>/dev/null
    rm -rf venv/
    echo "    ✅ venv/ supprimé"
fi

# 3. Logs
echo "  → Logs temporaires..."
LOG_COUNT=0
for log in backend/logs/*.log backend/*.log backend/.*.log frontend/*.log; do
    if [ -f "$log" ]; then
        rm -f "$log"
        ((LOG_COUNT++))
    fi
done
echo "    ✅ $LOG_COUNT fichiers log supprimés"

# 4. PIDs
echo "  → Fichiers PID..."
rm -f .*.pid 2>/dev/null || true
echo "    ✅ Fichiers .pid supprimés"

# 5. DB dupliquées
echo "  → Bases de données dupliquées..."
DB_SIZE=0
if [ -f "gw2_wvwbuilder.db" ]; then
    DB_SIZE=$(du -sh gw2_wvwbuilder.db 2>/dev/null | awk '{print $1}')
    rm -f gw2_wvwbuilder.db
fi
rm -f backend/test.db 2>/dev/null || true
rm -rf backend/test_db/ 2>/dev/null || true
echo "    ✅ DB dupliquées supprimées ($DB_SIZE racine)"

# 6. Coverage dupliqué
echo "  → Coverage reports HTML..."
COV_SIZE=0
if [ -d "htmlcov/" ]; then
    COV_SIZE=$(du -sh htmlcov/ 2>/dev/null | awk '{print $1}')
fi
rm -rf htmlcov/ 2>/dev/null || true
rm -rf backend/coverage_html/ 2>/dev/null || true
rm -f .coverage 2>/dev/null || true
rm -f backend/coverage.json 2>/dev/null || true
echo "    ✅ Coverage HTML supprimé ($COV_SIZE), gardé coverage.xml"

# 7. Scripts temporaires
echo "  → Scripts temporaires backend/..."
rm -f backend/analyze_test_errors.sh 2>/dev/null || true
rm -f backend/check_*.py 2>/dev/null || true
rm -f backend/cleanup_duplicate_tests.py 2>/dev/null || true
rm -f backend/fix_*.sh 2>/dev/null || true
rm -f backend/fix_*.py 2>/dev/null || true
rm -f backend/*test_db.py 2>/dev/null || true
rm -f backend/test_optimizer.py 2>/dev/null || true
rm -f backend/test_score.py 2>/dev/null || true
rm -f backend/test_split_balance_*.py 2>/dev/null || true
rm -f backend/test_webhook_service.py 2>/dev/null || true
rm -f backend/run_mutation_tests.sh 2>/dev/null || true
rm -f backend/EXECUTE_NOW.sh 2>/dev/null || true
rm -f backend/finalize_backend.sh 2>/dev/null || true
echo "    ✅ Scripts temporaires supprimés"

# 8. Fichiers texte temporaires
echo "  → Fichiers .txt temporaires..."
rm -f backend/*_COMPLETE.txt 2>/dev/null || true
rm -f backend/*_FIX*.txt 2>/dev/null || true
rm -f backend/COMMIT_MESSAGE.txt 2>/dev/null || true
rm -f backend/test_output.txt 2>/dev/null || true
rm -f backend/swe1_task.txt 2>/dev/null || true
rm -f backend/QUICK_START_TESTS.txt 2>/dev/null || true
echo "    ✅ Fichiers .txt temporaires supprimés"

# 9. get-pip.py
if [ -f "backend/get-pip.py" ]; then
    echo "  → get-pip.py (2.1 MB)..."
    rm -f backend/get-pip.py
    echo "    ✅ get-pip.py supprimé"
fi

# 10. .pyc files
echo "  → Fichiers .pyc..."
PYC_COUNT=$(find . -name "*.pyc" -o -name "*.pyo" 2>/dev/null | wc -l)
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
echo "    ✅ $PYC_COUNT fichiers .pyc supprimés"

# 11. node_modules/.cache (optionnel)
if [ -d "frontend/node_modules/.cache" ]; then
    echo "  → node_modules/.cache..."
    CACHE_SIZE=$(du -sh frontend/node_modules/.cache 2>/dev/null | awk '{print $1}')
    rm -rf frontend/node_modules/.cache 2>/dev/null || true
    echo "    ✅ npm cache supprimé ($CACHE_SIZE)"
fi

echo ""
echo "✅ Nettoyage final terminé !"
echo ""

# Calcul espace après
AFTER=$(du -sh . 2>/dev/null | awk '{print $1}')
echo "📊 Résultats:"
echo "  Avant:  $BEFORE"
echo "  Après:  $AFTER"
echo ""

echo "📁 Structure propre maintenue:"
echo "  ✅ backend/gw2_wvwbuilder.db (DB production)"
echo "  ✅ backend/app/var/*.json (AI meta data)"
echo "  ✅ backend/coverage.xml (CI/CD)"
echo "  ✅ .venv/ (virtualenv Poetry)"
echo "  ✅ backend/logs/ (structure vide)"
echo "  ✅ 42 fichiers .md essentiels"
echo ""

# Archive markdown (optionnel)
if [ -f "markdown_archive_"*".tar.gz" ]; then
    echo "📦 Archive markdown trouvée"
    read -p "  Supprimer markdown_archive_*.tar.gz ? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ARCHIVE_SIZE=$(du -sh markdown_archive_*.tar.gz 2>/dev/null | awk '{print $1}')
        rm -f markdown_archive_*.tar.gz
        echo "  ✅ Archive supprimée ($ARCHIVE_SIZE)"
    else
        echo "  ⏸️  Archive conservée"
    fi
    echo ""
fi

echo "💡 Prochaines étapes:"
echo "  1. Vérifier: git status"
echo "  2. Tests: cd backend && poetry run pytest tests/test_*ai*.py -v"
echo "  3. Commit: git add -A && git commit -m 'chore: cleanup final v4.3.1 - remove caches and temp files'"
echo "  4. Restaurer si besoin: git reset --hard $TAG"
echo ""
