#!/bin/bash

# GW2_WvWbuilder - Deployment Validation Script
# This script validates that the backend is ready for deployment

set -e

echo "============================================================"
echo "🎯 GW2_WvWbuilder - Deployment Validation"
echo "============================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0

# Function to check and report
check() {
    local name=$1
    local command=$2
    
    echo -n "Checking $name... "
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        ((FAILED++))
        return 1
    fi
}

echo "📋 Running validation checks..."
echo ""

# 1. Check Python version
check "Python 3.11+" "python3 --version | grep -E '3\.(11|12)'"

# 2. Check Poetry installation
check "Poetry" "poetry --version"

# 3. Check backend directory
check "Backend directory" "test -d backend"

# 4. Check pyproject.toml
check "pyproject.toml" "test -f backend/pyproject.toml"

# 5. Check Dockerfile
check "Dockerfile" "test -f backend/Dockerfile"

# 6. Check docker-compose.yml
check "docker-compose.yml" "test -f docker-compose.yml"

# 7. Check .env.example
check ".env.example" "test -f backend/.env.example"

# 8. Check main application file
check "app/main.py" "test -f backend/app/main.py"

# 9. Check tests directory
check "tests directory" "test -d backend/tests"

# 10. Check CI/CD workflows
check "GitHub Actions" "test -f .github/workflows/tests.yml"

# 11. Check documentation
check "QUICK_START.md" "test -f QUICK_START.md"
check "API_READY.md" "test -f backend/API_READY.md"
check "FINAL_DELIVERY_REPORT.md" "test -f backend/FINAL_DELIVERY_REPORT.md"
check "EXECUTIVE_FINAL_REPORT.md" "test -f EXECUTIVE_FINAL_REPORT.md"

# 12. Check if dependencies are installed
echo -n "Checking Poetry dependencies... "
cd backend
if poetry check > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  WARN - Run 'poetry install'${NC}"
fi
cd ..

# 13. Try to import the application
echo -n "Checking application imports... "
cd backend
if poetry run python -c "from app.main import app" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC}"
    ((FAILED++))
fi
cd ..

echo ""
echo "============================================================"
echo "📊 Validation Results"
echo "============================================================"
echo ""
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED!${NC}"
    echo ""
    echo "🚀 Backend is READY for deployment!"
    echo ""
    echo "📚 Next Steps:"
    echo "   1. Review EXECUTIVE_FINAL_REPORT.md for complete status"
    echo "   2. Follow QUICK_START.md for deployment instructions"
    echo "   3. Read API_READY.md for frontend integration"
    echo ""
    echo "Deployment Options:"
    echo "   - Local: cd backend && poetry run uvicorn app.main:app --reload"
    echo "   - Docker: docker-compose up -d"
    echo ""
    exit 0
else
    echo -e "${RED}❌ VALIDATION FAILED${NC}"
    echo ""
    echo "Please fix the failed checks before deploying."
    echo "See documentation for troubleshooting."
    echo ""
    exit 1
fi
