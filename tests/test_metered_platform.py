from stegcore.metered_platform import (
    REQUIRED_RETIREMENT_GATES,
    evaluate_metered_platform,
    verify_metered_platform_receipt,
)


def test_replacement_selection_allows_design_only():
    candidate = {"scope": "REPLACEMENT_DESIGN_ONLY", "provider": "render", "evidence": {}}
    receipt = evaluate_metered_platform(candidate)
    assert receipt["result"] == "ALLOW"
    assert receipt["reason_code"] == "replacement.selection_allowed"
    assert receipt["provider_retirement_authority"] is False
    assert receipt["cancellation_authority"] is False
    assert receipt["continuity_receipt_minted"] is False
    assert verify_metered_platform_receipt(candidate, receipt)


def test_retirement_denied_when_any_gate_missing():
    evidence = {gate: True for gate in REQUIRED_RETIREMENT_GATES}
    evidence["rollback_verified"] = False
    candidate = {"scope": "PROVIDER_RETIREMENT", "provider": "render", "evidence": evidence}
    receipt = evaluate_metered_platform(candidate)
    assert receipt["result"] == "DENY"
    assert receipt["reason_code"] == "retirement.evidence_incomplete"
    assert receipt["missing_retirement_gates"] == ["rollback_verified"]


def test_retirement_complete_still_grants_no_execution_authority():
    candidate = {
        "scope": "PROVIDER_RETIREMENT",
        "provider": "render",
        "evidence": {gate: True for gate in REQUIRED_RETIREMENT_GATES},
    }
    receipt = evaluate_metered_platform(candidate)
    assert receipt["result"] == "ALLOW"
    assert receipt["reason_code"] == "retirement.evidence_complete"
    assert receipt["provider_retirement_authority"] is False
    assert receipt["cancellation_authority"] is False


def test_invalid_scope_fails_closed():
    receipt = evaluate_metered_platform({"scope": "DELETE_PROVIDER", "evidence": {}})
    assert receipt["result"] == "DENY"
    assert receipt["reason_code"] == "replacement.scope_invalid"


def test_mutated_receipt_fails_replay_verification():
    candidate = {"scope": "REPLACEMENT_DESIGN_ONLY", "provider": "github", "evidence": {}}
    receipt = evaluate_metered_platform(candidate)
    receipt["result"] = "DENY"
    assert verify_metered_platform_receipt(candidate, receipt) is False
