from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/publish-pypi.yml"


def test_release_publication_is_bound_to_the_recorded_release_commit():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "if: github.event_name == 'release'" in workflow
    assert 'pathlib.Path("RELEASE_BINDING.json")' in workflow
    assert 'binding["tag"] == tag == f"v{version}"' in workflow
    assert 'git("rev-parse", f"refs/tags/{tag}^{{commit}}") == head' in workflow
    assert 'parents == [binding["source_parent"]]' in workflow
    assert 'changed == set(binding["release_commit_paths"])' in workflow


def test_binding_runs_before_build_and_rename():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    binding = workflow.index("Verify immutable release candidate binding")
    assert binding < workflow.index("Apply deterministic public distribution name")
    assert binding < workflow.index("Build wheel and source distribution")


def test_publish_uses_oidc_trusted_publishing_and_only_release_event():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "if: github.event_name == 'release'\n    needs: build" in workflow
    assert "id-token: write" in workflow
    assert "pypa/gh-action-pypi-publish@release/v1" in workflow
    assert "attestations: true" in workflow
    assert "replacement = 'name = \"stegverse-stegcore\"'" in workflow
