.PHONY: test test-v test-vv coverage clean

# Default target
test: build/venv
	poetry run pytest	
	poetry run ruff check .
	poetry run mypy .

# Run tests with coverage report
coverage: build/venv
	. ./build/venv/bin/activate && \
		poetry run pytest --cov=juggy --cov-report=term-missing

format: build/venv
	. ./build/venv/bin/activate && \
		poetry run ruff format .

fix: build/venv
	. ./build/venv/bin/activate && \
		poetry run ruff check . --fix

typecheck: build/venv
	. ./build/venv/bin/activate && \
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

