import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "prepare_portable_release.py"

spec = importlib.util.spec_from_file_location("portable_release_factory", TOOL)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def test_release_manifest_matches_source_version_and_requires_dual_archives():
    manifest = module.load_json(module.MANIFEST_PATH)
    module.validate_manifest(manifest)
    assert manifest["release_version"] == module.source_version()
    assert manifest["required_archive_formats"] == ["zip", "tar.gz"]
    assert manifest["version_change_policy"]["new_release_required_when_any_versioned_component_changes"] is True
    assert manifest["version_change_policy"]["same_version_may_not_replace_existing_release_assets"] is True


def test_release_candidate_builds_s_and_ns_in_both_formats(tmp_path):
    receipt = module.prepare_release(tmp_path)
    assert receipt["release_publication_state"] == "CANDIDATE_NOT_PUBLISHED"
    assert receipt["publication_authority"] == "TV/TVC"
    assert receipt["github_build_is_runtime_authority"] is False
    assert receipt["github_release_is_execution_authority"] is False
    assert receipt["node_membership_granted"] is False

    package_assets = [row for row in receipt["assets"] if row["deployment_class"]]
    pairs = {(row["deployment_class"], row["archive_format"]) for row in package_assets}
    assert pairs == {("S", "zip"), ("S", "tar.gz"), ("NS", "zip"), ("NS", "tar.gz")}
    assert all(len(row["sha256"]) == 64 for row in receipt["assets"])
    assert (tmp_path / "PORTABLE_RELEASE_RECEIPT.json").is_file()
    assert (tmp_path / "SHA256SUMS").is_file()


def test_component_version_drift_fails_closed():
    manifest = module.load_json(module.MANIFEST_PATH)
    manifest["versioned_components"]["S_package"] = "999.0.0"
    with pytest.raises(ValueError, match="component_version_mismatch"):
        module.validate_manifest(manifest)
