# Juggy

A simple command-line application managed with Poetry.

## Setup

1. Make sure you have Poetry installed:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies:
```bash
poetry install
```

3. Run the application:
```bash
poetry run python -m juggy.main
```

## Development

### Code Quality

This project uses Ruff for all code quality needs. Ruff is a fast all-in-one Python linter and formatter that replaces multiple tools (Black, Flake8, isort, etc.).

```bash
# Check code for issues
poetry run ruff check .

# Auto-fix issues
poetry run ruff check --fix .

# Format code (replacement for Black)
poetry run ruff format .
```

The project is configured to use a line length of 120 characters. All code quality settings can be found in `pyproject.toml`.

- Run tests:
```bash
poetry run pytest
```

## License

MIT
