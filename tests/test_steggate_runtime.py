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
from stegcore.steggate_runtime import governed_steggate_execute


def allowed_request() -> AdmissibilityRequest:
    return AdmissibilityRequest(
        candidate=Candidate(
            actor_class="system",
            action="write_record",
            target="record:1",
            scope="test",
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
            transformations=["test:v1"],
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


def capability_surface():
    return {
        "actions_exposed": ["write_record"],
        "execution_mode": "manual",
        "requires_governed_commit": True,
    }


def authority_resolution():
    return {"status": "approved", "basis_invalidated_by_action": False}


def test_executor_is_unreachable_when_steggate_denies():
    req = allowed_request()
    req.execution.policy_current = False
    calls = []
    result = governed_steggate_execute(
        req,
        lambda: calls.append("executed"),
        capability_surface=capability_surface(),
        authority_resolution=authority_resolution(),
    )
    assert result.status == "refused"
    assert result.evaluation.disposition == "DENY"
    assert result.executor_invoked is False
    assert calls == []


def test_executor_is_unreachable_during_review():
    req = allowed_request()
    req.approval.required = True
    calls = []
    result = governed_steggate_execute(
        req,
        lambda: calls.append("executed"),
        capability_surface=capability_surface(),
        authority_resolution=authority_resolution(),
    )
    assert result.status == "refused"
    assert result.evaluation.disposition == "REVIEW"
    assert result.executor_invoked is False
    assert calls == []


def test_executor_is_unreachable_when_commit_coherence_denies():
    req = allowed_request()
    calls = []
    result = governed_steggate_execute(
        req,
        lambda: calls.append("executed"),
        capability_surface={
            "actions_exposed": ["write_record"],
            "execution_mode": "autonomous",
            "requires_governed_commit": False,
        },
        authority_resolution=authority_resolution(),
    )
    assert result.evaluation.disposition == "ALLOW"
    assert result.status == "refused"
    assert result.executor_invoked is False
    assert result.coherence_receipt["decision"] == "DENY"
    assert calls == []


def test_missing_commit_authority_fails_closed_at_coherence_boundary():
    req = allowed_request()
    calls = []
    result = governed_steggate_execute(
        req,
        lambda: calls.append("executed"),
        capability_surface=capability_surface(),
        authority_resolution=None,
    )
    assert result.evaluation.disposition == "ALLOW"
    assert result.status == "refused"
    assert result.executor_invoked is False
    assert result.coherence_receipt["decision"] == "DENY"
    assert "authority_not_preserved" in result.coherence_receipt["coherence_reasons"]
    assert calls == []


def test_allow_plus_coherence_executes_and_binds_decision_state_hash():
    req = allowed_request()
    calls = []

    def executor():
        calls.append("executed")
        return {"record": "written"}

    result = governed_steggate_execute(
        req,
        executor,
        capability_surface=capability_surface(),
        authority_resolution=authority_resolution(),
    )
    assert result.status == "executed"
    assert result.executor_invoked is True
    assert result.result == {"record": "written"}
    assert calls == ["executed"]
    assert result.coherence_receipt["decision"] == "ALLOW"
    assert result.coherence_receipt["steggate_decision_state_hash"] == result.evaluation.decision_state_hash
