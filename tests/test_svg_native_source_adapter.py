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

    def stage_vector(self, disposition="ALLOW"):
        return {
            "schema_version": "1.0.0", "transition_id": "synthetic:transition",
            "governance_classes": ["G0"],
            "stages": [
                {"stage": f"A{i}", "name": f"synthetic stage {i}",
                 "status": "PASS", "evidence_refs": [f"synthetic:stage:{i}"]}
                for i in range(9)
            ],
            "aggregate_disposition": disposition,
            "authority_boundaries": {
                "taxonomy_grants_execution_authority": False,
                "continuity_receipt_minted": False,
                "certification_granted": False,
                "custody_granted": False,
            },
        }

    def test_governance_schema_valid_is_not_authentication(self):
        from stegcore._vendor import structural_validator

        r = evaluate_native_source(request(), governance_stage_vector=self.stage_vector())
        self.assertEqual(r["authority_effect"], "NONE")
        self.assertFalse(r["authentic_consequence_observed"])
        self.assertFalse(r["original_master_records_reconstruction_observed"])
        if "prefixItems" not in structural_validator.SUPPORTED:
            # Contract 1.6 does not support prefixItems: the pinned Governance schema is
            # refused at admission and the adapter fails closed, never a silent pass.
            self.assertEqual(r["governance_stage_vector_status"], "INVALID")
            self.assertEqual(r["disposition"], "FAIL_CLOSED")
            self.assertIn("GOVERNANCE_SCHEMA_UNAVAILABLE_OR_INVALID:UNSUPPORTED_KEYWORD:prefixItems",
                          r["governance_validation_errors"])
            self.assertIsNone(r["governance_stage_vector_sha256"])
            return
        self.assertEqual(r["governance_stage_vector_status"], "SCHEMA_VALID_SOURCE_ONLY")
        self.assertEqual(r["disposition"], "ALLOW")
        self.assertTrue(r["governance_stage_vector_sha256"])

    def test_shape_only_vector_fails_closed(self):
        r = evaluate_native_source(request(), governance_stage_vector={
            "schema_version": "1.0.0",
            "stages": [{"stage": f"A{i}"} for i in range(9)]})
        self.assertEqual(r["disposition"], "FAIL_CLOSED")
        self.assertEqual(r["governance_stage_vector_status"], "INVALID")

    def test_invalid_authority_boundary_fails_closed(self):
        v = self.stage_vector()
        v["authority_boundaries"]["custody_granted"] = True
        r = evaluate_native_source(request(), governance_stage_vector=v)
        self.assertEqual(r["disposition"], "FAIL_CLOSED")
        self.assertEqual(r["native_disposition"], "ALLOW")

    def test_native_disposition_conflict_fails_closed(self):
        r = evaluate_native_source(request(authority=False), governance_stage_vector=self.stage_vector("ALLOW"))
        self.assertEqual(r["native_disposition"], "DENY")
        self.assertEqual(r["disposition"], "FAIL_CLOSED")
        from stegcore._vendor import structural_validator

        if "prefixItems" not in structural_validator.SUPPORTED:
            # Contract 1.6: the pinned schema is refused first, so the vector never
            # reaches the disposition comparison; still fail closed.
            self.assertIn("GOVERNANCE_SCHEMA_UNAVAILABLE_OR_INVALID:UNSUPPORTED_KEYWORD:prefixItems",
                          r["governance_validation_errors"])
            return
        self.assertIn("AGGREGATE_DISPOSITION_CONFLICTS_WITH_NATIVE_EVALUATION", r["governance_validation_errors"])

    def test_stage_order_and_missing_evidence_fail_closed(self):
        v = self.stage_vector()
        v["stages"][0], v["stages"][1] = v["stages"][1], v["stages"][0]
        self.assertEqual(evaluate_native_source(request(), governance_stage_vector=v)["disposition"], "FAIL_CLOSED")
        v = self.stage_vector()
        del v["stages"][4]["evidence_refs"]
        self.assertEqual(evaluate_native_source(request(), governance_stage_vector=v)["disposition"], "FAIL_CLOSED")


    def test_undecodable_pinned_governance_schema_fails_closed(self):
        from pathlib import Path
        from unittest.mock import patch

        original_read_text = Path.read_text

        def read_text_with_corrupt_schema(path, *args, **kwargs):
            if path.name == "governance_admissibility_stage_vector.schema.json":
                raise UnicodeDecodeError("utf-8", bytes([0xFF]), 0, 1, "invalid start byte")
            return original_read_text(path, *args, **kwargs)

        with patch.object(Path, "read_text", read_text_with_corrupt_schema):
            result = evaluate_native_source(request(), governance_stage_vector=self.stage_vector())
        self.assertEqual(result["disposition"], "FAIL_CLOSED")
        self.assertEqual(result["governance_stage_vector_status"], "INVALID")
        self.assertIn("GOVERNANCE_SCHEMA_UNAVAILABLE_OR_INVALID:UnicodeDecodeError", result["governance_validation_errors"])


    def test_prefix_items_ref_allof_rejects_duplicate_stage_identity(self):
        vector = self.stage_vector()
        vector["stages"][1]["stage"] = "A0"
        result = evaluate_native_source(request(), governance_stage_vector=vector)
        self.assertEqual(result["disposition"], "FAIL_CLOSED")
        self.assertEqual(result["governance_stage_vector_status"], "INVALID")
        self.assertTrue(result["governance_validation_errors"])

    def test_ref_stage_required_status_fails_closed(self):
        vector = self.stage_vector()
        del vector["stages"][8]["status"]
        result = evaluate_native_source(request(), governance_stage_vector=vector)
        self.assertEqual(result["disposition"], "FAIL_CLOSED")
        self.assertEqual(result["governance_stage_vector_status"], "INVALID")
        self.assertTrue(result["governance_validation_errors"])


if __name__ == "__main__":
    unittest.main()
