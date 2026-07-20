"""Dependency-free conformance checks for staged StegVerse v1.3 artifacts.

This module validates the minimum execution semantics documented in
``docs/spec/STEGVERSE_SPEC_V1_3.md``. It does not claim JSON Schema compliance,
formal verification, or production authority.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

DECISIONS = {"ALLOW", "DENY", "FAIL_CLOSED"}
HEX64 = set("0123456789abcdefABCDEF")


class ConformanceError(ValueError):
    pass


def require_fields(record: dict[str, Any], fields: Iterable[str], kind: str) -> None:
    missing = [field for field in fields if field not in record]
    if missing:
        raise ConformanceError(f"{kind}: missing required fields: {', '.join(missing)}")


def require_digest(value: Any, field: str) -> None:
    if not isinstance(value, str) or len(value) != 64 or any(ch not in HEX64 for ch in value):
        raise ConformanceError(f"{field}: expected 64-character hexadecimal digest")


def validate_action_request(record: dict[str, Any]) -> None:
    require_fields(record, ("transition_id", "action", "actor_identity", "scope", "policy_reference", "policy_version", "evidence_references", "execution_context", "validity_window", "recoverability_profile", "state_digest"), "action_request")
    if not record["scope"]:
        raise ConformanceError("action_request: scope must not be empty")
    if not record["evidence_references"]:
        raise ConformanceError("action_request: missing evidence must fail closed")
    require_digest(record["state_digest"], "action_request.state_digest")


def validate_decision_receipt(record: dict[str, Any]) -> None:
    require_fields(record, ("transition_id", "decision", "reason_codes", "policy_reference", "policy_version", "state_digest", "evaluator_version", "evaluated_at", "receipt_digest"), "decision_receipt")
    if record["decision"] not in DECISIONS:
        raise ConformanceError("decision_receipt: invalid decision")
    if not record["reason_codes"]:
        raise ConformanceError("decision_receipt: at least one reason code is required")
    require_digest(record["state_digest"], "decision_receipt.state_digest")
    require_digest(record["receipt_digest"], "decision_receipt.receipt_digest")


def validate_commit_time(request: dict[str, Any], decision: dict[str, Any], current_policy_version: str, current_state_digest: str) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if decision.get("decision") != "ALLOW":
        reasons.append("PRIOR_DECISION_NOT_ALLOW")
    if request.get("policy_version") != decision.get("policy_version"):
        reasons.append("REQUEST_DECISION_POLICY_MISMATCH")
    if current_policy_version != decision.get("policy_version"):
        reasons.append("POLICY_DRIFT")
    if request.get("state_digest") != decision.get("state_digest"):
        reasons.append("REQUEST_DECISION_STATE_MISMATCH")
    if current_state_digest != decision.get("state_digest"):
        reasons.append("STATE_DRIFT")
    return not reasons, reasons


def validate_execution_receipt(record: dict[str, Any]) -> None:
    require_fields(record, ("transition_id", "decision_receipt_digest", "commit_time_valid", "execution_status", "executed_at", "effect_references", "receipt_digest"), "execution_receipt")
    require_digest(record["decision_receipt_digest"], "execution_receipt.decision_receipt_digest")
    require_digest(record["receipt_digest"], "execution_receipt.receipt_digest")
    if record["commit_time_valid"] is False and record["execution_status"] != "BLOCKED":
        raise ConformanceError("execution_receipt: invalid commit-time state must be BLOCKED")


def validate_replay_result(record: dict[str, Any]) -> None:
    require_fields(record, ("transition_id", "original_decision", "replayed_decision", "original_state_digest", "replay_state_digest", "evaluator_version", "matches_original", "divergence_codes", "replayed_at"), "replay_result")
    require_digest(record["original_state_digest"], "replay_result.original_state_digest")
    require_digest(record["replay_state_digest"], "replay_result.replay_state_digest")
    expected_match = record["original_decision"] == record["replayed_decision"] and record["original_state_digest"] == record["replay_state_digest"]
    if bool(record["matches_original"]) != expected_match:
        raise ConformanceError("replay_result: matches_original contradicts replay evidence")
    if expected_match and record["divergence_codes"]:
        raise ConformanceError("replay_result: matching replay cannot contain divergence codes")
    if not expected_match and not record["divergence_codes"]:
        raise ConformanceError("replay_result: divergence requires at least one divergence code")


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ConformanceError(f"{path}: expected JSON object")
    return data
