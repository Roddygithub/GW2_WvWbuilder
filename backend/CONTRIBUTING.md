# Guide de contribution – Backend GW2 Team Builder

## Introduction
Ce guide explique comment contribuer au backend.

## Prérequis
- Python 3.13
- Poetry
- Accès GitHub

## Installation
cd /home/roddy/Documents/GW2_WvWbuilder/backend
poetry install

## Tests
poetry run pytest --cov=app --cov-report=term-missing

## Ajouter des tests
- Placer les tests dans backend/tests/
- Utiliser TestClient pour les tests d'API

## Surcharge des dépendances
from app.api import deps
client.app.dependency_overrides[deps.get_db] = lambda: iter([test_db])
client.app.dependency_overrides[deps.get_current_active_superuser] = lambda: test_superuser

## Développement local
poetry run uvicorn app.main:app --reload

## Contribution
Créer une branche : git checkout -b feature/ma-fonctionnalite
Commits atomiques
PR vers develop ou main avec tests et documentation

## CI & Couverture
Workflow : .github/workflows/test-and-coverage.yml
Badges : Build Status, Coverage

## Questions
Ouvrez une issue avec :
- Étapes pour reproduire
- Comportement attendu
- Logs/captures si nécessaire
