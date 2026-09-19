from __future__ import annotations

"""End-to-end StegGate governed execution composition.

This module binds the reconciled StegGate admissibility evaluation to the existing
present-state and commit-coherence gates and an injected mutation callback. It does
not replace ``three_layer`` or ``commit_governance`` and it does not expose a remote
mutation endpoint. The executor remains unreachable unless the complete StegGate
evaluation, present-state evaluation, and commit coherence all ALLOW.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Generic, Literal, Mapping, Optional, TypeVar

from .commit_governance import (
    canonical_hash,
    coherence_gate,
    evaluate_present_state,
    finalize_receipt,
)
from .standing_binding import evaluate_admissibility_with_standing
from .steggate import AdmissibilityEvaluation, AdmissibilityRequest

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
    pre_execution_observer: Optional[Callable[[Mapping[str, Any]], Any]] = None,
) -> StegGateExecutionObservation[T]:
    """Evaluate, check present state/coherence, and only then invoke ``executor``."""

    context = dict(declared_execution_context or {})
    request_data = request.model_dump(mode="json", exclude_none=False)
    evaluation_dt = datetime.now(timezone.utc)
    observed_at = evaluation_dt.isoformat()
    authority = dict(authority_resolution or {})
    if not authority:
        authority = {
            "status": "missing",
            "basis_invalidated_by_action": None,
            "reason": "authority_state_not_supplied",
        }

    pre_state = {
        "request": request_data,
        "declared_execution_context": context,
        "authority_resolution": authority,
        "evaluation_time": observed_at,
    }
    pre_state_hash = canonical_hash(pre_state)
    evaluation = evaluate_admissibility_with_standing(request, context)

    if evaluation.disposition != "ALLOW":
        post_state = {
            "decision_state_hash": evaluation.decision_state_hash,
            "disposition": evaluation.disposition,
            "status": "refused",
            "reason": "steggate_admissibility_not_allow",
            "commit_state_hash": pre_state_hash,
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

    present_state = evaluate_present_state(
        authority_resolution=authority,
        target_binding=request.candidate.target,
        evaluation_time=evaluation_dt,
        evidence_current=request.execution.evidence_current,
    )
    if not present_state["allowed"]:
        receipt = finalize_receipt(
            {
                "timestamp": observed_at,
                "decision": present_state["disposition"],
                "reason": "present_state_not_established",
                "task": request.candidate.action,
                "state_hash": pre_state_hash,
                "commit_state": pre_state,
                "commit_state_hash": pre_state_hash,
                "evaluation_time": observed_at,
                "target_binding": request.candidate.target,
                "authority_resolution": authority,
                "present_state_checks": present_state["checks"],
                "present_state_reasons": list(present_state["reasons"]),
                "steggate_decision_state_hash": evaluation.decision_state_hash,
                "coherent": False,
                "coherence_checks": {"present_state_established": False},
                "coherence_reasons": list(present_state["reasons"]),
                "previous_receipt_hash": request.continuity.previous_receipt_hash,
            }
        )
        post_state = {
            "decision_state_hash": evaluation.decision_state_hash,
            "disposition": evaluation.disposition,
            "status": "refused",
            "reason": "present_state_not_established",
            "present_state_disposition": present_state["disposition"],
            "coherence_receipt_hash": receipt["receipt_hash"],
            "commit_state_hash": pre_state_hash,
        }
        return StegGateExecutionObservation(
            artifact_type="stegcore.steggate_execution_observation",
            status="refused",
            evaluation=evaluation,
            pre_state_hash=pre_state_hash,
            post_state_hash=canonical_hash(post_state),
            executor_invoked=False,
            coherence_receipt=receipt,
            observed_at=observed_at,
        )

    gate = coherence_gate(
        task=request.candidate.action,
        payload=request.candidate.parameters,
        capability_surface=capability_surface,
        state_hash=pre_state_hash,
        actor_binding=request.candidate.actor_class,
        authority_resolution=authority,
        previous_receipt_hash=request.continuity.previous_receipt_hash,
    )

    gate_receipt = finalize_receipt(
        {key: value for key, value in gate["receipt"].items() if key != "receipt_hash"}
        | {
            "commit_state": pre_state,
            "commit_state_hash": pre_state_hash,
            "evaluation_time": observed_at,
            "target_binding": request.candidate.target,
            "present_state_checks": present_state["checks"],
            "present_state_reasons": list(present_state["reasons"]),
            "steggate_decision_state_hash": evaluation.decision_state_hash,
        }
    )
    gate["receipt"] = gate_receipt

    if gate["allowed"] and pre_execution_observer is not None:
        pre_execution_evidence = {
            "schema": "stegcore.pre-execution-admission-observation/v1",
            "disposition": evaluation.disposition,
            "decision_state_hash": evaluation.decision_state_hash,
            "pre_state_hash": pre_state_hash,
            "coherence_receipt": gate["receipt"],
            "candidate_hash": evaluation.candidate_hash,
            "executor_invoked": False,
            "authority_effect": "NONE_OBSERVATION_ONLY",
        }
        try:
            pre_execution_observer(pre_execution_evidence)
        except Exception as exc:
            receipt = finalize_receipt(
                {key: value for key, value in gate["receipt"].items() if key != "receipt_hash"}
                | {
                    "execution_status": "refused",
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "pre_execution_observer_failed": True,
                }
            )
            post_state = {
                "decision_state_hash": evaluation.decision_state_hash,
                "disposition": evaluation.disposition,
                "status": "refused",
                "reason": "pre_execution_observer_failed",
                "coherence_receipt_hash": receipt["receipt_hash"],
                "commit_state_hash": pre_state_hash,
            }
            return StegGateExecutionObservation(
                artifact_type="stegcore.steggate_execution_observation",
                status="refused",
                evaluation=evaluation,
                pre_state_hash=pre_state_hash,
                post_state_hash=canonical_hash(post_state),
                executor_invoked=False,
                coherence_receipt=receipt,
                error_type=type(exc).__name__,
                error_message=str(exc),
                observed_at=observed_at,
            )

    if not gate["allowed"]:
        post_state = {
            "decision_state_hash": evaluation.decision_state_hash,
            "disposition": evaluation.disposition,
            "status": "refused",
            "reason": "coherence_failed",
            "coherence_receipt_hash": gate["receipt"]["receipt_hash"],
            "commit_state_hash": pre_state_hash,
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
                "execution_status": "failed",
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            }
        )
        post_state = {
            "decision_state_hash": evaluation.decision_state_hash,
            "status": "failed",
            "coherence_receipt_hash": receipt["receipt_hash"],
            "commit_state_hash": pre_state_hash,
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
            "execution_status": "executed",
            "execution_result": result,
        }
    )
    post_state = {
        "decision_state_hash": evaluation.decision_state_hash,
        "status": "executed",
        "coherence_receipt_hash": receipt["receipt_hash"],
        "commit_state_hash": pre_state_hash,
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
