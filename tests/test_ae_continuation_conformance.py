from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_ae_continuation_conformance.py"
spec = importlib.util.spec_from_file_location("ae_conformance", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
validate_bundle = module.validate_bundle


def base_bundle():
    completed = {
        "task_id": "done-1",
        "goal_id": "goal-1",
        "temporal_class": "RECENTLY_COMPLETED",
        "status": "COMPLETE",
        "owner_repository": "StegVerse-Labs/StegCore",
        "ae_impact": "CAPABILITY",
        "capability_id": "stegverse:capability:done:v1",
        "existence_phase": "ACTIVATED",
        "evidence_refs": ["commit:abc"],
        "integration_evidence_refs": ["integration:abc"],
        "activation_proof_ref": "receipt:abc",
        "blockers": [],
        "continuation_owner": None,
        "authority_claims": [],
        "registry_required": True,
        "handoff_required": True,
    }
    current = {
        "task_id": "current-1",
        "goal_id": "goal-2",
        "temporal_class": "CURRENT",
        "status": "MACHINE_OWNED",
        "owner_repository": "StegVerse-Labs/.github",
        "ae_impact": "CAPABILITY",
        "capability_id": "stegverse:capability:current:v1",
        "existence_phase": "ADMISSIBLE",
        "evidence_refs": ["issue:123"],
        "integration_evidence_refs": [],
        "activation_proof_ref": None,
        "blockers": ["activation_not_observed"],
        "continuation_owner": "StegVerse-Labs/.github#123",
        "authority_claims": [],
        "registry_required": True,
        "handoff_required": True,
    }
    future = {
        "task_id": "future-1",
        "goal_id": "goal-3",
        "temporal_class": "FUTURE",
        "status": "PLANNED",
        "owner_repository": "StegVerse-Labs/StegCore",
        "ae_impact": "CAPABILITY",
        "capability_id": "stegverse:capability:future:v1",
        "existence_phase": "DECLARED",
        "evidence_refs": ["issue:future"],
        "integration_evidence_refs": [],
        "activation_proof_ref": None,
        "blockers": [],
        "continuation_owner": None,
        "authority_claims": [],
        "registry_required": False,
        "handoff_required": False,
    }
    none = {
        "task_id": "none-1",
        "goal_id": "goal-4",
        "temporal_class": "CURRENT",
        "status": "ACTIVE_SESSION",
        "owner_repository": "StegVerse-Labs/StegCore",
        "ae_impact": "NONE",
        "ae_rationale": "documentation-only correction; no capability existence change",
        "capability_id": None,
        "existence_phase": None,
        "evidence_refs": ["issue:104"],
        "integration_evidence_refs": [],
        "activation_proof_ref": None,
        "blockers": [],
        "continuation_owner": None,
        "authority_claims": [],
        "registry_required": False,
        "handoff_required": False,
    }
    return {
        "artifact_type": "stegcore.ae_continuation_conformance_bundle",
        "schema_version": "1.0",
        "policy_id": "AE-CONTINUATION-CONFORMANCE-001",
        "authority": {
            "credential_authority": "TV/TVC",
            "github_token_runtime_authority": False,
            "heartbeat_role": "CARRIER_SYNCHRONIZATION_ONLY",
            "worker_control_plane_separate": True,
            "master_records_custody_separate": True,
        },
        "handoff": {"tasks": [completed.copy(), current.copy(), future.copy(), none.copy()]},
        "worker_registry": {"tasks": [completed.copy(), current.copy()]},
    }


def codes(result):
    return {finding["code"] for finding in result["findings"]}


def test_valid_completed_current_future_and_none():
    result = validate_bundle(base_bundle())
    assert result["valid"] is True
    assert result["findings"] == []


def test_activated_requires_integration_and_activation_proof():
    bundle = base_bundle()
    bundle["handoff"]["tasks"][0]["integration_evidence_refs"] = []
    bundle["handoff"]["tasks"][0]["activation_proof_ref"] = None
    result = validate_bundle(bundle)
    assert result["valid"] is False
    assert "activation_integration_evidence_missing" in codes(result)
    assert "activation_proof_missing" in codes(result)


def test_rejects_non_tvtvc_and_github_runtime_authority():
    bundle = base_bundle()
    bundle["authority"]["credential_authority"] = "OTHER"
    bundle["authority"]["github_token_runtime_authority"] = True
    result = validate_bundle(bundle)
    assert {"credential_authority_invalid", "github_token_runtime_authority_forbidden"} <= codes(result)


def test_rejects_heartbeat_executor_transport_or_custody_claims():
    for claim in (
        "HEARTBEAT_WORKER_EXECUTOR_AUTHORITY",
        "HEARTBEAT_TRANSPORT_AUTHORITY",
        "HEARTBEAT_CUSTODY_AUTHORITY",
    ):
        bundle = base_bundle()
        bundle["handoff"]["tasks"][1]["authority_claims"] = [claim]
        result = validate_bundle(bundle)
        assert "forbidden_authority_claim" in codes(result)


def test_blocked_current_requires_continuation_owner():
    bundle = base_bundle()
    bundle["handoff"]["tasks"][1]["continuation_owner"] = None
    result = validate_bundle(bundle)
    assert "blocked_current_without_continuation_owner" in codes(result)


def test_cross_surface_mismatch_fails_closed():
    bundle = base_bundle()
    bundle["worker_registry"]["tasks"][1]["existence_phase"] = "ACTIVATED"
    bundle["worker_registry"]["tasks"][1]["integration_evidence_refs"] = ["fake"]
    bundle["worker_registry"]["tasks"][1]["activation_proof_ref"] = "fake"
    result = validate_bundle(bundle)
    assert "cross_surface_mismatch" in codes(result)


def test_future_cannot_preclaim_activation():
    bundle = base_bundle()
    future = bundle["handoff"]["tasks"][2]
    future["existence_phase"] = "ACTIVATED"
    future["integration_evidence_refs"] = ["fake"]
    future["activation_proof_ref"] = "fake"
    result = validate_bundle(bundle)
    assert "future_activation_forbidden" in codes(result)


def test_ae_none_requires_rationale():
    bundle = base_bundle()
    bundle["handoff"]["tasks"][3]["ae_rationale"] = ""
    result = validate_bundle(bundle)
    assert "ae_none_rationale_missing" in codes(result)
