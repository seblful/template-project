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
| [Typer](https://typer.tiangolo.com/) | CLI interface (`project_type=cli`) |
| [mdformat](https://mdformat.readthedocs.io/) | Markdown formatting |
| [pre-commit](https://pre-commit.com/) | Automated quality checks |
| [MkDocs](https://www.mkdocs.org/) | Documentation |

## Prerequisites

- [uv](https://github.com/astral-sh/uv)
- [copier](https://copier.readthedocs.io/) 9.2+ — no plugins needed

## Create a Project

```bash
uvx copier copy --trust gh:seblful/template-project new-project
cd new-project
```

`--trust` is required: generation runs `git init`, `uv sync`, `ruff`, `mdformat` and `pre-commit install`, then makes the initial commit.

There is deliberately no default author, so `--defaults` alone will not generate a project. Pass the two answers explicitly in automation:

```bash
uvx copier copy --trust --defaults \
  -d author_name="Your Name" -d author_email=you@example.com \
  gh:seblful/template-project new-project
```

## Update a Project

Pull the latest template changes into an existing generated project:

```bash
cd your-project
uvx copier update --trust
```

Copier re-applies the template, preserving your answers from `.copier-answers.yml`.

## Project Structure

```
new-project/
├── .github/workflows/ci.yml   # or .gitlab-ci.yml, or neither — see the ci answer
├── src/
│   └── <package_name>/
│       ├── __init__.py       # metadata only — no re-exports
│       ├── __main__.py       # python -m <package_name>   } project_type=cli
│       ├── cli.py            #                            }
│       ├── logging.py
│       ├── settings.py
│       └── py.typed
├── tests/
│   ├── conftest.py
│   ├── test_cli.py           # project_type=cli
│   ├── test_config_roundtrip.py
│   ├── test_logging.py
│   └── test_settings.py
├── docs/
├── .claude/settings.json     # only when claude_settings=true
├── .env.example              # the committed config contract; copy it to .env
├── .python-version
├── AGENTS.md
├── pyproject.toml
├── TODO.md
└── README.md
```

`notebooks/` and `scripts/` are not created, but `pyproject.toml` already tells `ty` to ignore them if you add them later.

## Commands in a Generated Project

```bash
uv run <project_slug>             # run the CLI (project_type=cli)
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
| `project_type` | `cli` (Typer entry point) or `library` |
| `author_name` / `author_email` | Author information — no default, must be answered |
| `license` | None, MIT, or Apache |
| `python_version` | Target Python version (3.10+) |
| `ci` | github, gitlab, or none |
| `claude_settings` | Ship `.claude/settings.json` with project-scoped permissions |

### `project_type`

`cli` adds `cli.py`, `__main__.py`, `tests/test_cli.py`, a `[project.scripts]` console script and the `typer` dependency. `library` ships everything else — settings, logging, tests, docs, hooks — without them, so an importable package carries no CLI machinery to delete.

### Assistant instructions

Every project gets an `AGENTS.md`, which Claude Code, Cursor, opencode and the rest all read. `.ignore` holds only the delta from `.gitignore`, since ripgrep and fd already honor that; Cursor users who want a `.cursorignore` can copy it.

## Continuous Integration

The `ci` answer picks one pipeline definition, or none. Both run the same three things — the pre-commit suite plus `pytest --cov`, a strict `mkdocs build`, and a dependency audit — so the choice does not change what is checked.

| `ci` | Generates | Notes |
|------|-----------|-------|
| `github` | `.github/workflows/ci.yml` | Ubuntu and Windows matrix; weekly audit via `schedule:` |
| `gitlab` | `.gitlab-ci.yml` | Linux only; audit needs a pipeline schedule with `SCHEDULED_AUDIT` set, and a manual `pages` job publishes the docs |
| `none` | nothing | `uv run pre-commit run --all-files` is still the local gate, and the pre-push hooks still run the tests and the docs build |

## Developing the Template

The template cannot be linted directly — `from {{ package_name }} import ...` is not valid Python. The only real check is to generate a project and run its gates; [CI](.github/workflows/ci.yml) does exactly that across a matrix of answers, plus a `copier update` smoke test from the previous tag. See [CLAUDE.md](CLAUDE.md).

## Versioning

The template is released as git tags (`v0.8.0`, `v0.7.8`, …), which `copier copy` and `copier update` resolve to.
