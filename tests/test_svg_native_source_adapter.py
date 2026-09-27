import unittest
from benchmarks.svg_native_source_adapter import evaluate_native_source
from stegcore.three_layer import (
    ExecutionBoundary, JudgmentConditions, SignalAdmission, ThreeLayerRequest,
)


def request(authority=True):
    return ThreeLayerRequest(
        judgment_conditions=JudgmentConditions(
            refusal_available=True, operator_recoverability="available",
            workload_state="supported", time_pressure="normal",
            isolation_state="supported", evidence_refs=("synthetic:judgment",)),
        signal_admission=SignalAdmission(
            admitted_signal_refs=("synthetic:signal",),
            uncertainty_state="bounded", reference_state_hash="synthetic:state",
            expected_reference_state_hash="synthetic:state",
            reconstruction_available=True, transformation_provenance_complete=True),
        execution_boundary=ExecutionBoundary(
            actor_authority_current=authority, policy_current=True,
            delegation_current=True, evidence_current=True,
            affected_entity_conditions_represented=True,
            recoverability_profile="recoverable", validity_window_open=True,
            policy_ref="synthetic:policy", delegation_ref="synthetic:delegation",
            evidence_refs=("synthetic:execution",)),
        action="synthetic:operation", target="synthetic:target", scope="synthetic:test",
    )


class SVGNativeAdapterTests(unittest.TestCase):
    def test_native_allow(self):
        r = evaluate_native_source(request())
        self.assertEqual(r["native_disposition"], "ALLOW")
        self.assertEqual(r["disposition"], "ALLOW")
        self.assertEqual(r["governance_stage_vector_status"], "NOT_PROVIDED")
        self.assertFalse(r["authentic_consequence_observed"])
        self.assertFalse(r["original_master_records_reconstruction_observed"])
        self.assertFalse(r["native_continuity_receipt_minted"])
        self.assertTrue(r["native_receipt_hash"])

    def test_native_deny(self):
        r = evaluate_native_source(request(authority=False))
        self.assertEqual(r["disposition"], "DENY")

    def test_native_unknown_fails_closed(self):
        r = evaluate_native_source(request(authority=None))
        self.assertEqual(r["disposition"], "FAIL_CLOSED")

    def test_malformed_request_fails_closed(self):
        self.assertEqual(evaluate_native_source({})["disposition"], "FAIL_CLOSED")

    def test_stage_shape_is_not_authentication(self):
        stages = [{"stage": f"A{i}"} for i in range(9)]
        r = evaluate_native_source(request(), governance_stage_vector={
            "schema_version": "1.0.0", "stages": stages})
        self.assertEqual(r["governance_stage_vector_status"], "SHAPE_ONLY_UNVALIDATED")
        self.assertEqual(r["authority_effect"], "NONE")
        stages.pop()
        r = evaluate_native_source(request(), governance_stage_vector={
            "schema_version": "1.0.0", "stages": stages})
        self.assertEqual(r["governance_stage_vector_status"], "INVALID")


if __name__ == "__main__":
    unittest.main()
