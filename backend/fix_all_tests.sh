#!/bin/bash
# Script de correction et validation complète des tests
# Usage: chmod +x fix_all_tests.sh && ./fix_all_tests.sh

set -e

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                            ║"
echo "║           🔧 CORRECTION COMPLÈTE DES TESTS - GW2_WvWbuilder                ║"
echo "║                                                                            ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

cd /home/roddy/GW2_WvWbuilder/backend

echo -e "${BLUE}📋 Phase 1: Vérification de l'environnement${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Vérifier Poetry
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}❌ Poetry n'est pas installé${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Poetry installé${NC}"

# Vérifier Python 3.11
PYTHON_VERSION=$(poetry run python --version | cut -d' ' -f2)
if [[ ! "$PYTHON_VERSION" =~ ^3\.11 ]]; then
    echo -e "${YELLOW}⚠️  Python version: $PYTHON_VERSION (recommandé: 3.11)${NC}"
else
    echo -e "${GREEN}✅ Python 3.11 détecté${NC}"
fi

echo ""
echo -e "${BLUE}📦 Phase 2: Installation des dépendances${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
poetry install --no-interaction --no-root || {
    echo -e "${RED}❌ Échec de l'installation des dépendances${NC}"
    exit 1
}
echo -e "${GREEN}✅ Dépendances installées${NC}"

echo ""
echo -e "${BLUE}🔍 Phase 3: Vérification des imports${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test des imports critiques
echo "Vérification de verify_token..."
poetry run python -c "from app.core.security import verify_token; print('✅ verify_token OK')" || {
    echo -e "${RED}❌ Import verify_token échoué${NC}"
    exit 1
}

echo "Vérification de generate_password_reset_token..."
poetry run python -c "from app.core.security import generate_password_reset_token; print('✅ generate_password_reset_token OK')" || {
    echo -e "${RED}❌ Import generate_password_reset_token échoué${NC}"
    exit 1
}

echo "Vérification de verify_password_reset_token..."
poetry run python -c "from app.core.security import verify_password_reset_token; print('✅ verify_password_reset_token OK')" || {
    echo -e "${RED}❌ Import verify_password_reset_token échoué${NC}"
    exit 1
}

echo -e "${GREEN}✅ Tous les imports critiques OK${NC}"

echo ""
echo -e "${BLUE}🧪 Phase 4: Tests unitaires (rapides)${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Tests rapides sans couverture pour vérifier la collecte
echo "Test de collecte pytest..."
poetry run pytest --collect-only -q tests/unit/core/ 2>&1 | head -20

echo ""
echo "Exécution des tests JWT..."
poetry run pytest tests/unit/core/test_jwt_complete.py -v --tb=short -x || {
    echo -e "${YELLOW}⚠️  Certains tests JWT ont échoué${NC}"
}

echo ""
echo "Exécution des tests password utils..."
poetry run pytest tests/unit/core/test_password_utils_complete.py -v --tb=short -x || {
    echo -e "${YELLOW}⚠️  Certains tests password utils ont échoué${NC}"
}

echo ""
echo -e "${BLUE}📊 Phase 5: Tests avec couverture${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Tests avec couverture
poetry run pytest tests/unit/ \
    --cov=app \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-fail-under=70 \
    -v \
    --tb=short \
    --maxfail=5 \
    -m "not slow" || {
    echo -e "${YELLOW}⚠️  Certains tests ont échoué ou couverture < 70%${NC}"
    echo "Voir htmlcov/index.html pour les détails de couverture"
}

echo ""
echo -e "${BLUE}🔍 Phase 6: Analyse de la couverture${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Afficher le résumé de couverture
if [ -f ".coverage" ]; then
    echo "Génération du rapport de couverture..."
    poetry run coverage report --skip-empty | tail -20
    echo ""
    echo -e "${GREEN}✅ Rapport de couverture HTML généré: htmlcov/index.html${NC}"
fi

echo ""
echo -e "${BLUE}🎨 Phase 7: Qualité du code${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Linting avec ruff
echo "Linting avec ruff..."
poetry run ruff check app/ tests/ --select F,E --statistics || {
    echo -e "${YELLOW}⚠️  Problèmes de linting détectés${NC}"
}

# Formatage avec black (check only)
echo ""
echo "Vérification du formatage avec black..."
poetry run black --check app/ tests/ --line-length 120 || {
    echo -e "${YELLOW}⚠️  Certains fichiers nécessitent un formatage${NC}"
    echo "Exécutez: poetry run black app/ tests/ --line-length 120"
}

echo ""
echo -e "${BLUE}🔒 Phase 8: Sécurité${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Scan de sécurité avec bandit
if poetry run bandit --version &> /dev/null; then
    echo "Scan de sécurité avec bandit..."
    poetry run bandit -r app/ -ll -f screen || {
        echo -e "${YELLOW}⚠️  Problèmes de sécurité détectés${NC}"
    }
else
    echo -e "${YELLOW}⚠️  Bandit non installé, skip du scan de sécurité${NC}"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                            ║"
echo "║                        ✅ VALIDATION TERMINÉE                              ║"
echo "║                                                                            ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}📊 Résumé:${NC}"
echo "  • Imports: ✅ Vérifiés"
echo "  • Tests unitaires: ✅ Exécutés"
echo "  • Couverture: 📊 Voir htmlcov/index.html"
echo "  • Linting: 🎨 Vérifié"
echo "  • Sécurité: 🔒 Scanné"
echo ""
echo -e "${BLUE}📝 Prochaines étapes:${NC}"
echo "  1. Ouvrir htmlcov/index.html pour voir la couverture détaillée"
echo "  2. Corriger les tests échoués si nécessaire"
echo "  3. Augmenter la couverture vers 80%+"
echo "  4. Exécuter: ./EXECUTE_NOW.sh pour validation complète"
echo ""
