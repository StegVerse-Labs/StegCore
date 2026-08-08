from datetime import datetime, timezone

from scripts.validate_independent_release_policy import validate

NOW = datetime(2026, 8, 8, 16, 0, tzinfo=timezone.utc)

READINESS = {
    "stegcore_commit": "70bbb0eb8a5dec4f27ee7aca5cf09cdb17a924af",
    "assessment_hash": "92d4dd3e44c155d2362230142e4e611f86f196dc1baa190e1775c1f2b4427bbf",
    "runtime_evidence_hash": "7d03c0eb769fafafb57d940465274560e811ebf0850fb2c6e94e96e7b0d2bcfb",
    "governance_freshness_evidence_hash": "f0ebf561cb530d9f9a0535d02f3f563fc73b1a8568410f682f61001dc325b32c",
}


def decision(verdict="PASS"):
    return {
        "schema_version": "stegcore.independent-release-policy.v1",
        "decision_id": "release-policy-001",
        "policy_version": "1",
        "authority_ref": "repo-policy:issue-37",
        "repository": "StegVerse-Labs/StegCore",
        "candidate_commit": READINESS["stegcore_commit"],
        "release_readiness_assessment_hash": READINESS["assessment_hash"],
        "runtime_evidence_hash": READINESS["runtime_evidence_hash"],
        "governance_freshness_evidence_hash": READINESS["governance_freshness_evidence_hash"],
        "verdict": verdict,
        "issued_at": "2026-08-08T15:00:00Z",
        "expires_at": "2026-08-09T15:00:00Z",
    }


def test_exact_pass_binding():
    result = validate(decision(), READINESS, now=NOW)
    assert result["status"] == "PASS"
    assert result["exact_candidate_binding"] is True
    assert result["release_authority_created"] is False


def test_deny_does_not_open_gate():
    result = validate(decision("DENY"), READINESS, now=NOW)
    assert result["status"] == "BLOCKED"
    assert result["release_policy_gate"] == "pending_or_denied"


def test_candidate_mismatch_fails_closed():
    value = decision()
    value["candidate_commit"] = "0" * 40
    result = validate(value, READINESS, now=NOW)
    assert result["status"] == "BLOCKED"
    assert "binding_mismatch:candidate_commit" in result["errors"]


def test_assessment_mismatch_fails_closed():
    value = decision()
    value["release_readiness_assessment_hash"] = "0" * 64
    result = validate(value, READINESS, now=NOW)
    assert result["status"] == "BLOCKED"
    assert "binding_mismatch:release_readiness_assessment_hash" in result["errors"]


def test_expired_decision_fails_closed():
    value = decision()
    value["expires_at"] = "2026-08-08T15:30:00Z"
    result = validate(value, READINESS, now=NOW)
    assert result["status"] == "BLOCKED"
    assert "decision_expired" in result["errors"]


def test_future_decision_fails_closed():
    value = decision()
    value["issued_at"] = "2026-08-08T17:00:00Z"
    value["expires_at"] = "2026-08-09T17:00:00Z"
    result = validate(value, READINESS, now=NOW)
    assert result["status"] == "BLOCKED"
    assert "decision_not_yet_valid" in result["errors"]
