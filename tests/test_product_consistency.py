from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tomllib
import sys

from stegcore import __version__
from stegcore.cli import main as cli_main
from stegcore.service import SERVICE_VERSION, runtime_identity

ROOT = Path(__file__).resolve().parents[1]


def test_portable_product_versions_are_aligned():
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    package = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert version == package["project"]["version"]
    assert __version__ == version
    assert SERVICE_VERSION == version


def test_runtime_identity_is_canonical_and_transport_independent():
    identity = runtime_identity()
    assert identity["runtime_identity"] == "stegverse:steggate:canonical:three-layer:v1"
    assert identity["canonical_admissibility_runtime"] == "stegcore.three_layer.evaluate_three_layer"
    assert identity["transport_identity_authoritative"] is False


def test_cli_self_test_uses_live_runtime(capsys):
    assert cli_main(["self-test"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["state"] == "PASS"
    assert output["observed"] == output["expected"]


def test_cli_example_evaluates_allow(capsys):
    request = ROOT / "examples" / "steggate_allow_request.json"
    assert cli_main(["evaluate", str(request)]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["disposition"] == "ALLOW"
    assert output["canonical_three_layer_decision"] == "ALLOW"
    assert output["external_execution_performed"] is False
    assert output["continuity_receipt_minted"] is False


def test_repository_consistency_verifier_passes():
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "verify_product_consistency.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_unreleased_manifest_rejects_false_release_claims(monkeypatch):
    from scripts import verify_product_consistency as verifier

    original = verifier._read
    manifest = json.loads(original("VERSION.json"))
    assert manifest["version_stage"] == "SOURCE_VALIDATED_NOT_RELEASED"
    assert verifier.check() == []

    mutations = [
        (lambda m: m["release"].update(tag="v0.3.0"), "unreleased product must not claim an immutable tag or release commit"),
        (lambda m: m["release"].update(commit="58445bb14642c1889cf9802666c15bd48c6d2e39"), "unreleased product must not claim an immutable tag or release commit"),
        (lambda m: m["expected_aggregate_release_binding"].update(observed_as_released=True), "unreleased product must not claim observed aggregate publication"),
        (lambda m: m.update(component_version="0.2.0"), "VERSION.json component_version drift"),
        (lambda m: m["product_identity"].update(portable_product_version="0.2.0"), "VERSION.json portable_product_version drift"),
    ]
    for mutate, expected in mutations:
        changed = json.loads(json.dumps(manifest))
        mutate(changed)
        monkeypatch.setattr(verifier, "_read", lambda relative, changed=changed: json.dumps(changed) if relative == "VERSION.json" else original(relative))
        assert expected in verifier.check()
    monkeypatch.setattr(verifier, "_read", original)
    assert verifier.check() == []
