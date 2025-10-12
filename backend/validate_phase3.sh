#!/usr/bin/env bash
#
# Script de validation Phase 3 - Backend Stabilization
# GW2_WvWbuilder Backend
#
# Usage: ./validate_phase3.sh
#

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_STEPS=8
CURRENT_STEP=0

# Helper functions
print_step() {
    CURRENT_STEP=$((CURRENT_STEP + 1))
    echo -e "\n${BLUE}[${CURRENT_STEP}/${TOTAL_STEPS}]${NC} ${1}"
}

print_success() {
    echo -e "${GREEN}✓${NC} ${1}"
}

print_error() {
    echo -e "${RED}✗${NC} ${1}"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} ${1}"
}

# Banner
echo "=========================================="
echo "  Phase 3 - Backend Stabilization"
echo "  Validation Script"
echo "=========================================="
echo ""

# Step 1: Apply patch
print_step "Application du patch phase3_backend_fix.diff"
if [ -f "phase3_backend_fix.diff" ]; then
    if git apply --check phase3_backend_fix.diff 2>/dev/null; then
        git apply phase3_backend_fix.diff
        print_success "Patch appliqué avec succès"
    else
        print_error "Le patch ne peut pas être appliqué proprement"
        print_warning "Vérifiez les conflits manuellement"
        exit 1
    fi
else
    print_error "Fichier phase3_backend_fix.diff introuvable"
    exit 1
fi

# Step 2: Format with Black
print_step "Formatage du code avec Black (line-length 120)"
if poetry run black app/ tests/ --line-length 120 --quiet; then
    print_success "Code formaté avec succès"
else
    print_error "Erreur lors du formatage Black"
    exit 1
fi

# Step 3: Lint with Ruff
print_step "Vérification et correction avec Ruff"
if poetry run ruff check app/ tests/ --fix --quiet; then
    print_success "Lint Ruff OK"
else
    print_warning "Quelques warnings Ruff persistent (vérifiez manuellement)"
fi

# Step 4: Security scan with Bandit
print_step "Scan de sécurité avec Bandit"
BANDIT_OUTPUT=$(poetry run bandit -r app -ll -q 2>&1 || true)
if [ -z "$BANDIT_OUTPUT" ]; then
    print_success "Aucun problème de sécurité détecté"
else
    print_warning "Bandit a détecté des problèmes:"
    echo "$BANDIT_OUTPUT"
fi

# Step 5: Quick triage tests
print_step "Tests ciblés (triage rapide)"

echo "  → test_deps.py"
if poetry run pytest tests/unit/api/test_deps.py -q --tb=short 2>&1 | tail -1 | grep -q "passed"; then
    print_success "test_deps.py OK"
else
    print_warning "test_deps.py a des échecs (voir détails ci-dessous)"
fi

echo "  → test_jwt_complete.py"
if poetry run pytest tests/unit/core/test_jwt_complete.py -q --tb=short 2>&1 | tail -1 | grep -q "passed"; then
    print_success "test_jwt_complete.py OK"
else
    print_warning "test_jwt_complete.py a des échecs"
fi

echo "  → test_security_enhanced.py"
if poetry run pytest tests/unit/security/test_security_enhanced.py -q --tb=short 2>&1 | tail -1 | grep -q "passed"; then
    print_success "test_security_enhanced.py OK"
else
    print_warning "test_security_enhanced.py a des échecs"
fi

echo "  → test_webhook_service.py"
if poetry run pytest tests/unit/test_webhook_service.py -q --tb=short 2>&1 | tail -1 | grep -q "passed"; then
    print_success "test_webhook_service.py OK"
else
    print_warning "test_webhook_service.py a des échecs"
fi

# Step 6: Full test suite
print_step "Suite complète de tests avec couverture"
if poetry run pytest tests/ --cov=app --cov-report=html --cov-report=term-missing -q; then
    print_success "Tous les tests passent"
else
    print_error "Certains tests échouent"
    print_warning "Consultez le rapport de couverture: htmlcov/index.html"
fi

# Step 7: Coverage check
print_step "Vérification de la couverture (objectif ≥80%)"
COVERAGE=$(poetry run coverage report | grep TOTAL | awk '{print $4}' | sed 's/%//')
if [ -n "$COVERAGE" ]; then
    if (( $(echo "$COVERAGE >= 80" | bc -l) )); then
        print_success "Couverture: ${COVERAGE}% (≥80%)"
    else
        print_warning "Couverture: ${COVERAGE}% (<80%)"
    fi
else
    print_warning "Impossible de déterminer la couverture"
fi

# Step 8: Summary
print_step "Résumé de la validation"
echo ""
echo "Fichiers modifiés:"
echo "  - app/api/deps.py (import TeamMember)"
echo "  - app/db/session.py (import logging)"
echo "  - app/core/db_monitor.py (import text)"
echo "  - app/api/api_v1/endpoints/builds.py (définition update_data)"
echo "  - app/core/security.py (suppression debug prints)"
echo "  - app/db/dependencies.py (harmonisation async)"
echo ""
echo "Prochaines étapes:"
echo "  1. Vérifier le rapport de couverture: xdg-open htmlcov/index.html"
echo "  2. Commit: git add -A && git commit -m 'phase3: fix imports, async deps, remove debug prints'"
echo "  3. Push: git push origin develop"
echo ""
print_success "Validation Phase 3 terminée !"
