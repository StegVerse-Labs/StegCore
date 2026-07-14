from __future__ import annotations

"""Fail-closed runtime binding for the canonical StegCore decision interface.

This module does not verify or mint continuity receipts. It consumes the existing
``DecisionRequest`` contract and produces a local execution observation that an
integrating system may attach to its own evidence flow.
"""

from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Callable, Generic, Literal, Optional, TypeVar

from .decision import DecisionRequest, DecisionResult, decide


T = TypeVar("T")
ExecutionStatus = Literal["executed", "refused", "failed"]


def _json_default(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    raise TypeError(f"Unsupported value for canonical hashing: {type(value)!r}")


def canonical_hash(value: Any) -> str:
    """Return a deterministic SHA-256 hash for JSON-compatible declared state."""

    encoded = json.dumps(
        value,
        default=_json_default,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class ExecutionObservation(Generic[T]):
    """Repository-local observation of how a StegCore decision bound execution.

    ``artifact_type`` deliberately distinguishes this object from a continuity
    receipt. Receipt creation and verification remain external to StegCore.
    """

    artifact_type: Literal["stegcore.execution_observation"]
    status: ExecutionStatus
    decision: DecisionResult
    pre_state_hash: str
    post_state_hash: str
    result: Optional[T] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    observed_at: str = ""

    @property
    def executed(self) -> bool:
        return self.status == "executed"


class GovernedRuntime:
    """Bind the canonical StegCore decision to an injected execution callback."""

    def evaluate_and_execute(
        self,
        request: DecisionRequest,
        executor: Callable[[], T],
        *,
        declared_execution_context: Optional[dict[str, Any]] = None,
    ) -> ExecutionObservation[T]:
        context = declared_execution_context or {}
        pre_state = {
            "request": request,
            "declared_execution_context": context,
        }
        pre_state_hash = canonical_hash(pre_state)
        decision = decide(request)
        observed_at = datetime.now(timezone.utc).isoformat()

        if decision.decision != "allow":
            post_state = {
                "decision": decision,
                "status": "refused",
                "result": None,
            }
            return ExecutionObservation(
                artifact_type="stegcore.execution_observation",
                status="refused",
                decision=decision,
                pre_state_hash=pre_state_hash,
                post_state_hash=canonical_hash(post_state),
                observed_at=observed_at,
            )

        try:
            result = executor()
        except Exception as exc:
            post_state = {
                "decision": decision,
                "status": "failed",
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            }
            return ExecutionObservation(
                artifact_type="stegcore.execution_observation",
                status="failed",
                decision=decision,
                pre_state_hash=pre_state_hash,
                post_state_hash=canonical_hash(post_state),
                error_type=type(exc).__name__,
                error_message=str(exc),
                observed_at=observed_at,
            )

        post_state = {
            "decision": decision,
            "status": "executed",
            "result": result,
        }
        return ExecutionObservation(
            artifact_type="stegcore.execution_observation",
            status="executed",
            decision=decision,
            pre_state_hash=pre_state_hash,
            post_state_hash=canonical_hash(post_state),
            result=result,
            observed_at=observed_at,
        )


def governed_execute(
    request: DecisionRequest,
    executor: Callable[[], T],
    *,
    declared_execution_context: Optional[dict[str, Any]] = None,
) -> ExecutionObservation[T]:
    """Convenience function for the default governed runtime boundary."""

    return GovernedRuntime().evaluate_and_execute(
        request,
        executor,
        declared_execution_context=declared_execution_context,
    )
