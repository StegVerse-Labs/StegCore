import hashlib
import json

from stegcore.standing_binding import verify_spe_standing_binding
from stegcore.steggate_runtime import governed_steggate_execute
from tests.test_steggate_runtime import allowed_request, authority_resolution, capability_surface


def stable_hash(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def standing_context():
    package_id = "pkg-standing-001"
    transition_id = "tx-standing-001"
    run_id = "run-standing-001"
    ingress_hash = "sha256:" + "a" * 64
    participant_id = "reference-participant"

    candidate_core = {
        "schema_version": "stegverse.sdk.spe_commitment_candidate.v0.1",
        "package_id": package_id,
        "transition_id": transition_id,
        "run_id": run_id,
        "authorizing": False,
        "requires_fresh_standing_determination": True,
        "validity_window": {
            "not_before": "2026-08-23T00:00:00+00:00",
            "not_after": "2026-08-25T00:00:00+00:00",
        },
    }
    candidate_hash = stable_hash(candidate_core)
    candidate = {**candidate_core, "candidate_hash": candidate_hash}
    envelope_core = {
        "schema_version": "stegverse.sdk.spe_commitment_intake.v0.1",
        "source_repo": "StegVerse-org/StegVerse-SDK",
        "destination_repo": "StegVerse-Labs/Standing-Proof-Engine",
        "route_purpose": "FRESH_STANDING_DETERMINATION",
        "receipt_required": True,
        "package_id": package_id,
        "transition_id": transition_id,
        "run_id": run_id,
        "candidate_hash": candidate_hash,
        "candidate": candidate,
    }
    envelope_hash = stable_hash(envelope_core)
    envelope = {**envelope_core, "envelope_hash": envelope_hash}
    receipt_core = {
        "schema_version": "stegverse.spe.sdk_commitment_intake.v0.1",
        "receipt_type": "SPE_STANDING_DETERMINATION",
        "source_repo": "StegVerse-org/StegVerse-SDK",
        "destination_repo": "StegVerse-Labs/Standing-Proof-Engine",
        "package_id": package_id,
        "transition_id": transition_id,
        "run_id": run_id,
        "candidate_hash": candidate_hash,
        "envelope_hash": envelope_hash,
        "standing_result": "ALLOW",
        "policy_refs": [],
        "delegation_refs": [],
        "evidence_refs": [],
        "reasons": ["standing satisfied"],
        "execution_authorized": False,
        "execution_performed": False,
        "master_record_installed": False,
        "next_boundary": "GOVERNED_EXECUTION_AUTHORITY",
    }
    receipt_hash = stable_hash(receipt_core)
    receipt = {**receipt_core, "receipt_hash": receipt_hash}
    bridge_core = {
        "schema": "stegverse.sdk.spe-steggate-bridge.v1",
        "package_id": package_id,
        "transition_id": transition_id,
        "run_id": run_id,
        "interlock": {
            "ingress_interlock_hash": ingress_hash,
            "participant_id": participant_id,
        },
        "standing_binding": {
            "receipt_hash": receipt_hash,
            "candidate_hash": candidate_hash,
            "envelope_hash": envelope_hash,
            "standing_result": "ALLOW",
            "standing_current": True,
            "observed_at": "2026-08-24T00:00:00+00:00",
            "execution_authorized": False,
        },
        "admissibility_candidate": {
            "runtime_identity": "stegverse:steggate:canonical:three-layer:v1",
            "permission_contract": {"contract_id": "PA-001", "version": "1.0.0"},
            "permission_predicates": {
                "authority_current": True,
                "continuity_current": True,
                "governing_conditions_current": True,
                "consequence_attributable": True,
                "consequence_reconstructable": True,
                "consent_or_standing_required": True,
                "consent_or_standing_current": True,
            },
            "three_layer_request": {},
            "three_layer_request_hash": stable_hash({}),
            "decision": "PENDING",
        },
        "authority": {
            "sdk_authority": "NONE",
            "spe_execution_authority": "NONE",
            "steggate_decision_authority": "CANONICAL_RUNTIME_ONLY",
            "execution_authorized": False,
            "master_records_organization_record_claimed": False,
        },
    }
    bridge = {**bridge_core, "bridge_hash": stable_hash(bridge_core)}
    return {
        "standing_required": True,
        "standing_evidence": {
            "required": True,
            "expected_interlock": {
                "package_id": package_id,
                "transition_id": transition_id,
                "run_id": run_id,
                "participant_id": participant_id,
                "ingress_interlock_hash": ingress_hash,
            },
            "spe_envelope": envelope,
            "spe_receipt": receipt,
            "steggate_bridge": bridge,
        },
    }


def test_valid_standing_binding_rehashes_inside_stegcore():
    verified = verify_spe_standing_binding(standing_context()["standing_evidence"])
    assert verified["verified"] is True
    assert verified["standing_result"] == "ALLOW"
    assert verified["authority_effect"] == "NONE"


def test_required_valid_standing_allows_existing_canonical_path_to_execute():
    calls = []
    result = governed_steggate_execute(
        allowed_request(),
        lambda: calls.append("executed") or {"ok": True},
        declared_execution_context=standing_context(),
        capability_surface=capability_surface(),
        authority_resolution=authority_resolution(),
    )
    assert result.evaluation.disposition == "ALLOW"
    assert result.status == "executed"
    assert result.executor_invoked is True
    assert calls == ["executed"]
    standing_rows = [row for row in result.evaluation.matrix if row.predicate == "standing.spe_binding"]
    assert len(standing_rows) == 1
    assert standing_rows[0].state == "PASS"


def test_missing_required_standing_fails_closed_before_executor():
    calls = []
    result = governed_steggate_execute(
        allowed_request(),
        lambda: calls.append("executed"),
        declared_execution_context={"standing_required": True},
        capability_surface=capability_surface(),
        authority_resolution=authority_resolution(),
    )
    assert result.evaluation.disposition == "FAIL_CLOSED"
    assert result.status == "refused"
    assert result.executor_invoked is False
    assert calls == []


def test_tampered_spe_receipt_fails_closed_before_executor():
    context = standing_context()
    context["standing_evidence"]["spe_receipt"]["reasons"] = ["tampered"]
    calls = []
    result = governed_steggate_execute(
        allowed_request(),
        lambda: calls.append("executed"),
        declared_execution_context=context,
        capability_surface=capability_surface(),
        authority_resolution=authority_resolution(),
    )
    assert result.evaluation.disposition == "FAIL_CLOSED"
    assert result.executor_invoked is False
    assert calls == []
    assert "receipt_hash mismatch" in result.evaluation.reasons[0]


def test_wrong_interlock_binding_fails_closed_before_executor():
    context = standing_context()
    context["standing_evidence"]["expected_interlock"]["ingress_interlock_hash"] = "sha256:" + "b" * 64
    calls = []
    result = governed_steggate_execute(
        allowed_request(),
        lambda: calls.append("executed"),
        declared_execution_context=context,
        capability_surface=capability_surface(),
        authority_resolution=authority_resolution(),
    )
    assert result.evaluation.disposition == "FAIL_CLOSED"
    assert result.executor_invoked is False
    assert calls == []
    assert "ingress interlock hash mismatch" in result.evaluation.reasons[0]


def test_non_allow_spe_standing_fails_closed_before_executor():
    context = standing_context()
    receipt = context["standing_evidence"]["spe_receipt"]
    receipt_core = dict(receipt)
    receipt_core.pop("receipt_hash")
    receipt_core["standing_result"] = "DENY"
    receipt_core["next_boundary"] = None
    receipt = {**receipt_core, "receipt_hash": stable_hash(receipt_core)}
    context["standing_evidence"]["spe_receipt"] = receipt
    calls = []
    result = governed_steggate_execute(
        allowed_request(),
        lambda: calls.append("executed"),
        declared_execution_context=context,
        capability_surface=capability_surface(),
        authority_resolution=authority_resolution(),
    )
    assert result.evaluation.disposition == "FAIL_CLOSED"
    assert result.executor_invoked is False
    assert calls == []


def test_public_sdk_interlock_fixture_traverses_same_canonical_runtime():
    from pathlib import Path

    from tools.run_portable_interlock_bounded_traversal import run_traversal

    root = Path(__file__).resolve().parents[1]
    evidence = run_traversal(
        root / "fixtures" / "portable_interlock_bounded_traversal.v1.json",
        root / "examples" / "steggate_allow_request.json",
    )
    assert evidence["proof_state"] == "PASS"
    assert evidence["execution"]["status"] == "executed"
    assert evidence["execution"]["executor_invoked"] is True
    assert evidence["execution"]["coherence_receipt"]["decision"] == "ALLOW"
    assert evidence["next_boundary"] == "SDK_INTERLOCK_RETURN_ASSEMBLY"
