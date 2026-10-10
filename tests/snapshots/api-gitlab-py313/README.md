# demo-proj

A generated demo project.

## Setup

Needs Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

## Usage

```bash
uv run demo-proj serve            # interactive docs at http://127.0.0.1:8000/api/docs
uv run demo-proj serve --reload   # restarts on source changes, for development
uv run demo-proj openapi          # the OpenAPI schema, as JSON
```

Each feature is a package under `src/demo_proj/`, shaped like `health/`: `router.py` holds the HTTP routes and nothing else, `schemas.py` the request and response models, and `service.py` the logic, free of FastAPI so it is testable without HTTP. Every route lives under `/api`, which leaves the other paths free for a web app on the same origin.

## Configuration

Settings come from environment variables such as `DEMO_PROJ_LOGGING__FORMAT=json`, where the upper-cased package name prefixes every variable and `__` separates a group from its field. A dotenv file is read only when you select it:

```bash
cp .env.example .env   # local overrides, gitignored
uv run demo-proj serve --env-file .env
```

In Python, pass the same path to `load_settings(env_file=...)`.

Highest priority first: constructor arguments, environment variables, the `.env` file, defaults. A missing selected path, or a misspelled key inside a group, fails at startup.

To add a setting, add a field to a group in `src/demo_proj/settings.py` (use `SecretStr` for secrets) and list it in `.env.example`. A test checks that they match. To read a TOML file as well, override `settings_customise_sources` on `Settings`, as the [pydantic-settings documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/#customise-settings-sources) shows.

## Logging

Logs go to stderr as text, or as JSON with `DEMO_PROJ_LOGGING__FORMAT=json`, uvicorn's access and error logs included. `DEMO_PROJ_LOGGING__LEVEL` sets the lowest level that is logged, in any letter case. Python warnings are logged too.

## Development

```bash
uv run prek run --all-files --hook-stage manual   # every check, as CI runs it
uv run --group docs zensical serve                # docs at http://localhost:8001
```

Commits run lint, formatting and types, and check that the message is a [Conventional Commit](https://www.conventionalcommits.org/); pushes run the tests and the docs build.

For the weekly dependency audit, add a pipeline schedule in GitLab with `SCHEDULED_AUDIT` set to `1`. The `pages` job publishes the docs when run manually.

## License

Apache, see the `LICENSE` file.
