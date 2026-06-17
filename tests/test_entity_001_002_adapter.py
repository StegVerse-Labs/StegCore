import json
from pathlib import Path
import unittest

from stegcore.adapters import evaluate_schema_record, map_schema_record_to_transition


FIXTURES = Path(__file__).parent / "fixtures" / "entity_records"


class TestEntity001002Adapter(unittest.TestCase):
    def test_fixture_statuses(self):
        for fixture_path in sorted(FIXTURES.glob("*.json")):
            with self.subTest(fixture=fixture_path.name):
                record = json.loads(fixture_path.read_text(encoding="utf-8"))
                result = evaluate_schema_record(record)
                self.assertEqual(result.status, record["expected_status"])

    def test_continuity_maps_to_stegverse_001(self):
        record = json.loads((FIXTURES / "continuity_allow.json").read_text(encoding="utf-8"))
        transition = map_schema_record_to_transition(record)
        self.assertEqual(transition["entity"], "StegVerse-001")

    def test_master_records_map_to_stegverse_002(self):
        record = json.loads((FIXTURES / "master_ingestion_public_raw_deny.json").read_text(encoding="utf-8"))
        transition = map_schema_record_to_transition(record)
        self.assertEqual(transition["entity"], "StegVerse-002")

    def test_wrong_owner_is_rejected(self):
        record = {
            "schema_id": "master_record_ingestion",
            "owner_entity": "StegVerse-001",
            "authority_context_ref": "auth:bad",
            "policy_ref": "policy:bad",
        }
        with self.assertRaises(ValueError):
            map_schema_record_to_transition(record)


if __name__ == "__main__":
    unittest.main()
