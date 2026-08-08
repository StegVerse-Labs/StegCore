from stegcore.steggate import (
    AdmissibilityRequest,
    ApprovalState,
    AuthorityState,
    Candidate,
    CapabilityState,
    ContinuityState,
    EvidenceState,
    PolicyState,
    evaluate_admissibility,
)
from stegcore.service import health, self_test


def request_all_pass() -> AdmissibilityRequest:
    return AdmissibilityRequest(
        candidate=Candidate(
            actor_class="ai",
            action="publish_candidate",
            target="example-record",
            parameters={"record_id": "r-1"},
        ),
        evidence=EvidenceState(verified=True, fresh=True),
        authority=AuthorityState(valid=True, action_allowed=True, target_allowed=True),
        policy=PolicyState(applicable=True, current=True, permits=True),
        capability=CapabilityState(allowed=True),
        continuity=ContinuityState(required=True, previous_receipt_verified=True),
        approval=ApprovalState(required=False),
    )


def test_allow_contains_complete_matrix_and_hashes():
    result = evaluate_admissibility(request_all_pass())
    assert result.disposition == "ALLOW"
    assert result.candidate_hash
    assert result.decision_state_hash
    predicates = {row.predicate: row.state for row in result.matrix}
    assert predicates["evidence.verified"] == "PASS"
    assert predicates["authority.valid"] == "PASS"
    assert predicates["policy.permits"] == "PASS"
    assert predicates["capability.allowed"] == "PASS"
    assert predicates["continuity.previous_receipt_verified"] == "PASS"
    assert predicates["approval.candidate_hash_binding"] == "PASS"


def test_known_policy_prohibition_denies():
    request = request_all_pass()
    request.policy.permits = False
    result = evaluate_admissibility(request)
    assert result.disposition == "DENY"
    assert "policy_prohibits_candidate" in result.reasons


def test_missing_critical_evidence_fails_closed():
    request = request_all_pass()
    request.evidence.verified = None
    result = evaluate_admissibility(request)
    assert result.disposition == "FAIL_CLOSED"
    assert "required_evidence_unavailable" in result.reasons


def test_required_approval_missing_routes_to_review():
    request = request_all_pass()
    request.approval.required = True
    result = evaluate_admissibility(request)
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


def test_live_service_health_and_self_test_contract():
    assert health()["state"] == "healthy"
    result = self_test()
    assert result["state"] == "PASS"
    assert result["observed"] == result["expected"]
