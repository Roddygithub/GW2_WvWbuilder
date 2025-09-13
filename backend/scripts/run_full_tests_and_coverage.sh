#!/bin/bash
set -e

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Create test reports directory if it doesn't exist
mkdir -p "$PROJECT_ROOT/test_reports/coverage/html"

cd "$PROJECT_ROOT"
echo "Running tests with coverage from $(pwd)..."

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Install test dependencies if needed
pip install -e ".[test]"

# Run tests with coverage
python -m pytest \
    --cov=app \
    --cov-report=term-missing \
    --cov-report=html:test_reports/coverage/html \
    --cov-report=xml:test_reports/coverage.xml \
    --junitxml=test_reports/junit.xml \
    -v tests/

# Check if coverage meets requirements
coverage report --fail-under=90

# Generate coverage badge
coverage-badge -o test_reports/coverage/coverage.svg -f

echo "Coverage report generated at $PROJECT_ROOT/test_reports/coverage/html/index.html"
