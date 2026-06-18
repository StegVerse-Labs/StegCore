import unittest

from stegcore.adapters import decide_schema_record


class Test001002ProofPathMatrix(unittest.TestCase):
    def test_proof_path_matrix(self):
        cases = [
            (
                "sv001_continuity_allow",
                {
                    "schema_id": "continuity_receipt",
                    "owner_entity": "StegVerse-001",
                    "authority_context_ref": "auth:continuity:baseline",
                    "policy_ref": "policy:continuity:baseline",
                    "identity_valid": True,
                    "evidence_fresh": True,
                    "context_valid": True,
                },
                "allow",
                "entity_001_002.allow",
            ),
            (
                "sv001_evidence_review",
                {
                    "schema_id": "continuity_receipt",
                    "owner_entity": "StegVerse-001",
                    "authority_context_ref": "auth:continuity:baseline",
                    "policy_ref": "policy:continuity:baseline",
                    "identity_valid": True,
                    "evidence_fresh": False,
                    "context_valid": True,
                },
                "defer",
                "entity_001_002.stale",
            ),
            (
                "sv002_restricted_access_deny",
                {
                    "schema_id": "master_record_ingestion",
                    "owner_entity": "StegVerse-002",
                    "authority_context_ref": "auth:records:baseline",
                    "policy_ref": "policy:records:baseline",
                    "identity_valid": True,
                    "evidence_fresh": True,
                    "context_valid": True,
                    "public_user_direct_access": True,
                    "raw_master_record_ingestion": True,
                },
                "deny",
                "entity_001_002.deny",
            ),
            (
                "sv002_reviewer_refusal",
                {
                    "schema_id": "master_record_ingestion",
                    "owner_entity": "StegVerse-002",
                    "authority_context_ref": "auth:records:baseline",
                    "policy_ref": "policy:records:baseline",
                    "identity_valid": True,
                    "evidence_fresh": True,
                    "context_valid": True,
                    "reviewer_refusal": True,
                    "override_authority_verified": False,
                },
                "defer",
                "entity_001_002.refusal",
            ),
            (
                "sv002_override_unverified",
                {
                    "schema_id": "master_record_ingestion",
                    "owner_entity": "StegVerse-002",
                    "authority_context_ref": "auth:records:baseline",
                    "policy_ref": "policy:records:baseline",
                    "identity_valid": True,
                    "evidence_fresh": True,
                    "context_valid": True,
                    "override_requested": True,
                    "override_authority_verified": False,
                },
                "defer",
                "entity_001_002.override_required",
            ),
        ]

        for case_id, record, expected_decision, expected_reason_code in cases:
            with self.subTest(case_id=case_id):
                decision = decide_schema_record(record)
                self.assertEqual(decision.decision, expected_decision)
                self.assertEqual(decision.reason_code, expected_reason_code)


if __name__ == "__main__":
    unittest.main()
