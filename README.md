# Python Project Template

A [Copier](https://copier.readthedocs.io/) template for Python projects with modern tooling.

## Features

- [uv](https://github.com/astral-sh/uv) for fast dependency management
- [Ruff](https://github.com/astral-sh/ruff) for linting and formatting
- [ty](https://github.com/astral-sh/ty) for type checking
- [pytest](https://pytest.org/) for testing with coverage
- [Pydantic](https://docs.pydantic.dev/) for settings management
- [structlog](https://www.structlog.org/) for structured logging
- [Typer](https://typer.tiangolo.com/) for CLI interface
- [mdformat](https://mdformat.readthedocs.io/) for markdown formatting
- [pre-commit hooks](https://pre-commit.com/) for automated quality checks

## Usage

```bash
copier copy path/to/template-project new-project
cd new-project
make install
```

## Generated Project Structure

```
new-project/
├── src/
│   └── {{ package_name }}/      # Main package source
│       ├── __init__.py
│       ├── cli.py               # CLI entry point
│       ├── logging.py           # Logging configuration
│       ├── settings.py          # Pydantic settings
│       ├── py.typed             # PEP 561 type marker
│       └── utils/
├── tests/
├── docs/
├── scripts/
├── pyproject.toml
├── .env                         # Environment template
├── .python-version
├── AGENTS.md                    # AI coding standards
└── README.md
```

## Available Commands

```bash
make dev          # Run CLI application
make test         # Run tests with coverage
make lint         # Run ruff linter and formatter
make typecheck    # Run ty type checker
make install      # Install dependencies and pre-commit hooks
```

## Configuration

Edit `copier.yml` to customize project defaults:

- `project_name` - Your project name
- `package_name` - Python package name (snake_case)
- `author_name` / `author_email` - Author information
- `license` - None, MIT, Apache, or EULA
- `python_version` - Target Python version
- `include_notebooks` - Include notebooks directory

## Development

```bash
# Lint and format
make lint

# Run tests
make test

# Type check
make typecheck
```
