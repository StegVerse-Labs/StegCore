from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Mapping


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def parse_state_time(value: Any) -> datetime | None:
    """Parse an RFC3339/ISO-8601 timestamp as an aware UTC datetime."""
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


def evaluate_present_state(
    *,
    authority_resolution: Mapping[str, Any],
    target_binding: str | None,
    evaluation_time: datetime,
    evidence_issued_at: str | None = None,
    evidence_valid_until: str | None = None,
    evidence_current: bool | None = None,
) -> dict[str, Any]:
    """Evaluate the minimum present state required before consequence-bearing commit.

    This is a shared state-validation primitive, not a new policy engine. It preserves
    the distinction between an explicit negative state (``DENY``) and an
    unestablished/indeterminate state (``FAIL_CLOSED``). Callers may supply exact
    evidence validity timestamps or an already-governed current-evidence finding.
    """

    authority = dict(authority_resolution)
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

    authority_target = authority.get("target_binding")
    if not target_binding:
        checks["target_current"] = False
        indeterminate.append("candidate_target_unavailable")
    elif not isinstance(authority_target, str) or not authority_target:
        checks["target_current"] = False
        indeterminate.append("authority_target_unestablished")
    elif authority_target != target_binding:
        checks["target_current"] = False
        failures.append("authority_target_mismatch")
    else:
        checks["target_current"] = True

    temporal_scope = str(authority.get("temporal_scope", "bounded")).lower()
    if temporal_scope == "unbounded":
        checks["authority_temporal_current"] = True
    else:
        valid_from = parse_state_time(authority.get("valid_from"))
        valid_until = parse_state_time(authority.get("valid_until"))
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

    if evidence_issued_at is not None or evidence_valid_until is not None:
        issued_at = parse_state_time(evidence_issued_at)
        valid_until = parse_state_time(evidence_valid_until)
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
    elif evidence_current is True:
        checks["evidence_current"] = True
    elif evidence_current is False:
        checks["evidence_current"] = False
        failures.append("evidence_not_current")
    else:
        checks["evidence_current"] = False
        indeterminate.append("evidence_current_state_unestablished")

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


@dataclass(frozen=True)
class CoherenceResult:
    coherent: bool
    checks: dict[str, bool]
    reasons: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "coherent": self.coherent,
            "coherence_checks": dict(self.checks),
            "coherence_reasons": list(self.reasons),
        }


def normalize_capability_surface(
    capability_surface: Mapping[str, Any] | None,
    *,
    action_name: str,
) -> dict[str, Any]:
    raw = dict(capability_surface or {})
    surface: dict[str, Any] = {
        "actions_exposed": sorted(
            {str(item) for item in raw.get("actions_exposed", [action_name])}
        ),
        "execution_mode": str(raw.get("execution_mode", "manual")).lower(),
        "requires_governed_commit": bool(
            raw.get("requires_governed_commit", True)
        ),
    }
    if "parameter_bounds" in raw:
        surface["parameter_bounds"] = raw["parameter_bounds"]
    if "confirmation_required" in raw:
        surface["confirmation_required"] = bool(raw["confirmation_required"])
    return surface


def evaluate_coherence(
    *,
    capability_surface: Mapping[str, Any],
    action: Mapping[str, Any],
    next_state: Mapping[str, Any],
    authority_resolution: Mapping[str, Any],
) -> CoherenceResult:
    reasons: list[str] = []

    authority_status = str(authority_resolution.get("status", "")).lower()
    authority_preserved = (
        authority_status in {"approved", "allow", "allowed", "valid"}
        and authority_resolution.get("basis_invalidated_by_action") is not True
    )
    if not authority_preserved:
        reasons.append("authority_not_preserved")

    execution_mode = str(capability_surface.get("execution_mode", "")).lower()
    denial_preserved = (
        execution_mode not in {"auto", "autonomous", "unbounded"}
        and capability_surface.get("requires_governed_commit") is True
        and action.get("creates_unbounded_chaining") is not True
        and next_state.get("requires_governed_commit") is True
    )
    if not denial_preserved:
        reasons.append("denial_not_preserved")

    required_successor_fields = (
        "state_hash",
        "governance_mode",
        "actor_binding",
        "capability_hash",
    )
    continuation_preserved = (
        all(next_state.get(field) for field in required_successor_fields)
        and str(next_state.get("governance_mode", "")).lower()
        not in {"unguarded", "disabled", "none"}
    )
    if not continuation_preserved:
        reasons.append("continuation_not_preserved")

    checks = {
        "authority_preserved": authority_preserved,
        "denial_preserved": denial_preserved,
        "continuation_preserved": continuation_preserved,
    }
    return CoherenceResult(
        coherent=all(checks.values()),
        checks=checks,
        reasons=tuple(reasons),
    )


def finalize_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    finalized = dict(receipt)
    finalized.pop("receipt_hash", None)
    finalized["receipt_hash"] = canonical_hash(finalized)
    return finalized


def verify_receipt_integrity(receipt: Mapping[str, Any]) -> bool:
    expected = receipt.get("receipt_hash")
    if not isinstance(expected, str) or not expected:
        return False
    unsigned = dict(receipt)
    unsigned.pop("receipt_hash", None)
    return canonical_hash(unsigned) == expected


def coherence_gate(
    *,
    task: str,
    payload: Mapping[str, Any] | None,
    capability_surface: Mapping[str, Any] | None,
    state_hash: str,
    actor_binding: str,
    authority_resolution: Mapping[str, Any],
    previous_receipt_hash: str | None = None,
    governance_mode: str = "governed",
) -> dict[str, Any]:
    surface = normalize_capability_surface(
        capability_surface,
        action_name=task,
    )
    capability_hash = canonical_hash(surface)
    action = {
        "type": task,
        "payload": dict(payload or {}),
    }
    next_state = {
        "state_hash": state_hash,
        "governance_mode": governance_mode,
        "actor_binding": actor_binding,
        "capability_hash": capability_hash,
        "requires_governed_commit": True,
    }
    result = evaluate_coherence(
        capability_surface=surface,
        action=action,
        next_state=next_state,
        authority_resolution=authority_resolution,
    )
    receipt = finalize_receipt(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "decision": "ALLOW" if result.coherent else "DENY",
            "reason": None if result.coherent else "coherence_failed",
            "task": task,
            "state_hash": state_hash,
            "capability_hash": capability_hash,
            "capability_surface": surface,
            "action": action,
            "next_state": next_state,
            "authority_resolution": dict(authority_resolution),
            "coherent": result.coherent,
            "coherence_checks": result.checks,
            "coherence_reasons": list(result.reasons),
            "previous_receipt_hash": previous_receipt_hash,
        }
    )
    return {
        "allowed": result.coherent,
        "receipt": receipt,
        "capability_surface": surface,
        "action": action,
        "next_state": next_state,
    }


def execute_if_coherent(
    *,
    task_runner: Callable[[str, Mapping[str, Any]], Any],
    task: str,
    payload: Mapping[str, Any] | None,
    capability_surface: Mapping[str, Any] | None,
    state_hash: str,
    actor_binding: str,
    authority_resolution: Mapping[str, Any],
    previous_receipt_hash: str | None = None,
) -> dict[str, Any]:
    gate = coherence_gate(
        task=task,
        payload=payload,
        capability_surface=capability_surface,
        state_hash=state_hash,
        actor_binding=actor_binding,
        authority_resolution=authority_resolution,
        previous_receipt_hash=previous_receipt_hash,
    )
    if not gate["allowed"]:
        return {"status": "DENIED", "receipt": gate["receipt"]}

    result = task_runner(task, dict(payload or {}))
    receipt = finalize_receipt(
        {
            key: value
            for key, value in gate["receipt"].items()
            if key != "receipt_hash"
        }
        | {"execution_result": result}
    )
    return {
        "status": "COMPLETED",
        "result": result,
        "receipt": receipt,
    }


def verify_coherence_receipt(
    receipt: Mapping[str, Any],
    *,
    capability_surface: Mapping[str, Any],
    action: Mapping[str, Any],
    next_state: Mapping[str, Any],
    authority_resolution: Mapping[str, Any],
) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if not verify_receipt_integrity(receipt):
        failures.append("receipt_hash_mismatch")

    recomputed = evaluate_coherence(
        capability_surface=capability_surface,
        action=action,
        next_state=next_state,
        authority_resolution=authority_resolution,
    )
    if receipt.get("coherent") is not recomputed.coherent:
        failures.append("coherent_flag_mismatch")
    if receipt.get("coherence_checks") != recomputed.checks:
        failures.append("coherence_checks_mismatch")
    if receipt.get("capability_hash") != next_state.get("capability_hash"):
        failures.append("capability_hash_mismatch")
    return not failures, failures
