#!/usr/bin/env python3
"""
StegCore Emergency Governance Stub (v0.1)

Implements:
- declare_emergency(event)
- verify_ece_and_authorize_spend(spend_intent)
- produce receipts + reason codes

This is a policy boundary: it should be deterministic, testable, and auditable.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple
import time
import uuid

@dataclass
class Decision:
    outcome: str  # "allow" | "defer" | "deny"
    reason_code: str
    constraints: Dict[str, Any]

def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

# In-memory stores (replace with StegDB)
ACTIVE_EMERGENCIES: Dict[str, Dict[str, Any]] = {}
ECE_REGISTRY: Dict[str, Dict[str, Any]] = {}     # envelope_id -> envelope
ECE_SPEND_STATE: Dict[str, Dict[str, Any]] = {}  # envelope_id -> spend totals / buckets

STATE_ORDER = {"watch": 0, "alert": 1, "critical": 2, "catastrophic": 3}

def _state_gte(a: str, b: str) -> bool:
    return STATE_ORDER.get(a, -1) >= STATE_ORDER.get(b, -1)

def _init_ece_state(envelope_id: str):
    if envelope_id not in ECE_SPEND_STATE:
        ECE_SPEND_STATE[envelope_id] = {
            "total_usd": 0.0,
            "minute_bucket": {},
            "hour_bucket": {},
        }

def _bucket_key(period: str) -> str:
    t = time.gmtime()
    if period == "minute":
        return time.strftime("%Y%m%d%H%M", t)
    if period == "hour":
        return time.strftime("%Y%m%d%H", t)
    raise ValueError("bad period")

def declare_emergency(event: Dict[str, Any]) -> Tuple[Decision, Optional[Dict[str, Any]]]:
    """Declare an emergency state from EDM fused output."""
    event_id = event.get("event_id") or f"EDM-{uuid.uuid4().hex[:8]}"
    proposed = event.get("proposed_state", "watch")

    fused_score = float(event.get("fused_score", 0.0))
    conf_low = float(event.get("confidence", {}).get("low", 0.0))
    tth = float(event.get("time_to_harm_minutes", 9999))

    # Minimal deterministic gating (expand later)
    if proposed in ("critical", "catastrophic"):
        if fused_score < 0.85 or conf_low < 0.80:
            return Decision("defer", "EMERG_CONF_TOO_LOW", {"requested_state": proposed}), None
        if tth > 180:
            return Decision("defer", "EMERG_TTH_NOT_IMMINENT", {"requested_state": proposed}), None

    expires_minutes = 180 if proposed == "critical" else 240 if proposed == "catastrophic" else 60
    record = {
        "event_id": event_id,
        "state": proposed,
        "declared_at": now_iso(),
        "expires_at_epoch": time.time() + (expires_minutes * 60),
        "evidence": event.get("evidence", []),
        "confidence": event.get("confidence", {}),
    }
    ACTIVE_EMERGENCIES[event_id] = record
    return Decision("allow", "EMERG_DECLARED", {"state": proposed, "expires_minutes": expires_minutes}), record

def is_emergency_active(event_id: str) -> bool:
    rec = ACTIVE_EMERGENCIES.get(event_id)
    if not rec:
        return False
    if time.time() > rec["expires_at_epoch"]:
        del ACTIVE_EMERGENCIES[event_id]
        return False
    return True

def verify_ece_and_authorize_spend(spend_intent: Dict[str, Any]) -> Tuple[Decision, Optional[Dict[str, Any]]]:
    """Verify envelope constraints and authorize emergency spend."""
    actor = spend_intent.get("actor", "")
    envelope_id = spend_intent.get("envelope_id", "")
    vendor = spend_intent.get("vendor", "")
    asset = spend_intent.get("asset", "")
    amount = float(spend_intent.get("amount_usd", 0.0))
    event_id = spend_intent.get("event_id", "")

    if amount <= 0:
        return Decision("deny", "ECE_BAD_AMOUNT", {}), None

    if not is_emergency_active(event_id):
        return Decision("deny", "ECE_NO_ACTIVE_EMERGENCY", {"event_id": event_id}), None

    ece = ECE_REGISTRY.get(envelope_id)
    if not ece:
        return Decision("deny", "ECE_NOT_FOUND", {"envelope_id": envelope_id}), None

    if actor not in ece.get("authorized_entities", []):
        return Decision("deny", "ECE_ACTOR_NOT_AUTHORIZED", {"actor": actor}), None

    em_state = ACTIVE_EMERGENCIES[event_id]["state"]
    if not _state_gte(em_state, "critical"):
        return Decision("deny", "ECE_STATE_TOO_LOW", {"state": em_state}), None

    if vendor not in ece.get("allowed_targets", []):
        return Decision("deny", "ECE_VENDOR_NOT_ALLOWED", {"vendor": vendor}), None
    if asset not in ece.get("allowed_assets", []):
        return Decision("deny", "ECE_ASSET_NOT_ALLOWED", {"asset": asset}), None

    # Time bound: compare against emergency declaration time
    declared_epoch = time.mktime(time.strptime(ACTIVE_EMERGENCIES[event_id]["declared_at"], "%Y-%m-%dT%H:%M:%SZ"))
    elapsed_min = (time.time() - declared_epoch) / 60.0
    if elapsed_min > float(ece.get("time_bound_minutes", 0)):
        return Decision("deny", "ECE_TIME_EXPIRED", {"elapsed_min": elapsed_min}), None

    limits = ece.get("spend_limits", {})
    max_per_minute = float(limits.get("max_per_minute_usd", 0))
    max_per_hour = float(limits.get("max_per_hour_usd", 0))
    max_total = float(limits.get("max_total_usd", 0))

    _init_ece_state(envelope_id)
    st = ECE_SPEND_STATE[envelope_id]

    minute_key = _bucket_key("minute")
    hour_key = _bucket_key("hour")

    minute_spent = float(st["minute_bucket"].get(minute_key, 0.0))
    hour_spent = float(st["hour_bucket"].get(hour_key, 0.0))
    total_spent = float(st["total_usd"])

    if max_total and (total_spent + amount) > max_total:
        return Decision("deny", "ECE_CAP_TOTAL_EXCEEDED", {"remaining": max_total - total_spent}), None
    if max_per_minute and (minute_spent + amount) > max_per_minute:
        return Decision("deny", "ECE_CAP_MINUTE_EXCEEDED", {"remaining": max_per_minute - minute_spent}), None
    if max_per_hour and (hour_spent + amount) > max_per_hour:
        return Decision("deny", "ECE_CAP_HOUR_EXCEEDED", {"remaining": max_per_hour - hour_spent}), None

    st["total_usd"] = total_spent + amount
    st["minute_bucket"][minute_key] = minute_spent + amount
    st["hour_bucket"][hour_key] = hour_spent + amount

    receipt = {
        "receipt_id": f"ece_{uuid.uuid4().hex[:12]}",
        "timestamp": now_iso(),
        "event_id": event_id,
        "envelope_id": envelope_id,
        "actor": actor,
        "vendor": vendor,
        "asset": asset,
        "amount_usd": amount,
        "decision": {"outcome": "allow", "reason_code": "ECE_SPEND_ALLOWED"},
        "justification": spend_intent.get("justification", ""),
    }
    return Decision("allow", "ECE_SPEND_ALLOWED", {"receipt_id": receipt["receipt_id"]}), receipt

def register_ece(envelope: Dict[str, Any]) -> None:
    eid = envelope["envelope_id"]
    ECE_REGISTRY[eid] = envelope
    _init_ece_state(eid)
