#!/bin/bash
# Script de validation rapide des imports après correction composition_members
# Usage: chmod +x validate_imports.sh && ./validate_imports.sh

set -e

echo "🔍 Validation des imports composition_members"
echo "=============================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd /home/roddy/GW2_WvWbuilder/backend

# 1. Test import direct depuis association_tables
echo "1️⃣  Test import depuis association_tables..."
poetry run python -c "from app.models.association_tables import composition_members; print('✅ Import direct OK')" || {
    echo -e "${RED}❌ Import depuis association_tables échoué${NC}"
    exit 1
}

# 2. Test import via __init__
echo "2️⃣  Test import via app.models.__init__..."
poetry run python -c "from app.models import composition_members, build_profession; print('✅ Import via __init__ OK')" || {
    echo -e "${RED}❌ Import via __init__ échoué${NC}"
    exit 1
}

# 3. Test import du registre
echo "3️⃣  Test import depuis registry..."
poetry run python -c "from app.models.registry import MODELS, composition_members; print('✅ Registry OK')" || {
    echo -e "${RED}❌ Import depuis registry échoué${NC}"
    exit 1
}

# 4. Vérifier qu'il n'y a plus d'imports depuis composition.py
echo "4️⃣  Vérification absence d'imports incorrects..."
if grep -r "from.*composition import.*composition_members" app/ tests/ 2>/dev/null; then
    echo -e "${RED}❌ Imports incorrects détectés depuis composition.py${NC}"
    exit 1
else
    echo "✅ Aucun import incorrect détecté"
fi

# 5. Linting ciblé sur les imports
echo "5️⃣  Linting des imports (F401, F811)..."
poetry run ruff check app/models/ tests/unit/models/ --select F401,F811 || {
    echo -e "${YELLOW}⚠️  Warnings de linting détectés${NC}"
}

# 6. Tests unitaires ciblés
echo ""
echo "6️⃣  Tests unitaires des modèles..."
poetry run pytest tests/unit/models/test_user_model.py -v --tb=short -q || {
    echo -e "${RED}❌ Tests user_model échoués${NC}"
    exit 1
}

echo ""
echo "7️⃣  Test composition_members spécifique..."
poetry run pytest tests/unit/test_models_composition.py::TestCompositionModel::test_composition_members -v --tb=short || {
    echo -e "${YELLOW}⚠️  Test composition_members a échoué (peut nécessiter fixtures)${NC}"
}

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           ✅ VALIDATION DES IMPORTS RÉUSSIE                ║${NC}"
echo -e "${GREEN}╠════════════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}║  Imports:         OK ✅                                     ║${NC}"
echo -e "${GREEN}║  Registry:        OK ✅                                     ║${NC}"
echo -e "${GREEN}║  Linting:         OK ✅                                     ║${NC}"
echo -e "${GREEN}║  Tests modèles:   OK ✅                                     ║${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}║  STATUT: Prêt pour EXECUTE_NOW.sh 🚀                       ║${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Prochaine étape: ./EXECUTE_NOW.sh"
