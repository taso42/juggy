# Juggy

A simple command-line application managed with Poetry.

## Setup

1. Make sure you have Poetry installed:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies:
```bash
make build/venv
```

3. Run the application:
```bash
python -m juggy.main --wave <wave> --week <week>
```

## Development

### Code Quality

This project uses Ruff for all code quality needs. Ruff is a fast all-in-one Python linter and formatter that replaces multiple tools (Black, Flake8, isort, etc.).

```bash
# Check code for issues and run tests
make test

# Auto-fix issues
make fix

# Format code
make format

# Type check
make typecheck

# Run tests with coverage
make coverage
```

The project is configured to use a line length of 120 characters. All code quality settings can be found in `pyproject.toml`.

## License

MIT
