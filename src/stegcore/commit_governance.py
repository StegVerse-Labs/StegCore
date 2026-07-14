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
