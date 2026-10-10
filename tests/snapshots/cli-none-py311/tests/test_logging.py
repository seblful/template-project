"""Unit tests for logging setup."""

import json
import logging
import warnings

import pytest

from demo_proj.logging import get_logger, reset_logging, setup_logging
from demo_proj.settings import LoggingSettings

# Made at import, as application modules do, before any setup has run.
_MODULE_LOGGER = get_logger("module")


def _json_records(captured: str) -> list[dict[str, object]]:
    """Parse the JSON lines written to stderr."""
    return [json.loads(line) for line in captured.splitlines() if line.strip()]


def _raise_boom() -> None:
    """Raise from a named frame, so the serialized traceback has something to show."""
    raise ValueError("boom")


def test_setup_logging_is_idempotent() -> None:
    """A second call adds nothing, even though pytest owns handlers of its own."""
    setup_logging(LoggingSettings())
    count = len(logging.root.handlers)

    setup_logging(LoggingSettings())
    assert len(logging.root.handlers) == count


def test_console_defaults_to_text(capsys: pytest.CaptureFixture[str]) -> None:
    """Console output is human-readable unless JSON is asked for."""
    setup_logging(LoggingSettings())

    get_logger("test").info("readable event", answer=42)

    output = capsys.readouterr().err
    assert "readable event" in output
    assert "answer=42" in output
    with pytest.raises(json.JSONDecodeError):
        json.loads(output)


def test_json_records_have_a_timestamp(capsys: pytest.CaptureFixture[str]) -> None:
    """JSON output is machine-readable and every record is timestamped."""
    setup_logging(LoggingSettings(format="json"))

    get_logger("test").info("hello", answer=42)

    record = _json_records(capsys.readouterr().err)[0]
    assert record["event"] == "hello"
    assert record["answer"] == 42
    assert record["level"] == "info"
    assert record["timestamp"]


def test_level_drops_quieter_events(capsys: pytest.CaptureFixture[str]) -> None:
    """Events below the configured level are never written."""
    setup_logging(LoggingSettings(format="json", level="WARNING"))

    get_logger("test").info("dropped")
    logging.getLogger("some.library").info("dropped too")
    get_logger("test").warning("kept")

    assert [r["event"] for r in _json_records(capsys.readouterr().err)] == ["kept"]


def test_library_logs_are_rendered_like_application_logs(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A third-party logger using plain stdlib logging still lands as JSON."""
    setup_logging(LoggingSettings(format="json"))

    logging.getLogger("some.library").warning("from a library")

    record = _json_records(capsys.readouterr().err)[0]
    assert record["event"] == "from a library"
    assert record["level"] == "warning"
    assert record["logger"] == "some.library"
    assert record["timestamp"]


def test_exceptions_are_serialized_not_dropped(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """`log.exception` writes a real traceback rather than `exc_info: true`."""
    setup_logging(LoggingSettings(format="json"))

    try:
        _raise_boom()
    except ValueError:
        get_logger("test").exception("it broke")

    record = _json_records(capsys.readouterr().err)[0]
    assert record["exception"]
    assert "ValueError" in json.dumps(record["exception"])


def test_reset_logging_detaches_and_allows_reconfiguration(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """reset_logging undoes setup exactly, so a later call takes effect again."""
    before = list(logging.root.handlers)
    setup_logging(LoggingSettings())

    reset_logging()
    assert logging.root.handlers == before

    setup_logging(LoggingSettings(format="json"))
    get_logger("test").info("reconfigured")
    assert _json_records(capsys.readouterr().err)[0]["event"] == "reconfigured"


def test_a_logger_made_at_import_follows_the_latest_setup(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A module-level logger is not pinned to the configuration it first logged with."""
    setup_logging(LoggingSettings(format="json", level="WARNING"))
    _MODULE_LOGGER.warning("first")
    reset_logging()

    setup_logging(LoggingSettings(format="json", level="DEBUG"))
    _MODULE_LOGGER.debug("second")

    events = [r["event"] for r in _json_records(capsys.readouterr().err)]
    assert events == ["first", "second"]


def test_warnings_are_rendered_like_other_records(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """`warnings.warn` output goes through the handler instead of raw to stderr."""
    setup_logging(LoggingSettings(format="json"))

    with warnings.catch_warnings():
        warnings.simplefilter("always")
        warnings.warn("careful", UserWarning, stacklevel=2)

    record = _json_records(capsys.readouterr().err)[0]
    assert record["logger"] == "py.warnings"
    assert "careful" in str(record["event"])
