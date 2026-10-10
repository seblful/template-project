# demo-proj

A generated demo project.

## Setup

Needs Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

## Usage

```python
import demo_proj

print(demo_proj.__version__)
```

## Logging

Use `logging.getLogger(__name__)` and leave handlers and levels to the application that imports this package.

## Development

```bash
uv run prek run --all-files --hook-stage manual   # every check, as CI runs it
```

Commits run lint, formatting and types, and check that the message is a [Conventional Commit](https://www.conventionalcommits.org/); pushes run the tests.

## License

MIT, see the `LICENSE` file.
