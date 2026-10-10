# Working on this repo

This is a [Copier](https://copier.readthedocs.io/) template, not a Python project. Nothing here is installed or importable — every file under `template/` is rendered into someone else's repo. The only Python that runs here is `tests/`, which drives copier.

## The one rule that matters

**You cannot lint the template. You can only lint what it generates.**

`template/src/{{ package_name }}/{% if project_type == 'cli' %}cli.py{% endif %}.jinja` is not valid Python (`from {{ package_name }} import ...`), so ruff, ty and pytest cannot see it. The only real check is to generate a project and run its checks. The tests come in two tiers:

```bash
uv run pytest                            # fast: render every answer set, compare snapshots
uv run pytest --update-snapshots         # after an intended change: refresh, then read the diff
uv run pytest -m slow -k cli-github      # slow: generate one answer set, run its checks
uv run pytest -m slow -k latest_release  # slow: copier update from the last tag
```

The fast tier renders each answer set without its tasks and compares the files with `tests/snapshots/`, so a template change shows up in review as the change to every project it affects. Never edit a snapshot by hand; refresh them and read the diff. The slow tier is the load-bearing one, and what CI's `generate` and `update` jobs run.

Copier includes uncommitted template changes (with a `DirtyLocalWarning`), so there is no need to commit before testing. Generated projects resolve dependencies as of `PINNED_DATE` in `tests/conftest.py`, so an upstream release cannot fail an unrelated change; move the date forward on purpose, and when you raise a floor in `pyproject.toml.jinja` past it, or resolution fails. The weekly canary run sets `TEMPLATE_UNPINNED` and resolves the newest releases instead. Bun has no such cutoff.

The generated project's ruff-format and mdformat hooks are the load-bearing checks. `_tasks` deliberately runs no formatter, so rendered output is exactly what the template sources produce: template sources must already be formatted the way the shipped config formats them, Markdown included. Don't add a formatter task back — it would hide exactly these bugs from the tests, and on `copier update` it would reformat the user's own code.

A generated project defines its checks once, in `.pre-commit-config.yaml`, and `prek run --all-files --hook-stage manual` runs all of them. Its CI, AGENTS.md and README call that command. Add a check there, never to one of the callers.

CI (`.github/workflows/ci.yml`) runs the same tests, one answer set per job. Trust it over local eyeballing.

## Conventions

- **Docstrings**: Google style, one imperative summary line ending in a period (`Return the cached settings.`), `Args:` on public functions only, single backticks because mkdocstrings renders Markdown; test docstrings state the property under test, never `Test that ...`.
- **Comments**: complete sentences that explain *why* and name the alternative rejected — a comment restating the code gets deleted, not reworded. American spelling throughout.
- **Line length is 88.** Jinja placeholders expand: `{{ package_name }}` (18 chars) usually becomes something shorter, `{{ project_slug }}` likewise. Write template source so it fits at 88 *after* rendering a mid-length name — CI checks the rendered form.
- **Comments in generated files are the fewest that stop a wrong "fix".** Every one lands in each project's `copier update` diff, and a reader has no access to this repo. Keep a comment only where deleting the thing it explains would look like an improvement; how a decision was reached stays here, in `copier.yml` or in a test docstring. The existing `pyproject.toml.jinja` is the reference.
- **Defaults are the mainstream ones, strict opt-ins are commented out.** Ruff selects a small set and lists the stricter families in a comment; pytest, coverage and the example code impose nothing a newcomer must undo. A new default that every project would have to relax belongs in a comment instead.
- **Every answer in `copier.yml` needs a validator** unless it is a `choices` list or a `bool` — both are already constrained by copier itself.
- **A file that only some answers produce gets a conditional filename**, not an `_exclude` entry: `_exclude` has to guess whether copier matches the source name or the rendered one. `_exclude` is for whole directories. A conditional name that renders empty is skipped silently, so add it to `test_answers_produce_the_right_files`.
- **Every project is one flat Python package** (`src/`, `tests/`, one `pyproject.toml`, no uv workspace), and `web: true` adds a self-contained Bun project in `web/` beside it, so adding it later by `copier update --data web=true` is purely additive; `test_adding_the_web_app_leaves_the_python_side_alone` holds that. The `project_type` is `cli`, `library` or `api`; there is no web-only type. The one derived value, `application` (a `when: false` question: never asked, never stored, recomputed on every update), says whether the project loads settings and configures logging. Everything else tests `project_type` or `web` directly.
- **GitHub workflow templates are `{% raw %}` blocks**, because GitHub's own `${{ }}` expressions would collide with Jinja. `ci.yml.jinja` leaves raw only where an answer adds steps, as the web app's Bun steps are added: a step that never runs still shows up in every project's update diff.
- **An answer adds files, not branches inside Python files.** `project_type == 'api'` is the model: `app.py` and `health/` exist only then, and `settings.py` does not mention it. Two sources may render to the same path when their conditions are exclusive: the cli's and the api's `cli.py` are separate files, not one with an `{% if %}` in it. Keep `{% if %}` in `.py` sources to the few places a feature has to surface.
- **`author_name` and `author_email` have no defaults on purpose.** Don't add any — a default there attributes strangers' projects to whoever maintains the template. Automation passes `-d`.
- **Don't add a dependency to `pyproject.toml.jinja` without capping the major version** when upstream has a known breaking release coming. Pre-1.0 tools such as `ty` and `zensical` are capped below `0.1` for that reason.

## Versioning

Released as git tags (`v0.8.0`, `v0.8.1`, …), which `copier copy` and `copier update` resolve to.

Bump the **patch** number only — `0.8.0` → `0.8.1`. Never bump the minor number unless explicitly asked to.

## Commits

[Conventional Commits](https://www.conventionalcommits.org/), subject ≤ 50 chars, imperative mood. No body unless the change needs a "why" (then max 5 bullets). No `Co-Authored-By` footers.
