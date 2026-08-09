from stegcore.steggate import (
    AdmissibilityRequest,
    ApprovalState,
    Candidate,
    CapabilityState,
    ContinuityState,
    ExecutionState,
    JudgmentState,
    SignalState,
    evaluate_admissibility,
)
from stegcore.service import capabilities, health, runtime_identity, self_test


def request_all_pass() -> AdmissibilityRequest:
    return AdmissibilityRequest(
        candidate=Candidate(
            actor_class="ai",
            action="publish_candidate",
            target="example-record",
            scope="example",
            parameters={"record_id": "r-1"},
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
            transformations=["canonicalize:v1"],
            missing_inputs=[],
            uncertainty_state="bounded",
            reference_state_hash="state:1",
            expected_reference_state_hash="state:1",
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


def test_allow_is_bound_to_existing_three_layer_runtime_and_complete_matrix():
    result = evaluate_admissibility(request_all_pass())
    assert result.disposition == "ALLOW"
    assert result.canonical_three_layer_decision == "ALLOW"
    assert result.canonical_three_layer_request_hash
    assert result.canonical_three_layer_receipt_hash
    assert result.candidate_hash
    assert result.decision_state_hash
    assert result.permission_is_not_admissibility is True
    assert result.continuity_receipt_minted is False
    assert result.external_execution_performed is False
    predicates = {row.predicate: row.state for row in result.matrix}
    assert predicates["judgment.refusal_available"] == "PASS"
    assert predicates["signal.reference_state_match"] == "PASS"
    assert predicates["execution.actor_authority_current"] == "PASS"
    assert predicates["capability.allowed"] == "PASS"
    assert predicates["continuity.previous_receipt_verified"] == "PASS"
    assert predicates["approval.candidate_hash_binding"] == "PASS"


def test_canonical_three_layer_denial_outranks_review():
    request = request_all_pass()
    request.execution.policy_current = False
    request.approval.required = True
    result = evaluate_admissibility(request)
    assert result.canonical_three_layer_decision == "DENY"
    assert result.disposition == "DENY"
    assert "execution.policy_or_delegation_stale" in result.reasons


def test_missing_reference_state_fails_closed_from_canonical_runtime():
    request = request_all_pass()
    request.signal.reference_state_hash = None
    result = evaluate_admissibility(request)
    assert result.canonical_three_layer_decision == "FAIL-CLOSED"
    assert result.disposition == "FAIL_CLOSED"
    assert "signal.reference_state_missing" in result.reasons


def test_required_approval_missing_routes_to_review_after_canonical_allow():
    request = request_all_pass()
    request.approval.required = True
    result = evaluate_admissibility(request)
    assert result.canonical_three_layer_decision == "ALLOW"
    assert result.disposition == "REVIEW"
    states = {row.predicate: row.state for row in result.matrix}
    assert states["approval.valid"] == "REVIEW"
    assert states["approval.candidate_hash_binding"] == "REVIEW"


def test_approval_must_bind_exact_candidate_hash():
    request = request_all_pass()
    preliminary = evaluate_admissibility(request)

    request.approval.required = True
    request.approval.valid = True
    request.approval.candidate_hash = preliminary.candidate_hash
    allowed = evaluate_admissibility(request)
    assert allowed.disposition == "ALLOW"

    request.approval.candidate_hash = "0" * 64
    denied = evaluate_admissibility(request)
    assert denied.disposition == "DENY"
    assert "approval_bound_to_different_candidate" in denied.reasons


def test_missing_runtime_binding_fails_closed():
    request = request_all_pass()
    request.capability.allowed = None
    result = evaluate_admissibility(request)
    assert result.canonical_three_layer_decision == "ALLOW"
    assert result.disposition == "FAIL_CLOSED"
    assert "required_evidence_unavailable" in result.reasons


def test_permission_is_recorded_but_not_used_as_admissibility_authority():
    denied_request = request_all_pass()
    denied_request.permission_present = True
    denied_request.execution.actor_authority_current = False
    denied = evaluate_admissibility(denied_request)
    assert denied.disposition == "DENY"
    assert denied.permission_present is True

    allowed_request = request_all_pass()
    allowed_request.permission_present = False
    allowed = evaluate_admissibility(allowed_request)
    assert allowed.disposition == "ALLOW"
    assert allowed.permission_present is False


def test_live_service_health_and_self_test_contract():
    status = health()
    assert status["state"] == "healthy"
    assert status["canonical_three_layer_bound"] is True
    assert status["runtime_identity"] == "stegverse:steggate:canonical:three-layer:v1"
    result = self_test()
    assert result["state"] == "PASS"
    assert result["canonical_three_layer_bound"] is True
    assert result["runtime_identity"] == status["runtime_identity"]
    assert result["observed"] == result["expected"]


def test_runtime_identity_is_stable_transport_independent_contract():
    identity = runtime_identity()
    caps = capabilities()
    assert identity["contract_version"] == "stegverse.steggate.runtime-identity.v1"
    assert identity["runtime_identity"] == "stegverse:steggate:canonical:three-layer:v1"
    assert identity["canonical_owner"] == "StegVerse-Labs/StegCore"
    assert identity["canonical_admissibility_runtime"] == "stegcore.three_layer.evaluate_three_layer"
    assert identity["binding_fields"] == [
        "contract_version",
        "runtime_identity",
        "canonical_owner",
        "canonical_admissibility_runtime",
    ]
    assert identity["application_specific_policy_authority"] is False
    assert identity["transport_identity_authoritative"] is False
    assert identity["execution_authority"] is False
    assert caps["runtime_identity"] == identity["runtime_identity"]
    assert caps["contract_version"] == identity["contract_version"]
    assert caps["canonical_owner"] == identity["canonical_owner"]
    assert caps["canonical_admissibility_runtime"] == identity["canonical_admissibility_runtime"]
    assert caps["application_specific_policy_authority"] is False
    assert caps["transport_identity_authoritative"] is False
