import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools" / "run_stegverse_micro_ecosystem.py"

spec = importlib.util.spec_from_file_location("stegverse_micro_ecosystem_runner", RUNNER)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def test_micro_ecosystem_proof_passes_without_external_authority():
    receipt = module.run_proof(
        ROOT / "micro_ecosystem" / "manifest.json",
        ROOT / "examples" / "steggate_allow_request.json",
    )
    assert receipt["proof_state"] == "PASS"
    assert receipt["evaluation"]["disposition"] == "ALLOW"
    assert receipt["runtime_identity"]["runtime_identity"] == "stegverse:steggate:canonical:three-layer:v1"
    assert receipt["external_side_effect"] is False
    assert receipt["execution_authority"] is False
    assert receipt["continuity_receipt_minted"] is False
    assert all(receipt["checks"].values())
    assert len(receipt["manifest_sha256"]) == 64
    assert len(receipt["request_sha256"]) == 64
    assert len(receipt["result_sha256"]) == 64
