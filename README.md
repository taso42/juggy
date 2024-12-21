# Juggy

A simple command-line application that generates routines for the Juggernaut method in the [Hevy app](https://hevy.com/), using the Hevy API.

## Pre-requisites

- You need to have a Hevy account and API key.  This requires a Pro subscription.
- A Mac or *nix environment
- Python 3.12, Poetry, Make

## Setup and using

1. Setup venv and install dependencies:
```bash
python -m venv venv
. ./venv/bin/activate
poetry install
```

2. Run the application:
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
