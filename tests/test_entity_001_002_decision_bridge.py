import unittest

from stegcore.adapters import decide_schema_record
from stegcore.decision import DecisionResult


class TestEntity001002DecisionBridge(unittest.TestCase):
    def test_allow_maps_to_native_allow(self):
        decision = decide_schema_record(
            {
                "schema_id": "continuity_receipt",
                "owner_entity": "StegVerse-001",
                "authority_context_ref": "auth:continuity:baseline",
                "policy_ref": "policy:continuity:baseline",
                "identity_valid": True,
                "evidence_fresh": True,
                "context_valid": True,
            }
        )
        self.assertIsInstance(decision, DecisionResult)
        self.assertEqual(decision.decision, "allow")
        self.assertEqual(decision.reason_code, "entity_001_002.allow")

    def test_public_raw_master_ingestion_maps_to_native_deny(self):
        decision = decide_schema_record(
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
            }
        )
        self.assertEqual(decision.decision, "deny")
        self.assertEqual(decision.reason_code, "entity_001_002.deny")
        self.assertEqual(
            decision.reason_detail["principle"],
            "restricted_internal_entities_are_not_public_user_surfaces",
        )

    def test_stale_maps_to_native_defer_with_detail_preserved(self):
        decision = decide_schema_record(
            {
                "schema_id": "continuity_receipt",
                "owner_entity": "StegVerse-001",
                "authority_context_ref": "auth:continuity:baseline",
                "policy_ref": "policy:continuity:baseline",
                "identity_valid": True,
                "evidence_fresh": False,
                "context_valid": True,
            }
        )
        self.assertEqual(decision.decision, "defer")
        self.assertEqual(decision.reason_code, "entity_001_002.stale")
        self.assertEqual(decision.reason_detail["adapter_status"], "stale")

    def test_refusal_maps_to_native_defer_with_refusal_detail(self):
        decision = decide_schema_record(
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
            }
        )
        self.assertEqual(decision.decision, "defer")
        self.assertEqual(decision.reason_code, "entity_001_002.refusal")
        self.assertEqual(decision.reason_detail["principle"], "refusal_must_bind_consequence")


if __name__ == "__main__":
    unittest.main()
