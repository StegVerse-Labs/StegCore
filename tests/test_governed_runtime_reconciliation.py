from dataclasses import replace

from stegcore.decision import ActionIntent, DecisionRequest, PolicyContext, VerifiedReceiptEnvelope
from stegcore.runtime_adapters import ExecutionBinding, GovernedAdapterRequest, execute_adapter, reconcile_effect


def base_request():
    return DecisionRequest(
        verified_receipt=VerifiedReceiptEnvelope(
            receipt_id="receipt-001",
            key_id="key-001",
            verified=True,
            issued_at="2026-08-08T00:00:00+00:00",
        ),
        actor_class="ai",
        intent=ActionIntent(
            action="bounded_action",
            target="target-001",
            parameters={"amount": 5},
            requested_at="2026-08-08T00:00:00+00:00",
        ),
        policy=PolicyContext(),
    )


def base_binding():
    return ExecutionBinding(
        candidate_id="candidate-001",
        candidate_hash="sha256:candidate001",
        credential_id="credential-001",
        credential_hash="sha256:credential001",
        credential_subject="subject-001",
        authority_reference="authority-001",
        capability_surface={
            "actions_exposed": ["bounded_action"],
            "execution_mode": "manual",
            "requires_governed_commit": True,
        },
        previous_receipt_hash="receipt-hash-000",
    )


def authority():
    return {
        "status": "approved",
        "basis_invalidated_by_action": False,
        "authority_ref": "authority-001",
    }


def adapter(kind="api", request=None, supplied=None, admitted=None, authority_state=None):
    admitted = admitted or base_binding()
    return GovernedAdapterRequest(
        adapter_kind=kind,
        decision_request=request or base_request(),
        binding=supplied or admitted,
        admitted_binding=admitted,
        authority_resolution=authority() if authority_state is None else authority_state,
    )


def test_all_supported_entry_kinds_have_identical_allow_result():
    for kind in ("ui", "api", "human", "ai", "agent", "batch", "workflow", "replay"):
        calls = []
        result = execute_adapter(adapter(kind), lambda: calls.append(kind) or kind)
        assert result.status == "executed"
        assert result.decision_state.outcome == "ALLOW"
        assert result.decision_state.commit_state == "COMMITTED"
        assert result.decision_state.previous_receipt_hash == "receipt-hash-000"
        assert calls == [kind]


def test_missing_authority_never_reconciles_as_committed_allow():
    calls = []
    result = execute_adapter(adapter(authority_state={}), lambda: calls.append("called"))
    assert result.status == "refused"
    assert result.decision_state.outcome == "DENY"
    assert result.decision_state.commit_state == "NOT_COMMITTED"
    assert calls == []


def test_missing_prior_pointer_fails_closed():
    supplied = replace(base_binding(), previous_receipt_hash=None)
    result = execute_adapter(adapter(supplied=supplied), lambda: "not-reached")
    assert result.decision_state.outcome == "FAIL_CLOSED"
    assert result.decision_state.reason_code == "previous_receipt_pointer_mismatch"
    assert result.decision_state.executor_invoked is False


def test_replay_pointer_mismatch_fails_closed():
    supplied = replace(base_binding(), previous_receipt_hash="older-pointer")
    result = execute_adapter(adapter("replay", supplied=supplied), lambda: "not-reached")
    assert result.decision_state.outcome == "FAIL_CLOSED"
    assert result.decision_state.reason_code == "previous_receipt_pointer_mismatch"
    assert result.decision_state.executor_invoked is False


def test_executor_failure_is_unknown_commit_state():
    def fail():
        raise RuntimeError("expected")

    result = execute_adapter(adapter(), fail)
    assert result.status == "failed"
    assert result.decision_state.outcome == "ALLOW"
    assert result.decision_state.commit_state == "COMMIT_UNKNOWN"
    assert result.decision_state.reconciliation == "UNKNOWN"


def test_non_allow_with_observed_effect_reconciles_to_bypass():
    request = base_request()
    request.verified_receipt.verified = False
    result = execute_adapter(adapter(request=request), lambda: "not-reached")
    reconciled = reconcile_effect(result.decision_state, effect_observed=True)
    assert reconciled.outcome == "DENY"
    assert reconciled.observation_state == "DIVERGENT"
    assert reconciled.reconciliation == "GOVERNANCE_BYPASS"


def test_committed_allow_without_observed_effect_is_divergent():
    result = execute_adapter(adapter(), lambda: {"ok": True})
    reconciled = reconcile_effect(result.decision_state, effect_observed=False)
    assert reconciled.outcome == "ALLOW"
    assert reconciled.commit_state == "COMMITTED"
    assert reconciled.observation_state == "DIVERGENT"
    assert reconciled.reconciliation == "DIVERGENT"


def test_unknown_observation_stays_unknown():
    result = execute_adapter(adapter(), lambda: {"ok": True})
    reconciled = reconcile_effect(result.decision_state, effect_observed=None)
    assert reconciled.observation_state == "OBSERVATION_UNKNOWN"
    assert reconciled.reconciliation == "UNKNOWN"
