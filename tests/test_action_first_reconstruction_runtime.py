import pytest

from stegcore.action_first_reconstruction import (
    ActionFirstRuntimeInput,
    ReconstructionPosture,
    ResidualObservation,
    RuntimeStateIdentity,
    build_action_first_record,
    runtime_semantic_source,
)
from stegcore.runtime_adapters import AdapterObservation, DecisionStateRecord

HASH_A = "sha256:" + "a" * 64
HASH_B = "sha256:" + "b" * 64


def decision_state(*, executed=True, outcome="ALLOW"):
    return DecisionStateRecord(
        artifact_type="stegcore.runtime_decision_state",
        adapter_kind="api",
        outcome=outcome,
        phase="EXECUTION" if executed else "ADMISSIBILITY",
        reason_code="test",
        candidate_id="candidate-1",
        candidate_hash=HASH_A,
        credential_id="cred-1",
        credential_hash=HASH_B,
        credential_subject="subject-1",
        authority_reference="authority:1",
        capability_hash=HASH_B,
        previous_receipt_hash=None,
        executor_invoked=executed,
        commit_state="COMMITTED" if executed else "NOT_ATTEMPTED",
        observation_state="OBSERVED" if executed else "NOT_OBSERVED",
        reconciliation="MATCH" if executed else "NOT_APPLICABLE",
    )


def observation(*, executed=True, outcome="ALLOW"):
    return AdapterObservation(
        artifact_type="stegcore.adapter_observation",
        status="executed" if executed else "refused",
        decision_state=decision_state(executed=executed, outcome=outcome),
    )


def runtime_input(**overrides):
    base = dict(
        record_id="afr-1",
        transition_id="transition-1",
        prior_state_ref="state:1",
        admissibility_matrix_ref="matrix:state-1",
        action_candidate_ref="candidate-1",
        calculated_state=RuntimeStateIdentity("state:2:calculated", HASH_A, "RECORDED"),
        realized_state=RuntimeStateIdentity("state:2:realized", HASH_A, "OBSERVED"),
        observed_state=RuntimeStateIdentity("state:2:observed", HASH_A, "VERIFIED"),
        model_reality_delta=ResidualObservation("metric:exact-hash", 0.0, "ZERO"),
        reality_observation_delta=ResidualObservation("metric:exact-hash", 0.0, "ZERO"),
        observer_universe_ref="observers:test",
        observation_coverage=1.0,
        observation_level="VERIFIED",
        known_constraint_refs=("constraint:known-1",),
        unknown_candidate_refs=(),
        latent_candidate_refs=(),
        irreversibility_crossed=True,
        irreversibility_boundary_ref="boundary:commit-1",
        rollback_requires_new_transition=True,
        reconstruction=ReconstructionPosture(
            status="COMPLETE",
            causal_reconstructability=1.0,
            identifiability="IDENTIFIABLE",
            prediction_fit=1.0,
            constraint_promotion="TESTABLE",
        ),
        continuity_consequence="UNKNOWN",
        terminal_declared=False,
        viability_horizon_ref="horizon:next",
        future_admissible_transition_capacity=1.0,
    )
    base.update(overrides)
    return ActionFirstRuntimeInput(**base)


def test_builds_schema_shaped_runtime_record_without_authority_expansion():
    record = build_action_first_record(observation(), runtime_input())
    assert record["schema_version"] == "stegverse.action-first-reconstruction.v1"
    assert record["action_candidate_ref"] == "candidate-1"
    assert record["irreversibility"]["crossed"] is True
    assert record["model_reality_delta"]["status"] == "ZERO"
    assert record["reality_observation_delta"]["status"] == "ZERO"
    assert record["reconstruction"]["constraint_promotion"] == "TESTABLE"
    assert record["continuity_consequence"] == "UNKNOWN"


def test_unobserved_realized_transition_is_preserved_not_erased():
    value = runtime_input(
        observed_state=RuntimeStateIdentity("state:2:observed", None, "UNOBSERVED"),
        reality_observation_delta=ResidualObservation("metric:observer-gap", None, "NOT_COMPUTABLE"),
        observation_coverage=0.0,
        observation_level="UNOBSERVED",
        reconstruction=ReconstructionPosture(status="PARTIAL", causal_reconstructability=0.5),
    )
    record = build_action_first_record(observation(), value)
    assert record["realized_state"]["state_hash"] == HASH_A
    assert record["observed_state"]["state_hash"] is None
    assert record["reality_observation_delta"]["status"] == "NOT_COMPUTABLE"


def test_nonexecuted_runtime_cannot_claim_irreversibility():
    with pytest.raises(ValueError, match="non-executed"):
        build_action_first_record(observation(executed=False, outcome="DENY"), runtime_input())


def test_candidate_binding_is_exact():
    with pytest.raises(ValueError, match="action_candidate_ref"):
        build_action_first_record(observation(), runtime_input(action_candidate_ref="candidate-other"))


def test_runtime_refuses_constraint_promotion_into_governance_truth():
    posture = ReconstructionPosture(
        status="COMPLETE",
        causal_reconstructability=1.0,
        identifiability="IDENTIFIABLE",
        prediction_fit=1.0,
        constraint_promotion="PROMOTED",  # type: ignore[arg-type]
    )
    with pytest.raises(ValueError, match="cannot promote"):
        build_action_first_record(observation(), runtime_input(reconstruction=posture))


def test_unknown_residual_must_not_invent_numeric_value():
    with pytest.raises(ValueError, match="must not invent"):
        build_action_first_record(
            observation(),
            runtime_input(model_reality_delta=ResidualObservation("metric:test", 0.3, "UNKNOWN")),
        )


def test_semantic_source_is_immutable_pinned_interop_schema():
    source = runtime_semantic_source()
    assert source["repository"] == "StegVerse-Labs/ara-admissibility-interop"
    assert source["commit"] == "d48b2734c2fdb8018271e2413a0d786f6cc5e479"
    assert source["blob"] == "c49f70190ad313e2c849564c411080cd3c7a610f"
