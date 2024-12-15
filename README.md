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

- Run tests:
```bash
poetry run pytest
```

- Format code:
```bash
poetry run black .
poetry run isort .
```

- Check code quality:
```bash
poetry run flake8
```

## License

MIT
