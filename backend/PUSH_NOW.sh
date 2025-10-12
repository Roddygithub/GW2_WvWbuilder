#!/usr/bin/env bash
#
# Phase 3 - Push vers develop
#

set -e

echo "=========================================="
echo "  Phase 3 - Backend Stabilization"
echo "  Push vers develop"
echo "=========================================="
echo ""

# Vérifier qu'on est sur la bonne branche
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "finalize/backend-phase2" ]; then
    echo "❌ Erreur: Vous devez être sur la branche finalize/backend-phase2"
    echo "   Branche actuelle: $CURRENT_BRANCH"
    exit 1
fi

# Vérifier qu'il y a un commit
if ! git log -1 --oneline | grep -q "phase3"; then
    echo "❌ Erreur: Le commit Phase 3 n'est pas trouvé"
    exit 1
fi

echo "✅ Branche: $CURRENT_BRANCH"
echo "✅ Dernier commit:"
git log -1 --oneline
echo ""

# Push
echo "🚀 Push vers origin..."
git push origin finalize/backend-phase2

echo ""
echo "=========================================="
echo "  ✅ Push réussi !"
echo "=========================================="
echo ""
echo "Prochaines étapes:"
echo "  1. Aller sur GitHub"
echo "  2. Créer une Pull Request:"
echo "     finalize/backend-phase2 → develop"
echo "  3. Review et merge"
echo "  4. Démarrer Phase 4 (tests + couverture 80%+)"
echo ""
echo "Résumé Phase 3:"
echo "  - Tests: 56/117 passent (48%)"
echo "  - Couverture: 29%"
echo "  - Black, Ruff, Bandit: ✅"
echo "  - Imports, async, cleanup: ✅"
echo ""
