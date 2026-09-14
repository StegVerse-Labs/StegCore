from __future__ import annotations

import unittest

from stegcore.fresh_commit_binding import (
    consume_execution_binding,
    evaluate_fresh_commit_binding,
)


def binding(**changes):
    value = {
        "state_version": "V1",
        "state_hash": "sha256:" + "1" * 64,
        "policy_epoch": "P1",
        "policy_hash": "sha256:" + "2" * 64,
        "evidence_bundle_hash": "sha256:" + "3" * 64,
        "execution_binding_id": "EXECUTION-BINDING-V1",
    }
    value.update(changes)
    return value


class FreshCommitBindingTests(unittest.TestCase):
    def test_exact_current_unconsumed_binding_allows(self):
        consumed = set()
        result = evaluate_fresh_commit_binding(
            expected=binding(),
            observed=binding(),
            consumed_execution_bindings=consumed,
        )
        self.assertEqual(result.disposition, "ALLOW")
        self.assertTrue(result.allowed)
        self.assertTrue(result.checks["state_version_current"])
        self.assertTrue(result.checks["policy_epoch_current"])
        self.assertTrue(result.checks["evidence_bundle_hash_current"])
        self.assertTrue(result.checks["execution_binding_unconsumed"])

    def test_material_state_drift_denies(self):
        result = evaluate_fresh_commit_binding(
            expected=binding(),
            observed=binding(
                state_version="V2",
                state_hash="sha256:" + "4" * 64,
                policy_epoch="P2",
                policy_hash="sha256:" + "5" * 64,
                evidence_bundle_hash="sha256:" + "6" * 64,
            ),
            consumed_execution_bindings=set(),
        )
        self.assertEqual(result.disposition, "DENY")
        self.assertIn("state_version_mismatch", result.reasons)
        self.assertIn("policy_epoch_mismatch", result.reasons)
        self.assertIn("evidence_bundle_hash_mismatch", result.reasons)

    def test_missing_observed_state_fails_closed(self):
        result = evaluate_fresh_commit_binding(
            expected=binding(),
            observed=None,
            consumed_execution_bindings=set(),
        )
        self.assertEqual(result.disposition, "FAIL_CLOSED")
        self.assertIn("observed_commit_state_unestablished", result.reasons)

    def test_consumed_binding_cannot_replay(self):
        consumed = set()
        consume_execution_binding(binding(), consumed)
        result = evaluate_fresh_commit_binding(
            expected=binding(),
            observed=binding(),
            consumed_execution_bindings=consumed,
        )
        self.assertEqual(result.disposition, "DENY")
        self.assertIn("execution_binding_already_consumed", result.reasons)

    def test_missing_consumption_state_fails_closed(self):
        result = evaluate_fresh_commit_binding(
            expected=binding(),
            observed=binding(),
            consumed_execution_bindings=None,
        )
        self.assertEqual(result.disposition, "FAIL_CLOSED")
        self.assertIn(
            "execution_binding_consumption_state_unestablished",
            result.reasons,
        )


if __name__ == "__main__":
    unittest.main()
