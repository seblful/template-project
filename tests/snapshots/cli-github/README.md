# demo-proj

A generated demo project.

## Setup

Needs Python 3.15+ and [uv](https://docs.astral.sh/uv/).

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
from demo_proj.settings import Settings

settings = Settings()
setup_logging(settings.logging)
get_logger(__name__).info("started", user_id=42)
```

## Configuration

Settings come from environment variables such as `DEMO_PROJ_LOGGING__FORMAT=json`, where the upper-cased package name prefixes every variable and `__` separates a group from its field. The application reads no dotenv file itself; uv loads one into the environment when you select it:

```bash
cp .env.example .env   # local overrides, gitignored
uv run --env-file .env demo-proj settings
```

Set `UV_ENV_FILE=.env` to select it for every `uv run`. Variables already set in the shell win over the file. A missing file, or a misspelled key inside a group, fails at startup.

To add a setting, add a field to a group in `src/demo_proj/settings.py` (use `SecretStr` for secrets) and list it in `.env.example`. A test checks that they match. To read a TOML file as well, override `settings_customise_sources` on `Settings`, as the [pydantic-settings documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/#customise-settings-sources) shows.

## Logging

Logs go to stderr as text, or as JSON with `DEMO_PROJ_LOGGING__FORMAT=json`. `DEMO_PROJ_LOGGING__LEVEL` sets the lowest level that is logged, in any letter case. Python warnings are logged too.

## Development

```bash
uv run prek run --all-files --hook-stage manual   # every check, as CI runs it
```

Commits run lint, formatting and types, and check that the message is a [Conventional Commit](https://www.conventionalcommits.org/); pushes run the tests.
