from __future__ import annotations

"""Fail-closed external evidence envelope interoperability.

External telemetry, attestation, and verification providers produce evidence only.
This module maps a Governance 1.0 evidence envelope into the existing three-layer
commit-time evaluator without granting the provider execution authority or minting
a Continuity receipt.
"""

from dataclasses import dataclass
from typing import Any, Literal, Mapping

from .three_layer import (
    ExecutionBoundary,
    JudgmentConditions,
    SignalAdmission,
    ThreeLayerRequest,
    ThreeLayerResult,
    evaluate_three_layer,
)

ExternalDecision = Literal["ALLOW", "DENY", "FAIL-CLOSED"]


@dataclass(frozen=True)
class ExternalEvidenceResult:
    artifact_type: Literal["stegcore.external_evidence_admissibility"]
    decision: ExternalDecision
    reason_code: str
    provider_id: str
    envelope_id: str
    commitment_candidate_id: str
    three_layer_result: ThreeLayerResult | None
    receipt: Mapping[str, Any]


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _base_receipt(
    envelope: Mapping[str, Any], decision: ExternalDecision, reason_code: str
) -> dict[str, Any]:
    provider = _mapping(envelope.get("provider"))
    candidate = _mapping(envelope.get("commitment_candidate"))
    return {
        "artifact_type": "stegcore.external_evidence_admissibility_receipt",
        "external_evidence_envelope_version": envelope.get("external_evidence_envelope_version"),
        "envelope_id": envelope.get("envelope_id", ""),
        "provider_id": provider.get("provider_id", ""),
        "commitment_candidate_id": candidate.get("candidate_id", ""),
        "decision": decision,
        "reason_code": reason_code,
        "evidence_provider_execution_authority": False,
        "continuity_receipt_minted": False,
    }


def _result(
    envelope: Mapping[str, Any],
    decision: ExternalDecision,
    reason_code: str,
    three_layer_result: ThreeLayerResult | None = None,
) -> ExternalEvidenceResult:
    receipt = _base_receipt(envelope, decision, reason_code)
    if three_layer_result is not None:
        receipt["three_layer_request_hash"] = three_layer_result.request_hash
        receipt["three_layer_receipt_hash"] = three_layer_result.receipt.get("receipt_hash")
    provider = _mapping(envelope.get("provider"))
    candidate = _mapping(envelope.get("commitment_candidate"))
    return ExternalEvidenceResult(
        artifact_type="stegcore.external_evidence_admissibility",
        decision=decision,
        reason_code=reason_code,
        provider_id=str(provider.get("provider_id", "")),
        envelope_id=str(envelope.get("envelope_id", "")),
        commitment_candidate_id=str(candidate.get("candidate_id", "")),
        three_layer_result=three_layer_result,
        receipt=receipt,
    )


def _complete(envelope: Mapping[str, Any]) -> bool:
    provider = _mapping(envelope.get("provider"))
    subject = _mapping(envelope.get("subject"))
    capture = _mapping(envelope.get("capture"))
    integrity = _mapping(envelope.get("integrity"))
    candidate = _mapping(envelope.get("commitment_candidate"))
    claims = envelope.get("claims")
    evidence_refs = envelope.get("evidence_refs")
    required_strings = (
        envelope.get("envelope_id"),
        provider.get("provider_id"),
        provider.get("public_key_ref"),
        subject.get("actor_ref"),
        subject.get("target_ref"),
        capture.get("execution_context"),
        capture.get("reference_state_hash"),
        integrity.get("content_digest"),
        integrity.get("signature_algorithm"),
        integrity.get("signature"),
        envelope.get("prior_hash"),
        candidate.get("candidate_id"),
        candidate.get("actor_ref"),
        candidate.get("target_ref"),
        candidate.get("scope"),
        candidate.get("action"),
        candidate.get("policy_ref"),
        candidate.get("delegation_ref"),
        candidate.get("consent_ref"),
        candidate.get("identity_ref"),
        candidate.get("reference_state_hash"),
        candidate.get("authorized_reference_state_hash"),
        candidate.get("provider_authorization_ref"),
    )
    return (
        all(_nonempty(value) for value in required_strings)
        and isinstance(claims, list)
        and bool(claims)
        and isinstance(evidence_refs, list)
        and bool(evidence_refs)
        and isinstance(candidate.get("evidence_refs"), list)
        and bool(candidate.get("evidence_refs"))
        and isinstance(candidate.get("evidence_digests"), list)
        and bool(candidate.get("evidence_digests"))
        and integrity.get("chain_valid") is True
        and candidate.get("evidence_provider_execution_authority") is False
    )


def request_from_external_evidence(envelope: Mapping[str, Any]) -> ThreeLayerRequest:
    """Map a structurally valid envelope into the existing commit-time evaluator."""

    candidate = _mapping(envelope.get("commitment_candidate"))
    subject = _mapping(envelope.get("subject"))
    capture = _mapping(envelope.get("capture"))
    freshness = _mapping(envelope.get("freshness"))
    claims = envelope.get("claims", [])
    evidence_refs = tuple(str(item) for item in envelope.get("evidence_refs", []))
    claim_refs = tuple(
        str(_mapping(claim).get("evidence_digest"))
        for claim in claims
        if _nonempty(_mapping(claim).get("evidence_digest"))
    )
    recoverability = candidate.get("recoverability_profile")
    recoverability_profile = {
        "operator_recoverable": "recoverable",
        "recoverable": "recoverable",
        "constrained": "constrained",
        "irreversible": "irreversible",
    }.get(recoverability, "unknown")

    validity_open = (
        freshness.get("is_current") is True
        and isinstance(freshness.get("valid_from"), int)
        and isinstance(freshness.get("valid_until"), int)
        and isinstance(freshness.get("evaluated_at"), int)
        and freshness["valid_from"] <= freshness["evaluated_at"] <= freshness["valid_until"]
    )

    return ThreeLayerRequest(
        judgment_conditions=JudgmentConditions(
            refusal_available=True,
            operator_recoverability="available",
            workload_state="supported",
            time_pressure="normal",
            isolation_state="supported",
            evidence_refs=evidence_refs,
        ),
        signal_admission=SignalAdmission(
            admitted_signal_refs=claim_refs,
            transformations=("external_evidence_envelope:v1.0",),
            missing_inputs=(),
            uncertainty_state="bounded",
            reference_state_hash=str(candidate.get("reference_state_hash", capture.get("reference_state_hash", ""))),
            expected_reference_state_hash=str(candidate.get("authorized_reference_state_hash", "")),
            reconstruction_available=True,
            transformation_provenance_complete=True,
        ),
        execution_boundary=ExecutionBoundary(
            actor_authority_current=bool(candidate.get("identity_ref")),
            policy_current=bool(candidate.get("policy_ref")),
            delegation_current=bool(candidate.get("delegation_ref")),
            evidence_current=validity_open,
            affected_entity_conditions_represented=bool(subject.get("target_ref")),
            recoverability_profile=recoverability_profile,
            validity_window_open=validity_open,
            policy_ref=str(candidate.get("policy_ref", "")),
            delegation_ref=str(candidate.get("delegation_ref", "")),
            evidence_refs=evidence_refs,
        ),
        action=str(candidate.get("action", "")),
        target=str(candidate.get("target_ref", "")),
        scope=str(candidate.get("scope", "")),
    )


def evaluate_external_evidence(envelope: Mapping[str, Any]) -> ExternalEvidenceResult:
    """Evaluate a Governance external evidence envelope in fail-closed order."""

    if envelope.get("external_evidence_envelope_version") != "1.0":
        return _result(envelope, "DENY", "evidence.incomplete")
    if not _complete(envelope):
        return _result(envelope, "DENY", "evidence.incomplete")

    authorization = _mapping(envelope.get("authorization"))
    if authorization.get("provider_authorized") is not True or authorization.get("scope_match") is not True:
        return _result(envelope, "DENY", "evidence.provider_unauthorized")

    freshness = _mapping(envelope.get("freshness"))
    if freshness.get("is_current") is not True:
        return _result(envelope, "DENY", "evidence.stale")

    candidate = _mapping(envelope.get("commitment_candidate"))
    if candidate.get("evidence_provider_execution_authority") is not False:
        return _result(envelope, "DENY", "evidence.provider_authority_forbidden")

    request = request_from_external_evidence(envelope)
    runtime_result = evaluate_three_layer(request)
    reason_code = runtime_result.reason_code
    if reason_code == "signal.reference_state_discontinuous":
        reason_code = "evidence.reference_state_drift"
    return _result(envelope, runtime_result.decision, reason_code, runtime_result)
