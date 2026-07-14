from stegcore.three_layer import (
    ExecutionBoundary,
    JudgmentConditions,
    SignalAdmission,
    ThreeLayerRequest,
    evaluate_three_layer,
)


def valid_request(**overrides):
    judgment = overrides.get(
        "judgment_conditions",
        JudgmentConditions(
            refusal_available=True,
            operator_recoverability="available",
            workload_state="supported",
            time_pressure="normal",
            isolation_state="supported",
            evidence_refs=("judgment-evidence-1",),
        ),
    )
    signal = overrides.get(
        "signal_admission",
        SignalAdmission(
            admitted_signal_refs=("signal-1", "signal-2"),
            excluded_signal_refs=(),
            transformations=("canonicalize:v1",),
            missing_inputs=(),
            uncertainty_state="bounded",
            reference_state_hash="state-abc",
            expected_reference_state_hash="state-abc",
            reconstruction_available=True,
            transformation_provenance_complete=True,
        ),
    )
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
    return ThreeLayerRequest(
        judgment_conditions=judgment,
        signal_admission=signal,
        execution_boundary=boundary,
        action="repo.apply",
        target="StegVerse-Labs/StegCore",
        scope="runtime",
    )


def test_condition_degraded_judgment_denies():
    request = valid_request(
        judgment_conditions=JudgmentConditions(
            refusal_available=False,
            operator_recoverability="degraded",
            workload_state="overloaded",
            time_pressure="critical",
            isolation_state="isolated",
        )
    )
    result = evaluate_three_layer(request)
    assert result.decision == "DENY"
    assert result.reason_code == "judgment.refusal_unavailable"
    assert result.receipt["continuity_receipt_minted"] is False


def test_signal_admission_drift_denies_when_state_unreconstructable():
    request = valid_request(
        signal_admission=SignalAdmission(
            admitted_signal_refs=("compressed-signal",),
            transformations=("summarize:unknown",),
            missing_inputs=("source-context",),
            uncertainty_state="material",
            reference_state_hash="shifted-state",
            expected_reference_state_hash="authorized-state",
            reconstruction_available=False,
            transformation_provenance_complete=False,
        )
    )
    result = evaluate_three_layer(request)
    assert result.decision == "DENY"
    assert result.reason_code == "signal.inputs_incomplete"


def test_governance_validation_of_drift_fails_closed():
    request = valid_request(
        signal_admission=SignalAdmission(
            admitted_signal_refs=("signal-1",),
            transformations=("canonicalize:v1",),
            missing_inputs=(),
            uncertainty_state="bounded",
            reference_state_hash="shifted-state",
            expected_reference_state_hash="authorized-state",
            reconstruction_available=True,
            transformation_provenance_complete=True,
        )
    )
    result = evaluate_three_layer(request)
    assert result.decision == "FAIL-CLOSED"
    assert result.reason_code == "signal.reference_state_discontinuous"


def test_positive_control_allows():
    result = evaluate_three_layer(valid_request())
    assert result.decision == "ALLOW"
    assert result.reason_code == "ok"
    assert result.receipt["policy_ref"] == "policy:v1"
    assert result.receipt["delegation_ref"] == "delegation:v1"
    assert result.receipt["receipt_hash"]


def test_replay_changes_when_reference_state_changes():
    first = evaluate_three_layer(valid_request())
    second = evaluate_three_layer(
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
        )
    )
    assert first.decision == "ALLOW"
    assert second.decision == "FAIL-CLOSED"
    assert first.request_hash != second.request_hash


def test_unreconstructable_state_never_allows():
    request = valid_request(
        signal_admission=SignalAdmission(
            admitted_signal_refs=("signal-1",),
            transformations=("opaque-transform",),
            missing_inputs=(),
            uncertainty_state="bounded",
            reference_state_hash="state-abc",
            expected_reference_state_hash="state-abc",
            reconstruction_available=False,
            transformation_provenance_complete=False,
        )
    )
    assert evaluate_three_layer(request).decision == "DENY"
