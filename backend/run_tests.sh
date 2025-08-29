#!/bin/bash

# Activer l'environnement virtuel si on utilise Poetry
if command -v poetry &> /dev/null; then
    echo "Using Poetry to run tests..."
    poetry run pytest "$@"
else
    echo "Poetry not found, running tests directly..."
    pytest "$@"
fi

# Générer un rapport HTML de couverture
if [ $? -eq 0 ]; then
    echo "Generating HTML coverage report..."
    coverage html
    echo "Coverage report generated at: $(pwd)/coverage_html/index.html"
fi
