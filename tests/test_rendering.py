"""Render every answer set and compare it with what is committed.

These run in seconds because no task runs: no git, uv or Bun, only copier rendering
files. Each answer set has a committed snapshot of its output in `tests/snapshots`, so
a change to the template shows up in review as the change to every project it
affects. After an intended change, refresh them and read the diff:

    uv run pytest --update-snapshots

Whether those files then pass their own checks is the slow tier's job; see
`test_generated_projects.py`.
"""

import difflib
import json
import re
import shutil
from pathlib import Path
from typing import Any

import pytest
import yaml
from support import ANSWER_SETS, BASE_ANSWERS, REPO, Project, generate, run

SNAPSHOTS = Path(__file__).parent / "snapshots"
# Names the rendered project has no say in: the answers file records where the
# template came from, which differs on every checkout.
UNSTABLE = {".copier-answers.yml"}

# `[^$]` before `{{` excludes GitHub Actions' own `${{ ... }}` expressions.
UNRENDERED_JINJA = re.compile(r"(^|[^$])\{\{|\{%", re.MULTILINE)


def _tree(root: Path) -> dict[str, bytes]:
    """Map every file under `root` to its content."""
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.relative_to(root).as_posix() not in UNSTABLE
    }


def _describe(expected: dict[str, bytes], actual: dict[str, bytes]) -> str:
    """Summarize how a rendered tree differs from its snapshot."""
    lines = [f"missing from the output: {name}" for name in expected.keys() - actual]
    lines += [f"not in the snapshot: {name}" for name in actual.keys() - expected]
    for name in sorted(expected.keys() & actual):
        if expected[name] != actual[name]:
            diff = difflib.unified_diff(
                expected[name].decode("utf-8", "replace").splitlines(),
                actual[name].decode("utf-8", "replace").splitlines(),
                fromfile=f"snapshot/{name}",
                tofile=f"output/{name}",
                lineterm="",
            )
            lines += [*diff][:30]
    return "\n".join(sorted(lines) if len(lines) < 0 else lines)


@pytest.fixture(scope="module", params=list(ANSWER_SETS))
def rendered(
    request: pytest.FixtureRequest, tmp_path_factory: pytest.TempPathFactory
) -> Project:
    """Render one answer set without its tasks, shared by every test below."""
    answers = {**BASE_ANSWERS, **ANSWER_SETS[request.param]}
    path = tmp_path_factory.mktemp(request.param) / "demo-proj"
    generate(path, answers, tasks=False)
    return Project(request.param, path, answers)


def test_output_matches_the_snapshot(
    rendered: Project, request: pytest.FixtureRequest
) -> None:
    """The rendered files are exactly the committed snapshot, none more, none less.

    Copier silently skips a conditional filename that renders empty, so a typo in one
    would otherwise be a missing file with no error: here it is a failing diff.
    """
    snapshot = SNAPSHOTS / rendered.name
    actual = _tree(rendered.path)
    if request.config.getoption("--update-snapshots"):
        shutil.rmtree(snapshot, ignore_errors=True)
        for name, content in actual.items():
            target = snapshot / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        return

    expected = _tree(snapshot) if snapshot.is_dir() else {}
    assert actual == expected, _describe(expected, actual)


def test_no_unrendered_jinja_survives(rendered: Project) -> None:
    """No rendered file still contains a Jinja expression or tag."""
    leftovers = [
        name
        for name, content in _tree(rendered.path).items()
        if UNRENDERED_JINJA.search(content.decode("utf-8", "replace"))
    ]

    assert leftovers == []


def test_ci_configuration_is_valid(rendered: Project) -> None:
    """The CI files for the chosen provider pass that provider's offline checks."""
    match rendered.answers["ci"]:
        case "github":
            # By path: with no .git, actionlint finds no project to look in.
            workflows = sorted((rendered.path / ".github/workflows").glob("*.yml"))
            run("actionlint", *map(str, workflows), cwd=rendered.path)
        case "gitlab":
            # Parse only: real validation needs a GitLab token, which this repo lacks.
            yaml.safe_load((rendered.path / ".gitlab-ci.yml").read_text("utf-8"))
        case _:
            assert not (rendered.path / ".github").exists()
            assert not (rendered.path / ".gitlab-ci.yml").exists()


def test_bun_version_matches_what_ci_installs(rendered: Project) -> None:
    """The Bun the template pins is the Bun this repo's CI tests it with."""
    manifest = rendered.path / "web" / "package.json"
    if not manifest.is_file():
        pytest.skip("no web app in this answer set")
    workflow = yaml.safe_load((REPO / ".github/workflows/ci.yml").read_text("utf-8"))

    package = json.loads(manifest.read_text("utf-8"))

    assert package["packageManager"] == f"bun@{workflow['env']['BUN_VERSION']}"


@pytest.mark.parametrize(
    ("question", "value"),
    [
        ("project_slug", "My Project"),
        ("package_name", "1st_package"),
        ("project_description", 'says "hi"'),
        ("author_name", ""),
        ("author_email", "not-an-email"),
        ("python_version", "3.10"),
        ("python_version", "3.14.1"),
    ],
)
def test_invalid_answers_are_rejected(
    question: str, value: str, tmp_path: Path
) -> None:
    """Each answer's validator refuses a value that would break the output."""
    answers: dict[str, Any] = {**BASE_ANSWERS, question: value}

    with pytest.raises(ValueError, match=question):
        generate(tmp_path / "demo-proj", answers, tasks=False)
