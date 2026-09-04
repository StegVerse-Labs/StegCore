from __future__ import annotations

import unittest

from stegcore.legacy_release import LegacyReleaseError, evaluate_legacy_release


def allowed_facts():
    return {
        "transition_id": "LEGACY-SOURCE-CONTRACT-001",
        "capsule_id": "LEGACY-CAPSULE-SOURCE-CONTRACT-001",
        "recipient_identity_id": "stegid:source-contract:001",
        "requested_transition": "DISCLOSE_CAPSULE",
        "recipient_identity_verified": True,
        "participation_required": True,
        "participation_qualified": True,
        "release_trigger_verified": True,
        "tvc_authorization_verified": True,
        "participant_policy_current": True,
        "delegation_current": True,
        "evidence_current": True,
        "reconstruction_available": True,
        "transformation_provenance_complete": True,
        "affected_recipient_conditions_represented": True,
        "validity_window_open": True,
        "recipient_refusal_available": True,
        "operator_recoverability": "available",
        "workload_state": "supported",
        "time_pressure": "normal",
        "isolation_state": "supported",
        "uncertainty_state": "bounded",
        "recoverability_profile": "recoverable",
        "reference_state_hash": "source-contract-state",
        "expected_reference_state_hash": "source-contract-state",
        "policy_ref": "kv://personal/legacy/policies/source-contract",
        "delegation_ref": "tvc://legacy/source-contract",
        "evidence_refs": [
            "stegid://legacy/source-contract",
            "continuity://trigger/source-contract",
            "tvc://authorization/source-contract",
        ],
    }


class LegacyReleaseSourceContractTests(unittest.TestCase):
    def test_allow_is_canonical_admissibility_not_consequence_authority(self):
        result = evaluate_legacy_release(allowed_facts())
        self.assertEqual(result["decision"], "ALLOW")
        self.assertEqual(result["canonical_runtime"], "stegcore.three_layer.evaluate_three_layer")
        self.assertFalse(result["disclosure_authority_granted"])
        self.assertFalse(result["economic_transfer_authority_granted"])
        self.assertFalse(result["external_execution_performed"])
        self.assertEqual(result["authority_effect"], "NONE")

    def test_state_discontinuity_is_fail_closed_by_canonical_runtime(self):
        facts = allowed_facts()
        facts["expected_reference_state_hash"] = "different-state"
        result = evaluate_legacy_release(facts)
        self.assertEqual(result["decision"], "FAIL-CLOSED")
        self.assertEqual(result["reason_code"], "signal.reference_state_discontinuous")

    def test_missing_tvc_authorization_never_reaches_allow(self):
        facts = allowed_facts()
        facts["tvc_authorization_verified"] = False
        with self.assertRaises(LegacyReleaseError):
            evaluate_legacy_release(facts)

    def test_unknown_governance_state_is_rejected_before_evaluation(self):
        facts = allowed_facts()
        facts["recoverability_profile"] = "invented"
        with self.assertRaises(LegacyReleaseError):
            evaluate_legacy_release(facts)


if __name__ == "__main__":
    unittest.main()
