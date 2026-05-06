---
name: python-testing
description: Professional Python testing with pytest — TDD, fixtures, parametrization, mocking, async, and coverage.
origin: ECC
---

# Python Testing

## Philosophy

- **TDD cycle**: red → green → refactor.
- **Test behavior, not implementation.** Refactors should not break tests.
- **One assertion concern per test.** Names describe the behavior: `test_login_with_invalid_credentials_fails`.
- **Independent tests.** No shared mutable state; order must not matter.
- **Coverage**: 80%+ overall, 100% on critical paths.

## Layout

```
tests/
├── conftest.py        # shared fixtures
├── unit/
├── integration/
└── e2e/
```

`pyproject.toml`:

```toml
[tool.pytest.ini_options]
addopts = "-ra --strict-markers"
testpaths = ["tests"]
markers = [
    "slow: long-running tests",
    "integration: hits external systems",
    "unit: pure unit tests",
]
```

## Assertions

Use plain `assert` — pytest rewrites it for rich diffs.

```python
assert result == expected
assert item in collection
assert value is None              # never `== None`
assert isinstance(obj, str)

with pytest.raises(ValueError, match="invalid input"):
    validate(bad)

with pytest.raises(CustomError) as exc_info:
    raise CustomError("boom", code=400)
assert exc_info.value.code == 400
```

## Fixtures

```python
@pytest.fixture
def user() -> User:
    return User(id=1, name="Alice")

@pytest.fixture
def database():
    db = Database(":memory:")
    db.create_tables()
    try:
        yield db
    finally:
        db.close()
```

Scopes: `function` (default), `class`, `module`, `session`. Promote scope only when setup is genuinely expensive — broader scopes invite cross-test pollution.

`autouse=True` for unconditional setup/teardown (e.g. resetting global config).

Share fixtures via `conftest.py` at the appropriate directory level.

### Built-in fixtures

| Fixture | Use |
|---------|-----|
| `tmp_path` | Temp `Path` directory (preferred over `tempfile`) |
| `monkeypatch` | Patch attrs/env vars for a test |
| `caplog` | Capture log records |
| `capsys` | Capture stdout/stderr |

```python
def test_processes_file(tmp_path: Path):
    f = tmp_path / "in.txt"
    f.write_text("hello")
    assert process(f) == "HELLO"

def test_uses_env(monkeypatch):
    monkeypatch.setenv("APP__DEBUG", "true")
    assert load_settings().debug is True
```

## Parametrization

```python
@pytest.mark.parametrize(
    "email,expected",
    [
        ("a@b.com", True),
        ("invalid", False),
        ("@no-domain.com", False),
    ],
    ids=["valid", "missing-at", "missing-domain"],
)
def test_email_validation(email: str, expected: bool):
    assert is_valid_email(email) is expected
```

Parametrize fixtures to run a suite across backends:

```python
@pytest.fixture(params=["sqlite", "postgres"])
def db(request):
    return Database(URLS[request.param])
```

## Mocking

Use `unittest.mock` (or `pytest-mock`'s `mocker`). **Patch where it's looked up, not where it's defined.** Prefer `autospec=True` to catch API drift.

```python
from unittest.mock import patch

@patch("mypkg.service.api_call", autospec=True)
def test_handles_error(api_call):
    api_call.side_effect = ConnectionError("net")
    with pytest.raises(ConnectionError):
        run()
    api_call.assert_called_once()
```

Don't mock what you don't own — wrap third-party calls in your own thin adapter and mock the adapter. Don't mock the system under test.

## Async

```python
# pyproject.toml: pytest-asyncio with asyncio_mode = "auto"

async def test_fetch():
    result = await fetch("https://api.example.com")
    assert result["status"] == "ok"

@patch("mypkg.async_call", autospec=True)
async def test_async_mock(async_call):
    async_call.return_value = {"ok": True}
    assert (await run())["ok"] is True
    async_call.assert_awaited_once()
```

## Logging assertions (structlog)

```python
def test_logs_user_processed(caplog):
    with caplog.at_level("INFO"):
        process_user("u1")
    assert any(r.message == "user_processed" for r in caplog.records)
```

## Test Organization Patterns

Group cohesive tests in a class when they share setup:

```python
class TestCalculator:
    @pytest.fixture
    def calc(self) -> Calculator:
        return Calculator()

    def test_add(self, calc):
        assert calc.add(2, 3) == 5

    def test_divide_by_zero(self, calc):
        with pytest.raises(ZeroDivisionError):
            calc.divide(10, 0)
```

Database tests: roll back per test for isolation.

```python
@pytest.fixture
def session():
    s = Session(bind=engine)
    s.begin_nested()
    try:
        yield s
    finally:
        s.rollback()
        s.close()
```

## DO / DON'T

**DO**

- Write the test first; let it drive the API.
- Use `tmp_path`, `monkeypatch`, `caplog` instead of rolling your own.
- Cover edge cases: empty, None, boundaries, unicode, errors.
- Keep slow/integration tests behind markers so the unit suite stays fast.

**DON'T**

- Test private internals — test through the public interface.
- Use bare `try/except` in tests — use `pytest.raises`.
- Share mutable state between tests (module-level lists, singletons).
- Over-specify mocks (every arg, every call order) — tests become brittle.
- Mock the thing you're trying to test.

## Running

```bash
uv run pytest                          # all tests
uv run pytest -v                       # verbose
uv run pytest -x --lf                  # stop at first failure, only last-failed
uv run pytest -k "user and not slow"   # filter by name
uv run pytest -m "not slow"            # filter by marker
uv run pytest --cov=src --cov-report=term-missing --cov-report=html
uv run pytest --pdb                    # debugger on failure
```

## Quick Reference

| Tool | Purpose |
|------|---------|
| `assert` | All assertions |
| `pytest.raises` | Expected exceptions |
| `@pytest.fixture` | Reusable setup/teardown |
| `@pytest.mark.parametrize` | Table-driven tests |
| `tmp_path` | Temp directory |
| `monkeypatch` | Patch attrs/env |
| `caplog` / `capsys` | Capture logs/output |
| `@patch(..., autospec=True)` | Spec-checked mocks |
| `pytest-asyncio` | Async tests |
| `--cov` | Coverage report |

**Tests are production code. Keep them clean, fast, and behavior-focused.**
