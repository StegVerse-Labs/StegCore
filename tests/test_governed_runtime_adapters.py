from dataclasses import replace

from stegcore.runtime_adapters import (
    ExecutionBinding,
    GovernedAdapterRequest,
    execute_adapter,
    execute_http,
)
from stegcore.decision import (
    ActionIntent,
    DecisionRequest,
    PolicyContext,
    VerifiedReceiptEnvelope,
)


def decision_request(*, shapes=None, amount=5):
    return DecisionRequest(
        verified_receipt=VerifiedReceiptEnvelope(
            receipt_id="receipt-verified-001",
            key_id="key-001",
            verified=True,
            issued_at="2026-01-01T00:00:00+00:00",
            valid_until="2027-01-01T00:00:00+00:00",
        ),
        actor_class="ai",
        intent=ActionIntent(
            action="transfer_units",
            target="account-001",
            parameters={"amount": amount},
            requested_at="2026-08-08T00:00:00+00:00",
        ),
        policy=PolicyContext(shapes=list(shapes or []), scope="test"),
    )


def binding(**overrides):
    values = {
        "candidate_id": "candidate-001",
        "candidate_hash": "sha256:candidate001",
        "credential_id": "credential-001",
        "credential_hash": "sha256:credential001",
        "credential_subject": "agent-001",
        "authority_reference": "authority-001",
        "capability_surface": {
            "actions_exposed": ["transfer_units"],
            "execution_mode": "manual",
            "requires_governed_commit": True,
            "parameter_bounds": {"amount": {"min": 1, "max": 10}},
        },
        "parameter_bounds": {"amount": {"min": 1, "max": 10}},
        "previous_receipt_hash": "receipt-hash-000",
    }
    values.update(overrides)
    return ExecutionBinding(**values)


def authority(**overrides):
    value = {
        "status": "approved",
        "basis_invalidated_by_action": False,
        "authority_ref": "authority-001",
        "target_binding": "account-001",
        "valid_from": "2026-01-01T00:00:00+00:00",
        "valid_until": "2027-01-01T00:00:00+00:00",
    }
    value.update(overrides)
    return value


def adapter(kind="api", *, req=None, supplied=None, admitted=None, authority_state=None):
    admitted = admitted or binding()
    supplied = supplied or admitted
    return GovernedAdapterRequest(
        adapter_kind=kind,
        decision_request=req or decision_request(),
        binding=supplied,
        admitted_binding=admitted,
        declared_execution_context={"transport_request_id": "transport-001"},
        authority_resolution=authority() if authority_state is None else authority_state,
    )


def test_api_exact_binding_executes_once_and_preserves_receipt_pointer():
    calls = []
    result = execute_http(adapter("api"), lambda: calls.append("called") or {"ok": True})

    assert result.status == "executed"
    assert calls == ["called"]
    assert result.decision_state.outcome == "ALLOW"
    assert result.decision_state.executor_invoked is True
    assert result.decision_state.previous_receipt_hash == "receipt-hash-000"
    assert result.runtime_observation.coherence_receipt["previous_receipt_hash"] == "receipt-hash-000"
    assert result.runtime_observation.coherence_receipt["commit_state"]["authority_resolution"]["authority_ref"] == "authority-001"
    assert all(result.runtime_observation.coherence_receipt["present_state_checks"].values())


def test_missing_authority_state_fails_closed_before_executor():
    calls = []
    result = execute_adapter(
        adapter("api", authority_state={}),
        lambda: calls.append("called"),
    )

    assert result.status == "refused"
    assert result.decision_state.outcome == "FAIL_CLOSED"
    assert result.decision_state.phase == "COMMIT_COHERENCE"
    assert result.decision_state.reason_code == "authority_state_unestablished"
    assert result.decision_state.executor_invoked is False
    assert result.runtime_observation.coherence_receipt["authority_resolution"]["status"] == "missing"
    assert calls == []


def test_changed_authority_target_is_denied_through_adapter():
    calls = []
    result = execute_adapter(
        adapter("api", authority_state=authority(target_binding="account-002")),
        lambda: calls.append("called"),
    )

    assert result.status == "refused"
    assert result.decision_state.outcome == "DENY"
    assert result.decision_state.reason_code == "authority_target_mismatch"
    assert result.decision_state.executor_invoked is False
    assert calls == []


def test_all_required_adapter_kinds_share_same_allow_semantics():
    for kind in ("api", "agent", "batch", "workflow"):
        calls = []
        result = execute_adapter(adapter(kind), lambda: calls.append(kind) or kind)
        assert result.status == "executed"
        assert result.decision_state.outcome == "ALLOW"
        assert result.decision_state.commit_state == "COMMITTED"
        assert calls == [kind]


def test_candidate_mismatch_fails_closed_without_executor():
    calls = []
    supplied = replace(binding(), candidate_hash="sha256:wrong")
    result = execute_adapter(adapter(supplied=supplied), lambda: calls.append("called"))

    assert result.status == "refused"
    assert result.decision_state.outcome == "FAIL_CLOSED"
    assert result.decision_state.reason_code == "candidate_hash_mismatch"
    assert result.decision_state.executor_invoked is False
    assert calls == []


def test_credential_mismatch_fails_closed_without_executor():
    calls = []
    supplied = replace(binding(), credential_subject="other-agent")
    result = execute_adapter(adapter(supplied=supplied), lambda: calls.append("called"))

    assert result.decision_state.outcome == "FAIL_CLOSED"
    assert result.decision_state.reason_code == "credential_subject_mismatch"
    assert calls == []


def test_unexposed_action_fails_closed_without_executor():
    calls = []
    req = decision_request()
    supplied = replace(
        binding(),
        capability_surface={
            "actions_exposed": ["read_only"],
            "execution_mode": "manual",
            "requires_governed_commit": True,
        },
    )
    admitted = replace(
        binding(),
        capability_surface={
            "actions_exposed": ["read_only", "transfer_units"],
            "execution_mode": "manual",
            "requires_governed_commit": True,
        },
    )
    result = execute_adapter(adapter(req=req, supplied=supplied, admitted=admitted), lambda: calls.append("called"))

    assert result.decision_state.outcome == "FAIL_CLOSED"
    assert result.decision_state.reason_code == "unexposed_action"
    assert calls == []


def test_parameter_out_of_bounds_fails_closed_without_executor():
    calls = []
    result = execute_adapter(adapter(req=decision_request(amount=11)), lambda: calls.append("called"))

    assert result.decision_state.outcome == "FAIL_CLOSED"
    assert result.decision_state.reason_code == "parameter_above_max:amount"
    assert calls == []


def test_capability_broadening_fails_closed_without_executor():
    calls = []
    supplied = replace(
        binding(),
        capability_surface={
            "actions_exposed": ["transfer_units", "delete_account"],
            "execution_mode": "manual",
            "requires_governed_commit": True,
        },
    )
    result = execute_adapter(adapter(supplied=supplied), lambda: calls.append("called"))

    assert result.decision_state.outcome == "FAIL_CLOSED"
    assert result.decision_state.reason_code == "capability_action_broadening"
    assert calls == []


def test_review_is_evidence_bearing_and_never_executes():
    calls = []
    result = execute_adapter(
        adapter(req=decision_request(shapes=["quorum"])),
        lambda: calls.append("called"),
    )

    assert result.status == "refused"
    assert result.decision_state.outcome == "REVIEW"
    assert result.decision_state.phase == "ADMISSIBILITY"
    assert result.decision_state.executor_invoked is False
    assert result.decision_state.commit_state == "NOT_ATTEMPTED"
    assert calls == []


def test_admissibility_deny_is_evidence_bearing_and_never_executes():
    calls = []
    req = decision_request()
    req.verified_receipt.verified = False
    result = execute_adapter(adapter(req=req), lambda: calls.append("called"))

    assert result.status == "refused"
    assert result.decision_state.outcome == "DENY"
    assert result.decision_state.executor_invoked is False
    assert calls == []


def test_coherence_deny_never_executes():
    calls = []
    supplied = replace(
        binding(),
        capability_surface={
            "actions_exposed": ["transfer_units"],
            "execution_mode": "auto",
            "requires_governed_commit": True,
        },
    )
    admitted = supplied
    result = execute_adapter(adapter(supplied=supplied, admitted=admitted), lambda: calls.append("called"))

    assert result.status == "refused"
    assert result.decision_state.outcome == "DENY"
    assert result.decision_state.phase == "COMMIT_COHERENCE"
    assert result.decision_state.executor_invoked is False
    assert result.decision_state.commit_state == "NOT_COMMITTED"
    assert calls == []


def test_receipt_pointer_mismatch_fails_closed():
    supplied = replace(binding(), previous_receipt_hash="wrong-prev")
    result = execute_adapter(adapter(supplied=supplied), lambda: "should-not-run")

    assert result.decision_state.outcome == "FAIL_CLOSED"
    assert result.decision_state.reason_code == "previous_receipt_pointer_mismatch"


def test_http_shim_refuses_non_api_adapter_kind():
    calls = []
    result = execute_http(adapter("agent"), lambda: calls.append("called"))

    assert result.decision_state.outcome == "FAIL_CLOSED"
    assert result.decision_state.reason_code == "http_adapter_kind_mismatch"
    assert calls == []
