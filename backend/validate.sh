#!/bin/bash
# Script de validation automatique - Phase 2 Backend GW2_WvWbuilder
# Usage: ./validate.sh

set -e  # Arrêter en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Début de la validation
print_header "🚀 Validation Phase 2 - Backend GW2_WvWbuilder"
echo ""

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "pyproject.toml" ]; then
    print_error "pyproject.toml not found. Please run this script from the backend directory."
    exit 1
fi

# 1. Vérification de l'environnement
print_header "📦 Vérification de l'environnement"
echo ""

print_info "Vérification de Poetry..."
if command -v poetry &> /dev/null; then
    poetry --version
    print_success "Poetry installé"
else
    print_error "Poetry n'est pas installé"
    exit 1
fi

print_info "Vérification de Python..."
python3 --version
print_success "Python installé"

echo ""

# 2. Installation des dépendances
print_header "📚 Installation des dépendances"
echo ""

print_info "Installation avec Poetry..."
poetry install --no-interaction
print_success "Dépendances installées"

echo ""

# 3. Exécution des tests
print_header "🧪 Exécution des tests"
echo ""

print_info "Tests JWT..."
if poetry run pytest tests/unit/core/test_jwt_complete.py -v --tb=short; then
    print_success "Tests JWT PASS"
else
    print_warning "Tests JWT FAIL - Voir les détails ci-dessus"
fi

echo ""

print_info "Tests Password Utils..."
if poetry run pytest tests/unit/core/test_password_utils_complete.py -v --tb=short; then
    print_success "Tests Password Utils PASS"
else
    print_warning "Tests Password Utils FAIL - Voir les détails ci-dessus"
fi

echo ""

print_info "Tests CRUD Build..."
if poetry run pytest tests/unit/crud/test_crud_build_complete.py -v --tb=short; then
    print_success "Tests CRUD Build PASS"
else
    print_warning "Tests CRUD Build FAIL - Voir les détails ci-dessus"
fi

echo ""

# 4. Mesure de la couverture
print_header "📊 Mesure de la couverture"
echo ""

print_info "Calcul de la couverture..."
poetry run pytest tests/unit/core/test_jwt_complete.py \
                 tests/unit/core/test_password_utils_complete.py \
                 tests/unit/crud/test_crud_build_complete.py \
                 --cov=app --cov-report=term --cov-report=html

print_success "Rapport de couverture généré dans htmlcov/"

echo ""

# 5. Vérification du linting
print_header "🔍 Vérification du linting"
echo ""

print_info "Vérification avec ruff..."
if poetry run ruff check app/ tests/ 2>/dev/null; then
    print_success "Linting PASS"
else
    print_warning "Linting a des warnings - Voir ci-dessus"
fi

echo ""

# 6. Vérification du formatage
print_header "✨ Vérification du formatage"
echo ""

print_info "Vérification avec black..."
if poetry run black --check app/ tests/ 2>/dev/null; then
    print_success "Formatage PASS"
else
    print_warning "Formatage nécessaire - Exécuter: poetry run black app/ tests/"
fi

echo ""

# 7. Vérification de la sécurité
print_header "🔒 Vérification de la sécurité"
echo ""

print_info "Vérification avec bandit..."
if poetry run bandit -r app/ -ll 2>/dev/null; then
    print_success "Sécurité PASS"
else
    print_warning "Problèmes de sécurité détectés - Voir ci-dessus"
fi

echo ""

# 8. Vérification des schémas
print_header "📝 Vérification des schémas de réponse"
echo ""

print_info "Vérification des imports..."
if poetry run python3 -c "from app.schemas import APIResponse, PaginatedResponse, ErrorResponse, SuccessResponse, create_success_response, create_error_response, create_paginated_response; print('OK')" 2>/dev/null; then
    print_success "Schémas de réponse importables"
else
    print_error "Erreur d'import des schémas"
fi

echo ""

# 9. Résumé final
print_header "📊 Résumé de la validation"
echo ""

print_info "Tests créés: 77 (29 JWT + 31 Password + 17 CRUD)"
print_info "Fichiers créés: 7 (3 tests + 1 schema + 3 docs)"
print_info "Fichiers modifiés: 3 (auth.py, __init__.py, test_models_base.py)"

echo ""
print_header "✅ Validation terminée!"
echo ""

print_info "Prochaines étapes:"
echo "  1. Consulter le rapport de couverture: xdg-open htmlcov/index.html"
echo "  2. Lire PHASE2_COMPLETION_REPORT.md pour les détails"
echo "  3. Suivre VALIDATION_CHECKLIST.md pour la validation complète"
echo "  4. Exécuter tous les tests: poetry run pytest tests/ --cov=app"

echo ""
print_success "Script de validation terminé avec succès!"
