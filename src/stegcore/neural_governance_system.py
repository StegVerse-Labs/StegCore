from __future__ import annotations

"""Full governed composition for modeled neural micro-node transitions.

This module does not create authority from neural or physical evidence. It binds a
neural receiver decision and a physical-channel decision into the existing
canonical StegGate request, then relies on governed_steggate_execute for complete
admissibility + independent commit coherence before a modeled consequence can run.
"""

from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any, Literal, Mapping, Optional

from .neural_micronode import NeuralMicroNodeDecision, NeuralObservation, evaluate_neural_transition
from .neural_physical_channel import (
    PhysicalChannelDecision,
    PhysicalChannelState,
    PhysicalTransitionRequest,
    evaluate_physical_channel,
)
from .steggate import AdmissibilityRequest, canonical_sha256
from .steggate_runtime import StegGateExecutionObservation, governed_steggate_execute

SystemStatus = Literal["EXECUTED", "REFUSED", "FAIL_CLOSED", "FAILED"]


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False, default=str).encode("utf-8")


def _hash(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


@dataclass(frozen=True)
class NeuralGovernanceReceipt:
    artifact_type: str
    transition_id: str
    status: SystemStatus
    reason: str
    candidate_hash: str
    neural_decision_hash: Optional[str]
    physical_decision_hash: Optional[str]
    steggate_decision_state_hash: Optional[str]
    commit_receipt_hash: Optional[str]
    consequence_invoked: bool
    consequence_result: Optional[Mapping[str, Any]]
    receipt_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _finish(
    *,
    transition_id: str,
    status: SystemStatus,
    reason: str,
    candidate_hash: str,
    neural_decision: Optional[NeuralMicroNodeDecision] = None,
    physical_decision: Optional[PhysicalChannelDecision] = None,
    execution: Optional[StegGateExecutionObservation[Any]] = None,
) -> NeuralGovernanceReceipt:
    commit_receipt_hash = None
    consequence_result: Optional[Mapping[str, Any]] = None
    if execution and execution.coherence_receipt:
        commit_receipt_hash = str(execution.coherence_receipt.get("receipt_hash", "")) or None
    if execution and isinstance(execution.result, Mapping):
        consequence_result = dict(execution.result)
    body = {
        "artifact_type": "stegcore.neural_governance_receipt",
        "transition_id": transition_id,
        "status": status,
        "reason": reason,
        "candidate_hash": candidate_hash,
        "neural_decision_hash": neural_decision.decision_hash if neural_decision else None,
        "physical_decision_hash": physical_decision.decision_hash if physical_decision else None,
        "steggate_decision_state_hash": execution.evaluation.decision_state_hash if execution else None,
        "commit_receipt_hash": commit_receipt_hash,
        "consequence_invoked": bool(execution.executor_invoked) if execution else False,
        "consequence_result": consequence_result,
    }
    return NeuralGovernanceReceipt(**body, receipt_hash=_hash(body))


def _bind_neural_evidence(request: AdmissibilityRequest, neural: NeuralMicroNodeDecision, physical: PhysicalChannelDecision) -> AdmissibilityRequest:
    """Add evidence references only; never synthesize authority predicates."""

    bound = request.model_copy(deep=True)
    neural_ref = f"neural:{neural.decision_hash}"
    physical_ref = f"neural-physical:{physical.decision_hash}"
    for ref in (neural_ref, physical_ref):
        if ref not in bound.signal.admitted_signal_refs:
            bound.signal.admitted_signal_refs.append(ref)
        if ref not in bound.execution.evidence_refs:
            bound.execution.evidence_refs.append(ref)
    if "neural_micronode_bounded_translation" not in bound.signal.transformations:
        bound.signal.transformations.append("neural_micronode_bounded_translation")
    return bound


def govern_neural_write(
    *,
    packet: Mapping[str, Any],
    observation: NeuralObservation,
    admissibility_request: AdmissibilityRequest,
    physical_request: PhysicalTransitionRequest,
    physical_state: PhysicalChannelState,
    declared_execution_context: Optional[Mapping[str, Any]] = None,
    capability_surface: Optional[Mapping[str, Any]] = None,
    authority_resolution: Optional[Mapping[str, Any]] = None,
) -> NeuralGovernanceReceipt:
    """Govern a modeled external -> addressed-neural write transition end to end.

    The modeled physical consequence is unreachable unless:
      * packet candidate binding is exact,
      * neural receiver evidence is ALLOW,
      * physical channel evidence is ELIGIBLE,
      * canonical StegGate returns ALLOW, and
      * commit coherence independently returns ALLOW.
    """

    transition_id = str(packet.get("transition_id", ""))
    candidate_body = admissibility_request.candidate.model_dump(mode="json", exclude_none=True)
    candidate_hash = canonical_sha256(candidate_body)
    packet_candidate_hash = str(packet.get("payload", {}).get("candidate_hash", ""))

    if not transition_id or packet_candidate_hash != candidate_hash:
        return _finish(
            transition_id=transition_id,
            status="FAIL_CLOSED",
            reason="CANDIDATE_BINDING_FAILED",
            candidate_hash=candidate_hash,
        )
    if physical_request.transition_id != transition_id or physical_request.payload_hash != candidate_hash or physical_request.direction != "WRITE":
        return _finish(
            transition_id=transition_id,
            status="FAIL_CLOSED",
            reason="PHYSICAL_CANDIDATE_BINDING_FAILED",
            candidate_hash=candidate_hash,
        )

    neural = evaluate_neural_transition(packet, observation)
    if neural.disposition != "ALLOW":
        return _finish(
            transition_id=transition_id,
            status="FAIL_CLOSED" if neural.disposition == "FAIL_CLOSED" else "REFUSED",
            reason=f"NEURAL_BOUNDARY_{neural.reason}",
            candidate_hash=candidate_hash,
            neural_decision=neural,
        )

    physical = evaluate_physical_channel(physical_request, physical_state)
    if physical.disposition != "ELIGIBLE":
        return _finish(
            transition_id=transition_id,
            status="FAIL_CLOSED",
            reason=physical.reason,
            candidate_hash=candidate_hash,
            neural_decision=neural,
            physical_decision=physical,
        )

    bound_request = _bind_neural_evidence(admissibility_request, neural, physical)

    def modeled_consequence() -> dict[str, Any]:
        return {
            "artifact_type": "stegcore.modeled_neural_physical_consequence",
            "transition_id": transition_id,
            "receiver_locator": physical_state.receiver_locator,
            "modality": physical_state.modality,
            "channel_score": physical.channel_score,
            "consequence_class": physical_request.consequence_class,
            "reversible_declared": physical_request.reversible_declared,
            "software_model_only": True,
            "biological_activation_claimed": False,
        }

    execution = governed_steggate_execute(
        bound_request,
        modeled_consequence,
        declared_execution_context=declared_execution_context,
        capability_surface=capability_surface,
        authority_resolution=authority_resolution,
    )
    if execution.status == "executed":
        status: SystemStatus = "EXECUTED"
        reason = "GOVERNED_MODELED_NEURAL_CONSEQUENCE_EXECUTED"
    elif execution.status == "failed":
        status = "FAILED"
        reason = "MODELED_CONSEQUENCE_FAILED"
    elif execution.evaluation.disposition == "FAIL_CLOSED":
        status = "FAIL_CLOSED"
        reason = "STEGGATE_FAIL_CLOSED"
    else:
        status = "REFUSED"
        reason = "STEGGATE_OR_COMMIT_REFUSED"
    return _finish(
        transition_id=transition_id,
        status=status,
        reason=reason,
        candidate_hash=candidate_hash,
        neural_decision=neural,
        physical_decision=physical,
        execution=execution,
    )
