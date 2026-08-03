from __future__ import annotations

from copy import deepcopy

from stegcore.external_evidence import evaluate_external_evidence


def valid_envelope():
    return {
        "external_evidence_envelope_version": "1.0",
        "envelope_id": "ext-evidence-valid-001",
        "provider": {
            "provider_id": "provider.demo.telemetry",
            "provider_type": "composite",
            "public_key_ref": "keys/provider-demo-ed25519",
            "declared_scope": ["runtime.telemetry", "gate.verification"],
        },
        "subject": {
            "actor_ref": "actor/alice",
            "target_ref": "runtime/service-a",
            "workload_ref": "run/001",
        },
        "capture": {
            "started_at": 100,
            "ended_at": 160,
            "execution_context": "prod-us-central-1",
            "reference_state_hash": "sha256:state-authorized",
        },
        "claims": [
            {
                "claim_id": "claim-001",
                "claim_type": "runtime.policy_conformance",
                "value": True,
                "evidence_digest": "sha256:evidence-valid",
            }
        ],
        "integrity": {
            "content_digest": "sha256:envelope-valid",
            "signature_algorithm": "Ed25519",
            "signature": "base64url:demo-valid",
            "chain_valid": True,
        },
        "authorization": {
            "provider_authorized": True,
            "authorization_ref": "provider-auth/v1",
            "scope_match": True,
        },
        "freshness": {"valid_from": 100, "valid_until": 500, "evaluated_at": 200, "is_current": True},
        "evidence_refs": ["evidence/runtime-valid-001"],
        "prior_hash": "sha256:prior-valid",
        "issued_at": 161,
        "commitment_candidate": {
            "candidate_id": "candidate-valid-001",
            "actor_ref": "actor/alice",
            "target_ref": "runtime/service-a",
            "scope": "runtime.execute",
            "action": "apply_config",
            "execution_context": "prod-us-central-1",
            "policy_ref": "policy/runtime/v1",
            "delegation_ref": "delegation/alice/v1",
            "consent_ref": "consent/owner/v1",
            "identity_ref": "identity/alice/v3",
            "evidence_refs": ["evidence/runtime-valid-001"],
            "evidence_digests": ["sha256:evidence-valid"],
            "capture_interval": {"started_at": 100, "ended_at": 160},
            "prior_hash": "sha256:prior-valid",
            "validity_window": {"valid_from": 100, "valid_until": 500},
            "reference_state_hash": "sha256:state-authorized",
            "authorized_reference_state_hash": "sha256:state-authorized",
            "recoverability_profile": "operator_recoverable",
            "provider_authorization_ref": "provider-auth/v1",
            "evidence_provider_execution_authority": False,
        },
    }


def assert_boundaries(result):
    assert result.receipt["continuity_receipt_minted"] is False
    assert result.receipt["evidence_provider_execution_authority"] is False


def test_valid_evidence_allows():
    result = evaluate_external_evidence(valid_envelope())
    assert (result.decision, result.reason_code) == ("ALLOW", "ok")
    assert_boundaries(result)


def test_stale_evidence_denies():
    envelope = valid_envelope()
    envelope["freshness"]["is_current"] = False
    result = evaluate_external_evidence(envelope)
    assert (result.decision, result.reason_code) == ("DENY", "evidence.stale")
    assert_boundaries(result)


def test_reference_state_drift_fails_closed():
    envelope = valid_envelope()
    envelope["commitment_candidate"]["reference_state_hash"] = "sha256:state-drifted"
    result = evaluate_external_evidence(envelope)
    assert (result.decision, result.reason_code) == ("FAIL-CLOSED", "evidence.reference_state_drift")
    assert_boundaries(result)


def test_incomplete_evidence_denies():
    envelope = valid_envelope()
    envelope["claims"] = []
    envelope["evidence_refs"] = []
    result = evaluate_external_evidence(envelope)
    assert (result.decision, result.reason_code) == ("DENY", "evidence.incomplete")
    assert_boundaries(result)


def test_unauthorized_provider_denies():
    envelope = valid_envelope()
    envelope["authorization"] = {
        "provider_authorized": False,
        "authorization_ref": "provider-auth/missing",
        "scope_match": False,
    }
    result = evaluate_external_evidence(envelope)
    assert (result.decision, result.reason_code) == ("DENY", "evidence.provider_unauthorized")
    assert_boundaries(result)


def test_provider_cannot_claim_execution_authority():
    envelope = deepcopy(valid_envelope())
    envelope["commitment_candidate"]["evidence_provider_execution_authority"] = True
    result = evaluate_external_evidence(envelope)
    assert result.decision == "DENY"
    assert result.reason_code in {"evidence.incomplete", "evidence.provider_authority_forbidden"}
    assert_boundaries(result)
