import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CASES = (
    ("evidence/release-readiness.json", "assessment_hash", "release_readiness_assessment"),
    ("evidence/runtime-validation.json", "evidence_hash", "runtime_validation_evidence"),
)


class CustodyEvidenceEnvelopeTests(unittest.TestCase):
    def test_evidence_envelopes_verify(self):
        for path, hash_field, record_type in CASES:
            with self.subTest(path=path):
                record = json.loads((ROOT / path).read_text(encoding="utf-8"))
                self.assertEqual(record["record_type"], record_type)
                self.assertEqual(record["source_repository"], "StegVerse-Labs/StegCore")
                self.assertEqual(record["destination_repository"], "StegVerse-Labs/StegCore")
                self.assertEqual(record["hash_convention"]["excluded_field"], hash_field)
                body = dict(record)
                declared = body.pop(hash_field)
                computed = hashlib.sha256(
                    json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
                ).hexdigest()
                self.assertEqual(declared, computed)


if __name__ == "__main__":
    unittest.main()
