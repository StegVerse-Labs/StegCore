import unittest

from stegcore.spec_conformance import (
    ConformanceError,
    validate_action_request,
    validate_commit_time,
    validate_decision_receipt,
    validate_execution_receipt,
    validate_replay_result,
)

DIGEST_A = "a" * 64
DIGEST_B = "b" * 64


class StegVerseSpecConformanceTests(unittest.TestCase):
    def action_request(self):
        return {
            "transition_id": "transition-001",
            "action": {"type": "publish", "target": "artifact-001", "parameters": {}},
            "actor_identity": "agent-alice",
            "actor_authority": "authority-human-001",
            "scope": ["publish:artifact-001"],
            "policy_reference": "policy://stegverse/publish",
            "policy_version": "1",
            "delegation_reference": "delegation-001",
            "consent_reference": "consent-001",
            "evidence_references": ["evidence-001"],
            "execution_context": {"repository": "StegVerse-Labs/StegCore"},
            "validity_window": {
                "not_before": "2026-07-14T00:00:00Z",
                "not_after": "2026-07-15T00:00:00Z",
            },
            "recoverability_profile": {"mode": "compensation"},
            "state_digest": DIGEST_A,
        }

    def decision_receipt(self):
        return {
            "transition_id": "transition-001",
            "decision": "ALLOW",
            "reason_codes": ["POLICY_AND_AUTHORITY_VALID"],
            "policy_reference": "policy://stegverse/publish",
            "policy_version": "1",
            "delegation_reference": "delegation-001",
            "evidence_references": ["evidence-001"],
            "state_digest": DIGEST_A,
            "evaluator_version": "stegverse-spec-checker/1.3",
            "evaluated_at": "2026-07-14T00:00:01Z",
            "valid_until": "2026-07-15T00:00:00Z",
            "receipt_digest": DIGEST_B,
        }

    def test_valid_action_and_decision_pass(self):
        validate_action_request(self.action_request())
        validate_decision_receipt(self.decision_receipt())

    def test_missing_evidence_fails_closed(self):
        request = self.action_request()
        request["evidence_references"] = []
        with self.assertRaises(ConformanceError):
            validate_action_request(request)

    def test_policy_drift_denies_commit(self):
        valid, reasons = validate_commit_time(self.action_request(), self.decision_receipt(), "2", DIGEST_A)
        self.assertFalse(valid)
        self.assertIn("POLICY_DRIFT", reasons)

    def test_state_drift_denies_commit(self):
        valid, reasons = validate_commit_time(self.action_request(), self.decision_receipt(), "1", DIGEST_B)
        self.assertFalse(valid)
        self.assertIn("STATE_DRIFT", reasons)

    def test_invalid_commit_cannot_claim_execution(self):
        receipt = {
            "transition_id": "transition-001",
            "decision_receipt_digest": DIGEST_B,
            "commit_time_valid": False,
            "commit_time_reason_codes": ["POLICY_DRIFT"],
            "execution_status": "EXECUTED",
            "executed_at": "2026-07-14T00:00:02Z",
            "effect_references": [],
            "compensation_reference": None,
            "post_state_digest": None,
            "receipt_digest": DIGEST_A,
        }
        with self.assertRaises(ConformanceError):
            validate_execution_receipt(receipt)

    def test_replay_divergence_must_be_explicit(self):
        result = {
            "transition_id": "transition-001",
            "original_decision": "ALLOW",
            "replayed_decision": "DENY",
            "original_state_digest": DIGEST_A,
            "replay_state_digest": DIGEST_B,
            "evaluator_version": "stegverse-spec-checker/1.3",
            "matches_original": False,
            "divergence_codes": ["STATE_DRIFT", "DECISION_CHANGED"],
            "replayed_at": "2026-07-14T00:01:00Z",
        }
        validate_replay_result(result)

    def test_matching_replay_cannot_report_divergence(self):
        result = {
            "transition_id": "transition-001",
            "original_decision": "ALLOW",
            "replayed_decision": "ALLOW",
            "original_state_digest": DIGEST_A,
            "replay_state_digest": DIGEST_A,
            "evaluator_version": "stegverse-spec-checker/1.3",
            "matches_original": True,
            "divergence_codes": ["UNEXPECTED"],
            "replayed_at": "2026-07-14T00:01:00Z",
        }
        with self.assertRaises(ConformanceError):
            validate_replay_result(result)


if __name__ == "__main__":
    unittest.main()
