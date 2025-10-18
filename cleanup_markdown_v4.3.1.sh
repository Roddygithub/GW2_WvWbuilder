#!/bin/bash
# Nettoyage Fichiers Markdown Obsolètes v4.3.1
# Date: 2025-10-18

set -e

echo "🧹 Nettoyage Markdown v4.3.1"
echo "=============================="
echo ""

# Compter avant
BEFORE=$(find . -name "*.md" -type f | grep -v node_modules | grep -v venv | grep -v ".git" | wc -l)
echo "📊 Fichiers .md AVANT: $BEFORE"
echo ""

# Confirmation
read -p "⚠️  Supprimer 121+ fichiers .md obsolètes ? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Annulé"
    exit 1
fi

# Backup Git
echo "💾 Création backup Git..."
git add -A
git commit -m "backup: avant nettoyage markdown v4.3.1" || true
TAG="pre-cleanup-md-$(date +%Y%m%d-%H%M%S)"
git tag "$TAG"
echo "✅ Backup créé: $TAG"
echo ""

# Archive optionnelle
echo "📦 Création archive ZIP..."
tar -czf "markdown_archive_$(date +%Y%m%d-%H%M%S).tar.gz" \
    backend/PHASE*.md \
    backend/FINAL_*.md \
    backend/README_PHASE*.md \
    docs/*_v3.*.md \
    docs/archive/ \
    2>/dev/null || true
echo "✅ Archive créée"
echo ""

echo "🗑️  Suppression fichiers obsolètes..."

# Catégorie 1: PHASE* (32 fichiers)
echo "  → PHASE* reports..."
rm -f backend/PHASE*.md
rm -f backend/README_PHASE*.md

# Catégorie 2: FINAL*/EXECUTIVE (18 fichiers)
echo "  → FINAL/EXECUTIVE reports..."
rm -f backend/FINAL_*.md
rm -f backend/EXECUTIVE_SUMMARY.md
rm -f backend/RELEASE_NOTES.md
rm -f backend/RELEASE_NOTES_TEMPLATE.md
rm -f backend/GIT_COMMIT_*.md
rm -f backend/VALIDATION_CHECKLIST.md
rm -f backend/DOCUMENTATION_INDEX.md

# Catégorie 3: Fixes temporaires (12 fichiers)
echo "  → Fixes temporaires..."
rm -f backend/ALL_FIXES_SUMMARY.md
rm -f backend/IMPORTS_FIX_COMPLETE.md
rm -f backend/TEST_FIXES_COMPLETE.md
rm -f backend/COMPOSITION_MEMBERS_FIX_SUMMARY.md
rm -f backend/CORRECTIONS_TODO.md
rm -f backend/API_READY.md
rm -f backend/AUDIT_REPORT.md
rm -f backend/QUICK_START_FIXES.md
rm -f backend/QUICK_VALIDATION_GUIDE.md
rm -f backend/EXECUTE_NOW.md
rm -f backend/README_FINALISATION.md
rm -f backend/TODO.md

# Catégorie 4: Guides multiples (8 fichiers)
echo "  → Guides redondants..."
rm -f backend/INCREASE_COVERAGE_GUIDE.md
rm -f docs/GUIDE_TEST_FRONTEND_v3.4.4.md
rm -f docs/QUICK_START_OPTIMIZER.md
rm -f docs/TEST_OPTIMIZER_NO_AUTH.md
rm -f INSTRUCTIONS_VALIDATION_CICD.md
rm -f QUICK_GITHUB_COMMANDS.md
rm -f OPTIMIZER_IMPLEMENTATION.md
rm -f OPTIMIZER_READY.md
rm -f MODE_EFFECTS_SYSTEM.md

# Catégorie 5: Versions v3.x (28 fichiers)
echo "  → Versions v3.x obsolètes..."
rm -f docs/BLOCKERS_v3.4.x.md
rm -f docs/COVERAGE_PROGRESS_v3.4.x.md
rm -f docs/ETAT_CONNEXIONS_v3.4.6.md
rm -f docs/FIX_DATABASE_v3.4.4.md
rm -f docs/FIX_OPTIMIZER_v3.5.0.md
rm -f docs/FIX_SCORE_v3.5.1.md
rm -f docs/FIX_15_FIREBRANDS.md
rm -f docs/IMPLEMENTATION_GW2_MECHANICS_v3.5.2.md
rm -f docs/MYPY_PROGRESS_v3.4.x.md
rm -f docs/OPTIMIZER_UI_v3.5.0.md
rm -f docs/OPTIMIZER_V3.7_IMPLEMENTATION.md
rm -f docs/OPTIMIZER_DND_V3.7_GUIDE.md
rm -f docs/RAPPORT_FINAL_v3.4.4.md
rm -f docs/RAPPORT_FINAL_SYNTHESE_v3.4.5.md
rm -f docs/RAPPORT_FINAL_VALIDATION_v3.4.3.md
rm -f docs/RELEASE_NOTES_v3.4.*.md
rm -f docs/SESSION_COMPLETE_v3.4.7.md
rm -f docs/TEST_RESULTS_V3.7.1.md
rm -f docs/THEME_GW2_v3.4.5.md
rm -f docs/VALIDATION_FONCTIONNELLE_v3.4.3.md
rm -f docs/CHANGELOG_SPLIT_BALANCE_v3.6.md
rm -f docs/API_GW2_SPLIT_BALANCE_INVESTIGATION.md

# Catégorie 6: Archive complète (16 fichiers)
echo "  → Archive docs..."
rm -rf docs/archive/

# Catégorie 7: Frontend temporaires (7 fichiers)
echo "  → Frontend temporaires..."
rm -f frontend/API_INTEGRATION.md
rm -f frontend/AUTH_FRONTEND_FIX_REPORT.md
rm -f frontend/DASHBOARD_OVERVIEW.md
rm -f frontend/DASHBOARD_REDESIGN_TESTING.md
rm -f frontend/DASHBOARD_UI_UPDATE.md
rm -f frontend/FRONTEND_READY.md

# Catégorie 8: Backend temporaires
echo "  → Backend temporaires..."
rm -f backend/tests/TEST_PROGRESS.md

# Catégorie 9: Cleanup actuel (garder pour référence)
echo "  → Cleanup docs (temporaires)..."
# Garder pour l'instant:
# - CLEANUP_PLAN_v4.3.1.md
# - CLEANUP_ANALYSIS.md
# - CLEANUP_SUMMARY.md
# - CLEANUP_MARKDOWN_ANALYSIS.md

echo ""
echo "✅ Suppression terminée !"
echo ""

# Compter après
AFTER=$(find . -name "*.md" -type f | grep -v node_modules | grep -v venv | grep -v ".git" | wc -l)
DELETED=$((BEFORE - AFTER))

echo "📊 Résultats:"
echo "  Avant:     $BEFORE fichiers"
echo "  Après:     $AFTER fichiers"
echo "  Supprimés: $DELETED fichiers (-$(echo "scale=1; $DELETED*100/$BEFORE" | bc)%)"
echo ""

echo "📁 Fichiers .md essentiels restants:"
find . -name "*.md" -type f | grep -v node_modules | grep -v venv | grep -v ".git" | sort

echo ""
echo "✅ Nettoyage Markdown terminé !"
echo ""
echo "💡 Prochaines étapes:"
echo "  1. Vérifier structure: tree -P '*.md' -I 'node_modules|venv|.git'"
echo "  2. Commit: git add -A && git commit -m 'docs: cleanup markdown v4.3.1 - remove 121 obsolete files'"
echo "  3. Restaurer si besoin: git reset --hard $TAG"
echo ""
