# Makefile for GW2 WvW Builder Backend

.PHONY: install test test-cov test-coverage lint format clean help

# Install dependencies
install:
	poetry install

# Run tests
TEST_PATH=./tests

# Run all tests
test:
	poetry run pytest $(TEST_PATH) -v

# Run tests with coverage report in terminal
test-cov:
	poetry run pytest --cov=app --cov-report=term-missing $(TEST_PATH)

# Run tests with HTML coverage report
test-coverage:
	poetry run pytest --cov=app --cov-report=term-missing --cov-report=html:test_reports/coverage/html $(TEST_PATH)

# Run linter
lint:
	poetry run black --check .
	poetry run isort --check-only .
	poetry run mypy .

# Format code
format:
	poetry run black .
	poetry run isort .

# Clean up Python cache and test artifacts
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	rm -rf .mypy_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf test_reports

# Help command to show available targets
help:
	@echo "Available targets:"
	@echo "  install      - Install dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage report in terminal"
	@echo "  test-coverage- Run tests with HTML coverage report"
	@echo "  lint         - Run linters (black, isort, mypy)"
	@echo "  format       - Format code (black, isort)"
	@echo "  clean        - Clean up Python cache and test artifacts"
	@echo "  help         - Show this help message"
