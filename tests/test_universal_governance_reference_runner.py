from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts.run_universal_governance_reference_boundary import execute


class UniversalGovernanceReferenceRunnerTests(unittest.TestCase):
    def test_reference_boundary_requires_fresh_single_use_binding_and_emits_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = execute(root)

            self.assertTrue(receipt["reference_enforced_boundary_observed"])
            self.assertTrue(receipt["bypass_negative_control_passed"])
            self.assertTrue(receipt["alternate_consequence_path_closed"])
            self.assertTrue(receipt["stale_binding_rejected"])
            self.assertTrue(receipt["fresh_binding_required"])
            self.assertTrue(receipt["fresh_binding_single_use"])
            self.assertEqual(receipt["governed_target_mutation_count"], 1)
            self.assertEqual(receipt["final_target_mutation_count"], 1)
            self.assertFalse(receipt["real_external_system_enforced_activation"])
            self.assertFalse(receipt["resident_execution_observed"])
            self.assertEqual(receipt["credential_authority"], "TV/TVC")
            self.assertFalse(receipt["repository_writeback_performed"])
            self.assertFalse(receipt["network_used"])

            self.assertEqual(receipt["initial_state_version"], "V0")
            self.assertEqual(receipt["post_transition_state_version"], "V1")
            self.assertEqual(receipt["stale_canonical_route_disposition"], "DENY")
            self.assertFalse(receipt["stale_canonical_executor_invoked"])
            self.assertEqual(receipt["stale_alternate_route_disposition"], "DENY")
            self.assertFalse(receipt["stale_alternate_executor_invoked"])
            self.assertEqual(receipt["post_commit_alternate_route_disposition"], "DENY")
            self.assertIn(
                "execution_binding_already_consumed",
                receipt["post_commit_alternate_route_reasons"],
            )
            self.assertFalse(receipt["post_commit_alternate_executor_invoked"])
            self.assertNotEqual(receipt["initial_binding_hash"], receipt["fresh_binding_hash"])

            target = json.loads((root / "target" / "state.json").read_text())
            self.assertEqual(target["mutation_count"], 1)
            self.assertEqual(target["mutation_path"], "GOVERNED_CANONICAL_COMMIT")
            self.assertEqual(target["material_state"]["state_version"], "V1")

            transition = json.loads(
                (root / "receipts" / "material-state-transition.json").read_text()
            )
            self.assertEqual(transition["before_state_version"], "V0")
            self.assertEqual(transition["after_state_version"], "V1")
            self.assertEqual(transition["consequence_mutation_count_before"], 0)
            self.assertEqual(transition["consequence_mutation_count_after"], 0)
            self.assertEqual(
                transition["receipt_hash"],
                receipt["material_state_transition_receipt_hash"],
            )

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
