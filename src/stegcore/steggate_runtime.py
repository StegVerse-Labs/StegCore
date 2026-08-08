from __future__ import annotations

"""End-to-end StegGate governed execution composition.

This module binds the reconciled StegGate admissibility evaluation to the existing
commit-coherence gate and an injected mutation callback. It does not replace
``three_layer`` or ``commit_governance`` and it does not expose a remote mutation
endpoint. The executor remains unreachable unless the complete StegGate evaluation
returns ALLOW and commit coherence independently returns ALLOW.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Generic, Literal, Mapping, Optional, TypeVar

from .commit_governance import canonical_hash, coherence_gate, finalize_receipt
from .steggate import AdmissibilityEvaluation, AdmissibilityRequest, evaluate_admissibility

T = TypeVar("T")
ExecutionStatus = Literal["executed", "refused", "failed"]


@dataclass(frozen=True)
class StegGateExecutionObservation(Generic[T]):
    artifact_type: Literal["stegcore.steggate_execution_observation"]
    status: ExecutionStatus
    evaluation: AdmissibilityEvaluation
    pre_state_hash: str
    post_state_hash: str
    executor_invoked: bool
    coherence_receipt: Optional[dict[str, Any]] = None
    result: Optional[T] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    observed_at: str = ""

    @property
    def executed(self) -> bool:
        return self.status == "executed"


def governed_steggate_execute(
    request: AdmissibilityRequest,
    executor: Callable[[], T],
    *,
    declared_execution_context: Optional[Mapping[str, Any]] = None,
    capability_surface: Optional[Mapping[str, Any]] = None,
    authority_resolution: Optional[Mapping[str, Any]] = None,
) -> StegGateExecutionObservation[T]:
    """Evaluate, check commit coherence, and only then invoke ``executor``."""

    context = dict(declared_execution_context or {})
    request_data = request.model_dump(mode="json", exclude_none=False)
    pre_state = {
        "request": request_data,
        "declared_execution_context": context,
    }
    pre_state_hash = canonical_hash(pre_state)
    evaluation = evaluate_admissibility(request)
    observed_at = datetime.now(timezone.utc).isoformat()

    if evaluation.disposition != "ALLOW":
        post_state = {
            "decision_state_hash": evaluation.decision_state_hash,
            "disposition": evaluation.disposition,
            "status": "refused",
            "reason": "steggate_admissibility_not_allow",
        }
        return StegGateExecutionObservation(
            artifact_type="stegcore.steggate_execution_observation",
            status="refused",
            evaluation=evaluation,
            pre_state_hash=pre_state_hash,
            post_state_hash=canonical_hash(post_state),
            executor_invoked=False,
            observed_at=observed_at,
        )

    authority = dict(authority_resolution or {})
    gate = coherence_gate(
        task=request.candidate.action,
        payload=request.candidate.parameters,
        capability_surface=capability_surface,
        state_hash=pre_state_hash,
        actor_binding=request.candidate.actor_class,
        authority_resolution=authority,
        previous_receipt_hash=request.continuity.previous_receipt_hash,
    )

    if not gate["allowed"]:
        post_state = {
            "decision_state_hash": evaluation.decision_state_hash,
            "disposition": evaluation.disposition,
            "status": "refused",
            "reason": "coherence_failed",
            "coherence_receipt_hash": gate["receipt"]["receipt_hash"],
        }
        return StegGateExecutionObservation(
            artifact_type="stegcore.steggate_execution_observation",
            status="refused",
            evaluation=evaluation,
            pre_state_hash=pre_state_hash,
            post_state_hash=canonical_hash(post_state),
            executor_invoked=False,
            coherence_receipt=gate["receipt"],
            observed_at=observed_at,
        )

    try:
        result = executor()
    except Exception as exc:
        receipt = finalize_receipt(
            {key: value for key, value in gate["receipt"].items() if key != "receipt_hash"}
            | {
                "steggate_decision_state_hash": evaluation.decision_state_hash,
                "execution_status": "failed",
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            }
        )
        post_state = {
            "decision_state_hash": evaluation.decision_state_hash,
            "status": "failed",
            "coherence_receipt_hash": receipt["receipt_hash"],
            "error_type": type(exc).__name__,
            "error_message": str(exc),
        }
        return StegGateExecutionObservation(
            artifact_type="stegcore.steggate_execution_observation",
            status="failed",
            evaluation=evaluation,
            pre_state_hash=pre_state_hash,
            post_state_hash=canonical_hash(post_state),
            executor_invoked=True,
            coherence_receipt=receipt,
            error_type=type(exc).__name__,
            error_message=str(exc),
            observed_at=observed_at,
        )

    receipt = finalize_receipt(
        {key: value for key, value in gate["receipt"].items() if key != "receipt_hash"}
        | {
            "steggate_decision_state_hash": evaluation.decision_state_hash,
            "execution_status": "executed",
            "execution_result": result,
        }
    )
    post_state = {
        "decision_state_hash": evaluation.decision_state_hash,
        "status": "executed",
        "coherence_receipt_hash": receipt["receipt_hash"],
        "result": result,
    }
    return StegGateExecutionObservation(
        artifact_type="stegcore.steggate_execution_observation",
        status="executed",
        evaluation=evaluation,
        pre_state_hash=pre_state_hash,
        post_state_hash=canonical_hash(post_state),
        executor_invoked=True,
        coherence_receipt=receipt,
        result=result,
        observed_at=observed_at,
    )
