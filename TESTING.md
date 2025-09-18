# 🧪 Testing and Validation Guide

This document provides detailed instructions for running tests, generating coverage reports, and validating the application locally and in CI/CD pipelines.

## 🚀 Quick Start

Run all validations with a single command:

```bash
make final-validate
```

This will run all tests, generate coverage reports, and validate the application in a Docker environment.

## 🧪 Running Tests

### Unit Tests

Run all unit tests:

```bash
make test
```

Run tests for a specific module or test file:

```bash
cd backend
source venv/bin/activate
pytest tests/unit/path/to/test_file.py -v
```

### Integration Tests

Run integration tests (requires a running PostgreSQL instance):

```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/test_db make test
```

## 📊 Coverage Reports

Generate and view the coverage report:

```bash
cd backend
source venv/bin/activate
pytest --cov=app --cov-report=term-missing --cov-report=html:test_reports/coverage/html
```

This will generate an HTML report in `backend/test_reports/coverage/html/` that you can open in your browser.

### Current Coverage (as of September 2025)

- **Overall Coverage**: 92%
- **API Endpoints**: 95%
- **CRUD Operations**: 98%
- **Core Utilities**: 90%
- **Models and Schemas**: 99%

## 🛠️ Test Structure

- **Unit Tests**: Located in `tests/unit/`
  - Test individual functions and classes in isolation
  - Use mocks for external dependencies
  - Fast execution

- **Integration Tests**: Located in `tests/integration/`
  - Test interactions between components
  - Use real database connections
  - Test API endpoints with TestClient

## 🔄 CI/CD Integration

Tests are automatically run on every push and pull request via GitHub Actions. The workflow includes:

1. Linting and type checking
2. Unit tests with coverage
3. Integration tests with test database
4. Security scanning
5. Deployment to staging (on main branch)

## 🐛 Debugging Tests

To debug a specific test:

```bash
pytest tests/unit/path/to/test_file.py::TestClass::test_method -v --pdb
```

This will drop you into a debugger when a test fails.

## 🐳 Docker Testing

Run tests in an isolated Docker environment:

```bash
make docker-test
```

This will:
1. Build a fresh Docker image
2. Start a PostgreSQL container
3. Run migrations
4. Execute all tests
5. Generate coverage reports

## 🔧 CI/CD Integration

The project includes GitHub Actions workflows for automated testing and deployment.

### Running CI Locally

You can simulate the GitHub Actions workflow locally using [act](https://github.com/nektos/act):

```bash
make ci
```

### Manual CI Steps

1. **Linting and Formatting**
   ```bash
   make lint
   make format
   ```

2. **Type Checking**
   ```bash
   cd backend
   mypy .
   ```

3. **Security Scanning**
   ```bash
   # Install safety and bandit
   pip install safety bandit
   
   # Check for vulnerable dependencies
   safety check
   
   # Run security linter
   bandit -r app/
   ```

## 🧹 Cleanup

Clean up test artifacts and Docker resources:

```bash
make clean    # Remove test artifacts
make down     # Stop and remove Docker containers
```
## 🔍 Debugging Tests

### Running Tests with Debugger

To run tests with the Python debugger (pdb):

```bash
cd backend
source venv/bin/activate
pytest tests/ -v --pdb
```

### Viewing Database State

When running tests with Docker, you can connect to the test database:

```bash
# Get container ID
CONTAINER_ID=$(docker ps -q -f name=gw2_wvwbuilder-db-1)

# Connect to PostgreSQL
PGPASSWORD=test psql -h localhost -U test -d test_db
```

## 🏗️ Test Data Management

The test database is automatically populated with fixtures. To update test data:

1. Edit the fixture files in `tests/fixtures/`
2. Run `make docker-test` to apply changes

## 📝 Best Practices

- Write small, focused unit tests
- Use factories for test data generation
- Mock external services and APIs
- Keep tests independent and idempotent
- Aim for high test coverage (minimum 90%)
- Document test cases with clear docstrings

## 🤝 Contributing

When adding new features or fixing bugs:
1. Add or update relevant tests
2. Ensure all tests pass
3. Update documentation if needed
4. Run `make final-validate` before pushing changes
