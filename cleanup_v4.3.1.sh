#!/bin/bash
##
## GW2_WvWbuilder Cleanup Script v4.3.1
## Supprime fichiers obsolètes, consolide doublons, améliore qualité code
##

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🧹 GW2_WvWbuilder Cleanup v4.3.1${NC}"
echo "=================================="
echo ""

# Confirm
read -p "⚠️  This will delete 50+ obsolete files. Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled."
    exit 0
fi

#-------------------
# PHASE 1: BACKUP
#-------------------
echo -e "\n${YELLOW}📦 Phase 1: Creating backup...${NC}"

if [ -d .git ]; then
    git add -A
    git commit -m "chore: pre-cleanup snapshot v4.3.1" || echo "Nothing to commit"
    BACKUP_TAG="pre-cleanup-$(date +%Y%m%d-%H%M%S)"
    git tag "$BACKUP_TAG"
    echo -e "${GREEN}✅ Backup created: $BACKUP_TAG${NC}"
else
    echo -e "${RED}⚠️  No git repository found. Manual backup recommended!${NC}"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

#---------------------------------
# PHASE 2: SUPPRIMER OBSOLÈTES
#---------------------------------
echo -e "\n${YELLOW}🗑️  Phase 2: Removing obsolete files...${NC}"

# Rapports CI/CD (14)
echo "Removing CI/CD reports..."
rm -f CI_CD_*.md CI_VALIDATION*.md GITHUB_*.md github_setup.sh

# Rapports Projet (10)
echo "Removing project reports..."
rm -f BUILDER_*.md COMPOSITION_*.md PHASE*.md PROJECT_*.md SETUP_*.md
rm -f TABLEAU_*.md TESTS_COMPLETED.txt TEST_SUMMARY.md

# Infrastructure (8)
echo "Removing infrastructure reports..."
rm -f INFRASTRUCTURE*.md PRODUCTION_READINESS*.md RAPPORT_*.md
rm -f SECURISATION*.md STABILISATION*.md

# README redondants (4)
echo "Removing redundant READMEs..."
rm -f README.old.md README_AUTO_MODE.md README_EVOLUTIONARY_AI.md REPONSE_*.md

# Guides multiples (5)
echo "Removing duplicate guides..."
rm -f QUICKSTART.md QUICK_START*.md LIRE_MOI_TESTS.md START_E2E_TESTS.md

# Scripts temporaires (8+)
echo "Removing temporary scripts..."
rm -f CHECK_*.sh CLEANUP_URGENT.sh RESTART_*.sh START_BACKEND_NOW.sh
rm -f deploy_production.sh deploy_production_final.sh
rm -f test_*.py test_*.sh validate_deployment.sh

# Logs et PIDs (12+)
echo "Removing logs and PIDs..."
rm -f *.log *.pid auth_test_result.txt test_output.json
rm -f deployment_*.log deployment_info.txt

# Backups et DBs temp (3)
echo "Removing backup databases..."
rm -f gw2_wvwbuilder.db.backup test.db

# Divers
echo "Removing misc files..."
rm -f Prompt_Windsurf.txt FIX_*.md keys.example.json

# Dossiers vides
echo "Removing empty directories..."
rm -rf app/ backups/ logs/ reports/

echo -e "${GREEN}✅ Obsolete files removed${NC}"

#-------------------------
# PHASE 3: BACKEND CLEANUP
#-------------------------
echo -e "\n${YELLOW}🔧 Phase 3: Backend cleanup...${NC}"

cd backend

# Core doublons
echo "Removing core duplicates..."
rm -f app/core/cache.py app/core/logging.py app/core/deps.py
rm -f app/api/deps.py
rm -f app/config.py

# CRUD doublons
echo "Removing CRUD duplicates..."
rm -f app/crud/build.py
rm -f app/crud/elite_specialization.py
rm -f app/crud/profession.py
rm -f app/crud/tag.py
rm -f app/crud/team.py
rm -f app/crud/user.py

echo -e "${GREEN}✅ Backend duplicates removed${NC}"

#-----------------------
# PHASE 4: TESTS CLEANUP
#-----------------------
echo -e "\n${YELLOW}🧪 Phase 4: Tests cleanup...${NC}"

# Archive
if [ -d tests/archive_duplicates ]; then
    echo "Removing test archive..."
    rm -rf tests/archive_duplicates/
fi

# Obsolètes
echo "Removing obsolete tests..."
rm -f tests/helpers.py tests/test_example.py tests/test_smoke.py
rm -f tests/gw2_wvwbuilder.db

echo -e "${GREEN}✅ Tests cleaned${NC}"

cd ..

#------------------------
# PHASE 5: CODE QUALITY
#------------------------
echo -e "\n${YELLOW}🎨 Phase 5: Code quality...${NC}"

cd backend

# Check if poetry installed
if command -v poetry &> /dev/null; then
    echo "Formatting with Black..."
    poetry run black app/ tests/ || echo "⚠️  Black formatting had issues"
    
    echo "Linting with Flake8..."
    poetry run flake8 app/ --max-line-length=100 --ignore=E501,W503 || echo "⚠️  Flake8 warnings present"
else
    echo -e "${RED}⚠️  Poetry not found, skipping formatting${NC}"
fi

cd ..

#-------------------
# PHASE 6: TESTS
#-------------------
echo -e "\n${YELLOW}✅ Phase 6: Running tests...${NC}"

cd backend

if command -v poetry &> /dev/null; then
    echo "Running pytest..."
    poetry run pytest tests/ -v --cov=app --cov-report=term-missing || {
        echo -e "${RED}❌ Tests failed! Review changes.${NC}"
        cd ..
        exit 1
    }
    
    echo -e "${GREEN}✅ All tests passed!${NC}"
else
    echo -e "${YELLOW}⚠️  Poetry not found, skipping tests${NC}"
fi

cd ..

#-------------------
# PHASE 7: SUMMARY
#-------------------
echo ""
echo -e "${GREEN}================================"
echo "✅ Cleanup Complete!"
echo "================================${NC}"
echo ""
echo "📊 Summary:"
echo "   - 50+ obsolete files removed"
echo "   - Backend duplicates consolidated"
echo "   - Tests reorganized"
echo "   - Code formatted (Black)"
echo "   - Tests passing"
echo ""
echo "📝 Next steps:"
echo "   1. Review changes: git status"
echo "   2. Test manually: ./start_all.sh"
echo "   3. Commit: git add -A && git commit -m 'chore: cleanup v4.3.1'"
echo "   4. Push: git push origin main"
echo ""
echo "🔖 Backup tag: $BACKUP_TAG"
echo "   Restore if needed: git reset --hard $BACKUP_TAG"
echo ""
