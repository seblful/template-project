# Python Project Template

A [Copier](https://copier.readthedocs.io/) template for Python projects with modern tooling.

## Features

- [uv](https://github.com/astral-sh/uv) for fast dependency management
- [Ruff](https://github.com/astral-sh/ruff) for linting and formatting
- [mypy](https://mypy.readthedocs.io/) for type checking
- [pytest](https://pytest.org/) for testing
- [Pydantic](https://docs.pydantic.dev/) for settings management
- [structlog](https://www.structlog.org/) for structured logging
- [Typer](https://typer.tiangolo.com/) for CLI interface

## Usage

```bash
copier copy path/to/template-project new-project
cd new-project
```

## Project Structure

```
template-project/
├── template/                  # Copier template files
│   ├── LICENSE.jinja         # License template (MIT/Apache/EULA)
│   └── README.md.jinja       # README template
├── copier.yml                # Copier configuration
├── README.md                 # This file
└── uv.lock                   # Locked dependencies
```

## Supported Licenses

- MIT
- Apache 2.0
- EULA (custom end-user license agreement)

## Configuration

Edit `copier.yml` to customize default values and add new variables.
