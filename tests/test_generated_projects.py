"""Generate each answer set with its tasks and hold it to the checks it defines.

Slow: this needs uv, Bun and network access, and installs a project per answer set.
Template sources are not valid Python until rendered, so this is the only real test of
them. Run one set with `uv run pytest -m slow -k cli-none-py311`.
"""

import subprocess
from pathlib import Path

import pytest
from support import (
    ANSWER_SETS,
    BASE_ANSWERS,
    PACKAGE,
    Project,
    generate,
    run,
    run_every_check,
)

pytestmark = pytest.mark.slow


@pytest.fixture(scope="module", params=list(ANSWER_SETS))
def project(
    request: pytest.FixtureRequest, tmp_path_factory: pytest.TempPathFactory
) -> Project:
    """Generate one project per answer set, shared by every test that checks it."""
    answers = {**BASE_ANSWERS, **ANSWER_SETS[request.param]}
    path = tmp_path_factory.mktemp(request.param) / "demo-proj"
    generate(path, answers)
    return Project(request.param, path, answers)


def test_every_check_passes(project: Project) -> None:
    """The project passes every check it defines, and its git hooks are installed.

    The ruff-format and mdformat hooks carry the most weight: the template runs no
    formatter, so they see exactly what the template sources render to.
    """
    hooks = project.path / ".git" / "hooks"
    assert (hooks / "pre-commit").is_file()
    assert (hooks / "pre-push").is_file()
    assert (hooks / "commit-msg").is_file()

    run_every_check(
        project.path,
        web=project.answers.get("web", False),
        github=project.answers["ci"] == "github",
    )


def test_commit_message_hook_enforces_conventional_commits(project: Project) -> None:
    """The commit-msg hook rejects a free-form subject, accepts a conventional one."""

    def commit(message: str) -> subprocess.CompletedProcess[str]:
        """Make an empty commit with `message`, the hooks enabled."""
        identity = ("-c", "user.name=Demo Author", "-c", "user.email=demo@example.com")
        return subprocess.run(
            ["git", *identity, "commit", "--allow-empty", "-m", message],
            cwd=project.path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

    rejected = commit("updated some stuff")
    assert rejected.returncode != 0, rejected.stdout + rejected.stderr
    accepted = commit("chore: check the commit-msg hook")
    assert accepted.returncode == 0, accepted.stdout + accepted.stderr


def test_installed_wheel_works(project: Project, tmp_path: Path) -> None:
    """The built wheel imports and runs from an empty directory, and writes nothing.

    Packaging only: settings behavior is the generated test suite's job. Running
    outside the checkout keeps the import from falling back to the source tree.
    """
    project_type = project.answers["project_type"]
    dist = tmp_path / "dist"
    run("uv", "build", "--wheel", "--out-dir", str(dist), cwd=project.path)
    wheel = next(dist.glob("*.whl"))
    smoke = tmp_path / "smoke"
    smoke.mkdir()

    def run_installed(*args: str) -> str:
        """Run a command with only the wheel installed, from the empty directory."""
        python = project.answers["python_version"]
        return run(
            *("uv", "run", "--no-project", "--isolated", "--python", python),
            *("--with", str(wheel), *args),
            cwd=smoke,
        ).stdout

    version = run_installed(
        "python", "-c", f"import {PACKAGE}; print({PACKAGE}.__version__)"
    )
    assert version.strip() == "0.1.0"
    if project_type != "library":
        assert "demo-proj 0.1.0" in run_installed("demo-proj", "--version")
    if project_type == "cli":
        run_installed("demo-proj", "settings")
    if project_type == "api":
        assert '"/api/health"' in run_installed("demo-proj", "openapi")

    assert list(smoke.iterdir()) == []
