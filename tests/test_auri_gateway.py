from __future__ import annotations

from stegc​​ore.auri_gateway import canonical_sha256, evaluate_auri_candidate
from stegc​​ore.decision import VerifiedReceiptEnvelope


def candidate(consequential: bool = False):
    return {
        "schema_version": "1.0.0",
        "candidate_id": "auri:test",
        "prepared_by": "stegverse:auri",
        "action": "prepare_repository_change",
        "target": "StegVerse-Labs/StegTalk",
        "scope": "advisory_only",
        "policy_ref": "policy:test" if consequential else None,
        "delegation_ref": "delegation:test" if consequential else None,
        "execution_context": {"consequential": consequential},
        "auri_posture": {
            "execution_authority": False,
            "final_consequence_authority": False,
            "requires_external_admissibility": True,
        },
    }


def receipt():
    return VerifiedReceiptEnvelope(
        receipt_id="receipt:test",
        key_id="key:test",
        verified=True,
        issued_at="2026-07-14T00:00:00Z",
    )


def test_valid_advisory_candidate_allows_without_execution():
    value = candidate()
    result = evaluate_auri_candidate(value, verified_receipt=receipt())
    assert result.decision == "allow"
    assert result.execution_performed is False
    assert result.receipt["execution_performed"] is False


def test_missing_verified_receipt_denies():
    result = evaluate_auri_candidate(candidate(), verified_receipt=None)
    assert result.decision == "deny"
    assert result.reason_code == "receipt.missing"


def test_consequential_candidate_requires_policy_and_delegation():
    value = candidate(True)
    value["delegation_ref"] = None
    result = evaluate_auri_candidate(value, verified_receipt=receipt())
    assert result.decision == "deny"
    assert result.reason_code == "delegation.missing"


def test_policy_shape_can_defer():
    result = evaluate_auri_candidate(candidate(), verified_receipt=receipt(), policy_shapes=["guardian"])
    assert result.decision == "defer"
    assert result.reason_code == "requires.guardian"


def test_commit_time_hash_mismatch_denies():
    value = candidate()
    result = evaluate_auri_candidate(
        value,
        verified_receipt=receipt(),
        commit_candidate_sha256="0" * 64,
    )
    assert result.decision == "deny"
    assert result.reason_code == "commit.candidate_hash_mismatch"
    assert result.candidate_sha256 == canonical_sha256(value)


def test_auri_cannot_claim_execution_authority():
    value = candidate()
    value["auri_posture"]["execution_authority"] = True
    result = evaluate_auri_candidate(value, verified_receipt=receipt())
    assert result.decision == "deny"
    assert result.reason_code == "auri.execution_authority.forbidden"
