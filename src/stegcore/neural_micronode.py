from __future__ import annotations

"""Adapter-neutral governance boundary for addressed neural micro-nodes.

This module does not decode or stimulate neural tissue.  It accepts bounded
adapter observations and evaluates whether they are sufficient evidence for a
specific proposed transition.  Observation, translation confidence, and decoder
output are evidence only and never become intent, consent, authorization, or
execution authority by implication.
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Literal, Mapping, Optional

PROFILE = "steggate.neural-micronode.v0"
Disposition = Literal["ALLOW", "DENY", "REVIEW", "FAIL_CLOSED"]

FAIL_CLOSED = {
    "DESTINATION_UNRESOLVED",
    "DESTINATION_AMBIGUOUS",
    "ADAPTER_UNATTESTED",
    "CALIBRATION_MISSING",
    "CALIBRATION_STALE",
    "OBSERVATION_QUALITY_INSUFFICIENT",
    "RECEIVER_EVIDENCE_STALE",
    "TRANSLATION_PROVENANCE_INCOMPLETE",
    "REQUIRED_ASSERTION_UNRESOLVED",
    "PROHIBITED_STATE_PRESENT",
    "CANDIDATE_BINDING_FAILED",
    "AUTHORIZATION_UNESTABLISHED",
    "COMMIT_COHERENCE_FAILED",
}

_FORBIDDEN_AUTHORITY_UPGRADES = {
    "intended_by", "authorized_by", "consented_to_by", "execution_authority"
}


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False, default=str).encode()


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class NeuralObservation:
    receiver_locator: str
    locator_profile: str
    observed_at: str
    observation_ref: str
    adapter_profile: str
    adapter_attested: bool
    model_or_mapping_id: str
    calibration_ref: Optional[str]
    calibration_valid: bool
    observation_quality: float
    assertions: Mapping[str, bool]
    assertion_provenance: Mapping[str, str]
    destination_resolved: bool = True
    destination_ambiguous: bool = False


@dataclass(frozen=True)
class NeuralMicroNodeDecision:
    artifact_type: str
    profile: str
    transition_id: str
    disposition: Disposition
    reason: str
    receiver_locator: str
    candidate_hash: str
    evidence_hash: str
    evaluated_assertions: Mapping[str, bool]
    evaluated_at: str
    decision_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_neural_transition(
    packet: Mapping[str, Any],
    observation: NeuralObservation,
    *,
    now: Optional[datetime] = None,
) -> NeuralMicroNodeDecision:
    """Evaluate bounded receiver evidence for one addressed transition.

    ALLOW means only that this evidence boundary is satisfied.  It does not
    execute a consequence or manufacture higher-level authority.
    """
    evaluated_at = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    transition_id = str(packet.get("transition_id", ""))
    destination = packet.get("destination", {})
    payload = packet.get("payload", {})
    requirements = packet.get("requirements", {})
    translation = packet.get("translation", {})
    candidate_hash = str(payload.get("candidate_hash", ""))

    def finish(disposition: Disposition, reason: str) -> NeuralMicroNodeDecision:
        evidence = {
            "observation_ref": observation.observation_ref,
            "observed_at": observation.observed_at,
            "adapter_profile": observation.adapter_profile,
            "model_or_mapping_id": observation.model_or_mapping_id,
            "calibration_ref": observation.calibration_ref,
            "assertions": dict(observation.assertions),
            "assertion_provenance": dict(observation.assertion_provenance),
        }
        body = {
            "artifact_type": "stegcore.neural_micronode_decision",
            "profile": PROFILE,
            "transition_id": transition_id,
            "disposition": disposition,
            "reason": reason,
            "receiver_locator": observation.receiver_locator,
            "candidate_hash": candidate_hash,
            "evidence_hash": canonical_hash(evidence),
            "evaluated_assertions": dict(observation.assertions),
            "evaluated_at": evaluated_at.isoformat(),
        }
        return NeuralMicroNodeDecision(**body, decision_hash=canonical_hash(body))

    if packet.get("profile") != PROFILE or not transition_id or not candidate_hash:
        return finish("FAIL_CLOSED", "CANDIDATE_BINDING_FAILED")
    if destination.get("receiver_class") != "neural_micro_node":
        return finish("FAIL_CLOSED", "DESTINATION_UNRESOLVED")
    if not observation.destination_resolved:
        return finish("FAIL_CLOSED", "DESTINATION_UNRESOLVED")
    if observation.destination_ambiguous:
        return finish("FAIL_CLOSED", "DESTINATION_AMBIGUOUS")
    if destination.get("receiver_locator") != observation.receiver_locator or destination.get("locator_profile") != observation.locator_profile:
        return finish("FAIL_CLOSED", "DESTINATION_UNRESOLVED")
    if not observation.adapter_attested:
        return finish("FAIL_CLOSED", "ADAPTER_UNATTESTED")
    if not observation.calibration_ref:
        return finish("FAIL_CLOSED", "CALIBRATION_MISSING")
    if not observation.calibration_valid:
        return finish("FAIL_CLOSED", "CALIBRATION_STALE")
    if translation.get("adapter_profile") != observation.adapter_profile or translation.get("model_or_mapping_id") != observation.model_or_mapping_id or translation.get("calibration_ref") != observation.calibration_ref:
        return finish("FAIL_CLOSED", "TRANSLATION_PROVENANCE_INCOMPLETE")

    try:
        observed_at = _parse_time(observation.observed_at)
        age_ms = (evaluated_at - observed_at).total_seconds() * 1000
    except (TypeError, ValueError):
        return finish("FAIL_CLOSED", "RECEIVER_EVIDENCE_STALE")
    freshness_ms = requirements.get("freshness_ms")
    if not isinstance(freshness_ms, int) or freshness_ms <= 0 or age_ms < 0 or age_ms > freshness_ms:
        return finish("FAIL_CLOSED", "RECEIVER_EVIDENCE_STALE")
    minimum_quality = requirements.get("minimum_observation_quality")
    if not isinstance(minimum_quality, (int, float)) or not 0 <= observation.observation_quality <= 1 or observation.observation_quality < minimum_quality:
        return finish("FAIL_CLOSED", "OBSERVATION_QUALITY_INSUFFICIENT")

    required = requirements.get("required_assertions", [])
    prohibited = requirements.get("prohibited_assertions", [])
    for name in list(required) + list(prohibited):
        if name in _FORBIDDEN_AUTHORITY_UPGRADES:
            return finish("FAIL_CLOSED", "AUTHORIZATION_UNESTABLISHED")
        if name not in observation.assertions or name not in observation.assertion_provenance:
            return finish("FAIL_CLOSED", "REQUIRED_ASSERTION_UNRESOLVED")
    if any(not observation.assertions[name] for name in required):
        return finish("DENY", "REQUIRED_ASSERTION_FALSE")
    if any(observation.assertions[name] for name in prohibited):
        return finish("FAIL_CLOSED", "PROHIBITED_STATE_PRESENT")
    return finish("ALLOW", "RECEIVER_EVIDENCE_SATISFIES_TRANSITION")
