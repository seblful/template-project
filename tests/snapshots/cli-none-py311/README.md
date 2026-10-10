# demo-proj

A generated demo project.

## Setup

Needs Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

## Usage

```bash
uv run demo-proj settings
uv run demo-proj --version
```

From Python:

```python
from demo_proj.logging import get_logger, setup_logging
from demo_proj.settings import load_settings

settings = load_settings()
setup_logging(settings.logging)
get_logger(__name__).info("started", user_id=42)
```

## Configuration

Settings come from environment variables such as `LOGGING__FORMAT=json`, where `__` separates a group from its field. A dotenv file is read only when you select it:

```bash
cp .env.example .env   # local overrides, gitignored
uv run demo-proj --env-file .env settings
```

In Python, pass the same path to `load_settings(env_file=...)`.

Highest priority first: constructor arguments, environment variables, the `.env` file, defaults. A missing selected path, or a misspelled key inside a group, fails at startup.

To add a setting, add a field to a group in `src/demo_proj/settings.py` (use `SecretStr` for secrets) and list it in `.env.example`. A test checks that they match. To read a TOML file as well, override `settings_customise_sources` on `Settings`, as the [pydantic-settings documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/#customise-settings-sources) shows.

## Logging

Logs go to stderr as text, or as JSON with `LOGGING__FORMAT=json`. `LOGGING__LEVEL` sets the lowest level that is logged.

## Development

```bash
uv run prek run --all-files --hook-stage manual   # every check
uv run --group docs zensical serve                # docs at http://localhost:8000
```

Commits run lint, formatting and types, and check that the message is a [Conventional Commit](https://www.conventionalcommits.org/); pushes run the tests and the docs build.

## License

Apache, see the `LICENSE` file.
