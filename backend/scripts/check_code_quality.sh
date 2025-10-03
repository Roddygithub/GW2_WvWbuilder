#!/bin/bash

# Vérification du formatage avec black
echo "Vérification du formatage avec black..."
black --check .

# Vérification du tri des imports avec isort
echo "\nVérification du tri des imports avec isort..."
isort --check-only .

# Vérification des types avec mypy
echo "\nVérification des types avec mypy..."
mypy .

# Exécution des tests avec couverture
echo "\nExécution des tests avec couverture..."
pytest --cov=app --cov-report=term-missing --cov-fail-under=90

# Vérification de la qualité du code avec flake8
echo "\nVérification de la qualité du code avec flake8..."
flake8 .
