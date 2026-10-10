"""The migration notes script prints exactly the releases an update crosses."""

import os
import re
import subprocess
import sys

import pytest
from support import REPO


def _crossed(start: str, end: str) -> list[str]:
    """Return the versions whose notes print for an update from `start` to `end`."""
    result = subprocess.run(
        [sys.executable, str(REPO / "migrations" / "notes.py")],
        env={**os.environ, "VERSION_PEP440_FROM": start, "VERSION_PEP440_TO": end},
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return re.findall(r"^This update crossed (v[\d.]+)", result.stdout, re.MULTILINE)


@pytest.mark.parametrize(
    ("start", "end", "expected"),
    [
        ("0.8.0", "1.0.1", ["v0.9.0", "v0.9.3", "v1.0.0", "v1.0.1"]),
        ("0.9.0", "1.0.0", ["v0.9.3", "v1.0.0"]),
        ("1.0.0", "1.0.1", ["v1.0.1"]),
        ("1.0.1", "1.0.1", []),
        # An untagged template checkout reports `.postN`: its release is the last tag.
        ("1.0.0", "1.0.0.post6", []),
    ],
)
def test_notes_cover_every_release_in_the_range_oldest_first(
    start: str, end: str, expected: list[str]
) -> None:
    """A note prints when its release is after `start` and no later than `end`."""
    assert _crossed(start, end) == expected
