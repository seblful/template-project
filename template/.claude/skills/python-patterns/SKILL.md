---
name: python-patterns
description: Professional Python coding practices — PEP 8, type hints, modern idioms, and the project stack (uv, ruff, ty, structlog, pydantic, typer).
origin: ECC
---

# Python Coding Practices

## Core Principles

- **Readability counts.** Clear names over clever tricks.
- **Explicit over implicit.** No magic, no hidden side effects.
- **EAFP over LBYL.** Prefer `try/except` over pre-checks.
- **One obvious way.** Follow PEP 8 and PEP 20.

## Tooling

| Tool | Purpose |
|:-----|:--------|
| [uv](https://docs.astral.sh/uv/) | Package manager — **never** `pip` or `venv` |
| [Ruff](https://docs.astral.sh/ruff/) | Lint + format |
| [ty](https://github.com/astral-sh/ty) | Type checker |
| [pytest](https://pytest.org/) | Tests |

```bash
uv add <pkg>                 # prod dep
uv add --dev <pkg>           # dev dep
uv run ruff format .
uv run ruff check . --fix
uv run ty check src/ tests/
uv run pytest
```

## Naming & Style

- `snake_case` for variables, functions, modules.
- `CamelCase` for classes.
- `UPPER_SNAKE` for constants.
- f-strings for all formatting.
- Google-style docstrings on public functions/classes.

```python
def fetch_user(user_id: str, active: bool = True) -> User | None:
    """Fetch a user by ID.

    Args:
        user_id: Unique identifier.
        active: If True, only return active users.

    Returns:
        The user, or None if not found.

    Raises:
        DatabaseError: If the query fails.
    """
```

## Type Hints (mandatory on all signatures)

Modern syntax, Python 3.10+: built-in generics, `|` unions, no `Optional`/`Union`.

```python
def process(user_id: str, data: dict[str, Any]) -> User | None: ...

JSON = dict[str, Any] | list[Any] | str | int | float | bool | None

T = TypeVar("T")
def first(items: list[T]) -> T | None:
    return items[0] if items else None
```

- `typing.Protocol` for structural (duck) typing.
- `abc.ABC` only when explicit inheritance is required.

## File System — `pathlib` only

Never `os.path.join` or string concatenation.

```python
from pathlib import Path

cfg = Path("config") / "settings.toml"
text = cfg.read_text(encoding="utf-8")

out = Path("output/result.json")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(data), encoding="utf-8")

for py in Path("src").rglob("*.py"): ...
```

## Logging — structlog

Never use `logging` directly. Configure once via `setup_logging()`.

```python
import structlog
logger = structlog.get_logger()

logger.info("user_processed", user_id=user_id, duration_ms=42)
```

Event names: lowercase, snake_case, past-tense verbs. Pass context as kwargs, never f-string the message.

## Settings — Pydantic

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    app_name: str = "myapp"
    database_url: str

    model_config = SettingsConfigDict(env_prefix="APP__", env_nested_delimiter="__")

settings = AppSettings()
```

| Use case | Choice |
|:---------|:-------|
| Env-var config | `BaseSettings` |
| External data validation | `BaseModel` |
| Internal data containers | `@dataclass` or `pydantic.dataclass` |
| Immutable DTOs | `@dataclass(frozen=True)` |

## Error Handling

- Catch specific exceptions; never bare `except`.
- Chain with `raise ... from e` to preserve context.
- Define a project-rooted exception hierarchy.

```python
class AppError(Exception): ...
class ValidationError(AppError): ...
class NotFoundError(AppError): ...

try:
    return Config.from_json(path.read_text())
except FileNotFoundError as e:
    raise ConfigError(f"missing: {path}") from e
```

## Context Managers

Use `with` for every resource. Build custom ones with `@contextmanager` or `__enter__/__exit__`.

```python
@contextmanager
def timer(name: str):
    start = time.perf_counter()
    try:
        yield
    finally:
        logger.info("timed", name=name, elapsed=time.perf_counter() - start)
```

## Comprehensions & Generators

- List/dict/set comprehensions for simple transforms.
- Generators for streaming or large datasets.
- If logic spans more than a couple of clauses, write a function.

```python
active = [u.name for u in users if u.is_active]
total = sum(x * x for x in range(1_000_000))

def read_lines(path: Path) -> Iterator[str]:
    with path.open() as f:
        for line in f:
            yield line.strip()
```

## Datetime — always timezone-aware

```python
from datetime import datetime, timezone
now = datetime.now(timezone.utc)   # never datetime.utcnow() or datetime.now()
```

## Async/Await (I/O-bound only)

- `httpx.AsyncClient` for HTTP — not `aiohttp` or `urllib`.
- `asyncio.gather` for concurrency; never block the loop.
- `asyncio.run` only at entry points.

```python
async def fetch(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.json()

results = await asyncio.gather(*(fetch(u) for u in urls))
```

## CLI — Typer

```python
import typer
app = typer.Typer()

@app.command()
def process(input_path: Path, verbose: bool = typer.Option(False, "-v")) -> None:
    """Process the input file."""

if __name__ == "__main__":
    app()
```

## Decorators

Always `@functools.wraps` to preserve metadata.

```python
def timed(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            logger.info("timed", name=func.__name__, elapsed=time.perf_counter() - start)
    return wrapper
```

## Performance

- `"".join(...)` over `+=` in loops.
- Generators over lists for large/streamed data.
- `__slots__` on classes with many instances.
- Profile before optimizing — `cProfile`, `timeit`.

## Package Layout

```
src/{package_name}/
├── __init__.py      # __version__, public exports, __all__
├── cli.py           # Typer entry point
├── logging.py       # structlog setup
├── settings.py      # Pydantic settings
├── py.typed         # PEP 561 marker
└── utils/
tests/
├── conftest.py
└── test_*.py
```

Import order (ruff-enforced): stdlib → third-party → local. Absolute imports only.

## Anti-Patterns

```python
def f(items=[]): ...                # mutable default — shared across calls
if type(x) == list: ...             # use isinstance(x, list)
if x == None: ...                   # use x is None
from os.path import *               # no wildcard imports
try: ...                            # no bare except
except: pass
datetime.utcnow()                   # naive — use datetime.now(timezone.utc)
os.path.join(a, b)                  # use Path(a) / b
```

## Quick Reference

| Use | For |
|-----|-----|
| Type hints | Every signature |
| `pathlib.Path` | All filesystem ops |
| f-strings | All formatting |
| `structlog` | All logging |
| `typer` | All CLIs |
| `httpx.AsyncClient` | Async HTTP |
| `BaseSettings` | Env config |
| `BaseModel` | External data |
| `@dataclass` | Internal data |
| `__slots__` | Hot, many-instance classes |
| EAFP + specific `except` | Error handling |

**Prioritize clarity over cleverness. When in doubt, write the obvious version.**
