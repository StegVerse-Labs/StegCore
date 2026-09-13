from __future__ import annotations

"""Canonical CGE decision-issuer adapter backed by StegCore admissibility.

This module issues decision/closure artifacts only. It does not execute the
admitted action, mutate canonical state, mint TV/TVC execution grants, perform
provider operations, or move data across Interlock/InTr. Master Records remains
custody/reconstruction owner and Interlock/InTr remains the transition executor.
"""

from datetime import datetime, timedelta, timezone
import hashlib
import json
from typing import Any, Mapping

from .steggate import AdmissibilityRequest, evaluate_admissibility

ISSUER_ID = "STEGCORE-CGE-DECISION-ISSUER"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def _hash_receipt(value: Mapping[str, Any], field: str) -> dict[str, Any]:
    out = dict(value)
    out[field] = sha256({k: v for k, v in out.items() if k != field})
    return out


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def _route_provider(route: Mapping[str, Any]) -> str:
    provider = route.get("provider")
    if isinstance(provider, Mapping):
        value = provider.get("provider_id")
        if isinstance(value, str) and value:
            return value
    value = route.get("provider_id")
    _require(isinstance(value, str) and bool(value), "provider_id_missing")
    return str(value)


def _authority_hash(authority: Mapping[str, Any]) -> str:
    expected = authority.get("authority_evidence_sha256")
    observed = sha256({k: v for k, v in authority.items() if k != "authority_evidence_sha256"})
    _require(isinstance(expected, str) and expected == observed, "authority_evidence_hash_mismatch")
    _require(authority.get("authority_valid") is True, "authority_evidence_not_valid")
    return observed


def issue_service_decision(
    *,
    route: Mapping[str, Any],
    authority_evidence: Mapping[str, Any],
    admissibility_request: Mapping[str, Any],
    subject_request_ref: str,
    repository_state_sha256: str,
    now: datetime | None = None,
    ttl_seconds: int = 600,
) -> dict[str, Any]:
    """Evaluate one exact service route and emit CGE + closure artifacts.

    ``admissibility_request`` must be a complete StegGate request assembled by a
    caller from authentic current state. Missing/unknown predicates therefore
    fail closed through the canonical StegGate evaluator rather than being filled
    optimistically by this issuer.
    """

    _require(ttl_seconds > 0 and ttl_seconds <= 900, "ttl_out_of_bounds")
    _require(isinstance(subject_request_ref, str) and bool(subject_request_ref), "subject_request_ref_required")
    _require(isinstance(repository_state_sha256, str) and len(repository_state_sha256) == 64, "repository_state_sha256_invalid")

    for field in ("request_id", "request_sha256", "route_sha256", "service_id"):
        _require(isinstance(route.get(field), str) and bool(route.get(field)), f"route_{field}_required")
        _require(authority_evidence.get(field) == route.get(field), f"authority_{field}_mismatch")
    provider_id = _route_provider(route)
    _require(authority_evidence.get("provider_id") == provider_id, "authority_provider_id_mismatch")
    authority_hash = _authority_hash(authority_evidence)

    request = AdmissibilityRequest.model_validate(dict(admissibility_request))
    evaluation = evaluate_admissibility(request)
    _require(request.candidate.action == route["service_id"], "candidate_action_service_mismatch")

    timestamp = now or datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    issued_at = timestamp.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    expires_at = (timestamp + timedelta(seconds=ttl_seconds)).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    disposition = evaluation.disposition
    authority_class = {
        "ALLOW": "allowed",
        "DENY": "denied",
        "REVIEW": "requires-human-review",
        "FAIL_CLOSED": "fail-closed",
    }[disposition]
    execution_scope = [route["service_id"]] if disposition == "ALLOW" else []
    tvc_admissibility = {
        "ALLOW": "ADMIT",
        "DENY": "DENY",
        "REVIEW": "DEFER",
        "FAIL_CLOSED": "DEFER",
    }[disposition]
    review_posture = {
        "ALLOW": "CGE_REVIEW_ACCEPTED",
        "DENY": "CGE_REVIEW_DENIED",
        "REVIEW": "CGE_REVIEW_DEFERRED",
        "FAIL_CLOSED": "CGE_REVIEW_BLOCKED",
    }[disposition]

    authority_receipt_id = "MR.AUTHORITY_RECEIPT." + route["request_id"].upper().replace("/", "-")
    authority_receipt = _hash_receipt(
        {
            "schema_version": "authority_context_receipt.v0.1",
            "receipt_id": authority_receipt_id,
            "issued_at": issued_at,
            "issuer": {"authority_system": "CGE_MASTER_RECORDS", "issuer_id": ISSUER_ID},
            "subject_request_ref": subject_request_ref,
            "authority_class": authority_class,
            "authority_scope": [route["service_id"]],
            "authority_source_refs": [f"sha256:{authority_hash}"],
            "authority_proven": True,
            "execution_authority_granted": False,
            "credential_authority": "TV/TVC",
            "supersedes_receipt_ref": None,
        },
        "receipt_sha256",
    )

    policy_state = {
        "policy_ref": request.execution.policy_ref,
        "delegation_ref": request.execution.delegation_ref,
        "policy_current": request.execution.policy_current,
        "delegation_current": request.execution.delegation_current,
        "validity_window_open": request.execution.validity_window_open,
    }
    evidence_state = {
        "judgment_evidence_refs": request.judgment.evidence_refs,
        "execution_evidence_refs": request.execution.evidence_refs,
        "signal_refs": request.signal.admitted_signal_refs,
        "decision_state_hash": evaluation.decision_state_hash,
    }
    unresolved_conditions = sorted({
        row.reason
        for row in evaluation.matrix
        if row.state in {"UNKNOWN", "REVIEW"}
    })
    commit_decision = "PROCEED" if disposition == "ALLOW" else ("DENY" if disposition == "DENY" else "PAUSE")
    commit_receipt_id = "MR.COMMIT_TIME_RECEIPT." + route["request_id"].upper().replace("/", "-")
    commit_receipt = _hash_receipt(
        {
            "schema_version": "commit_time_admissibility_receipt.v0.1",
            "receipt_id": commit_receipt_id,
            "evaluated_at": issued_at,
            "issuer": {"evaluation_system": "STEGCORE", "issuer_id": ISSUER_ID},
            "subject_request_ref": subject_request_ref,
            "candidate_action_sha256": evaluation.candidate_hash,
            "policy_state_sha256": sha256(policy_state),
            "evidence_state_sha256": sha256(evidence_state),
            "authority_context_receipt_ref": authority_receipt_id,
            "authority_context_sha256": authority_receipt["receipt_sha256"],
            "repository_state_sha256": repository_state_sha256,
            "unresolved_conditions": unresolved_conditions,
            "decision": commit_decision,
            "decision_reason": ";".join(evaluation.reasons) if evaluation.reasons else "admissibility_evaluation_complete",
            "execution_authority_granted": False,
            "credential_authority": "TV/TVC",
        },
        "receipt_sha256",
    )

    cge_decision = {
        "schema": {"name": "stegverse.cge_admissibility_decision", "version": "1.0.0"},
        "request_id": route["request_id"],
        "request_sha256": route["request_sha256"],
        "route_sha256": route["route_sha256"],
        "provider_id": provider_id,
        "service_id": route["service_id"],
        "authority_evidence_sha256": authority_hash,
        "admissibility": tvc_admissibility,
        "execution_scope": execution_scope,
        "review_posture": review_posture,
        "stegcore_disposition": disposition,
        "stegcore_decision_state_sha256": evaluation.decision_state_hash,
        "authority_context_receipt_sha256": authority_receipt["receipt_sha256"],
        "commit_time_admissibility_receipt_sha256": commit_receipt["receipt_sha256"],
        "issued_at": issued_at,
        "expires_at": expires_at,
        "execution_authorized_by_cge": False,
        "transition_executed": False,
        "transition_executor": "Interlock/InTr",
        "credential_authority": "TV/TVC",
    }
    cge_decision["decision_sha256"] = sha256(cge_decision)

    return {
        "schema": "stegcore.cge_decision_issuer_result/v1",
        "state": review_posture,
        "evaluation": evaluation.model_dump(mode="json"),
        "authority_context_receipt": authority_receipt,
        "commit_time_admissibility_receipt": commit_receipt,
        "cge_decision": cge_decision,
        "execution_performed": False,
        "canonical_state_mutated": False,
        "transition_executor": "Interlock/InTr",
        "master_records_custody_required": True,
        "credential_authority": "TV/TVC",
        "authority_effect": "CGE_DECISION_ISSUED_ONLY",
    }
