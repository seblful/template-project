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
| [MkDocs](https://www.mkdocs.org/) | Documentation |

## Prerequisites

- [uv](https://github.com/astral-sh/uv)
- [copier](https://copier.readthedocs.io/) 9.2+ with the `jinja2-time` extension (used to stamp the current year into the license):
  - `uvx --with jinja2-time copier`, or
  - `uv tool install copier --with jinja2-time`

## Create a Project

```bash
uvx --with jinja2-time copier copy --trust gh:seblful/template-project new-project
cd new-project
```

`--trust` is required: generation runs `git init`, `uv sync`, `ruff`, `mdformat` and `pre-commit install`, then makes the initial commit.

## Update a Project

Pull the latest template changes into an existing generated project:

```bash
cd your-project
uvx --with jinja2-time copier update --trust
```

Copier re-applies the template, preserving your answers from `.copier-answers.yml`. `.env` is never overwritten.

## Project Structure

```
new-project/
├── .github/workflows/ci.yml   # or .gitlab-ci.yml, or neither — see the ci answer
├── src/
│   └── <package_name>/
│       ├── __init__.py
│       ├── __main__.py      # python -m <package_name>
│       ├── cli.py
│       ├── logging.py
│       ├── settings.py
│       ├── py.typed
│       └── utils/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/
├── .env                     # generated once, gitignored, never updated
├── .env.example             # the committed config contract
├── .python-version
├── CLAUDE.md                # or AGENTS.md, depending on code_assistant
├── pyproject.toml
├── TODO.md
└── README.md
```

`notebooks/` and `scripts/` are not created — they are excluded on purpose, but `pyproject.toml` already tells `ty` to ignore them if you add them later.

## Commands in a Generated Project

```bash
uv run <project_slug>             # run the CLI
uv run pytest                     # run tests
uv run pytest --cov               # run tests with the coverage gate
uv run ruff check . --fix         # lint and auto-fix
uv run ruff format .              # format
uv run ty check                   # type check
uv run pre-commit run --all-files # everything CI runs
```

## Configuration

Answers are saved in `.copier-answers.yml` and reused on `copier update`:

| Variable | Description |
|----------|-------------|
| `project_slug` | Project name (kebab-case) |
| `package_name` | Python package name (snake_case) |
| `project_description` | One-line description |
| `author_name` / `author_email` | Author information |
| `license` | None, MIT, Apache, or EULA |
| `python_version` | Target Python version (3.10+) |
| `code_assistant` | claude, opencode, or cursor |
| `ci` | github, gitlab, or none |

The author defaults are the template maintainer's; both are free-text, so override them when generating.

## Continuous Integration

The `ci` answer picks one pipeline definition, or none. Both run the same three things — the pre-commit suite plus `pytest --cov`, a strict `mkdocs build`, and a dependency audit — so the choice does not change what is checked.

| `ci` | Generates | Notes |
|------|-----------|-------|
| `github` | `.github/workflows/ci.yml` | Ubuntu and Windows matrix; weekly audit via `schedule:` |
| `gitlab` | `.gitlab-ci.yml` | Linux only; audit needs a pipeline schedule with `SCHEDULED_AUDIT` set, and a manual `pages` job publishes the docs |
| `none` | nothing | `uv run pre-commit run --all-files` is still the local gate |

## Developing the Template

The template cannot be linted directly — `from {{ package_name }} import ...` is not valid Python. The only real check is to generate a project and run its gates; [CI](.github/workflows/ci.yml) does exactly that across a matrix of answers, plus a `copier update` smoke test from the previous tag. See [CLAUDE.md](CLAUDE.md).

## Versioning

The template is released as git tags (`v0.8.0`, `v0.7.8`, …), which `copier copy` and `copier update` resolve to.
