"""Update generated projects with `copier update`, as their owners would.

Slow, like `test_generated_projects.py`: each update re-runs the template's tasks and
then every check of the updated project.
"""

import shutil
from pathlib import Path

import pytest
from copier import run_update
from support import BASE_ANSWERS, REPO, generate, run, run_every_check

pytestmark = pytest.mark.slow


def _update(path: Path, **data: object) -> None:
    """Update the project at `path` to the template's working tree, never prompting."""
    run_update(
        path,
        data=data,
        defaults=True,
        unsafe=True,
        overwrite=True,
        vcs_ref="HEAD",
        conflict="rej",
        quiet=True,
    )
    rejects = [p for p in path.rglob("*.rej") if ".git" not in p.parts]
    assert rejects == []


def test_update_from_the_latest_release(tmp_path: Path) -> None:
    """A project generated at the latest tag updates to HEAD with no conflicts."""
    tags = run("git", "tag", "--sort=-v:refname", cwd=REPO).stdout.split()
    if not tags:
        pytest.skip("no release tag to update from")
    path = tmp_path / "demo-proj"
    generate(path, {**BASE_ANSWERS, "license": "MIT"}, vcs_ref=tags[0])

    _update(path)

    run_every_check(path, github=True)  # ci defaults to github


def _committed_copy(dst: Path) -> Path:
    """Copy the template, uncommitted changes included, into a one-commit repo.

    `copier update` re-renders the version a project came from, by its commit. From
    uncommitted changes copier generates through a commit that only its own scratch
    clone has, so a later update would find nothing to check out.
    """
    listed = run(
        "git", "ls-files", "--cached", "--others", "--exclude-standard", "-z", cwd=REPO
    ).stdout.split("\0")
    for name in filter(None, listed):
        source = REPO / name
        # Only what copier reads. A file still in the index but deleted from the
        # working tree is skipped too.
        wanted = name == "copier.yml" or name.startswith(("template/", "migrations/"))
        if wanted and source.is_file():
            target = dst / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    run("git", "init", "--quiet", cwd=dst)
    # Template paths spell out their Jinja conditions, which can push a deep temporary
    # directory past Windows' 260-character limit.
    run("git", "config", "core.longpaths", "true", cwd=dst)
    run("git", "add", "--all", cwd=dst)
    identity = ("-c", "user.name=Demo Author", "-c", "user.email=demo@example.com")
    run("git", *identity, "commit", "--quiet", "--message", "template", cwd=dst)
    # Copier runs no migrations at all for a template without a version tag.
    run("git", "tag", "v0.0.0", cwd=dst)
    return dst


def _files(root: Path) -> dict[str, bytes]:
    """Map every file under `root` to its content, skipping what tools write there."""
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }


def test_adding_the_web_app_leaves_the_python_side_alone(tmp_path: Path) -> None:
    """An api updates to api plus web with no conflicts, and still passes its checks.

    This is what the flat layout with a `web/` folder is for: the side added later
    lands beside the existing one. The Python package, its tests and its packaging
    come through byte for byte.
    """
    template = _committed_copy(tmp_path / "template")
    path = tmp_path / "demo-proj"
    generate(
        path,
        {**BASE_ANSWERS, "project_type": "api", "license": "MIT"},
        src=template,
    )
    python_side = ["src", "tests"]
    before = {name: _files(path / name) for name in python_side}
    before_packaging = (path / "pyproject.toml").read_bytes()

    _update(path, web=True)

    assert {name: _files(path / name) for name in python_side} == before
    assert (path / "pyproject.toml").read_bytes() == before_packaging
    assert (path / "web" / "package.json").is_file()
    # Staged as anyone would before committing: hooks only see tracked files, and an
    # update leaves the side it adds untracked.
    run("git", "add", "--all", cwd=path)
    run_every_check(path, web=True, github=True)
