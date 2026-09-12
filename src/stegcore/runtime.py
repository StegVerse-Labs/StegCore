from __future__ import annotations

"""Fail-closed execution boundary for StegCore decisions and commit coherence.

The runtime consumes already-verified continuity evidence through ``DecisionRequest``.
It neither verifies nor mints continuity receipts. The injected executor is invoked
only when the existing decision interface returns ``allow`` and the commit-coherence
gate independently preserves authority, denial reachability, and governable
continuation.

Authority and evaluation time are part of the commit-time state. Missing authority
must therefore remain missing and fail closed; it must never be synthesized as an
implicit approval by the runtime.
"""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Generic, Literal, Mapping, Optional, TypeVar

from .commit_governance import canonical_hash, coherence_gate, finalize_receipt
from .decision import DecisionRequest, DecisionResult, decide


T = TypeVar("T")
ExecutionStatus = Literal["executed", "refused", "failed"]


@dataclass(frozen=True)
class ExecutionObservation(Generic[T]):
    artifact_type: Literal["stegcore.execution_observation"]
    status: ExecutionStatus
    decision: DecisionResult
    pre_state_hash: str
    post_state_hash: str
    coherence_receipt: Optional[dict[str, Any]] = None
    result: Optional[T] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    observed_at: str = ""

    @property
    def executed(self) -> bool:
        return self.status == "executed"


class GovernedRuntime:
    """Bind StegCore admissibility and coherence to an injected executor callback."""

    def evaluate_and_execute(
        self,
        request: DecisionRequest,
        executor: Callable[[], T],
        *,
        declared_execution_context: Optional[Mapping[str, Any]] = None,
        capability_surface: Optional[Mapping[str, Any]] = None,
        authority_resolution: Optional[Mapping[str, Any]] = None,
        previous_receipt_hash: Optional[str] = None,
    ) -> ExecutionObservation[T]:
        context = dict(declared_execution_context or {})
        request_data = asdict(request)
        observed_at = datetime.now(timezone.utc).isoformat()

        # Authority is state, not a convenience default. If no authority state is
        # supplied, retain that absence explicitly so coherence fails closed.
        authority = dict(authority_resolution or {})
        if not authority:
            authority = {
                "status": "missing",
                "basis_invalidated_by_action": None,
                "reason": "authority_state_not_supplied",
            }

        # Commit-time state binds the exact request (including target and request
        # time), declared execution context, current authority state, and the
        # evaluation instant. This hash is the state evaluated immediately before
        # any consequence-bearing commit.
        pre_state = {
            "request": request_data,
            "declared_execution_context": context,
            "authority_resolution": authority,
            "evaluation_time": observed_at,
        }
        pre_state_hash = canonical_hash(pre_state)
        decision = decide(request)

        if decision.decision != "allow":
            post_state = {
                "decision": asdict(decision),
                "status": "refused",
                "reason": "admissibility_not_allow",
                "commit_state_hash": pre_state_hash,
            }
            return ExecutionObservation(
                artifact_type="stegcore.execution_observation",
                status="refused",
                decision=decision,
                pre_state_hash=pre_state_hash,
                post_state_hash=canonical_hash(post_state),
                observed_at=observed_at,
            )

        if request.intent is None:
            raise ValueError("Allowed decision has no action intent")

        gate = coherence_gate(
            task=request.intent.action,
            payload=request.intent.parameters,
            capability_surface=capability_surface,
            state_hash=pre_state_hash,
            actor_binding=request.actor_class,
            authority_resolution=authority,
            previous_receipt_hash=previous_receipt_hash,
        )

        # Preserve the material commit-time state constituents in the receipt so a
        # later reconstruction can prove which authority/target/time state was
        # actually evaluated rather than only observing a boolean outcome.
        gate_receipt = finalize_receipt(
            {
                key: value
                for key, value in gate["receipt"].items()
                if key != "receipt_hash"
            }
            | {
                "commit_state": pre_state,
                "commit_state_hash": pre_state_hash,
                "evaluation_time": observed_at,
                "target_binding": request.intent.target,
            }
        )
        gate["receipt"] = gate_receipt

        if not gate["allowed"]:
            post_state = {
                "decision": asdict(decision),
                "status": "refused",
                "reason": "coherence_failed",
                "coherence_receipt_hash": gate["receipt"]["receipt_hash"],
                "commit_state_hash": pre_state_hash,
            }
            return ExecutionObservation(
                artifact_type="stegcore.execution_observation",
                status="refused",
                decision=decision,
                pre_state_hash=pre_state_hash,
                post_state_hash=canonical_hash(post_state),
                coherence_receipt=gate["receipt"],
                observed_at=observed_at,
            )

        try:
            result = executor()
        except Exception as exc:
            receipt = finalize_receipt(
                {
                    key: value
                    for key, value in gate["receipt"].items()
                    if key != "receipt_hash"
                }
                | {
                    "execution_status": "failed",
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                }
            )
            post_state = {
                "decision": asdict(decision),
                "status": "failed",
                "coherence_receipt_hash": receipt["receipt_hash"],
                "commit_state_hash": pre_state_hash,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            }
            return ExecutionObservation(
                artifact_type="stegcore.execution_observation",
                status="failed",
                decision=decision,
                pre_state_hash=pre_state_hash,
                post_state_hash=canonical_hash(post_state),
                coherence_receipt=receipt,
                error_type=type(exc).__name__,
                error_message=str(exc),
                observed_at=observed_at,
            )

        receipt = finalize_receipt(
            {
                key: value
                for key, value in gate["receipt"].items()
                if key != "receipt_hash"
            }
            | {
                "execution_status": "executed",
                "execution_result": result,
            }
        )
        post_state = {
            "decision": asdict(decision),
            "status": "executed",
            "coherence_receipt_hash": receipt["receipt_hash"],
            "commit_state_hash": pre_state_hash,
            "result": result,
        }
        return ExecutionObservation(
            artifact_type="stegcore.execution_observation",
            status="executed",
            decision=decision,
            pre_state_hash=pre_state_hash,
            post_state_hash=canonical_hash(post_state),
            coherence_receipt=receipt,
            result=result,
            observed_at=observed_at,
        )


def governed_execute(
    request: DecisionRequest,
    executor: Callable[[], T],
    *,
    declared_execution_context: Optional[Mapping[str, Any]] = None,
    capability_surface: Optional[Mapping[str, Any]] = None,
    authority_resolution: Optional[Mapping[str, Any]] = None,
    previous_receipt_hash: Optional[str] = None,
) -> ExecutionObservation[T]:
    return GovernedRuntime().evaluate_and_execute(
        request,
        executor,
        declared_execution_context=declared_execution_context,
        capability_surface=capability_surface,
        authority_resolution=authority_resolution,
        previous_receipt_hash=previous_receipt_hash,
    )
