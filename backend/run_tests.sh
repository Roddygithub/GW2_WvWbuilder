#!/bin/bash

# Exit on error
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default test paths
TEST_PATHS=("tests/unit" "tests/integration" "tests/api")
COV_THRESHOLD=90

# Parse command line arguments
RUN_UNIT=true
RUN_INTEGRATION=true
RUN_API=true
RUN_COVERAGE=true
GENERATE_REPORT=true

while [[ $# -gt 0 ]]; do
    case $1 in
        --unit-only)
            RUN_INTEGRATION=false
            RUN_API=false
            shift
            ;;
        --integration-only)
            RUN_UNIT=false
            RUN_API=false
            shift
            ;;
        --api-only)
            RUN_UNIT=false
            RUN_INTEGRATION=false
            shift
            ;;
        --no-cov)
            RUN_COVERAGE=false
            shift
            ;;
        --no-report)
            GENERATE_REPORT=false
            shift
            ;;
        --threshold=*)
            COV_THRESHOLD="${1#*=}"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Build test paths array based on selected test types
TEST_PATHS=()
if [ "$RUN_UNIT" = true ]; then
    TEST_PATHS+=("tests/unit")
fi
if [ "$RUN_INTEGRATION" = true ]; then
    TEST_PATHS+=("tests/integration")
fi
if [ "$RUN_API" = true ]; then
    TEST_PATHS+=("tests/api")
fi

if [ ${#TEST_PATHS[@]} -eq 0 ]; then
    echo -e "${YELLOW}No test types selected. Running all tests.${NC}"
    TEST_PATHS=("tests/unit" "tests/integration" "tests/api")
fi

# Build pytest arguments
PYTEST_ARGS=("-v" "--color=yes" "--durations=10")
if [ "$RUN_COVERAGE" = true ]; then
    PYTEST_ARGS+=(
        "--cov=app"
        "--cov-report=term-missing"
        "--cov-fail-under=$COV_THRESHOLD"
    )
    if [ "$GENERATE_REPORT" = true ]; then
        PYTEST_ARGS+=(
            "--cov-report=html"
            "--cov-report=xml"
        )
    fi
fi

# Add test paths to pytest args
PYTEST_ARGS+=("${TEST_PATHS[@]}")

# Function to run tests with appropriate command
run_tests() {
    if command -v poetry &> /dev/null; then
        echo -e "${GREEN}Using Poetry to run tests...${NC}"
        poetry run pytest "${PYTEST_ARGS[@]}"
    else
        echo -e "${YELLOW}Poetry not found, running tests directly...${NC}"
        python -m pytest "${PYTEST_ARGS[@]}"
    fi
}

# Run tests
run_tests

# Generate badge if coverage report exists and coverage is enabled
if [ "$RUN_COVERAGE" = true ] && [ "$GENERATE_REPORT" = true ]; then
    if command -v coverage-badge &> /dev/null; then
        echo -e "${GREEN}Generating coverage badge...${NC}"
        coverage-badge -o coverage.svg -f
    else
        echo -e "${YELLOW}coverage-badge not found. Install with 'pip install coverage-badge'${NC}"
    fi
    
    echo -e "${GREEN}Coverage report generated at: $(pwd)/htmlcov/index.html${NC}"
    echo -e "${GREEN}XML report generated at: $(pwd)/coverage.xml${NC}"
fi

echo -e "${GREEN}Test run completed!${NC}"
