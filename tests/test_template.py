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
# cli-config-github runs the newest Python, which CI runs on Linux only.
ANSWER_SETS: dict[str, dict[str, Any]] = {
    "cli-config-github": {
        "python_version": "3.15",
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
    # A license on purpose: an api still gets no release.yml, since it is deployed.
    "api-github": {
        "python_version": "3.14",
        "license": "MIT",
        "project_type": "api",
        "ci": "github",
        "claude_settings": True,
    },
    "api-gitlab-py311": {
        "python_version": "3.11",
        "license": "None",
        "project_type": "api",
        "ci": "gitlab",
        "claude_settings": False,
    },
    "frontend-github": {
        "python_version": "3.14",
        "license": "MIT",
        "project_type": "frontend",
        "ci": "github",
        "claude_settings": True,
    },
    "frontend-gitlab": {
        "python_version": "3.13",
        "license": "None",
        "project_type": "frontend",
        "ci": "gitlab",
        "claude_settings": False,
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
# An api is a uv workspace member in apps/api; the root keeps only shared tooling.
API = "apps/api"
API_FILES = [
    f"{API}/pyproject.toml",
    f"{API}/.env.example",
    f"{API}/src/{PACKAGE}/__init__.py",
    f"{API}/src/{PACKAGE}/__main__.py",
    f"{API}/src/{PACKAGE}/app.py",
    f"{API}/src/{PACKAGE}/cli.py",
    f"{API}/src/{PACKAGE}/settings.py",
    f"{API}/src/{PACKAGE}/logging.py",
    f"{API}/src/{PACKAGE}/py.typed",
    f"{API}/src/{PACKAGE}/health/router.py",
    f"{API}/src/{PACKAGE}/health/schemas.py",
    f"{API}/src/{PACKAGE}/health/service.py",
    f"{API}/tests/conftest.py",
    f"{API}/tests/test_app.py",
    f"{API}/tests/test_cli.py",
    f"{API}/tests/test_health.py",
    f"{API}/tests/test_package.py",
    f"{API}/tests/test_settings.py",
    f"{API}/tests/test_logging.py",
    f"{API}/tests/test_config_roundtrip.py",
]
# A frontend is a Bun workspace member in apps/web; bun.lock comes from the first
# install, so it is generated rather than rendered.
WEB = "apps/web"
WEB_FILES = [
    "package.json",
    "bun.lock",
    "biome.json",
    f"{WEB}/package.json",
    f"{WEB}/tsconfig.json",
    f"{WEB}/vite.config.ts",
    f"{WEB}/index.html",
    f"{WEB}/src/main.tsx",
    f"{WEB}/src/router.tsx",
    f"{WEB}/src/styles.css",
    f"{WEB}/src/test-setup.ts",
    f"{WEB}/src/routes/root.tsx",
    f"{WEB}/src/routes/index.tsx",
    f"{WEB}/src/features/counter/Counter.tsx",
    f"{WEB}/src/features/counter/Counter.test.tsx",
]
CONFIG_FILES = [
    f"src/{PACKAGE}/config_file.py",
    "tests/test_config_file.py",
    "config.example.toml",
]

# Hooks from every repo in the generated .pre-commit-config.yaml. Asserting that they
# passed proves the manual stage really runs all of them, remote repos included.
REQUIRED_HOOKS = [
    "mdformat",
    "zensical build",
    "trim trailing whitespace",
    "uv-lock",
    "Detect hardcoded secrets",
]
PYTHON_HOOKS = ["ruff check", "ruff format", "ty type check", "pytest"]
FRONTEND_HOOKS = ["biome check", "tsc type check", "vitest", "vite build"]

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


def _run_every_check(
    path: Path, *, project_type: str = "cli", github: bool = False
) -> None:
    """Run the project's single definition of its checks, as its CI does.

    The hooks required depend on `project_type`: Python and frontend projects each
    add their own. With `github`, also require zizmor, which skips itself when there
    is no workflow.
    """
    result = _run(
        "uv",
        "run",
        "prek",
        "run",
        "--all-files",
        "--hook-stage",
        "manual",
        "--show-diff-on-failure",
        cwd=path,
    )
    required = [
        *REQUIRED_HOOKS,
        *(FRONTEND_HOOKS if project_type == "frontend" else PYTHON_HOOKS),
        *(["zizmor"] if github else []),
    ]
    for hook in required:
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
    assert (hooks / "commit-msg").is_file()

    _run_every_check(
        project.path,
        project_type=project.answers["project_type"],
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


def test_no_unrendered_jinja_survives(project: Project) -> None:
    """No committed file still contains a Jinja expression or tag."""
    tracked = _run("git", "ls-files", cwd=project.path).stdout.splitlines()
    leftovers = [
        name
        for name in tracked
        if name not in {"uv.lock", "bun.lock"}
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
    api = answers["project_type"] == "api"
    frontend = answers["project_type"] == "frontend"
    library = answers["project_type"] == "library"
    monorepo = api or frontend
    config = cli and answers["config_file"]
    expected = {
        "src": not monorepo,
        "tests": not monorepo,
        "tests/test_package.py": not monorepo,
        "apps": monorepo,
        "docs/reference.md": not frontend,
        **dict.fromkeys(CLI_FILES, cli),
        **dict.fromkeys(CONFIG_FILES, config),
        **dict.fromkeys(API_FILES, api),
        **dict.fromkeys(WEB_FILES, frontend),
        ".github": answers["ci"] == "github",
        ".github/workflows/ci.yml": answers["ci"] == "github",
        ".github/dependabot.yml": answers["ci"] == "github",
        # Only a package is published; an api is deployed.
        ".github/workflows/release.yml": (
            answers["ci"] == "github" and answers["license"] != "None" and not monorepo
        ),
        ".gitlab-ci.yml": answers["ci"] == "gitlab",
        ".claude": answers["claude_settings"],
        "LICENSE": answers["license"] != "None",
    }

    assert {name: (project.path / name).exists() for name in expected} == expected

    pyproject = (project.path / "pyproject.toml").read_text(encoding="utf-8")
    assert ("[project.scripts]" in pyproject) == cli
    # A library forces nothing on its consumers; a frontend's root holds only tooling.
    assert ("\ndependencies = []\n" in pyproject) == (library or frontend)
    assert ("[tool.uv.workspace]" in pyproject) == api
    if cli:
        cli_source = (project.path / CLI_FILES[0]).read_text(encoding="utf-8")
        assert ('"--config"' in cli_source) == config


def test_installed_wheel_works(project: Project, tmp_path: Path) -> None:
    """The built wheel imports and runs from an empty directory, and writes nothing.

    Packaging only: settings behavior is the generated test suite's job. Running
    outside the checkout keeps the import from falling back to the source tree.
    """
    project_type = project.answers["project_type"]
    if project_type == "frontend":
        pytest.skip("a frontend ships no Python package")
    dist = tmp_path / "dist"
    # The api is a workspace member; the workspace root itself ships nothing.
    package = ["--package", "demo-proj"] if project_type == "api" else []
    _run("uv", "build", *package, "--wheel", "--out-dir", str(dist), cwd=project.path)
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
    if project_type in {"cli", "api"}:
        assert "demo-proj 0.1.0" in run_installed("demo-proj", "--version")
    if project_type == "cli":
        run_installed("demo-proj", "info")
    if project_type == "api":
        assert '"/api/health"' in run_installed("demo-proj", "openapi")

    assert list(smoke.iterdir()) == []


def test_ci_configuration_is_valid(project: Project) -> None:
    """The CI file for the chosen provider passes that provider's offline checks."""
    match project.answers["ci"]:
        case "github":
            _run("actionlint", cwd=project.path)  # every workflow, release.yml too
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
    _run_every_check(path, github=True)  # ci defaults to github
