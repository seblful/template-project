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

Every route lives under `/api`, which leaves the other paths free for a web app on the same origin. `health/` is the example feature; `AGENTS.md` describes the layout every feature follows.

## Configuration

Settings come from environment variables such as `DEMO_PROJ_LOGGING__FORMAT=json`, where the upper-cased package name prefixes every variable and `__` separates a group from its field. The application reads no dotenv file itself; uv loads one into the environment when you select it:

```bash
cp .env.example .env   # local overrides, gitignored
uv run --env-file .env demo-proj serve
```

Set `UV_ENV_FILE=.env` to select it for every `uv run`. Variables already set in the shell win over the file. A missing file, or a misspelled key inside a group, fails at startup.

To add a setting, add a field to a group in `src/demo_proj/settings.py` (use `SecretStr` for secrets) and list it in `.env.example`. A test checks that they match. To read a TOML file as well, override `settings_customise_sources` on `Settings`, as the [pydantic-settings documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/#customise-settings-sources) shows.

## Logging

Logs go to stderr as text, or as JSON with `DEMO_PROJ_LOGGING__FORMAT=json`, uvicorn's access and error logs included. `DEMO_PROJ_LOGGING__LEVEL` sets the lowest level that is logged, in any letter case. Python warnings are logged too.

## Development

```bash
uv run prek run --all-files --hook-stage manual   # every check, as CI runs it
```

Commits run lint, formatting and types, and check that the message is a [Conventional Commit](https://www.conventionalcommits.org/); pushes run the tests.

For the weekly dependency audit, add a pipeline schedule in GitLab with `SCHEDULED_AUDIT` set to `1`.

## License

Apache, see the `LICENSE` file.
