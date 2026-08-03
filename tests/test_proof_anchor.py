from stegcore.proof_anchor import (
    ProofAnchorBinding,
    evaluate_bound_proof,
    execute_bound_proof,
    verify_bound_proof,
)
from stegcore.three_layer import (
    ExecutionBoundary,
    JudgmentConditions,
    SignalAdmission,
    ThreeLayerRequest,
)


def binding(**overrides):
    values = {
        "policy_version": "policy-v1",
        "policy_artifact_hash": "sha256:policy-abc",
        "delegation_version": "delegation-v1",
        "delegation_artifact_hash": "sha256:delegation-abc",
        "decision_epoch": "epoch-0001",
        "evaluated_at": "2026-08-02T22:31:00-05:00",
    }
    values.update(overrides)
    return ProofAnchorBinding(**values)


def valid_request(**overrides):
    boundary = overrides.get(
        "execution_boundary",
        ExecutionBoundary(
            actor_authority_current=True,
            policy_current=True,
            delegation_current=True,
            evidence_current=True,
            affected_entity_conditions_represented=True,
            recoverability_profile="recoverable",
            validity_window_open=True,
            policy_ref="policy:v1",
            delegation_ref="delegation:v1",
            evidence_refs=("execution-evidence-1",),
        ),
    )
    signal = overrides.get(
        "signal_admission",
        SignalAdmission(
            admitted_signal_refs=("signal-1", "signal-2"),
            transformations=("canonicalize:v1",),
            missing_inputs=(),
            uncertainty_state="bounded",
            reference_state_hash="state-abc",
            expected_reference_state_hash="state-abc",
            reconstruction_available=True,
            transformation_provenance_complete=True,
        ),
    )
    return ThreeLayerRequest(
        judgment_conditions=JudgmentConditions(
            refusal_available=True,
            operator_recoverability="available",
            workload_state="supported",
            time_pressure="normal",
            isolation_state="supported",
            evidence_refs=("judgment-evidence-1",),
        ),
        signal_admission=signal,
        execution_boundary=boundary,
        action="repo.apply",
        target="StegVerse-Labs/StegCore",
        scope="proof-anchor",
    )


def test_valid_identity_context_cannot_replace_stale_delegation():
    request = valid_request(
        execution_boundary=ExecutionBoundary(
            actor_authority_current=True,
            policy_current=True,
            delegation_current=False,
            evidence_current=True,
            affected_entity_conditions_represented=True,
            recoverability_profile="recoverable",
            validity_window_open=True,
            policy_ref="policy:v1",
            delegation_ref="delegation:v1",
            evidence_refs=("identity-valid", "receipt-valid"),
        )
    )
    proof = evaluate_bound_proof(request, binding())
    assert proof.decision == "DENY"
    assert proof.reason_code == "execution.policy_or_delegation_stale"
    assert proof.continuity_receipt_minted is False


def test_reference_state_mutation_fails_closed_and_changes_proof_hash():
    baseline = evaluate_bound_proof(valid_request(), binding())
    mutated = evaluate_bound_proof(
        valid_request(
            signal_admission=SignalAdmission(
                admitted_signal_refs=("signal-1", "signal-2"),
                transformations=("canonicalize:v1",),
                missing_inputs=(),
                uncertainty_state="bounded",
                reference_state_hash="state-mutated",
                expected_reference_state_hash="state-abc",
                reconstruction_available=True,
                transformation_provenance_complete=True,
            )
        ),
        binding(),
    )
    assert baseline.decision == "ALLOW"
    assert mutated.decision == "FAIL-CLOSED"
    assert mutated.reason_code == "signal.reference_state_discontinuous"
    assert baseline.proof_hash != mutated.proof_hash


def test_bound_proof_is_reproducible_despite_runtime_observation_time():
    request = valid_request()
    first = evaluate_bound_proof(request, binding())
    second = evaluate_bound_proof(request, binding())
    assert first.request_hash == second.request_hash
    assert first.binding_hash == second.binding_hash
    assert first.proof_hash == second.proof_hash
    assert verify_bound_proof(request, binding(), first) is True


def test_binding_version_or_epoch_substitution_changes_proof_hash():
    request = valid_request()
    baseline = evaluate_bound_proof(request, binding())
    substituted = evaluate_bound_proof(
        request,
        binding(policy_version="policy-v2", decision_epoch="epoch-0002"),
    )
    assert baseline.proof_hash != substituted.proof_hash
    assert baseline.binding_hash != substituted.binding_hash


def test_fail_closed_cannot_be_overridden_by_downstream_callback():
    called = False

    def executor():
        nonlocal called
        called = True
        return "should-not-run"

    request = valid_request(
        signal_admission=SignalAdmission(
            admitted_signal_refs=("signal-1",),
            transformations=("canonicalize:v1",),
            missing_inputs=(),
            uncertainty_state="bounded",
            reference_state_hash="state-mutated",
            expected_reference_state_hash="state-abc",
            reconstruction_available=True,
            transformation_provenance_complete=True,
        )
    )
    observation = execute_bound_proof(request, binding(), executor)
    assert observation.status == "refused"
    assert observation.executed is False
    assert observation.proof.decision == "FAIL-CLOSED"
    assert called is False


def test_allow_invokes_executor_only_after_bound_decision():
    called = False

    def executor():
        nonlocal called
        called = True
        return {"status": "applied"}

    observation = execute_bound_proof(valid_request(), binding(), executor)
    assert observation.status == "executed"
    assert observation.executed is True
    assert observation.proof.decision == "ALLOW"
    assert observation.result == {"status": "applied"}
    assert called is True


def test_missing_binding_field_fails_before_evaluation():
    try:
        evaluate_bound_proof(valid_request(), binding(policy_artifact_hash=""))
    except ValueError as exc:
        assert "policy_artifact_hash" in str(exc)
    else:
        raise AssertionError("missing immutable binding must fail closed")
