from __future__ import annotations

"""Deterministic, adapter-neutral physical channel model for neural micro-nodes.

This module models evidence about targeting, coupling, transfer, noise, latency,
and adapter-declared stimulation envelopes. It does not encode biological dosage,
claim semantic neural writing, or establish medical safety.
"""

from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any, Literal, Optional

PhysicalDisposition = Literal["ELIGIBLE", "FAIL_CLOSED"]
Direction = Literal["READ", "WRITE"]


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False, default=str).encode("utf-8")


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _bounded(value: float) -> bool:
    return isinstance(value, (int, float)) and 0.0 <= float(value) <= 1.0


@dataclass(frozen=True)
class PhysicalChannelState:
    adapter_profile: str
    modality: str
    receiver_locator: str
    locator_profile: str
    target_resolved: bool
    target_ambiguous: bool
    calibration_ref: Optional[str]
    calibration_valid: bool
    safe_envelope_available: bool
    targeting_confidence: float
    coupling_quality: float
    transfer_efficiency: float
    noise_fraction: float
    sensor_quality: float
    latency_ms: float


@dataclass(frozen=True)
class PhysicalTransitionRequest:
    transition_id: str
    direction: Direction
    receiver_locator: str
    locator_profile: str
    payload_hash: str
    minimum_targeting_confidence: float
    minimum_channel_score: float
    maximum_latency_ms: float
    normalized_intensity: Optional[float] = None
    declared_envelope_max: Optional[float] = None
    consequence_class: Optional[str] = None
    reversible_declared: Optional[bool] = None


@dataclass(frozen=True)
class PhysicalChannelDecision:
    artifact_type: str
    transition_id: str
    direction: Direction
    disposition: PhysicalDisposition
    reason: str
    receiver_locator: str
    channel_score: float
    calibration_ref: Optional[str]
    adapter_profile: str
    modality: str
    evidence_hash: str
    decision_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _score(state: PhysicalChannelState, *, include_sensor: bool) -> float:
    values = (
        state.targeting_confidence,
        state.coupling_quality,
        state.transfer_efficiency,
        1.0 - state.noise_fraction,
    )
    score = 1.0
    for value in values:
        score *= float(value)
    if include_sensor:
        score *= float(state.sensor_quality)
    return score


def evaluate_physical_channel(
    request: PhysicalTransitionRequest,
    state: PhysicalChannelState,
) -> PhysicalChannelDecision:
    """Evaluate whether physical-channel evidence is sufficient for one transition.

    ELIGIBLE is not execution authority. It only means the adapter-declared
    physical evidence satisfies this modeled channel boundary.
    """

    channel_score = 0.0

    def finish(disposition: PhysicalDisposition, reason: str) -> PhysicalChannelDecision:
        evidence = {
            "state": asdict(state),
            "request": asdict(request),
            "channel_score": channel_score,
        }
        body = {
            "artifact_type": "stegcore.neural_physical_channel_decision",
            "transition_id": request.transition_id,
            "direction": request.direction,
            "disposition": disposition,
            "reason": reason,
            "receiver_locator": state.receiver_locator,
            "channel_score": channel_score,
            "calibration_ref": state.calibration_ref,
            "adapter_profile": state.adapter_profile,
            "modality": state.modality,
            "evidence_hash": canonical_hash(evidence),
        }
        return PhysicalChannelDecision(**body, decision_hash=canonical_hash(body))

    required_normals = (
        state.targeting_confidence,
        state.coupling_quality,
        state.transfer_efficiency,
        state.noise_fraction,
        state.sensor_quality,
        request.minimum_targeting_confidence,
        request.minimum_channel_score,
    )
    if not all(_bounded(value) for value in required_normals):
        return finish("FAIL_CLOSED", "PHYSICAL_CHANNEL_QUALITY_LOW")
    if not state.target_resolved:
        return finish("FAIL_CLOSED", "PHYSICAL_TARGET_UNRESOLVED")
    if state.target_ambiguous:
        return finish("FAIL_CLOSED", "PHYSICAL_TARGET_AMBIGUOUS")
    if request.receiver_locator != state.receiver_locator or request.locator_profile != state.locator_profile:
        return finish("FAIL_CLOSED", "PHYSICAL_TARGET_UNRESOLVED")
    if not state.calibration_ref:
        return finish("FAIL_CLOSED", "PHYSICAL_CALIBRATION_MISSING")
    if not state.calibration_valid:
        return finish("FAIL_CLOSED", "PHYSICAL_CALIBRATION_INVALID")
    if state.targeting_confidence < request.minimum_targeting_confidence:
        return finish("FAIL_CLOSED", "PHYSICAL_TARGETING_CONFIDENCE_LOW")
    if not isinstance(state.latency_ms, (int, float)) or state.latency_ms < 0 or not isinstance(request.maximum_latency_ms, (int, float)) or request.maximum_latency_ms < 0 or state.latency_ms > request.maximum_latency_ms:
        return finish("FAIL_CLOSED", "PHYSICAL_LATENCY_EXCEEDED")

    if request.direction == "WRITE":
        if not state.safe_envelope_available:
            return finish("FAIL_CLOSED", "PHYSICAL_SAFE_ENVELOPE_UNAVAILABLE")
        if request.normalized_intensity is None or request.declared_envelope_max is None:
            return finish("FAIL_CLOSED", "PHYSICAL_SAFE_ENVELOPE_UNAVAILABLE")
        if not _bounded(request.normalized_intensity) or not _bounded(request.declared_envelope_max) or request.normalized_intensity > request.declared_envelope_max:
            return finish("FAIL_CLOSED", "PHYSICAL_INTENSITY_OUT_OF_ENVELOPE")
        channel_score = _score(state, include_sensor=False)
    elif request.direction == "READ":
        channel_score = _score(state, include_sensor=True)
        if state.sensor_quality < request.minimum_channel_score:
            return finish("FAIL_CLOSED", "PHYSICAL_OBSERVATION_QUALITY_LOW")
    else:
        return finish("FAIL_CLOSED", "PHYSICAL_CHANNEL_QUALITY_LOW")

    if channel_score < request.minimum_channel_score:
        reason = "PHYSICAL_OBSERVATION_QUALITY_LOW" if request.direction == "READ" else "PHYSICAL_CHANNEL_QUALITY_LOW"
        return finish("FAIL_CLOSED", reason)
    return finish("ELIGIBLE", "PHYSICAL_CHANNEL_EVIDENCE_SATISFIES_TRANSITION")
