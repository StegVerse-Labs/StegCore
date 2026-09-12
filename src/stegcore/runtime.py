from __future__ import annotations

"""Fail-closed execution boundary for StegCore decisions and commit coherence.

The runtime consumes already-verified continuity evidence through ``DecisionRequest``.
It neither verifies nor mints continuity receipts. The injected executor is invoked
only when the existing decision interface returns ``allow`` and the commit-coherence
gate independently preserves authority, denial reachability, and governable
continuation.

Authority and evaluation time are part of the commit-time state. Missing authority,
indeterminate temporal validity, stale continuity evidence, or an authority/target
mismatch must never be synthesized into approval.
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


def _parse_state_time(value: Any) -> Optional[datetime]:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def _present_state_evaluation(
    request: DecisionRequest,
    authority: Mapping[str, Any],
    *,
    evaluation_time: datetime,
) -> dict[str, Any]:
    """Evaluate state that must hold immediately before consequence-bearing commit.

    The result intentionally distinguishes an explicit negative state (``DENY``)
    from an unestablished/indeterminate state (``FAIL_CLOSED``). No result here
    creates authority; it only determines whether the supplied present state is
    sufficient to proceed to the existing coherence gate.
    """

    checks: dict[str, bool] = {}
    failures: list[str] = []
    indeterminate: list[str] = []

    authority_status = str(authority.get("status", "")).lower()
    if authority_status in {"approved", "allow", "allowed", "valid"}:
        checks["authority_current"] = True
    elif authority_status in {"revoked", "denied", "deny", "invalid", "expired"}:
        checks["authority_current"] = False
        failures.append("authority_not_current")
    else:
        checks["authority_current"] = False
        indeterminate.append("authority_state_unestablished")

    intent = request.intent
    authority_target = authority.get("target_binding")
    if intent is None:
        checks["target_current"] = False
        indeterminate.append("intent_target_unavailable")
    elif not isinstance(authority_target, str) or not authority_target:
        checks["target_current"] = False
        indeterminate.append("authority_target_unestablished")
    elif authority_target != intent.target:
        checks["target_current"] = False
        failures.append("authority_target_mismatch")
    else:
        checks["target_current"] = True

    temporal_scope = str(authority.get("temporal_scope", "bounded")).lower()
    if temporal_scope == "unbounded":
        checks["authority_temporal_current"] = True
    else:
        valid_from = _parse_state_time(authority.get("valid_from"))
        valid_until = _parse_state_time(authority.get("valid_until"))
        if valid_from is None or valid_until is None or valid_until < valid_from:
            checks["authority_temporal_current"] = False
            indeterminate.append("authority_temporal_state_unestablished")
        elif evaluation_time < valid_from:
            checks["authority_temporal_current"] = False
            failures.append("authority_not_yet_valid")
        elif evaluation_time > valid_until:
            checks["authority_temporal_current"] = False
            failures.append("authority_expired")
        else:
            checks["authority_temporal_current"] = True

    receipt = request.verified_receipt
    if receipt is None:
        checks["evidence_current"] = False
        indeterminate.append("continuity_evidence_unavailable")
    else:
        issued_at = _parse_state_time(receipt.issued_at)
        valid_until = _parse_state_time(receipt.valid_until)
        if issued_at is None or valid_until is None or valid_until < issued_at:
            checks["evidence_current"] = False
            indeterminate.append("continuity_evidence_freshness_unestablished")
        elif evaluation_time < issued_at:
            checks["evidence_current"] = False
            failures.append("continuity_evidence_not_yet_valid")
        elif evaluation_time > valid_until:
            checks["evidence_current"] = False
            failures.append("continuity_evidence_stale")
        else:
            checks["evidence_current"] = True

    if indeterminate:
        disposition = "FAIL_CLOSED"
        reasons = tuple(indeterminate + failures)
    elif failures:
        disposition = "DENY"
        reasons = tuple(failures)
    else:
        disposition = "ALLOW"
        reasons = ()

    return {
        "allowed": disposition == "ALLOW",
        "disposition": disposition,
        "checks": checks,
        "reasons": reasons,
    }


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
        evaluation_dt = datetime.now(timezone.utc)
        observed_at = evaluation_dt.isoformat()

        # Authority is state, not a convenience default. If no authority state is
        # supplied, retain that absence explicitly so present-state evaluation fails
        # closed before coherence or consequence invocation.
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

        present_state = _present_state_evaluation(
            request,
            authority,
            evaluation_time=evaluation_dt,
        )
        if not present_state["allowed"]:
            receipt = finalize_receipt(
                {
                    "timestamp": observed_at,
                    "decision": present_state["disposition"],
                    "reason": "present_state_not_established",
                    "task": request.intent.action,
                    "state_hash": pre_state_hash,
                    "commit_state": pre_state,
                    "commit_state_hash": pre_state_hash,
                    "evaluation_time": observed_at,
                    "target_binding": request.intent.target,
                    "authority_resolution": authority,
                    "present_state_checks": present_state["checks"],
                    "present_state_reasons": list(present_state["reasons"]),
                    "coherent": False,
                    "coherence_checks": {"present_state_established": False},
                    "coherence_reasons": list(present_state["reasons"]),
                    "previous_receipt_hash": previous_receipt_hash,
                }
            )
            post_state = {
                "decision": asdict(decision),
                "status": "refused",
                "reason": "present_state_not_established",
                "present_state_disposition": present_state["disposition"],
                "coherence_receipt_hash": receipt["receipt_hash"],
                "commit_state_hash": pre_state_hash,
            }
            return ExecutionObservation(
                artifact_type="stegcore.execution_observation",
                status="refused",
                decision=decision,
                pre_state_hash=pre_state_hash,
                post_state_hash=canonical_hash(post_state),
                coherence_receipt=receipt,
                observed_at=observed_at,
            )

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
                "present_state_checks": present_state["checks"],
                "present_state_reasons": list(present_state["reasons"]),
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
