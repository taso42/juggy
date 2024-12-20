.PHONY: test test-v test-vv coverage clean

# Default target
test: build/venv
	poetry run pytest	
	poetry run ruff check .
	poetry run mypy .

# Run tests with coverage report
coverage: build/venv
	poetry run pytest --cov=juggy --cov-report=term-missing

format:
	poetry run ruff format .

fix:
	poetry run ruff check . --fix

typecheck:
	poetry run mypy .

# Clean up Python cache files and coverage data
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".ruff_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	rm -rf build

build/venv:
	python -m venv build/venv
	. build/venv/bin/activate && poetry install

# Help target
help:
	@echo "Available targets:"
	@echo "  test       - Run tests, linting, and type checking"
	@echo "  test-v     - Run tests with verbose output"
	@echo "  test-vv    - Run tests with very verbose output"
	@echo "  coverage   - Run tests with coverage report"
	@echo "  format     - Format code with ruff"
	@echo "  fix        - Auto-fix linting issues with ruff"
	@echo "  typecheck  - Run mypy type checker"
	@echo "  clean      - Clean up Python cache files and build artifacts"
	@echo "  help       - Show this help message"
