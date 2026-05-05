---
name: python-patterns
description: Pythonic idioms, PEP 8 standards, type hints, and project-specific best practices for building robust, efficient, and maintainable Python applications with uv, ruff, ty, structlog, and pydantic.
origin: ECC
---

# Python Development Patterns

Idiomatic Python patterns and project-specific best practices for building robust, efficient, and maintainable applications.

## When to Activate

- Writing new Python code
- Reviewing Python code
- Refactoring existing Python code
- Designing Python packages/modules

## Core Principles

### 1. Readability Counts

Python prioritizes readability. Code should be obvious and easy to understand.

```python
# Good: Clear and readable
def get_active_users(users: list[User]) -> list[User]:
    """Return only active users from the provided list."""
    return [user for user in users if user.is_active]


# Bad: Clever but confusing
def get_active_users(u):
    return [x for x in u if x.a]
```

### 2. Explicit is Better Than Implicit

Avoid magic; be clear about what your code does.

### 3. EAFP - Easier to Ask Forgiveness Than Permission

Python prefers exception handling over checking conditions.

```python
# Good: EAFP style
def get_value(dictionary: dict, key: str) -> Any:
    try:
        return dictionary[key]
    except KeyError:
        return default_value

# Bad: LBYL (Look Before You Leap) style
def get_value(dictionary: dict, key: str) -> Any:
    if key in dictionary:
        return dictionary[key]
    else:
        return default_value
```

---

## Project Standards

### Tooling

| Tool | Purpose |
|:-----|:--------|
| [uv](https://docs.astral.sh/uv/) | Package manager — **never** use `pip` or `venv` |
| [Ruff](https://docs.astral.sh/ruff/) | Linting and formatting |
| [ty](https://github.com/astral-sh/ty) | Type checking |
| [pytest](https://pytest.org/) | Testing |

```bash
uv add <package>          # Production dependency
uv add --dev <package>    # Dev dependency
uv run <cmd>              # Run any command
uv run ruff format .      # Format code
uv run ruff check . --fix # Lint and auto-fix
uv run ty check src/ tests/  # Type check
uv run pytest             # Run tests
```

### Naming Conventions

| Element | Convention |
|:--------|:-----------|
| Variables/Functions | `snake_case` |
| Classes | `CamelCase` |
| Strings | f-strings (`f"..."`) |

### Docstrings

Google-style for all public functions and classes.

```python
def fetch_user(user_id: str, active: bool = True) -> User | None:
    """Fetch a user by ID.

    Args:
        user_id: The unique identifier of the user.
        active: If True, only return active users.

    Returns:
        The User object, or None if not found.

    Raises:
        DatabaseError: If the database query fails.
    """
```

---

## Type Hints

### Modern Syntax (Python 3.10+)

Type hints are **mandatory** for all function signatures.

```python
# Use built-in types and | for unions — no Optional, no Union
def process_user(
    user_id: str,
    data: dict[str, Any],
    active: bool = True,
) -> User | None:
    """Process a user and return the updated User or None."""
    if not active:
        return None
    return User(user_id, data)


def process_items(items: list[str]) -> dict[str, int]:
    return {item: len(item) for item in items}
```

### Type Aliases and TypeVar

```python
from typing import TypeVar

# Type alias for complex types
JSON = dict[str, Any] | list[Any] | str | int | float | bool | None

# Generic types
T = TypeVar("T")

def first(items: list[T]) -> T | None:
    """Return the first item or None if list is empty."""
    return items[0] if items else None
```

### Protocol-Based Duck Typing

```python
from typing import Protocol


class Renderable(Protocol):
    def render(self) -> str:
        """Render the object to a string."""


def render_all(items: list[Renderable]) -> str:
    return "\n".join(item.render() for item in items)
```

### ABC vs Protocol

```python
from abc import ABC, abstractmethod

# Use abc.ABC for explicit inheritance-based polymorphism
class BaseProcessor(ABC):
    @abstractmethod
    def process(self, data: str) -> str: ...

# Use typing.Protocol for structural typing (duck typing)
class Processable(Protocol):
    def process(self, data: str) -> str: ...
```

---

## File System

**Always** use `pathlib.Path`. **Never** use `os.path.join` or string concatenation.

```python
from pathlib import Path

# Reading files
config_path = Path("config") / "settings.toml"
content = config_path.read_text(encoding="utf-8")

# Writing files
output = Path("output") / "result.json"
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(data), encoding="utf-8")

# Iterating files
src = Path("src")
for py_file in src.rglob("*.py"):
    print(py_file.relative_to(src))

# Common operations
path = Path("data/users.csv")
path.exists()           # Check existence
path.suffix             # ".csv"
path.stem               # "users"
path.parent             # Path("data")
```

---

## Logging (structlog)

Never use `logging` directly. Always use structlog.

```python
import structlog

logger = structlog.get_logger()


def process_user(user_id: str) -> User:
    logger.info("processing_user", user_id=user_id)

    try:
        user = db.find(user_id)
        logger.info("user_found", user_id=user_id, name=user.name)
        return user
    except NotFoundError:
        logger.warning("user_not_found", user_id=user_id)
        raise
```

Configure once at startup via `setup_logging()` from `{package_name}.logging`. Import: `from {package_name}.logging import setup_logging`.

---

## Settings (Pydantic)

```python
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    app_name: str = "myapp"
    debug: bool = False
    database_url: str

    model_config = SettingsConfigDict(
        env_prefix="APP__",
        env_nested_delimiter="__",
    )


settings = AppSettings()
```

- Location: `src/{package_name}/settings.py`
- Import: `from {package_name}.settings import settings`
- Use `__` delimiter for nesting: `APP__APP_NAME`, `APP__LOGGING__LEVEL`

### Data Classes vs Pydantic

| Use Case | Choice |
|:---------|:-------|
| Configuration from env vars | `BaseSettings` |
| Simple data containers | `pydantic.dataclass` |
| External data validation | `BaseModel` |
| Immutable DTOs | `@pydantic.dataclass(frozen=True)` |

---

## Error Handling

### Specific Exception Handling

```python
# Good: Catch specific exceptions and chain them
def load_config(path: Path) -> Config:
    try:
        return Config.from_json(path.read_text())
    except FileNotFoundError as e:
        raise ConfigError(f"Config file not found: {path}") from e
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in config: {path}") from e

# Bad: Bare except
def load_config(path: Path) -> Config:
    try:
        return Config.from_json(path.read_text())
    except:
        return None  # Silent failure!
```

### Custom Exception Hierarchy

```python
class AppError(Exception):
    """Base exception for all application errors."""


class ValidationError(AppError):
    """Raised when input validation fails."""


class NotFoundError(AppError):
    """Raised when a requested resource is not found."""
```

---

## Context Managers

```python
from contextlib import contextmanager


@contextmanager
def timer(name: str):
    """Time a block of code."""
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    logger.info("timed_block", name=name, elapsed=elapsed)


class DatabaseTransaction:
    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        self.connection.begin_transaction()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.connection.commit()
        else:
            self.connection.rollback()
        return False
```

---

## Comprehensions and Generators

```python
# List comprehension for simple transformations
names = [user.name for user in users if user.is_active]

# Generator for lazy evaluation — prefer over list for large data
total = sum(x * x for x in range(1_000_000))

# Generator function for streaming large files
def read_large_file(path: Path) -> Iterator[str]:
    with path.open() as f:
        for line in f:
            yield line.strip()

# Expand complex comprehensions into a function
def filter_and_transform(items: Iterable[int]) -> list[int]:
    result = []
    for x in items:
        if x > 0 and x % 2 == 0:
            result.append(x * 2)
    return result
```

---

## Data Classes

```python
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class User:
    """User entity with automatic __init__, __repr__, and __eq__."""
    id: str
    name: str
    email: str
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

    def __post_init__(self):
        if "@" not in self.email:
            raise ValueError(f"Invalid email: {self.email}")


# Immutable value object
from typing import NamedTuple

class Point(NamedTuple):
    x: float
    y: float

    def distance(self, other: "Point") -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
```

---

## Datetime

**Always** use timezone-aware datetimes.

```python
from datetime import datetime, timezone

# Good
now = datetime.now(timezone.utc)
serialized = now.isoformat()
parsed = datetime.fromisoformat(serialized)

# Bad
now = datetime.utcnow()  # naive datetime, don't use
```

---

## Async/Await

Use `async def` only for I/O-bound operations.

```python
import asyncio
import httpx


async def fetch(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


async def fetch_all(urls: list[str]) -> list[dict]:
    """Fetch multiple URLs concurrently."""
    return await asyncio.gather(*[fetch(url) for url in urls])


# asyncio.run() only in entry points
if __name__ == "__main__":
    asyncio.run(fetch_all(urls))
```

Rules:
- Use `httpx.AsyncClient` for async HTTP (not `aiohttp` or `urllib`)
- Always `await` async calls; never block the event loop
- Use `asyncio.gather()` for concurrent operations
- Use `asyncio.run()` only in entry points

---

## CLI (Typer)

Use **typer** for all entry points.

```python
import typer

app = typer.Typer()


@app.command()
def process(
    input_path: Path = typer.Argument(..., help="Input file"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Process the input file."""
    if verbose:
        typer.echo(f"Processing {input_path}")
    # ...


if __name__ == "__main__":
    app()
```

---

## Decorators

```python
import functools


def timer(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logger.info("function_timed", name=func.__name__, elapsed=elapsed)
        return result
    return wrapper


def repeat(times: int):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return [func(*args, **kwargs) for _ in range(times)]
        return wrapper
    return decorator
```

---

## Memory and Performance

```python
# __slots__ reduces memory usage for many instances
class Point:
    __slots__ = ["x", "y"]

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


# String joining — never concatenate in a loop
result = "".join(str(item) for item in items)  # O(n)
# result = ""; for item in items: result += str(item)  # O(n²)
```

---

## Package Organization

```
src/{package_name}/
├── __init__.py
├── cli.py          # Typer entry point
├── logging.py      # structlog setup
├── settings.py     # Pydantic settings
├── py.typed        # PEP 561 marker
└── utils/
    └── __init__.py
tests/
├── conftest.py
└── test_*.py
```

### Imports

```python
# Order: stdlib → third-party → local (enforced by ruff)
import os
from pathlib import Path

import structlog
from pydantic import BaseModel

from {package_name}.settings import settings
```

### `__init__.py` Exports

```python
# {package_name}/__init__.py
__version__ = "0.1.0"

from {package_name}.models import User
from {package_name}.utils import format_name

__all__ = ["User", "format_name"]
```

---

## Anti-Patterns to Avoid

```python
# Bad: Mutable default argument
def append_to(item, items=[]):  # shared across calls!
    items.append(item)

# Good
def append_to(item, items=None):
    if items is None:
        items = []
    items.append(item)


# Bad: type() check
if type(obj) == list: ...

# Good
if isinstance(obj, list): ...


# Bad: comparing to None with ==
if value == None: ...

# Good
if value is None: ...


# Bad: wildcard import
from os.path import *

# Good
from os.path import join, exists


# Bad: bare except
try:
    risky()
except:
    pass

# Good
try:
    risky()
except SpecificError as e:
    logger.error("operation_failed", error=str(e))
```

---

## Quick Reference

| Idiom | Description |
|-------|-------------|
| EAFP | Try/except over condition checks |
| `with` | Context managers for all resources |
| List comprehension | Simple in-line transformations |
| Generator | Lazy evaluation, large datasets |
| Type hints | Mandatory on all function signatures |
| `pydantic.dataclass` | Simple data containers |
| `BaseSettings` | Config from env vars |
| `BaseModel` | External data validation |
| `__slots__` | Memory optimization for many instances |
| f-strings | All string formatting |
| `pathlib.Path` | All file system operations |
| `structlog` | All logging |
| `typer` | All CLI entry points |
| `httpx.AsyncClient` | Async HTTP requests |

**Remember**: Python code should be readable, explicit, and follow the principle of least surprise. When in doubt, prioritize clarity over cleverness.
