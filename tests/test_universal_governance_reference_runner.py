from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts.run_universal_governance_reference_boundary import execute


class UniversalGovernanceReferenceRunnerTests(unittest.TestCase):
    def test_reference_boundary_executes_once_and_emits_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = execute(root)

            self.assertTrue(receipt["reference_enforced_boundary_observed"])
            self.assertTrue(receipt["bypass_negative_control_passed"])
            self.assertEqual(receipt["governed_target_mutation_count"], 1)
            self.assertFalse(receipt["real_external_system_enforced_activation"])
            self.assertEqual(receipt["credential_authority"], "TV/TVC")
            self.assertFalse(receipt["repository_writeback_performed"])
            self.assertFalse(receipt["network_used"])

            target = json.loads((root / "target" / "state.json").read_text())
            self.assertEqual(target["mutation_count"], 1)
            self.assertEqual(target["mutation_path"], "GOVERNED_ONLY")

            evidence = json.loads((root / "evidence" / "consequence.json").read_text())
            projection = json.loads((root / "evidence" / "master-records-projection.json").read_text())
            durable = json.loads((root / "receipts" / "reference-boundary.latest.json").read_text())

            self.assertEqual(evidence["candidate"]["candidate_hash"], receipt["candidate_hash"])
            self.assertEqual(projection["source_evidence_hash"], evidence["evidence_hash"])
            self.assertEqual(projection["return_intr_packet_id"], receipt["return_intr_packet_id"])
            self.assertEqual(
                projection["return_terminal_receipt_hash"],
                receipt["return_terminal_receipt_hash"],
            )
            self.assertEqual(durable, receipt)


if __name__ == "__main__":
    unittest.main()
