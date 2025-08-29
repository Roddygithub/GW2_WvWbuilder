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
- GitHub Actions workflow: `.github/workflows/test-and-coverage.yml`
- Python 3.13 + Poetry are used in CI.
- Coverage report is uploaded as `backend/coverage.xml` (Codecov supported if configured).

### Badges
- Build status badge (GitHub Actions) and coverage badge (Codecov) are shown in `backend/README.md`. Ensure Codecov is enabled for the repository.

## Reporting Issues / Asking Questions
Open an issue with steps to reproduce, expected behavior, and any logs or screenshots.

Thanks for contributing!
