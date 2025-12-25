from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Literal


DecisionValue = Literal["allow", "deny", "defer"]


# -------------------------
# Inputs (minimal, docs-aligned)
# -------------------------

@dataclass
class VerifiedReceiptEnvelope:
    """
    Minimal envelope for verified continuity evidence (e.g., from StegID).

    StegCore does not verify receipts. This object must represent an already-verified result.
    """
    receipt_id: str
    key_id: str
    verified: bool
    issued_at: str  # RFC3339 string for now
    prev_receipt_id: Optional[str] = None
    notes: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ActionIntent:
    action: str
    target: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    requested_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    urgency: str = "normal"  # normal | elevated | emergency


@dataclass
class PolicyContext:
    """
    Shape references only (no executable policy rules in v0.1).
    """
    shapes: List[str] = field(default_factory=list)
    scope: Optional[str] = None


@dataclass
class DecisionRequest:
    verified_receipt: Optional[VerifiedReceiptEnvelope]
    actor_class: str  # human | ai | system
    intent: Optional[ActionIntent]
    policy: PolicyContext = field(default_factory=PolicyContext)


# -------------------------
# Output
# -------------------------

@dataclass
class Constraint:
    type: str
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DecisionResult:
    decision: DecisionValue
    reason_code: str
    reason_detail: Dict[str, Any] = field(default_factory=dict)
    constraints: List[Constraint] = field(default_factory=list)
    issued_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# -------------------------
# Reason codes (v0 set mirrors docs)
# -------------------------

REASON = {
    # Continuity
    "receipt_missing": "receipt.missing",
    "receipt_invalid": "receipt.invalid",
    "receipt_insufficient": "receipt.insufficient",

    # Actor / intent
    "actor_class_missing": "actor.class_missing",
    "intent_missing": "intent.missing",
    "intent_unknown": "intent.unknown",

    # Governance
    "requires_quorum": "requires.quorum",
    "requires_guardian": "requires.guardian",
    "requires_veto_window": "requires.veto_window",
    "requires_time_lock": "requires.time_lock",
    "requires_escalation": "requires.escalation",

    # Safety
    "risk_too_high": "risk.too_high",
    "system_degraded": "system.degraded",
}


# -------------------------
# Minimal decision function (no real policy engine)
# -------------------------

def decide(req: DecisionRequest) -> DecisionResult:
    """
    Minimal, deterministic decision interface.

    v0.1 behavior:
    - validate required fields
    - honor receipt verification boolean
    - if policy shapes include constraints, return `defer` with corresponding reason
    - otherwise default to `allow`

    This is NOT a full policy engine.
    """
    if not req.actor_class:
        return DecisionResult("deny", REASON["actor_class_missing"])

    if req.verified_receipt is None:
        return DecisionResult("deny", REASON["receipt_missing"])

    if req.verified_receipt.verified is not True:
        return DecisionResult("deny", REASON["receipt_invalid"])

    if req.intent is None or not req.intent.action or not req.intent.target:
        return DecisionResult("deny", REASON["intent_missing"])

    # Shape-driven deferrals (structure-only)
    shapes = [s.strip().lower() for s in (req.policy.shapes or [])]

    # Priority order (most restrictive first)
    if "escalation" in shapes:
        return DecisionResult("defer", REASON["requires_escalation"], constraints=[Constraint("escalation", {})])

    if "guardian" in shapes:
        return DecisionResult("defer", REASON["requires_guardian"], constraints=[Constraint("guardian", {})])

    if "quorum" in shapes:
        return DecisionResult("defer", REASON["requires_quorum"], constraints=[Constraint("quorum", {})])

    if "veto" in shapes or "veto_window" in shapes:
        return DecisionResult("defer", REASON["requires_veto_window"], constraints=[Constraint("veto_window", {})])

    if "time_lock" in shapes or "timelock" in shapes:
        return DecisionResult("defer", REASON["requires_time_lock"], constraints=[Constraint("time_lock", {})])

    return DecisionResult("allow", "ok")
