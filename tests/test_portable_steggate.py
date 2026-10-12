import json

from stegcore.portable_steggate import (
    GovernedTransitionPackage,
    create_governed_package,
    evaluate_governed_package,
    execute_governed_package,
)
from stegcore.steggate import (
    AdmissibilityRequest,
    ApprovalState,
    Candidate,
    CapabilityState,
    ContinuityState,
    ExecutionState,
    JudgmentState,
    SignalState,
)


def allowed_request() -> AdmissibilityRequest:
    return AdmissibilityRequest(
        candidate=Candidate(
            actor_class="system",
            action="write_record",
            target="record:portable:1",
            scope="portable-test",
            parameters={"value": 1},
        ),
        judgment=JudgmentState(
            refusal_available=True,
            operator_recoverability="available",
            workload_state="supported",
            time_pressure="normal",
            isolation_state="supported",
            evidence_refs=["judgment:e1"],
        ),
        signal=SignalState(
            admitted_signal_refs=["signal:s1"],
            transformations=["portable:v1"],
            missing_inputs=[],
            uncertainty_state="bounded",
            reference_state_hash="state:portable:1",
            expected_reference_state_hash="state:portable:1",
            reconstruction_available=True,
            transformation_provenance_complete=True,
        ),
        execution=ExecutionState(
            actor_authority_current=True,
            policy_current=True,
            delegation_current=True,
            evidence_current=True,
            affected_entity_conditions_represented=True,
            recoverability_profile="recoverable",
            validity_window_open=True,
            policy_ref="policy:p1",
            delegation_ref="delegation:d1",
            evidence_refs=["execution:e1"],
        ),
        capability=CapabilityState(allowed=True),
        continuity=ContinuityState(
            required=True,
            previous_receipt_verified=True,
            previous_receipt_hash="receipt:r0",
        ),
        approval=ApprovalState(required=False),
        permission_present=False,
    )


def capability_surface():
    return {
        "actions_exposed": ["write_record"],
        "execution_mode": "manual",
        "requires_governed_commit": True,
    }


def authority_resolution():
    return {
        "status": "approved",
        "basis_invalidated_by_action": False,
        "target_binding": "record:portable:1",
        "valid_from": "2026-01-01T00:00:00+00:00",
        "valid_until": "2100-01-01T00:00:00+00:00",
    }


def package():
    return create_governed_package(
        package_id="pkg-portable-001",
        request=allowed_request(),
        capability_surface=capability_surface(),
        authority_resolution=authority_resolution(),
    )


def test_package_survives_json_transport_and_evaluates_in_ephemeral_node():
    original = package()
    transported = GovernedTransitionPackage.model_validate(json.loads(original.model_dump_json()))
    receipt = evaluate_governed_package(transported)
    assert receipt.state == "EVALUATED"
    assert receipt.package_hash == original.package_hash
    assert receipt.evaluation["disposition"] == "ALLOW"
    assert receipt.node_instance_id.startswith("SGMU-")
    assert receipt.receipt_hash


def test_portable_node_executes_only_through_canonical_governed_boundary():
    calls = []
    p = package()
    receipt = execute_governed_package(p, lambda: calls.append("executed") or {"ok": True})
    assert receipt.state == "EXECUTED"
    assert calls == ["executed"]
    observation = receipt.execution_observation
    assert observation["executor_invoked"] is True
    assert observation["evaluation"]["disposition"] == "ALLOW"
    assert observation["coherence_receipt"]["decision"] == "ALLOW"
    assert observation["coherence_receipt"]["steggate_decision_state_hash"] == observation["evaluation"]["decision_state_hash"]


def test_runtime_fingerprint_mismatch_fails_closed_without_executor():
    p = package()
    p.micronode.runtime_fingerprint = "0" * 64
    p.package_hash = p.computed_hash()
    calls = []
    receipt = execute_governed_package(p, lambda: calls.append("should-not-run"))
    assert receipt.state == "FAIL_CLOSED"
    assert receipt.fail_closed_reason == "runtime_fingerprint_mismatch"
    assert calls == []


def test_package_tampering_fails_closed_without_executor():
    p = package()
    p.admissibility_request.candidate.parameters["value"] = 999
    calls = []
    receipt = execute_governed_package(p, lambda: calls.append("should-not-run"))
    assert receipt.state == "FAIL_CLOSED"
    assert receipt.fail_closed_reason == "package_hash_mismatch"
    assert calls == []


def test_denied_package_never_executes():
    p = package()
    p.admissibility_request.execution.policy_current = False
    p.package_hash = p.computed_hash()
    calls = []
    receipt = execute_governed_package(p, lambda: calls.append("should-not-run"))
    assert receipt.state == "REFUSED"
    assert receipt.execution_observation["evaluation"]["disposition"] == "DENY"
    assert receipt.execution_observation["executor_invoked"] is False
    assert calls == []
