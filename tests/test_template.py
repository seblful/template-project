"""Generate projects from the template and hold each one to its own checks.

Template sources are not valid Python until rendered, so this is the only real test
of them: render a project per answer set, then run what that project itself runs.
Select one set with `-k`, e.g. `uv run pytest -k cli-config-github`.
"""

import re
import subprocess
from pathlib import Path
from typing import Any, NamedTuple

import pytest
import yaml
from copier import run_copy, run_update

REPO = Path(__file__).resolve().parents[1]
PACKAGE = "demo_proj"

# The answers with no default, plus the names every assertion below relies on.
BASE_ANSWERS: dict[str, Any] = {
    "project_slug": "demo-proj",
    "package_name": PACKAGE,
    "project_description": "A generated demo project.",
    "author_name": "Demo Author",
    "author_email": "demo@example.com",
}

# Together these cover every value of every answer at least once. The py311 set is a
# cli with a config file on purpose: the oldest Python meets the stdlib tomllib there.
ANSWER_SETS: dict[str, dict[str, Any]] = {
    "cli-config-github": {
        "python_version": "3.14",
        "license": "None",
        "project_type": "cli",
        "config_file": True,
        "ci": "github",
        "claude_settings": True,
    },
    "library-gitlab": {
        "python_version": "3.14",
        "license": "MIT",
        "project_type": "library",
        "ci": "gitlab",
        "claude_settings": False,
    },
    "cli-config-py311": {
        "python_version": "3.11",
        "license": "Apache",
        "project_type": "cli",
        "config_file": True,
        "ci": "none",
        "claude_settings": False,
    },
    "library-py312-github": {
        "python_version": "3.12",
        "license": "MIT",
        "project_type": "library",
        "ci": "github",
        "claude_settings": True,
    },
    "cli-gitlab": {
        "python_version": "3.14",
        "license": "Apache",
        "project_type": "cli",
        "config_file": False,
        "ci": "gitlab",
        "claude_settings": True,
    },
}

CLI_FILES = [
    f"src/{PACKAGE}/cli.py",
    f"src/{PACKAGE}/__main__.py",
    f"src/{PACKAGE}/settings.py",
    f"src/{PACKAGE}/logging.py",
    ".env.example",
    "tests/conftest.py",
    "tests/test_cli.py",
    "tests/test_settings.py",
    "tests/test_logging.py",
    "tests/test_config_roundtrip.py",
]
CONFIG_FILES = [
    f"src/{PACKAGE}/config_file.py",
    "tests/test_config_file.py",
    "config.example.toml",
]

# Hooks from every repo in the generated .pre-commit-config.yaml. Asserting that they
# passed proves the manual stage really runs all of them, remote repos included.
REQUIRED_HOOKS = [
    "ruff check",
    "ruff format",
    "mdformat",
    "ty type check",
    "pytest",
    "mkdocs build",
    "trim trailing whitespace",
    "uv-lock",
    "Detect hardcoded secrets",
]

# `[^$]` before `{{` excludes GitHub Actions' own `${{ ... }}` expressions.
UNRENDERED_JINJA = re.compile(r"(^|[^$])\{\{|\{%", re.MULTILINE)


class Project(NamedTuple):
    """A generated project and the answers it was generated from."""

    path: Path
    answers: dict[str, Any]


def _run(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    """Run a command, failing the test with its output if it exits non-zero."""
    result = subprocess.run(
        args, cwd=cwd, capture_output=True, text=True, encoding="utf-8", check=False
    )
    assert result.returncode == 0, f"{' '.join(args)}\n{result.stdout}{result.stderr}"
    return result


def _generate(dst: Path, answers: dict[str, Any], vcs_ref: str = "HEAD") -> None:
    """Render the template into `dst`, running its tasks as `--trust` would.

    With `HEAD`, copier also includes uncommitted template changes, with a warning.
    """
    run_copy(
        str(REPO),
        dst,
        data=answers,
        defaults=True,
        unsafe=True,
        vcs_ref=vcs_ref,
        quiet=True,
    )


def _run_every_check(path: Path) -> None:
    """Run the project's single definition of its checks, as its CI does."""
    result = _run(
        "uv",
        "run",
        "pre-commit",
        "run",
        "--all-files",
        "--hook-stage",
        "manual",
        "--show-diff-on-failure",
        cwd=path,
    )
    for hook in REQUIRED_HOOKS:
        assert re.search(rf"^{re.escape(hook)}\.+Passed$", result.stdout, re.M), (
            f"hook {hook!r} did not run and pass:\n{result.stdout}"
        )


@pytest.fixture(scope="module", params=list(ANSWER_SETS))
def project(
    request: pytest.FixtureRequest, tmp_path_factory: pytest.TempPathFactory
) -> Project:
    """Generate one project per answer set, shared by every test that checks it."""
    answers = {**BASE_ANSWERS, **ANSWER_SETS[request.param]}
    path = tmp_path_factory.mktemp(request.param) / "demo-proj"
    _generate(path, answers)
    return Project(path, answers)


def test_every_check_passes(project: Project) -> None:
    """The project passes every check it defines, and its git hooks are installed.

    The ruff-format and mdformat hooks carry the most weight: the template runs no
    formatter, so they see exactly what the template sources render to.
    """
    hooks = project.path / ".git" / "hooks"
    assert (hooks / "pre-commit").is_file()
    assert (hooks / "pre-push").is_file()

    _run_every_check(project.path)


def test_no_unrendered_jinja_survives(project: Project) -> None:
    """No committed file still contains a Jinja expression or tag."""
    tracked = _run("git", "ls-files", cwd=project.path).stdout.splitlines()
    leftovers = [
        name
        for name in tracked
        if name != "uv.lock"
        and UNRENDERED_JINJA.search(
            (project.path / name).read_text(encoding="utf-8", errors="replace")
        )
    ]

    assert leftovers == []


def test_answers_produce_the_right_files(project: Project) -> None:
    """Each file exists exactly when its answers call for it.

    Copier silently skips a conditional filename that renders empty, so a typo in
    one would otherwise produce a missing file with no error.
    """
    answers = project.answers
    cli = answers["project_type"] == "cli"
    config = cli and answers["config_file"]
    expected = {
        "tests/test_package.py": True,
        **dict.fromkeys(CLI_FILES, cli),
        **dict.fromkeys(CONFIG_FILES, config),
        ".github": answers["ci"] == "github",
        ".github/workflows/ci.yml": answers["ci"] == "github",
        ".github/dependabot.yml": answers["ci"] == "github",
        ".gitlab-ci.yml": answers["ci"] == "gitlab",
        ".claude": answers["claude_settings"],
        "LICENSE": answers["license"] != "None",
    }

    assert {name: (project.path / name).exists() for name in expected} == expected

    pyproject = (project.path / "pyproject.toml").read_text(encoding="utf-8")
    assert ("[project.scripts]" in pyproject) == cli
    assert ("\ndependencies = []\n" in pyproject) == (not cli)
    if cli:
        cli_source = (project.path / CLI_FILES[0]).read_text(encoding="utf-8")
        assert ('"--config"' in cli_source) == config


def test_installed_wheel_works(project: Project, tmp_path: Path) -> None:
    """The built wheel imports and runs from an empty directory, and writes nothing.

    Packaging only: settings behavior is the generated test suite's job. Running
    outside the checkout keeps the import from falling back to the source tree.
    """
    dist = tmp_path / "dist"
    _run("uv", "build", "--wheel", "--out-dir", str(dist), cwd=project.path)
    wheel = next(dist.glob("*.whl"))
    smoke = tmp_path / "smoke"
    smoke.mkdir()

    def run_installed(*args: str) -> str:
        """Run a command with only the wheel installed, from the empty directory."""
        python = project.answers["python_version"]
        return _run(
            *("uv", "run", "--no-project", "--isolated", "--python", python),
            *("--with", str(wheel), *args),
            cwd=smoke,
        ).stdout

    version = run_installed(
        "python", "-c", f"import {PACKAGE}; print({PACKAGE}.__version__)"
    )
    assert version.strip() == "0.1.0"
    if project.answers["project_type"] == "cli":
        assert "demo-proj 0.1.0" in run_installed("demo-proj", "--version")
        run_installed("demo-proj", "info")

    assert list(smoke.iterdir()) == []


def test_ci_configuration_is_valid(project: Project) -> None:
    """The CI file for the chosen provider passes that provider's offline checks."""
    match project.answers["ci"]:
        case "github":
            _run("actionlint", ".github/workflows/ci.yml", cwd=project.path)
        case "gitlab":
            # Parse only: real validation needs a GitLab token, which this repo lacks.
            yaml.safe_load((project.path / ".gitlab-ci.yml").read_text("utf-8"))
        case _:
            pytest.skip("ci=none ships no CI configuration")


def test_update_from_the_latest_release(tmp_path: Path) -> None:
    """A project generated at the latest tag updates to HEAD with no conflicts."""
    tags = _run("git", "tag", "--sort=-v:refname", cwd=REPO).stdout.split()
    if not tags:
        pytest.skip("no release tag to update from")
    path = tmp_path / "demo-proj"
    _generate(path, {**BASE_ANSWERS, "license": "MIT"}, vcs_ref=tags[0])

    run_update(
        path,
        defaults=True,
        unsafe=True,
        overwrite=True,
        vcs_ref="HEAD",
        conflict="rej",
        quiet=True,
    )

    rejects = [p for p in path.rglob("*.rej") if ".git" not in p.parts]
    assert rejects == []
    _run_every_check(path)
