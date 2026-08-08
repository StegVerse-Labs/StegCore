from scripts.validate_independent_release_policy import validate

READINESS = {
    "stegcore_commit": "70bbb0eb8a5dec4f27ee7aca5cf09cdb17a924af",
}


def evidence():
    return {
        "artifact_type": "stegcore.independent_release_policy_evidence",
        "schema_version": "1.0",
        "status": "pass",
        "decision": "ALLOW",
        "policy_id": "stegcore-release-policy-v1",
        "decision_owner": "StegVerse-Labs/Governance",
        "source_repository": "StegVerse-Labs/Governance",
        "source_commit": "d12cfbfec733f601dcf4a97ccf74d0140bfe5f52",
        "source_path": "evidence/stegcore-release-decision.json",
        "decision_hash": "7b90b85d4c9a4fe0666dd72a13dd1e26e672d5cd57aa88ad98b4ac08a23e768c",
        "candidate_version": "0.1.0",
        "candidate_tag": "v0.1.0",
        "candidate_commit": READINESS["stegcore_commit"],
        "next_permitted_action": "create annotated tag only",
        "release_created": False,
        "tag_created": False,
        "deployment_authorized": False,
        "continuity_receipt_minted": False,
    }


def test_current_governance_allow_opens_only_policy_gate():
    result = validate(evidence(), READINESS)
    assert result["status"] == "PASS"
    assert result["release_policy_gate"] == "pass"
    assert result["next_permitted_action"] == "create annotated tag only"
    assert result["release_authority_created"] is False
    assert result["tag_authority_created"] is False


def test_candidate_mismatch_fails_closed():
    value = evidence()
    value["candidate_commit"] = "0" * 40
    result = validate(value, READINESS)
    assert result["status"] == "BLOCKED"
    assert "candidate_binding" in result["errors"]


def test_deny_fails_closed():
    value = evidence()
    value["decision"] = "DENY"
    result = validate(value, READINESS)
    assert result["status"] == "BLOCKED"
    assert "decision_allow" in result["errors"]


def test_unbounded_next_action_fails_closed():
    value = evidence()
    value["next_permitted_action"] = "deploy production"
    result = validate(value, READINESS)
    assert result["status"] == "BLOCKED"
    assert "next_action_bounded" in result["errors"]


def test_already_created_tag_is_not_reusable_authority():
    value = evidence()
    value["tag_created"] = True
    result = validate(value, READINESS)
    assert result["status"] == "BLOCKED"
    assert "tag_not_created" in result["errors"]


def test_non_governance_owner_fails_closed():
    value = evidence()
    value["decision_owner"] = "unknown"
    result = validate(value, READINESS)
    assert result["status"] == "BLOCKED"
    assert "decision_owner" in result["errors"]
