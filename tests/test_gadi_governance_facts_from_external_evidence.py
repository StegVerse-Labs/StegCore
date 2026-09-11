from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.materialize_gadi_governance_facts_from_external_evidence import (
    GADIExternalEvidenceFactsError,
    GADI_ACTION,
    GADI_POLICY,
    GADI_SCOPE,
    GADI_TARGET,
    VERIFIED_BINDING_SCHEMA,
    canonical_envelope_hash,
    resolved_facts_from_external_evidence,
)

FIXTURE = Path("contracts/governance_external_evidence_snapshot/docs/examples/interop/external_evidence_valid.json")


def envelope() -> dict:
    value = json.loads(FIXTURE.read_text(encoding="utf-8"))
    value["subject"]["target_ref"] = GADI_TARGET
    candidate = value["commitment_candidate"]
    candidate["target_ref"] = GADI_TARGET
    candidate["scope"] = GADI_SCOPE
    candidate["action"] = GADI_ACTION
    candidate["policy_ref"] = GADI_POLICY
    return value


def binding(value: dict | None = None, **overrides) -> dict:
    value = value or envelope()
    payload = {
        "schema": VERIFIED_BINDING_SCHEMA,
        "task_id": "GADI-001",
        "envelope_hash": canonical_envelope_hash(value),
        "provider_id": value["provider"]["provider_id"],
        "public_key_ref": value["provider"]["public_key_ref"],
        "content_digest": value["integrity"]["content_digest"],
        "authorization_ref": value["authorization"]["authorization_ref"],
        "signature_verified": True,
        "chain_verified": True,
        "provider_authorized": True,
        "scope_match": True,
        "freshness_verified": True,
        "verification_receipt_ref": "verification://gadi/ext-evidence/test-001",
        "verifier_authority_ref": "authority://external-evidence-verifier/test-001",
        "execution_authority_granted": False,
        "authority_effect": "NONE_EVIDENCE_VERIFICATION_ONLY",
    }
    payload.update(overrides)
    return payload


def test_valid_verified_external_evidence_projects_exact_three_layer_facts():
    value = envelope()
    result = resolved_facts_from_external_evidence(value, binding(value))
    facts = result["resolved_governance_facts"]
    assert result["state"] == "RESOLVED_GOVERNANCE_FACTS_PROJECTED_FROM_VERIFIED_EVIDENCE"
    assert set(facts) == {"judgment_conditions", "signal_admission", "execution_boundary"}
    assert facts["execution_boundary"]["policy_ref"] == GADI_POLICY
    assert facts["execution_boundary"]["actor_authority_current"] is True
    assert facts["execution_boundary"]["policy_current"] is True
    assert facts["execution_boundary"]["delegation_current"] is True
    assert facts["execution_boundary"]["evidence_current"] is True
    assert facts["signal_admission"]["reference_state_hash"] == facts["signal_admission"]["expected_reference_state_hash"]
    assert result["external_evidence_envelope_created"] is False
    assert result["external_evidence_verified_by_projector"] is False
    assert result["verified_binding_created"] is False
    assert result["resolved_governance_facts_invented"] is False
    assert result["intr_transport_performed"] is False
    assert result["gadi_admission_created"] is False
    assert result["runtime_binding_created"] is False
    assert result["claim_or_fence_minted"] is False
    assert result["execution_authority_granted"] is False
    assert result["authority_effect"] == "NONE_FACT_PROJECTION_ONLY"


def test_envelope_self_assertion_is_insufficient_without_verified_binding():
    value = envelope()
    with pytest.raises(TypeError):
        resolved_facts_from_external_evidence(value)  # type: ignore[call-arg]


def test_binding_envelope_hash_mismatch_is_rejected():
    value = envelope()
    with pytest.raises(GADIExternalEvidenceFactsError, match="envelope hash mismatch"):
        resolved_facts_from_external_evidence(value, binding(value, envelope_hash="sha256:" + "0" * 64))


def test_binding_provider_or_key_mismatch_is_rejected():
    value = envelope()
    with pytest.raises(GADIExternalEvidenceFactsError, match="provider mismatch"):
        resolved_facts_from_external_evidence(value, binding(value, provider_id="provider.other"))
    with pytest.raises(GADIExternalEvidenceFactsError, match="public key mismatch"):
        resolved_facts_from_external_evidence(value, binding(value, public_key_ref="keys/other"))


def test_unverified_signature_chain_authorization_scope_or_freshness_is_rejected():
    value = envelope()
    for field, message in (
        ("signature_verified", "signature not independently verified"),
        ("chain_verified", "chain not independently verified"),
        ("provider_authorized", "provider not independently authorized"),
        ("scope_match", "scope not independently verified"),
        ("freshness_verified", "freshness not independently verified"),
    ):
        with pytest.raises(GADIExternalEvidenceFactsError, match=message):
            resolved_facts_from_external_evidence(value, binding(value, **{field: False}))


def test_stale_envelope_is_rejected_even_if_binding_claims_freshness():
    value = envelope()
    value["freshness"]["is_current"] = False
    with pytest.raises(GADIExternalEvidenceFactsError, match="envelope freshness posture mismatch"):
        resolved_facts_from_external_evidence(value, binding(value))


def test_unauthorized_envelope_is_rejected_even_if_binding_claims_authorization():
    value = envelope()
    value["authorization"]["provider_authorized"] = False
    with pytest.raises(GADIExternalEvidenceFactsError, match="envelope provider posture mismatch"):
        resolved_facts_from_external_evidence(value, binding(value))


def test_provider_cannot_claim_execution_authority():
    value = envelope()
    value["commitment_candidate"]["evidence_provider_execution_authority"] = True
    with pytest.raises(GADIExternalEvidenceFactsError, match="provider authority forbidden"):
        resolved_facts_from_external_evidence(value, binding(value))


def test_verified_binding_cannot_claim_execution_authority():
    value = envelope()
    with pytest.raises(GADIExternalEvidenceFactsError, match="may not grant execution authority"):
        resolved_facts_from_external_evidence(value, binding(value, execution_authority_granted=True))


def test_wrong_gadi_policy_is_rejected_before_projection():
    value = envelope()
    value["commitment_candidate"]["policy_ref"] = "policy:wrong"
    with pytest.raises(GADIExternalEvidenceFactsError, match="policy mismatch"):
        resolved_facts_from_external_evidence(value, binding(value))


def test_wrong_gadi_target_is_rejected_before_projection():
    value = envelope()
    value["commitment_candidate"]["target_ref"] = "other-system"
    with pytest.raises(GADIExternalEvidenceFactsError, match="target mismatch"):
        resolved_facts_from_external_evidence(value, binding(value))


def test_valid_but_reference_drift_may_project_denial_facts_without_authority():
    value = envelope()
    value["commitment_candidate"]["reference_state_hash"] = "sha256:state-drifted"
    result = resolved_facts_from_external_evidence(value, binding(value))
    assert result["external_evidence_decision"] in {"DENY", "FAIL-CLOSED"}
    assert result["resolved_governance_facts"]["signal_admission"]["reference_state_hash"] == "sha256:state-drifted"
    assert result["execution_authority_granted"] is False
