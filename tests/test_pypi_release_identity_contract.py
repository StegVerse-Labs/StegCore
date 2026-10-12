from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/publish-pypi.yml"


def test_release_publication_is_frozen_to_approved_commit():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "if: github.event_name == 'release'" in workflow
    assert 'test "$RELEASE_TAG" = "v0.3.0"' in workflow
    assert 'EXPECTED="58445bb14642c1889cf9802666c15bd48c6d2e39"' in workflow
    assert 'PARENT="ef38410505b0ef3e84148892b1d6e3cdef20f300"' in workflow
    assert 'test "$ACTUAL" = "$EXPECTED"' in workflow
    assert 'test "$(git rev-parse "$EXPECTED^")" = "$PARENT"' in workflow
    assert 'test "$(git rev-parse HEAD)" = "$EXPECTED"' in workflow


def test_publish_uses_oidc_and_only_release_event():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "if: github.event_name == 'release'\n    needs: build" in workflow
    assert "id-token: write" in workflow
    assert "pypa/gh-action-pypi-publish@release/v1" in workflow
    assert "attestations: true" in workflow
