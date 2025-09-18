# Testing Guide

This document provides an overview of the testing strategy and instructions for running tests in the GW2 WvW Builder backend.

## Test Structure

Tests are organized into three main categories:

1. **Unit Tests** (`tests/unit/`): Test individual functions and classes in isolation.
2. **Integration Tests** (`tests/integration/`): Test interactions between components.
3. **API Tests** (`tests/api/`): Test API endpoints and their behavior.

## Running Tests

### Prerequisites

- Python 3.11+
- Poetry (recommended) or pip
- Dependencies installed (`poetry install` or `pip install -r requirements.txt`)

### Using the Test Runner Script

We provide a convenient script to run tests with various options:

```bash
# Make the script executable if needed
chmod +x run_tests.sh

# Run all tests with coverage
./run_tests.sh

# Run specific test types
./run_tests.sh --unit-only
./run_tests.sh --integration-only
./run_tests.sh --api-only

# Run without coverage report
./run_tests.sh --no-cov

# Set custom coverage threshold (default: 90%)
./run_tests.sh --threshold=95
```

### Running Tests Directly

You can also run tests directly using pytest:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_example.py

# Run specific test function
pytest tests/unit/test_example.py::test_function_name

# Run with coverage
pytest --cov=app --cov-report=term-missing
```

## Test Coverage

We aim to maintain at least 90% test coverage. The test runner will fail if coverage falls below this threshold.

To view the coverage report after running tests:

```bash
# Open HTML report (generated in htmlcov/)
open htmlcov/index.html  # On macOS
xdg-open htmlcov/index.html  # On Linux
```

## Writing Tests

### Best Practices

1. **Isolation**: Each test should be independent and not rely on the state from other tests.
2. **Descriptive Names**: Use clear, descriptive test function names.
3. **Fixtures**: Use pytest fixtures for common test data and setup.
4. **Mocks**: Use `unittest.mock` or `pytest-mock` to isolate components.

### Example Test

```python
def test_example_function():
    # Setup
    input_data = {...}
    expected = {...}
    
    # Execute
    result = example_function(input_data)
    
    # Assert
    assert result == expected
```

## Continuous Integration

Tests are automatically run on push and pull requests via GitHub Actions. The workflow includes:

- Running all tests
- Checking code coverage
- Uploading coverage reports to Codecov
- Running type checking with mypy
- Running linting with flake8

## Debugging Tests

To debug a failing test:

```bash
# Run with pdb on failure
pytest --pdb tests/path/to/test.py::test_name

# Run with detailed logging
pytest -vvs tests/path/to/test.py::test_name
```

## Performance Considerations

- Use `-n auto` to run tests in parallel with pytest-xdist
- Mark slow tests with `@pytest.mark.slow`
- Use `--durations=10` to identify slow tests

## Test Data

Test data is managed using factory_boy. Factories are located in `tests/factories.py`.
