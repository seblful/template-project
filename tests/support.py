"""Answer sets and helpers shared by the template tests."""

import re
import subprocess
from pathlib import Path
from typing import Any, NamedTuple

from copier import run_copy

REPO = Path(__file__).resolve().parents[1]
PACKAGE = "demo_proj"

# The answers with no default, plus the names every assertion relies on.
BASE_ANSWERS: dict[str, Any] = {
    "project_slug": "demo-proj",
    "package_name": PACKAGE,
    "project_description": "A generated demo project.",
    "author_name": "Demo Author",
    "author_email": "demo@example.com",
}

# Together these cover every value of every answer at least once. cli-none-py311 meets
# the oldest Python and the stdlib tomllib; cli-github runs the newest, which CI runs
# on Linux only. An api with a license on purpose: it still gets no release.yml.
ANSWER_SETS: dict[str, dict[str, Any]] = {
    "cli-github": {
        "project_type": "cli",
        "python_version": "3.15",
        "license": "None",
        "ci": "github",
    },
    "cli-none-py311": {
        "project_type": "cli",
        "python_version": "3.11",
        "license": "Apache",
        "publish": False,
        "ci": "none",
    },
    "library-github-py312": {
        "project_type": "library",
        "python_version": "3.12",
        "license": "MIT",
        "ci": "github",
    },
    "library-gitlab": {
        "project_type": "library",
        "python_version": "3.14",
        "license": "None",
        "ci": "gitlab",
    },
    "api-gitlab-py313": {
        "project_type": "api",
        "python_version": "3.13",
        "license": "Apache",
        "ci": "gitlab",
    },
    "api-web-github": {
        "project_type": "api",
        "web": True,
        "python_version": "3.14",
        "license": "MIT",
        "ci": "github",
    },
    "api-web-gitlab-py312": {
        "project_type": "api",
        "web": True,
        "python_version": "3.12",
        "license": "None",
        "ci": "gitlab",
    },
}


class Project(NamedTuple):
    """A generated project, the answer set it came from, and the answers used."""

    name: str
    path: Path
    answers: dict[str, Any]


def run(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    """Run a command, failing the test with its output if it exits non-zero."""
    result = subprocess.run(
        args, cwd=cwd, capture_output=True, text=True, encoding="utf-8", check=False
    )
    assert result.returncode == 0, f"{' '.join(args)}\n{result.stdout}{result.stderr}"
    return result


def generate(
    dst: Path,
    answers: dict[str, Any],
    *,
    tasks: bool = True,
    vcs_ref: str = "HEAD",
    src: Path = REPO,
) -> None:
    """Render the template into `dst`, running its tasks as `--trust` would.

    Without `tasks` nothing but the files is rendered: no git, uv or Bun runs, which
    is what keeps the fast tests fast. With `HEAD`, copier also includes uncommitted
    template changes, with a warning.
    """
    run_copy(
        str(src),
        dst,
        data=answers,
        defaults=True,
        unsafe=tasks,
        skip_tasks=not tasks,
        vcs_ref=vcs_ref,
        quiet=True,
    )


# Hooks from every repo in the generated .pre-commit-config.yaml. Asserting that they
# passed proves the manual stage really runs all of them, remote repos included.
REQUIRED_HOOKS = [
    "ruff check",
    "ruff format",
    "ty type check",
    "pytest",
    "mdformat",
    "trim trailing whitespace",
    "uv-lock",
    "Detect hardcoded secrets",
]
WEB_HOOKS = [
    "api client is current",
    "biome check",
    "tsc type check",
    "vitest",
    "vite build",
]


def run_every_check(path: Path, *, web: bool = False, github: bool = False) -> None:
    """Run the project's single definition of its checks, as its CI does.

    A web app adds its own hooks. With `github`, also require zizmor, which skips
    itself when there is no workflow.
    """
    result = run(
        *("uv", "run", "prek", "run", "--all-files", "--hook-stage", "manual"),
        "--show-diff-on-failure",
        cwd=path,
    )
    required = [*REQUIRED_HOOKS, *(WEB_HOOKS if web else []), *(["zizmor"] * github)]
    for hook in required:
        assert re.search(rf"^{re.escape(hook)}\.+Passed$", result.stdout, re.M), (
            f"hook {hook!r} did not run and pass:\n{result.stdout}"
        )
