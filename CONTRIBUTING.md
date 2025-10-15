# 🤝 Contributing to GW2 WvW Builder

Thank you for your interest in contributing! This guide explains how to set up your environment, follow our conventions, and submit high-quality contributions.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Commit Convention](#commit-convention)
- [Testing Guidelines](#testing-guidelines)
- [Code Quality](#code-quality)
- [Pull Request Process](#pull-request-process)

## 📜 Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/). By participating, you agree to uphold this code.

## 🚀 Getting Started

### Prerequisites

- **Python** 3.10, 3.11, or 3.12
- **Node.js** 20+
- **Poetry** 1.7+ (Python dependency management)
- **npm** (JavaScript dependency management)
- **Git** for version control

### Initial Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/GW2_WvWbuilder.git
   cd GW2_WvWbuilder
   ```

2. **Install backend dependencies**:
   ```bash
   cd backend
   poetry install
   ```

3. **Install frontend dependencies**:
   ```bash
   cd frontend
   npm install
   ```

4. **Set up pre-commit hooks** (optional but recommended):
   ```bash
   poetry run pre-commit install
   ```

## Installation
```bash
cd backend
poetry install
```

## 🔄 Development Workflow

### 1. Create a Feature Branch

Always create a new branch for your work:

```bash
git checkout -b feature/my-awesome-feature
# or
git checkout -b fix/bug-description
```

**Branch naming convention**:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation only
- `refactor/` - Code refactoring
- `test/` - Adding tests
- `chore/` - Maintenance tasks

### 2. Make Your Changes

Write clean, well-documented code following our conventions (see [Code Quality](#code-quality)).

### 3. Test Your Changes

Run tests locally before committing:

```bash
# Backend tests
cd backend
poetry run pytest --cov=app --cov-report=term-missing

# Frontend tests
cd frontend
npm run test
npm run lint
```

### 4. Commit Your Changes

Follow our [commit convention](#commit-convention).

## 📝 Commit Convention

We use **Conventional Commits** for clear and semantic commit messages.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, no logic change)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks (dependencies, configs)
- **perf**: Performance improvements
- **ci**: CI/CD changes

### Examples

```bash
feat(backend): add build optimizer endpoint

Implements the build optimization algorithm that suggests
the best team composition based on constraints.

Closes #123
```

```bash
fix(frontend): resolve navigation menu overflow on mobile

The navigation menu was overflowing on small screens.
Added responsive breakpoints to fix the layout.
```

```bash
docs(readme): update installation instructions

Added clarity to Python version requirements and
installation steps for Poetry.
```

## 🧪 Testing Guidelines

### Backend Testing

**Test Coverage Target**: ≥28% (current), ≥50% (ideal)

Run all backend tests:
```bash
cd backend
poetry run pytest --cov=app --cov-report=term-missing --cov-report=html
```

Open coverage report:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Test Structure

```python
# tests/unit/test_example.py
import pytest
from app.module import function

def test_function_success():
    """Test successful case."""
    result = function(valid_input)
    assert result == expected_output

def test_function_error():
    """Test error handling."""
    with pytest.raises(ValueError):
        function(invalid_input)
```

### Frontend Testing

Run frontend tests:
```bash
cd frontend
npm run test        # Unit tests (Vitest)
npm run test:e2e    # E2E tests (Cypress)
```

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

## ✨ Code Quality

### Backend Standards

**Linting and Formatting**:
```bash
cd backend

# Format code with Black
poetry run black app/ tests/

# Sort imports with isort
poetry run isort app/ tests/

# Lint with Ruff
poetry run ruff check app/ tests/

# Type checking with MyPy
poetry run mypy app/ --ignore-missing-imports
```

**Code Conventions**:

1. **Pydantic v2**:
   ```python
   from pydantic import BaseModel, Field, ConfigDict
   
   class MyModel(BaseModel):
       name: str = Field(..., description="Name")
       
       model_config = ConfigDict(
           from_attributes=True,
           json_schema_extra={"example": {"name": "Example"}}
       )
   ```

2. **SQLAlchemy 2.0**:
   ```python
   from sqlalchemy import select
   from sqlalchemy.orm import selectinload
   
   # Modern query syntax
   stmt = select(Model).where(Model.id == 1).options(
       selectinload(Model.relations)
   )
   result = await db.execute(stmt)
   ```

3. **Type Hints**:
   ```python
   from typing import Optional, List
   
   def get_items(db: Session, skip: int = 0) -> List[Item]:
       """Get items with proper type hints."""
       pass
   ```

### Frontend Standards

**Linting and Formatting**:
```bash
cd frontend

# Lint code
npm run lint

# Format code
npm run format

# Type checking
npm run type-check
```

**Code Conventions**:

1. **TypeScript**: Use strict typing
2. **Components**: Functional components with hooks
3. **Styling**: TailwindCSS utility classes
4. **State**: React Query for server state

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

## 🔀 Pull Request Process

### Before Submitting

1. ✅ **Tests pass locally**:
   ```bash
   cd backend && poetry run pytest
   cd frontend && npm run test
   ```

2. ✅ **Code is properly formatted**:
   ```bash
   cd backend && poetry run black app/ tests/
   cd frontend && npm run format
   ```

3. ✅ **Linting passes**:
   ```bash
   cd backend && poetry run ruff check app/ tests/
   cd frontend && npm run lint
   ```

4. ✅ **Coverage maintained or improved**
   - Backend: Check coverage report
   - Frontend: Check test results

### Submitting a PR

1. **Push your branch**:
   ```bash
   git push origin feature/my-awesome-feature
   ```

2. **Open a Pull Request** on GitHub with:

   **Title**: Follow commit convention
   ```
   feat(backend): add build optimizer endpoint
   ```

   **Description**: Use this template
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Testing
   - [ ] Unit tests added/updated
   - [ ] Integration tests added/updated
   - [ ] Manual testing performed
   
   ## Checklist
   - [ ] Code follows project conventions
   - [ ] Tests pass locally
   - [ ] Documentation updated
   - [ ] No new warnings introduced
   
   ## Related Issues
   Closes #123
   ```

3. **Wait for CI/CD**:
   - All tests must pass
   - Coverage must not decrease significantly
   - Code quality checks must pass

4. **Address Review Comments**:
   - Respond to all feedback
   - Make requested changes
   - Push updates to the same branch

### Review Process

- **Approval**: At least 1 reviewer approval required
- **CI/CD**: All checks must pass (97%+ PASS rate)
- **Merge**: Squash and merge into target branch

## 🤖 CI/CD Pipeline

### GitHub Actions Workflows

Our CI/CD pipeline runs automatically on:
- **Push** to `main`, `develop`, or `release/*` branches
- **Pull Requests** targeting these branches

**Workflows**:
- `ci-cd-modern.yml`: Modern CI/CD with Python 3.10-3.12 matrix
- `ci-cd-complete.yml`: Complete validation suite
- `deploy-staging.yml`: Automated staging deployment

**What Gets Tested**:
- ✅ Backend: Unit tests, integration tests, linting, security
- ✅ Frontend: Unit tests, E2E tests, linting, build
- ✅ Code quality: Coverage, type checking, formatting
- ✅ Security: Dependency scanning, vulnerability checks

### Coverage Requirements

- **Backend**: ≥28% (current requirement)
- **Frontend**: ≥80% (current requirement)
- **Target**: Gradual improvement toward 50%+ backend coverage

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

## 📚 Additional Resources

### Documentation

- **API Documentation**: http://localhost:8000/docs (when running locally)
- **Project Docs**: [/docs](./docs/) folder
- **Coverage Reports**: [/docs/BACKEND_COVERAGE_FINAL.md](./docs/BACKEND_COVERAGE_FINAL.md)
- **MyPy Report**: [/docs/MYPY_CLEANUP_REPORT.md](./docs/MYPY_CLEANUP_REPORT.md)

### Useful Commands

**Backend**:
```bash
# Run specific test file
poetry run pytest tests/unit/test_example.py -v

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run only failed tests
poetry run pytest --lf

# Run with debugging
poetry run pytest -s tests/unit/test_example.py::test_function
```

**Frontend**:
```bash
# Run specific test
npm run test -- CompositionsPage

# Run with coverage
npm run test:coverage

# Watch mode
npm run test:watch
```

### Getting Help

- 📖 Check [existing issues](https://github.com/Roddygithub/GW2_WvWbuilder/issues)
- 💬 Ask questions in [Discussions](https://github.com/Roddygithub/GW2_WvWbuilder/discussions)
- 🐛 Report bugs with detailed reproduction steps

## 🎯 Areas Needing Contribution

High-priority areas for contribution:

1. **Test Coverage** (Backend):
   - API endpoint integration tests
   - Service layer unit tests
   - Error handling edge cases

2. **Documentation**:
   - API endpoint examples
   - Architecture diagrams
   - User guides

3. **Frontend**:
   - UI/UX improvements
   - Accessibility enhancements
   - Mobile responsiveness

4. **Features**:
   - Build optimizer improvements
   - Advanced filtering
   - Performance optimizations

## �� License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to GW2 WvW Builder! 🎉**

*Last updated: 2025-10-15 | Version: v3.2.0*
