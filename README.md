# Python Project Template

A [Copier](https://copier.readthedocs.io/) template for Python projects with modern tooling.

## Stack

| Tool | Purpose |
|------|---------|
| [uv](https://github.com/astral-sh/uv) | Dependency management |
| [Ruff](https://github.com/astral-sh/ruff) | Linting and formatting |
| [ty](https://github.com/astral-sh/ty) | Type checking |
| [pytest](https://pytest.org/) | Testing with coverage |
| [Pydantic](https://docs.pydantic.dev/) | Settings management |
| [structlog](https://www.structlog.org/) | Structured logging |
| [Typer](https://typer.tiangolo.com/) | CLI interface |
| [mdformat](https://mdformat.readthedocs.io/) | Markdown formatting |
| [pre-commit](https://pre-commit.com/) | Automated quality checks |

## Prerequisites

- [uv](https://github.com/astral-sh/uv)
- [copier](https://copier.readthedocs.io/) — `uvx copier` or `uv tool install copier`

## Create a Project

```bash
copier copy gh:seblful/template-project new-project
cd new-project
```

Copier automatically runs `uv sync`, `pre-commit install`, and formats the project after generation.

## Update a Project

Pull the latest template changes into an existing generated project:

```bash
cd your-project
copier update --trust
```

Copier re-applies the template, preserving your answers from `.copier-answers.yml`.

## Project Structure

```
new-project/
├── src/
│   └── <package_name>/
│       ├── __init__.py
│       ├── cli.py
│       ├── logging.py
│       ├── settings.py
│       ├── py.typed
│       └── utils/
├── tests/
├── docs/
├── scripts/
├── pyproject.toml
├── .env.development        # created based on environments answer
├── .python-version
├── CLAUDE.md               # or AGENTS.md depending on code_assistant
└── README.md
```

## Commands

```bash
uv run dev          # Run CLI application
uv run test         # Run tests with coverage
uv run lint         # Lint and auto-fix
uv run format       # Format code
uv run typecheck    # Type check
```

## Configuration

Answers are saved in `.copier-answers.yml` and reused on `copier update`:

| Variable | Description |
|----------|-------------|
| `project_name` | Project name |
| `package_name` | Python package name (snake_case) |
| `author_name` / `author_email` | Author information |
| `license` | None, MIT, Apache, or EULA |
| `python_version` | Target Python version |
| `code_assistant` | Claude, Opencode, or Cursor |
| `environments` | Environment-specific .env files to generate |
