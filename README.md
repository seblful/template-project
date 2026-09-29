# Python Project Template

A [Copier](https://copier.readthedocs.io/) template for Python projects: uv, Ruff, ty, pytest, pre-commit and MkDocs, plus Typer, pydantic-settings and structlog for CLI projects.

## Create a project

Needs [uv](https://docs.astral.sh/uv/).

```bash
uvx copier copy --trust gh:seblful/template-project new-project
```

`--trust` lets Copier run `git init`, `uv sync` and `pre-commit install`, then make the first commit. There is no default author, so automation must pass one:

```bash
uvx copier copy --trust --defaults \
  -d author_name="Your Name" -d author_email=you@example.com \
  gh:seblful/template-project new-project
```

## Update a project

```bash
uvx copier update --trust
```

Your answers are kept in `.copier-answers.yml`. Notes for a breaking release print during the update; they live in [`migrations/`](migrations/).

## Questions

| Answer | Choices |
|--------|---------|
| `project_slug` | Project name, kebab-case |
| `package_name` | Python package, snake_case |
| `project_description` | One line |
| `project_type` | `cli`: an application with a Typer CLI, settings and logging. `library`: a package with no runtime dependencies |
| `config_file` | `cli` only: add `--config config.toml` support (default no) |
| `author_name`, `author_email` | Required, no default |
| `license` | None, MIT or Apache |
| `python_version` | 3.11 or newer (default 3.14) |
| `ci` | `github` (Ubuntu and Windows), `gitlab` or `none` |
| `claude_settings` | Add `.claude/settings.json` with Claude Code permissions |

Every project gets an `AGENTS.md` for coding assistants and defines its checks once, in `.pre-commit-config.yaml`: lint, format, types, a secret scan, `pytest --cov` and `mkdocs build --strict`. Git hooks run them on commit and push, and `uv run pre-commit run --all-files --hook-stage manual` runs all of them, locally and in CI. CI adds a weekly dependency audit.

## Developing the template

Template files are not valid Python until rendered, so the only real check is to generate a project and run its gates. [CI](.github/workflows/ci.yml) does that for a matrix of answers and tests `copier update` from the last release. See [CLAUDE.md](CLAUDE.md).

Releases are git tags (`v0.9.2`, `v0.9.3`, …).
