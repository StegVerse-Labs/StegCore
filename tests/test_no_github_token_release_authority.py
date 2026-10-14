"""Release authority is TV/TVC only; GitHub Actions holds no runtime or release authority.

StegVerse-Labs/.github TASK_REGISTRY_CANONICAL_INVARIANTS.md. No workflow may create a tag
or GitHub Release itself; publish workflows may only react to a release created elsewhere.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = sorted((ROOT / ".github" / "workflows").glob("*.y*ml"))

TAG_OR_RELEASE_CREATION = re.compile(
    r"createRef|createTag|createRelease"
    r"|git\s+tag\s+-[as]\b"
    r"|git\s+push\b[^\n]*(--tags|refs/tags)"
    r"|gh\s+release\s+create"
    r"|action-gh-release|ncipollo/release-action|actions/create-release"
)


def test_workflows_exist():
    assert WORKFLOWS


def test_no_workflow_creates_tags_or_releases():
    offenders = {
        path.name: sorted({m.group(0) for m in TAG_OR_RELEASE_CREATION.finditer(path.read_text(encoding="utf-8"))})
        for path in WORKFLOWS
    }
    offenders = {name: hits for name, hits in offenders.items() if hits}
    assert offenders == {}


def test_pattern_detects_known_creation_forms():
    for sample in (
        "await github.rest.git.createRef({ref: 'refs/tags/v1'})",
        "await github.rest.repos.createRelease({tag_name: 'v1'})",
        'git tag -a "$TAG" "$COMMIT" -m x',
        'git push origin "refs/tags/${TAG}"',
        "git push --tags",
        "gh release create v1",
        "uses: softprops/action-gh-release@v2",
    ):
        assert TAG_OR_RELEASE_CREATION.search(sample), sample
    for allowed in (
        'ACTUAL="$(git rev-parse "refs/tags/$RELEASE_TAG^{commit}")"',
        "git fetch --tags --force",
        "curl -fsSL https://github.com/o/r/archive/refs/tags/v1.tar.gz",
    ):
        assert not TAG_OR_RELEASE_CREATION.search(allowed), allowed
