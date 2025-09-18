#!/bin/bash
set -e

# Activate the virtualenv
if [ -d "backend/venv" ]; then
    source backend/venv/bin/activate
else
    echo "Virtual environment not found. Please set it up first."
    exit 1
fi

# Install test dependencies
echo "Installing test dependencies..."
pip install -q pytest pytest-cov pytest-asyncio httpx

# Run tests with coverage
echo "Running tests with coverage..."
cd backend
pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html:test_reports/coverage/html

# Check coverage
COVERAGE=$(coverage report --format=total --precision=0)
echo "Coverage: ${COVERAGE}%"

# Update README.md if needed
if ! grep -q "## Tests & Coverage" ../README.md; then
    echo -e "\n## Tests & Coverage\n\nTo run tests locally:\n\n\`\`\`bash\n# Install test dependencies\npip install -r requirements-test.txt\n\n# Run tests with coverage\npytest tests/ -v --cov=app --cov-report=term-missing\n\n# Generate HTML report\npytest --cov=app --cov-report=html:test_reports/coverage/html\n\`\`\`\n\nCoverage report is available at:\n- HTML: backend/test_reports/coverage/html/index.html\n" >> ../README.md
fi

echo "Test execution completed. Coverage: ${COVERAGE}%"

# Exit with non-zero status if coverage is below 90%
if [ "${COVERAGE}" -lt 90 ]; then
    echo "Error: Test coverage (${COVERAGE}%) is below the required 90%"
    exit 1
fi
