"""Print the migration notes for every release an update crosses.

Copier runs this after each update, with the versions it moved between in
`VERSION_PEP440_FROM` and `VERSION_PEP440_TO`. Each `vX.Y.Z.txt` next to this file is
the note for one release: it prints when `FROM < X.Y.Z <= TO`, oldest first, so one
update across several releases shows them all.
"""

import os
import re
import sys
from pathlib import Path


def release(version: str) -> tuple[int, ...]:
    """Return the release numbers of a version: `1.0.0.post6` is (1, 0, 0)."""
    match = re.match(r"\d+(?:\.\d+)*", version.removeprefix("v"))
    return tuple(int(part) for part in match[0].split(".")) if match else ()


def main() -> None:
    """Print the notes between the two versions copier passes in the environment."""
    # Notes use characters a Windows console encodes badly; stdout is only text here.
    sys.stdout.reconfigure(encoding="utf-8")
    start = release(os.environ["VERSION_PEP440_FROM"])
    end = release(os.environ["VERSION_PEP440_TO"])
    for note in sorted(
        Path(__file__).parent.glob("v*.txt"), key=lambda p: release(p.stem)
    ):
        if start < release(note.stem) <= end:
            print(note.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
