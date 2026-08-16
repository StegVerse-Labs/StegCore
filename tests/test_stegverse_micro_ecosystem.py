import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools" / "run_stegverse_micro_ecosystem.py"
MANIFEST = ROOT / "micro_ecosystem" / "manifest.json"
REQUEST = ROOT / "examples" / "steggate_allow_request.json"

spec = importlib.util.spec_from_file_location("stegverse_micro_ecosystem_runner", RUNNER)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def assert_common_proof(receipt):
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


def test_s_ecosystem_is_explicit_isolated_sovereign_deployment():
    receipt = module.run_proof(MANIFEST, REQUEST, "S")
    assert_common_proof(receipt)
    assert receipt["deployment_class"] == "S"
    assert receipt["deployment_profile"]["sovereignty_class"] == "Sovereign"
    assert receipt["deployment_profile"]["isolated"] is True
    assert receipt["deployment_profile"]["individually_operated"] is True
    assert receipt["deployment_profile"]["node_status_requested"] is False
    assert receipt["deployment_profile"]["ecosystem_membership_required"] is False
    assert receipt["node_activation_state"] == "NOT_APPLICABLE"
    assert receipt["node_sovereign_active"] is False


def test_ns_ecosystem_selects_profile_without_self_accrediting_node():
    receipt = module.run_proof(MANIFEST, REQUEST, "NS")
    assert_common_proof(receipt)
    assert receipt["deployment_class"] == "NS"
    assert receipt["deployment_profile"]["sovereignty_class"] == "Node Sovereign"
    assert receipt["deployment_profile"]["node_status_requested"] is True
    assert receipt["deployment_profile"]["node_status_self_assertable"] is False
    assert receipt["deployment_profile"]["ecosystem_membership_required"] is True
    assert receipt["node_sovereign_profile"]["schema"] == "stegverse.node-sovereign.profile.v1"
    assert receipt["node_activation_state"] == "PROFILE_DEFINED_NOT_ACTIVE"
    assert receipt["membership_proof_present"] is False
    assert receipt["node_sovereign_active"] is False
    assert receipt["checks"]["ns_selection_does_not_self_accredit_node"] is True


def test_invalid_deployment_class_fails_closed():
    receipt = module.run_proof(MANIFEST, REQUEST, "UNKNOWN")
    assert receipt["proof_state"] == "FAIL"
    assert receipt["checks"]["deployment_class_valid"] is False
    assert receipt["checks"]["deployment_class_invariants"] is False
