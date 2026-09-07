# Working on this repo

This is a [Copier](https://copier.readthedocs.io/) template, not a Python project. Nothing here is installed or importable — every file under `template/` is rendered into someone else's repo.

## The one rule that matters

**You cannot lint the template. You can only lint what it generates.**

`template/src/{{ package_name }}/cli.py.jinja` is not valid Python (`from {{ package_name }} import ...`), so ruff, ty and pytest cannot see it. The only real check is to generate a project and run its gates:

```bash
uvx --with jinja2-time copier copy --trust --defaults --vcs-ref=HEAD \
  -d project_slug=demo-proj -d package_name=demo_proj \
  . ../demo-proj
cd ../demo-proj
uv run ruff check . && uv run ruff format --check .
uv run ty check && uv run pytest --cov
uv sync --group docs && uv run mkdocs build --strict
```

`ruff format --check` is the load-bearing one. The `_tasks` hook runs `ruff format` after generation, so a badly formatted template still *looks* fine — but anyone generating with `--skip-tasks` gets a project that fails its own first commit. Template sources must already be formatted the way the shipped config formats them.

CI (`.github/workflows/ci.yml`) runs exactly this across a matrix of answers. Trust it over local eyeballing.

## Conventions

- **Docstrings**: Google style, one imperative summary line ending in a period (`Return the cached settings.`), `Args:` on public functions only, single backticks because mkdocstrings renders Markdown; test docstrings state the property under test, never `Test that ...`.
- **Comments**: complete sentences that explain *why* and name the alternative rejected — a comment restating the code gets deleted, not reworded. American spelling throughout.
- **Line length is 88.** Jinja placeholders expand: `{{ package_name }}` (18 chars) usually becomes something shorter, `{{ project_slug }}` likewise. Write template source so it fits at 88 *after* rendering a mid-length name — CI checks the rendered form.
- **Comments in generated files explain *why*, not *what*.** The existing `pyproject.toml.jinja` is the reference for tone. A reader of a generated project has no access to this repo, so a decision that looks odd must justify itself in place.
- **Every answer in `copier.yml` needs a validator** unless it is a `choices` list.
- **Don't add a dependency to `pyproject.toml.jinja` without capping the major version** when upstream has a known breaking release coming. `mkdocs<2` is there for a reason.

## Versioning

Released as git tags (`v0.8.0`, `v0.8.1`, …), which `copier copy` and `copier update` resolve to.

Bump the **patch** number only — `0.8.0` → `0.8.1`. Never bump the minor number unless explicitly asked to.

## Commits

[Conventional Commits](https://www.conventionalcommits.org/), subject ≤ 50 chars, imperative mood. No body unless the change needs a "why" (then max 5 bullets). No `Co-Authored-By` footers.
