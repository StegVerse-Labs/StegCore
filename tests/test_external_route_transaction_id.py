import unittest

from stegcore.steggate import AdmissibilityRequest
from stegcore.transaction_lifecycle import run_manifested_transaction


class ExternalRouteTransactionIdentityTests(unittest.TestCase):
    def test_run_preserves_supplied_transaction_id(self):
        request = AdmissibilityRequest.model_validate({
            "candidate": {"actor_class": "ai", "action": "inspect", "target": "record", "scope": "test", "parameters": {}},
            "judgment": {"refusal_available": True, "operator_recoverability": "available", "workload_state": "supported", "time_pressure": "normal", "isolation_state": "supported", "evidence_refs": ["j:1"]},
            "signal": {"admitted_signal_refs": ["s:1"], "transformations": [], "missing_inputs": [], "uncertainty_state": "bounded", "reference_state_hash": "state:1", "expected_reference_state_hash": "state:1", "reconstruction_available": True, "transformation_provenance_complete": True},
            "execution": {"actor_authority_current": True, "policy_current": True, "delegation_current": True, "evidence_current": True, "affected_entity_conditions_represented": True, "recoverability_profile": "recoverable", "validity_window_open": True, "policy_ref": "p:1", "delegation_ref": "d:1", "evidence_refs": ["e:1"]},
            "capability": {"allowed": True},
            "continuity": {"required": True, "previous_receipt_verified": True, "previous_receipt_hash": "prior:1"},
            "approval": {"required": False},
            "permission_present": False,
        })
        result = run_manifested_transaction(
            request,
            lambda: {"ok": True},
            input_data={"value": 1},
            source="route-carrier",
            subject="test",
            transaction_id="TX-EXTERNAL-ROUTE-1",
        )
        self.assertEqual("TX-EXTERNAL-ROUTE-1", result.transaction_id)
        self.assertEqual("TX-EXTERNAL-ROUTE-1", result.manifest.transaction_id)
        self.assertTrue(all(r.transaction_id == "TX-EXTERNAL-ROUTE-1" for r in result.receipts))


if __name__ == "__main__": unittest.main()
