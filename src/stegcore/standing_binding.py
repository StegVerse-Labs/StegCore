from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Mapping

from .steggate import (
    AdmissibilityEvaluation,
    AdmissibilityRequest,
    MatrixEntry,
    canonical_sha256,
    evaluate_admissibility,
)

SDK_ENVELOPE_SCHEMA = "stegverse.sdk.spe_commitment_intake.v0.1"
SPE_RECEIPT_SCHEMA = "stegverse.spe.sdk_commitment_intake.v0.1"
BRIDGE_SCHEMA = "stegverse.sdk.spe-steggate-bridge.v1"
CANONICAL_STEGGATE_RUNTIME = "stegverse:steggate:canonical:three-layer:v1"


def _stable_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _required_text(value: Any, name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{name} is required")
    return text


def _hex64(value: Any, name: str) -> str:
    text = _required_text(value, name).lower()
    if len(text) != 64 or any(char not in "0123456789abcdef" for char in text):
        raise ValueError(f"{name} must be 64 lowercase hex characters")
    return text


def _sha256_locator(value: Any, name: str) -> str:
    text = _required_text(value, name).lower()
    if not text.startswith("sha256:"):
        raise ValueError(f"{name} must use sha256: prefix")
    _hex64(text[7:], name)
    return text


def _time(value: Any, name: str) -> datetime:
    text = _required_text(value, name)
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"{name} must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{name} must include timezone")
    return parsed.astimezone(timezone.utc)


def _standing_current(candidate: Mapping[str, Any], observed_at: str) -> bool:
    observed = _time(observed_at, "standing_evidence.observed_at")
    window = candidate.get("validity_window")
    if not isinstance(window, Mapping):
        raise ValueError("candidate validity_window must be object")
    not_before = window.get("not_before")
    not_after = window.get("not_after")
    if not_before is not None and observed < _time(not_before, "validity_window.not_before"):
        return False
    if not_after is not None and observed > _time(not_after, "validity_window.not_after"):
        return False
    return True


def verify_spe_standing_binding(evidence: Mapping[str, Any]) -> dict[str, Any]:
    """Independently re-hash the SDK/SPE/bridge objects inside canonical StegCore."""
    value = dict(evidence)
    if value.get("required") is not True:
        raise ValueError("standing evidence must declare required=true")
    expected = value.get("expected_interlock")
    if not isinstance(expected, Mapping):
        raise ValueError("expected_interlock is required")

    package_id = _required_text(expected.get("package_id"), "expected_interlock.package_id")
    transition_id = _required_text(expected.get("transition_id"), "expected_interlock.transition_id")
    run_id = _required_text(expected.get("run_id"), "expected_interlock.run_id")
    participant_id = _required_text(expected.get("participant_id"), "expected_interlock.participant_id")
    ingress_hash = _sha256_locator(expected.get("ingress_interlock_hash"), "expected_interlock.ingress_interlock_hash")

    envelope = value.get("spe_envelope")
    receipt = value.get("spe_receipt")
    bridge = value.get("steggate_bridge")
    if not all(isinstance(item, Mapping) for item in (envelope, receipt, bridge)):
        raise ValueError("standing evidence requires envelope, receipt, and bridge objects")
    envelope = dict(envelope)
    receipt = dict(receipt)
    bridge = dict(bridge)

    if envelope.get("schema_version") != SDK_ENVELOPE_SCHEMA:
        raise ValueError("unsupported SDK SPE envelope schema")
    if envelope.get("destination_repo") != "StegVerse-Labs/Standing-Proof-Engine":
        raise ValueError("SPE envelope destination mismatch")
    if envelope.get("route_purpose") != "FRESH_STANDING_DETERMINATION":
        raise ValueError("SPE envelope route purpose mismatch")
    candidate = envelope.get("candidate")
    if not isinstance(candidate, Mapping):
        raise ValueError("SPE envelope candidate must be object")
    candidate = dict(candidate)
    if candidate.get("authorizing") is not False:
        raise ValueError("SPE candidate must remain non-authorizing")
    if candidate.get("requires_fresh_standing_determination") is not True:
        raise ValueError("fresh standing determination must be required")
    candidate_core = dict(candidate)
    claimed_candidate_hash = _hex64(candidate_core.pop("candidate_hash", None), "candidate_hash")
    if _stable_hash(candidate_core) != claimed_candidate_hash:
        raise ValueError("candidate_hash mismatch")
    if envelope.get("candidate_hash") != claimed_candidate_hash:
        raise ValueError("envelope candidate_hash mismatch")
    envelope_core = dict(envelope)
    claimed_envelope_hash = _hex64(envelope_core.pop("envelope_hash", None), "envelope_hash")
    if _stable_hash(envelope_core) != claimed_envelope_hash:
        raise ValueError("envelope_hash mismatch")

    if receipt.get("schema_version") != SPE_RECEIPT_SCHEMA:
        raise ValueError("unsupported SPE standing receipt schema")
    if receipt.get("receipt_type") != "SPE_STANDING_DETERMINATION":
        raise ValueError("unexpected SPE receipt type")
    if receipt.get("source_repo") != "StegVerse-org/StegVerse-SDK":
        raise ValueError("SPE receipt source mismatch")
    if receipt.get("destination_repo") != "StegVerse-Labs/Standing-Proof-Engine":
        raise ValueError("SPE receipt destination mismatch")
    for field in ("package_id", "transition_id", "run_id", "candidate_hash", "envelope_hash"):
        if receipt.get(field) != envelope.get(field):
            raise ValueError(f"SPE receipt {field} mismatch")
    if receipt.get("standing_result") != "ALLOW":
        raise ValueError("SPE standing does not allow canonical progression")
    if receipt.get("execution_authorized") is not False:
        raise ValueError("SPE receipt cannot authorize execution")
    if receipt.get("execution_performed") is not False:
        raise ValueError("SPE receipt cannot claim execution")
    if receipt.get("master_record_installed") is not False:
        raise ValueError("SPE receipt cannot claim a Master Records organization record")
    receipt_core = dict(receipt)
    receipt_hash = _hex64(receipt_core.pop("receipt_hash", None), "receipt_hash")
    if _stable_hash(receipt_core) != receipt_hash:
        raise ValueError("SPE receipt_hash mismatch")

    for field, expected_value in (("package_id", package_id), ("transition_id", transition_id), ("run_id", run_id)):
        if envelope.get(field) != expected_value:
            raise ValueError(f"standing {field} mismatch")

    if bridge.get("schema") != BRIDGE_SCHEMA:
        raise ValueError("unsupported SPE StegGate bridge schema")
    bridge_core = dict(bridge)
    bridge_hash = _hex64(bridge_core.pop("bridge_hash", None), "bridge_hash")
    if _stable_hash(bridge_core) != bridge_hash:
        raise ValueError("bridge_hash mismatch")
    for field, expected_value in (("package_id", package_id), ("transition_id", transition_id), ("run_id", run_id)):
        if bridge.get(field) != expected_value:
            raise ValueError(f"bridge {field} mismatch")
    interlock = bridge.get("interlock") or {}
    if interlock.get("ingress_interlock_hash") != ingress_hash:
        raise ValueError("bridge ingress interlock hash mismatch")
    if interlock.get("participant_id") != participant_id:
        raise ValueError("bridge participant identity mismatch")
    standing = bridge.get("standing_binding") or {}
    if standing.get("receipt_hash") != receipt_hash:
        raise ValueError("bridge standing receipt hash mismatch")
    if standing.get("candidate_hash") != claimed_candidate_hash:
        raise ValueError("bridge candidate hash mismatch")
    if standing.get("envelope_hash") != claimed_envelope_hash:
        raise ValueError("bridge envelope hash mismatch")
    if standing.get("standing_result") != "ALLOW" or standing.get("standing_current") is not True:
        raise ValueError("bridge standing is not current ALLOW")
    if standing.get("execution_authorized") is not False:
        raise ValueError("standing binding cannot authorize execution")
    observed_at = _required_text(standing.get("observed_at"), "standing_binding.observed_at")
    if not _standing_current(candidate, observed_at):
        raise ValueError("SPE standing validity window is not current")

    admissibility = bridge.get("admissibility_candidate") or {}
    if admissibility.get("runtime_identity") != CANONICAL_STEGGATE_RUNTIME:
        raise ValueError("canonical StegGate runtime identity mismatch")
    if admissibility.get("decision") != "PENDING":
        raise ValueError("upstream bridge cannot decide admissibility")
    predicates = admissibility.get("permission_predicates") or {}
    if predicates.get("consent_or_standing_required") is not True:
        raise ValueError("standing requirement is not bound")
    if predicates.get("consent_or_standing_current") is not True:
        raise ValueError("current standing predicate is not bound")
    authority = bridge.get("authority") or {}
    if authority.get("sdk_authority") != "NONE":
        raise ValueError("SDK authority escalation")
    if authority.get("spe_execution_authority") != "NONE":
        raise ValueError("SPE execution authority escalation")
    if authority.get("execution_authorized") is not False:
        raise ValueError("bridge cannot authorize execution")
    if authority.get("master_records_custody_claimed") is not False:
        raise ValueError("bridge cannot claim a Master Records organization record")

    return {
        "verified": True,
        "package_id": package_id,
        "transition_id": transition_id,
        "run_id": run_id,
        "participant_id": participant_id,
        "ingress_interlock_hash": ingress_hash,
        "candidate_hash": claimed_candidate_hash,
        "envelope_hash": claimed_envelope_hash,
        "receipt_hash": receipt_hash,
        "bridge_hash": bridge_hash,
        "standing_result": "ALLOW",
        "standing_current": True,
        "authority_effect": "NONE",
    }


def evaluate_admissibility_with_standing(
    request: AdmissibilityRequest,
    declared_execution_context: Mapping[str, Any] | None,
) -> AdmissibilityEvaluation:
    """Canonical admissibility plus exact standing evidence when the route requires it."""
    evaluation = evaluate_admissibility(request)
    context = dict(declared_execution_context or {})
    if context.get("standing_required") is not True:
        return evaluation

    state = "PASS"
    reason = "spe_standing_binding_verified"
    observed: Any
    try:
        observed = verify_spe_standing_binding(context.get("standing_evidence") or {})
    except (TypeError, ValueError) as exc:
        state = "FAIL"
        reason = f"spe_standing_binding_invalid:{exc}"
        observed = {"verified": False, "error": str(exc)}

    row = MatrixEntry(
        predicate="standing.spe_binding",
        state=state,
        observed=observed,
        reason=reason,
        authority_surface="standing_proof_engine_binding",
    )
    body = evaluation.model_dump(mode="json", exclude={"decision_state_hash"})
    body["matrix"] = [item.model_dump(mode="json") for item in evaluation.matrix] + [row.model_dump(mode="json")]
    if state != "PASS":
        body["disposition"] = "FAIL_CLOSED"
        body["reasons"] = [reason]
    else:
        body["reasons"] = list(evaluation.reasons)
    return AdmissibilityEvaluation(**body, decision_state_hash=canonical_sha256(body))


__all__ = [
    "verify_spe_standing_binding",
    "evaluate_admissibility_with_standing",
]
