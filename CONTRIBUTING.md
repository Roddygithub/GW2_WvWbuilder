# Contributing to GW2 Team Builder (Backend)

Thank you for your interest in contributing! This document explains how to set up your environment, run tests, interpret coverage, and follow our conventions.

## Introduction
The backend is a FastAPI application using SQLAlchemy 2.0 and Pydantic v2. Tests are run with pytest and Poetry manages dependencies.

## Prerequisites
- Python 3.13
- Poetry installed (https://python-poetry.org/)
- Access to this repository

## Installation
```bash
cd backend
poetry install
```

## Running Tests and Coverage
```bash
poetry run pytest --cov=app --cov-report=term-missing
```
- A summary shows which lines are not covered per module ("Missing").
- Target coverage: ≥ 90% overall. Please add tests if your change reduces coverage.

### Warnings & Filtering
- Gzip-related `PytestUnraisableExceptionWarning` are filtered globally via pytest `addopts`.
- Pydantic v2 deprecations may appear from dependencies; application code uses v2 patterns (`ConfigDict`, `json_schema_extra`).
- SQLAlchemy 2.0 warnings should not appear; if they do, prefer updating code rather than silencing, except for harmless teardown notices in tests.

### Reading the Coverage Output
- Each module lists uncovered line numbers under the "Missing" column.
- Prefer small, focused tests to cover specific branches (e.g., 400/403/404/422 paths).

## Adding New Tests
- Place tests under `backend/tests/` with names `test_*.py`.
- For API tests, use FastAPI `TestClient` via our test fixtures.

### Overriding Dependencies in Tests
To isolate behavior and permissions, override FastAPI dependencies:
```python
from app.api import deps

# Override DB dependency to use the test session
client.app.dependency_overrides[deps.get_db] = lambda: iter([db_session])

# Act as a specific user (e.g., superuser)
client.app.dependency_overrides[deps.get_current_active_superuser] = lambda: su_user
client.app.dependency_overrides[deps.get_current_active_user] = lambda: normal_user
```
Tip: keep overrides minimal and restore them after each test if needed to avoid cross-test interference.

## Code Conventions
- Pydantic v2:
  - Use `ConfigDict(from_attributes=True)` for ORM models.
  - Use `json_schema_extra={"example": ...}` instead of `example=` in `Field(...)`.
- SQLAlchemy 2.0:
  - Use the modern Declarative mapping. Relationships are defined in `app/models/models.py`.
  - Many-to-many examples: `composition_members` and `user_roles` association tables.
- Linting/formatting: prefer Black and isort.

## Running the Backend Locally (optional)

### Documenting New API Endpoints

When adding or modifying an API endpoint, documentation is crucial. Please update the following files:

1.  **`backend/README.md`**: Add the new endpoint to the `Available Endpoints` section. Include a `curl` example for easy testing.
    ```markdown
    - **`GET /api/v1/new-endpoint/`**: Description of the endpoint.
      ```bash
      curl -X GET "http://localhost:8000/api/v1/new-endpoint/" -H "Authorization: Bearer <token>"
      ```
    ```

2.  **OpenAPI Schema (Code)**: Use Pydantic's `Field` to provide clear descriptions and examples directly in your schemas (`app/schemas/`). This will automatically enrich the interactive documentation at `/docs`.

3.  **Performance Tests**: If the endpoint is critical, consider adding a performance test in `backend/tests/api/test_builds_performance.py` to monitor its latency.

```bash
cd backend
poetry run uvicorn app.main:app --reload
```
Visit: http://127.0.0.1:8000/docs

## Contribution Process
1. Create a feature branch: `git checkout -b feature/my-change` (or `fix/...`).
2. Make changes with clear, small commits.
3. Ensure tests pass locally and coverage stays ≥ 90%.
4. Open a Pull Request to `develop` or `main` with:
   - Description of changes
   - Test plan and coverage
5. CI will run tests and coverage on your PR.

## CI & Coverage

### Workflow GitHub Actions
Le workflow CI/CD est configuré dans `.github/workflows/test-and-coverage.yml` et s'exécute sur :
- Push et pull requests vers les branches `main` et `develop`
- Modification des fichiers du backend ou de la configuration CI

### Fonctionnalités du workflow
- **Tests automatisés** : Exécution des tests unitaires et d'intégration
- **Couverture de code** : Génération de rapports de couverture (XML et HTML)
- **Intégration Codecov** : Téléversement automatique des rapports de couverture
- **Artefacts** : Stockage des résultats des tests et des rapports pour débogage

### Badges
Les badges suivants sont disponibles dans le README principal :
- Statut des tests (GitHub Actions)
- Couverture du code (Codecov)
- Version Python
- Style de code (Black, isort)
- Licence MIT

### Vérification locale
Pour exécuter les mêmes vérifications que le CI localement :
```bash
# Installer les dépendances de développement
poetry install --with dev

# Exécuter les tests avec couverture
./backend/run_tests.sh
```

### Rapports de couverture
Les rapports de couverture sont disponibles :
1. **En local** : `backend/htmlcov/index.html`
2. **Dans les artefacts CI** : Téléchargeables depuis l'onglet "Actions" de GitHub
3. **En ligne** : Sur [Codecov](https://codecov.io/gh/Roddygithub/GW2_WvWbuilder) (après activation)

### Configuration requise pour les PR
- La couverture doit rester ≥ 90%
- Tous les tests doivent passer
- Le code doit être formaté avec Black et isort

## Reporting Issues / Asking Questions
Open an issue with steps to reproduce, expected behavior, and any logs or screenshots.

Thanks for contributing!
