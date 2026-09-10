from __future__ import annotations

import unittest

from stegcore.current_basis import evaluate_current_basis_vector
from stegcore.three_layer import (
    ExecutionBoundary,
    JudgmentConditions,
    SignalAdmission,
    ThreeLayerRequest,
    evaluate_three_layer,
)


def _three_layer_request(*, actor_authority_current):
    return ThreeLayerRequest(
        judgment_conditions=JudgmentConditions(
            refusal_available=True,
            operator_recoverability="available",
            workload_state="supported",
            time_pressure="normal",
            isolation_state="supported",
        ),
        signal_admission=SignalAdmission(
            admitted_signal_refs=("signal:test",),
            missing_inputs=(),
            uncertainty_state="bounded",
            reference_state_hash="state:s1",
            expected_reference_state_hash="state:s1",
            reconstruction_available=True,
            transformation_provenance_complete=True,
        ),
        execution_boundary=ExecutionBoundary(
            actor_authority_current=actor_authority_current,
            policy_current=True,
            delegation_current=True,
            evidence_current=True,
            affected_entity_conditions_represented=True,
            recoverability_profile="recoverable",
            validity_window_open=True,
            policy_ref="policy:test",
            delegation_ref="delegation:test",
        ),
        action="publish_candidate",
        target="test-target",
        scope="evaluation",
    )


def _frozen_v04_neutral_vector():
    return {
        "vector_schema": "stegverse.cross-framework-current-basis-vector.v0.4",
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
            "policy": {"reference": "policy:s1-materially-changed", "observation": "MATERIAL_CHANGE_PRESENT"},
            "delegation": {"reference": "delegation:s1", "observation": "SUPPLIED_FOR_EVALUATION"},
            "evidence": {
                "references": ["execution:s1-observed-inputs", "state:s0-declared-valid"],
                "observation": "SUPPLIED_FOR_EVALUATION",
            },
            "validity_window": {"observation": "WINDOW_FACTS_SUPPLIED_TO_EACH_ARCHITECTURE"},
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


class UnknownProbeSemanticsTests(unittest.TestCase):
    def test_unknown_execution_fact_requires_probe(self):
        result = evaluate_three_layer(_three_layer_request(actor_authority_current=None))
        self.assertEqual(result.decision, "FAIL-CLOSED")
        self.assertEqual(result.reason_code, "execution.probe_required")
        self.assertIn("actor_authority_current", result.findings[0].detail)

    def test_explicit_false_still_denies_as_stale(self):
        result = evaluate_three_layer(_three_layer_request(actor_authority_current=False))
        self.assertEqual(result.decision, "DENY")
        self.assertEqual(result.reason_code, "execution.authority_stale")

    def test_frozen_v04_neutral_currentness_no_longer_collapses_to_false(self):
        result = evaluate_current_basis_vector(_frozen_v04_neutral_vector())
        native = result["native_request"]["execution"]
        self.assertIsNone(native["actor_authority_current"])
        self.assertIsNone(native["policy_current"])
        self.assertIsNone(native["delegation_current"])
        self.assertIsNone(native["evidence_current"])
        self.assertIsNone(native["validity_window_open"])
        evaluation = result["evaluation"]
        self.assertEqual(evaluation["disposition"], "FAIL_CLOSED")
        self.assertEqual(evaluation["canonical_three_layer_reason"], "execution.probe_required")
        self.assertNotEqual(evaluation["canonical_three_layer_reason"], "execution.authority_stale")


if __name__ == "__main__":
    unittest.main()
