from __future__ import annotations

from typing import Any, Mapping

from .three_layer import (
    ExecutionBoundary,
    JudgmentConditions,
    SignalAdmission,
    ThreeLayerRequest,
    evaluate_three_layer,
)

LEGACY_RELEASE_SCHEMA = "stegverse.stegcore.legacy_release_admissibility.v1"

_ALLOWED_TRANSITIONS = {
    "DISCLOSE_CAPSULE",
    "DISCLOSE_ORIGINATOR",
    "DISCLOSE_ASSET_CLASS",
    "DISCLOSE_TERMS",
    "RELEASE_PAYLOAD",
    "REQUEST_ECONOMIC_RELEASE",
}
_ALLOWED_OPERATOR_RECOVERABILITY = {"available", "degraded", "unavailable", "unknown"}
_ALLOWED_WORKLOAD = {"supported", "elevated", "overloaded", "unknown"}
_ALLOWED_TIME_PRESSURE = {"normal", "elevated", "critical", "unknown"}
_ALLOWED_ISOLATION = {"supported", "isolated", "unknown"}
_ALLOWED_UNCERTAINTY = {"bounded", "material", "unknown"}
_ALLOWED_RECOVERABILITY = {"recoverable", "constrained", "irreversible", "unknown"}


class LegacyReleaseError(ValueError):
    pass


def _require_bool(facts: Mapping[str, Any], key: str) -> bool:
    if facts.get(key) is not True:
        raise LegacyReleaseError(f"required predicate not satisfied: {key}")
    return True


def _enum(facts: Mapping[str, Any], key: str, default: str, allowed: set[str]) -> str:
    value = str(facts.get(key, default)).strip()
    if value not in allowed:
        raise LegacyReleaseError(f"invalid {key}: {value}")
    return value


def evaluate_legacy_release(facts: Mapping[str, Any]) -> dict[str, Any]:
    """Translate resolved legacy facts into canonical three-layer admissibility.

    This function does not create a second evaluator. It validates the legacy
    request shape, derives one ThreeLayerRequest, and delegates the decision to
    evaluate_three_layer().
    """

    if not isinstance(facts, Mapping):
        raise LegacyReleaseError("facts must be a mapping")

    transition_id = str(facts.get("transition_id", "")).strip()
    capsule_id = str(facts.get("capsule_id", "")).strip()
    recipient_identity_id = str(facts.get("recipient_identity_id", "")).strip()
    policy_ref = str(facts.get("policy_ref", "")).strip()
    delegation_ref = str(facts.get("delegation_ref", "")).strip()
    reference_state_hash = str(facts.get("reference_state_hash", "")).strip()
    expected_reference_state_hash = str(facts.get("expected_reference_state_hash", "")).strip()
    requested_transition = str(facts.get("requested_transition", "")).strip().upper()

    if not all((transition_id, capsule_id, recipient_identity_id, policy_ref, delegation_ref)):
        raise LegacyReleaseError("transition, capsule, recipient, policy, and delegation references are required")
    if requested_transition not in _ALLOWED_TRANSITIONS:
        raise LegacyReleaseError("unsupported legacy transition")

    _require_bool(facts, "recipient_identity_verified")
    if facts.get("participation_required", False):
        _require_bool(facts, "participation_qualified")
    _require_bool(facts, "release_trigger_verified")
    _require_bool(facts, "tvc_authorization_verified")
    _require_bool(facts, "participant_policy_current")
    _require_bool(facts, "evidence_current")
    _require_bool(facts, "reconstruction_available")
    _require_bool(facts, "transformation_provenance_complete")
    _require_bool(facts, "affected_recipient_conditions_represented")
    _require_bool(facts, "validity_window_open")

    evidence_refs = tuple(str(x) for x in facts.get("evidence_refs", ()) if str(x).strip())
    if not evidence_refs:
        raise LegacyReleaseError("at least one evidence reference is required")

    operator_recoverability = _enum(
        facts, "operator_recoverability", "available", _ALLOWED_OPERATOR_RECOVERABILITY
    )
    workload_state = _enum(facts, "workload_state", "supported", _ALLOWED_WORKLOAD)
    time_pressure = _enum(facts, "time_pressure", "normal", _ALLOWED_TIME_PRESSURE)
    isolation_state = _enum(facts, "isolation_state", "supported", _ALLOWED_ISOLATION)
    uncertainty_state = _enum(facts, "uncertainty_state", "bounded", _ALLOWED_UNCERTAINTY)
    recoverability_profile = _enum(
        facts, "recoverability_profile", "recoverable", _ALLOWED_RECOVERABILITY
    )

    request = ThreeLayerRequest(
        judgment_conditions=JudgmentConditions(
            refusal_available=bool(facts.get("recipient_refusal_available", True)),
            operator_recoverability=operator_recoverability,
            workload_state=workload_state,
            time_pressure=time_pressure,
            isolation_state=isolation_state,
            evidence_refs=evidence_refs,
        ),
        signal_admission=SignalAdmission(
            admitted_signal_refs=evidence_refs,
            excluded_signal_refs=tuple(str(x) for x in facts.get("excluded_signal_refs", ())),
            transformations=tuple(str(x) for x in facts.get("transformations", ())),
            missing_inputs=tuple(str(x) for x in facts.get("missing_inputs", ())),
            uncertainty_state=uncertainty_state,
            reference_state_hash=reference_state_hash,
            expected_reference_state_hash=expected_reference_state_hash,
            reconstruction_available=True,
            transformation_provenance_complete=True,
        ),
        execution_boundary=ExecutionBoundary(
            actor_authority_current=True,
            policy_current=True,
            delegation_current=bool(facts.get("delegation_current", True)),
            evidence_current=True,
            affected_entity_conditions_represented=True,
            recoverability_profile=recoverability_profile,
            validity_window_open=True,
            policy_ref=policy_ref,
            delegation_ref=delegation_ref,
            evidence_refs=evidence_refs,
        ),
        action=requested_transition,
        target=f"legacy:{capsule_id}:recipient:{recipient_identity_id}",
        scope="legacy_continuity",
    )

    result = evaluate_three_layer(request)
    return {
        "schema": LEGACY_RELEASE_SCHEMA,
        "transition_id": transition_id,
        "capsule_id": capsule_id,
        "recipient_identity_id": recipient_identity_id,
        "requested_transition": requested_transition,
        "decision": result.decision,
        "reason_code": result.reason_code,
        "canonical_runtime": "stegcore.three_layer.evaluate_three_layer",
        "canonical_request_hash": result.request_hash,
        "canonical_receipt": dict(result.receipt),
        "disclosure_authority_granted": False,
        "economic_transfer_authority_granted": False,
        "external_execution_performed": False,
        "authority_effect": "NONE",
    }


__all__ = ["LEGACY_RELEASE_SCHEMA", "LegacyReleaseError", "evaluate_legacy_release"]
