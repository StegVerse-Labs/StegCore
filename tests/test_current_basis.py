import json
from pathlib import Path

from stegcore.current_basis import (
    VECTOR_SCHEMA,
    derive_admissibility_request,
    evaluate_current_basis_vector,
)


def vector():
    return {
        "vector_schema": VECTOR_SCHEMA,
        "freeze_state": "DRAFT_PRE_FREEZE",
        "initial_state": {
            "state_id": "S0",
            "standing": "DECLARED_VALID_FOR_TEST",
            "prior_determination": "DECLARED_VALID_FOR_TEST",
            "receipt_state": "NOT_RECEIPT_BEARING_PRE_OBSERVATION",
        },
        "transition": {
            "transition_id": "DELTA-S0-S1",
            "materiality": "MATERIAL",
            "changed_condition": "CURRENT_POLICY_BASIS_CHANGED",
            "invalidation_asserted_as_input": False,
            "transition_semantics": "MATERIAL_CHANGE_REQUIRING_CURRENT_BASIS_EVALUATION",
            "receipt_semantics": "S0_TO_S1_RECEIPT_IS_POST_OBSERVATION_EVIDENCE",
        },
        "successor_state_observed_inputs": {
            "state_id": "S1",
            "actor": {
                "class": "ai",
                "action": "publish_candidate",
                "target": "cross-framework-current-basis-vector",
                "scope": "evaluation",
            },
            "policy": {
                "reference": "policy:s1-materially-changed",
                "observation": "MATERIAL_CHANGE_PRESENT",
            },
            "delegation": {
                "reference": "delegation:s1",
                "observation": "SUPPLIED_FOR_EVALUATION",
            },
            "evidence": {
                "references": ["execution:s1-observed-inputs", "state:s0-declared-valid"],
                "observation": "SUPPLIED_FOR_EVALUATION",
            },
            "validity_window": {
                "observation": "WINDOW_FACTS_SUPPLIED_TO_EACH_ARCHITECTURE",
            },
            "judgment_context": {
                "refusal_available": True,
                "operator_recoverability": "available",
                "workload_state": "supported",
                "time_pressure": "normal",
                "isolation_state": "supported",
            },
            "signal_context": {
                "admitted_signal_refs": ["signal:current-basis:s1"],
                "transformations": ["state-transition:s0-to-s1"],
                "missing_inputs": [],
                "uncertainty_state": "bounded",
                "reference_state_hash": "state:s1",
                "expected_reference_state_hash": "state:s1",
                "reconstruction_available": True,
                "transformation_provenance_complete": True,
            },
        },
    }


def test_s0_is_declared_initial_state_without_historical_receipt():
    request = derive_admissibility_request(vector())
    assert request.continuity.required is False
    assert request.continuity.previous_receipt_verified is None
    assert request.continuity.previous_receipt_hash is None
    assert request.declared_context["s0_origin"] == "DECLARED_INITIAL_TEST_STATE"


def test_material_change_does_not_preassert_invalidation_or_noncurrentness():
    request = derive_admissibility_request(vector())
    assert request.execution.policy_current is None
    assert request.execution.actor_authority_current is None
    assert request.execution.delegation_current is None
    assert request.execution.evidence_current is None
    assert request.execution.validity_window_open is None
    assert request.declared_context["invalidation_asserted_as_input"] is False


def test_neutral_refs_are_preserved_for_native_evaluation():
    request = derive_admissibility_request(vector())
    assert request.execution.policy_ref == "policy:s1-materially-changed"
    assert request.execution.delegation_ref == "delegation:s1"
    assert request.execution.evidence_refs == [
        "execution:s1-observed-inputs",
        "state:s0-declared-valid",
    ]
    assert request.signal.reference_state_hash == "state:s1"
    assert request.signal.expected_reference_state_hash == "state:s1"


def test_canonical_steggate_produces_observable_s1_without_minting_transition_receipt():
    result = evaluate_current_basis_vector(vector())
    assert result["canonical_evaluator"] == "stegcore.steggate.evaluate_admissibility"
    assert result["parallel_evaluator"] is False
    assert result["s1_observed"] is True
    assert result["transition_receipt_minted"] is False
    assert result["transition_receipt_eligible_after_observation"] is True
    assert result["material_change_treated_as_invalidation_input"] is False

    matrix = {row["predicate"]: row for row in result["evaluation"]["matrix"]}
    assert matrix["execution.policy_current"]["state"] == "UNKNOWN"
    assert matrix["execution.delegation_current"]["state"] == "UNKNOWN"
    assert matrix["execution.evidence_current"]["state"] == "UNKNOWN"
    assert matrix["execution.validity_window_open"]["state"] == "UNKNOWN"


def test_explicit_currentness_fact_can_be_derived_when_common_input_supplies_it():
    value = vector()
    value["successor_state_observed_inputs"]["policy"]["currentness"] = "CURRENT"
    request = derive_admissibility_request(value)
    assert request.execution.policy_current is True
