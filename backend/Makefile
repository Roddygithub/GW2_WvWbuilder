.PHONY: help install test test-cov coverage lint format check-types run clean

help:
	@echo "Commands:"
	@echo "  install       : Install dependencies using Poetry."
	@echo "  test          : Run all tests."
	@echo "  test-cov      : Run all tests with a terminal coverage report."
	@echo "  coverage      : Generate an HTML coverage report and open it."
	@echo "  lint          : Run linters (black, isort, flake8)."
	@echo "  format        : Format code with black and isort."
	@echo "  check-types   : Run mypy for static type checking."
	@echo "  run           : Run the development server with uvicorn."
	@echo "  clean         : Remove temporary files and caches."

install:
	poetry install --with test,dev

test:
	poetry run pytest -v

test-cov:
	poetry run pytest -v --cov=app --cov-report=term-missing

coverage:
	poetry run pytest --cov=app --cov-report=html
	@echo "HTML coverage report generated in htmlcov/ folder."
	@# Tente d'ouvrir le rapport, fonctionne sur macOS et la plupart des Linux
	@sh -c 'which open &>/dev/null && open htmlcov/index.html || which xdg-open &>/dev/null && xdg-open htmlcov/index.html || echo "Please open htmlcov/index.html in your browser."'

lint:
	poetry run flake8 app tests
	poetry run black --check .
	poetry run isort --check-only .

format:
	poetry run black .
	poetry run isort .

check-types:
	poetry run mypy app

run:
	poetry run uvicorn app.main:app --reload

clean:
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov
	find . -type d -name "__pycache__" -exec rm -r {} +