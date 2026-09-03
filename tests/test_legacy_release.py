import pytest

from stegcore.legacy_release import LegacyReleaseError, evaluate_legacy_release


def base_facts():
    return {
        "transition_id": "LEGACY-TRANSITION-001",
        "capsule_id": "LEGACY-CAPSULE-001",
        "recipient_identity_id": "stegid:recipient:001",
        "requested_transition": "DISCLOSE_CAPSULE",
        "recipient_identity_verified": True,
        "participation_required": True,
        "participation_qualified": True,
        "release_trigger_verified": True,
        "tvc_authorization_verified": True,
        "participant_policy_current": True,
        "delegation_current": True,
        "evidence_current": True,
        "reconstruction_available": True,
        "transformation_provenance_complete": True,
        "affected_recipient_conditions_represented": True,
        "validity_window_open": True,
        "recipient_refusal_available": True,
        "operator_recoverability": "available",
        "workload_state": "supported",
        "time_pressure": "normal",
        "isolation_state": "supported",
        "uncertainty_state": "bounded",
        "recoverability_profile": "recoverable",
        "reference_state_hash": "state:abc",
        "expected_reference_state_hash": "state:abc",
        "policy_ref": "kv://personal/legacy/policies/001",
        "delegation_ref": "tvc://legacy/release/001",
        "evidence_refs": [
            "stegid://legacy-recipient/001",
            "continuity://legacy-trigger/001",
            "tvc://legacy-authorization/001",
        ],
    }


def test_valid_legacy_transition_uses_canonical_evaluator():
    result = evaluate_legacy_release(base_facts())
    assert result["decision"] == "ALLOW"
    assert result["canonical_runtime"] == "stegcore.three_layer.evaluate_three_layer"
    assert result["disclosure_authority_granted"] is False
    assert result["economic_transfer_authority_granted"] is False
    assert result["external_execution_performed"] is False


def test_participation_required_fails_closed_when_not_qualified():
    facts = base_facts()
    facts["participation_qualified"] = False
    with pytest.raises(LegacyReleaseError):
        evaluate_legacy_release(facts)


def test_missing_tvc_authorization_fails_closed():
    facts = base_facts()
    facts["tvc_authorization_verified"] = False
    with pytest.raises(LegacyReleaseError):
        evaluate_legacy_release(facts)


def test_reference_state_discontinuity_is_fail_closed_by_canonical_runtime():
    facts = base_facts()
    facts["expected_reference_state_hash"] = "state:different"
    result = evaluate_legacy_release(facts)
    assert result["decision"] == "FAIL-CLOSED"
    assert result["reason_code"] == "signal.reference_state_discontinuous"


def test_recipient_can_refuse_disclosure():
    facts = base_facts()
    facts["recipient_refusal_available"] = False
    result = evaluate_legacy_release(facts)
    assert result["decision"] == "DENY"
    assert result["reason_code"] == "judgment.refusal_unavailable"


def test_economic_release_is_only_admissibility_not_transfer():
    facts = base_facts()
    facts["requested_transition"] = "REQUEST_ECONOMIC_RELEASE"
    result = evaluate_legacy_release(facts)
    assert result["decision"] == "ALLOW"
    assert result["economic_transfer_authority_granted"] is False
    assert result["external_execution_performed"] is False
