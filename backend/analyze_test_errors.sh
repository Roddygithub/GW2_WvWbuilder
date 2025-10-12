#!/usr/bin/env bash
#
# Script d'analyse des erreurs de tests
# Phase 4 - Tests & CI/CD
#

set -e

echo "=========================================="
echo "  Phase 4 - Analyse des erreurs de tests"
echo "=========================================="
echo ""

# Créer le dossier de rapports
mkdir -p reports

echo "📊 Collecte des tests..."
poetry run pytest tests/ --co -q > reports/test_collection.txt 2>&1 || true

echo "📊 Exécution des tests (sans coverage pour plus de vitesse)..."
poetry run pytest tests/ --tb=line -v > reports/test_results_full.txt 2>&1 || true

echo "📊 Analyse des erreurs..."

# Extraire les erreurs d'import
echo ""
echo "=== Top 20 erreurs d'import ==="
grep -i "ImportError\|ModuleNotFoundError" reports/test_results_full.txt | \
    sed 's/.*ImportError: //' | \
    sed 's/.*ModuleNotFoundError: //' | \
    sort | uniq -c | sort -rn | head -20 | tee reports/import_errors.txt

# Extraire les erreurs de fixtures
echo ""
echo "=== Top 10 erreurs de fixtures ==="
grep -i "fixture.*not found" reports/test_results_full.txt | \
    sed 's/.*fixture //' | \
    sed 's/ not found.*//' | \
    sort | uniq -c | sort -rn | head -10 | tee reports/fixture_errors.txt

# Extraire les erreurs async
echo ""
echo "=== Erreurs async ==="
grep -i "async\|await\|coroutine" reports/test_results_full.txt | \
    grep -i "error\|failed" | \
    head -10 | tee reports/async_errors.txt

# Statistiques finales
echo ""
echo "=== Statistiques ==="
TOTAL=$(grep -c "collected" reports/test_collection.txt || echo "0")
PASSED=$(grep -oP '\d+(?= passed)' reports/test_results_full.txt | tail -1 || echo "0")
FAILED=$(grep -oP '\d+(?= failed)' reports/test_results_full.txt | tail -1 || echo "0")
ERRORS=$(grep -oP '\d+(?= error)' reports/test_results_full.txt | tail -1 || echo "0")

echo "Total tests collectés: $TOTAL"
echo "Tests passés: $PASSED"
echo "Tests échoués: $FAILED"
echo "Erreurs: $ERRORS"

echo ""
echo "✅ Analyse terminée. Rapports dans ./reports/"
echo ""
echo "Fichiers générés:"
echo "  - reports/test_collection.txt"
echo "  - reports/test_results_full.txt"
echo "  - reports/import_errors.txt"
echo "  - reports/fixture_errors.txt"
echo "  - reports/async_errors.txt"
