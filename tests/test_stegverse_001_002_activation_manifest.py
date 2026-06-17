import json
from pathlib import Path


def test_activation_manifest_names_controlled_baseline():
    manifest = json.loads(Path("activation_manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema"]["name"] == "stegverse.stegcore.activation_manifest"
    assert manifest["repository"]["organization"] == "StegVerse-Labs"
    assert manifest["repository"]["name"] == "StegCore"
    assert manifest["activation_target"]["name"] == "stegverse_001_002_controlled_baseline"


def test_activation_manifest_preserves_non_claims():
    non_claims = json.loads(Path("activation_manifest.json").read_text(encoding="utf-8"))["non_claims"]
    assert non_claims["identity_truth_system"] is False
    assert non_claims["receipt_minting_system"] is False
    assert non_claims["secret_storage_system"] is False
    assert non_claims["user_consent_system"] is False
    assert non_claims["org_wide_completion"] is False


def test_activation_manifest_requires_commit_time_context():
    manifest = json.loads(Path("activation_manifest.json").read_text(encoding="utf-8"))
    assert "commit_time_context_present" in manifest["required_inputs"]
    assert "stale_context" in manifest["blocking_conditions"]
    assert "authority_overreach" in manifest["blocking_conditions"]
