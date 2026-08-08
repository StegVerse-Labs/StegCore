#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTEXT = ROOT / "data" / "steggate-session-context.json"
RECEIPT = ROOT / "data" / "steggate-session-continuity-receipt.json"

REQUIRED_DISPOSITIONS = {"ALLOW", "DENY", "REVIEW", "FAIL_CLOSED"}
REQUIRED_REALITY_PLANES = {"decision", "execution", "observed"}


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical(value)).hexdigest()


def validate_context(context: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    if context.get("schema") != "stegverse.steggate_session_context.v1":
        findings.append("schema_invalid")
    if not context.get("goal_id"):
        findings.append("goal_id_missing")
    if not context.get("canonical_issue"):
        findings.append("canonical_issue_missing")
    if not context.get("canonical_handoff"):
        findings.append("canonical_handoff_missing")

    architectural = context.get("architectural_context") or {}
    if architectural.get("decision_py_is_intentionally_minimal") is not True:
        findings.append("minimal_interface_context_missing")
    if architectural.get("minimal_means_interface_scope_not_resource_budget") is not True:
        findings.append("minimal_interface_meaning_not_preserved")
    if architectural.get("minimal_interface_does_not_prove_missing_system_engine") is not True:
        findings.append("anti_duplication_context_missing")
    if architectural.get("complete_decision_state_is_reconstructable_reality") is not True:
        findings.append("decision_state_reconstruction_context_missing")
    if set(architectural.get("required_dispositions") or []) != REQUIRED_DISPOSITIONS:
        findings.append("required_dispositions_incomplete")
    if set(architectural.get("reality_planes") or []) != REQUIRED_REALITY_PLANES:
        findings.append("reality_planes_incomplete")

    guard = context.get("archive_guard") or {}
    if guard.get("historical_context_loss_is_failure") is not True:
        findings.append("historical_context_loss_guard_missing")
    if len(guard.get("required_before_archive") or []) < 5:
        findings.append("archive_preconditions_incomplete")

    current = context.get("current_work") or {}
    worker = context.get("worker_policy") or {}
    if not current.get("implementation_owner"):
        findings.append("implementation_owner_missing")
    if not worker.get("next_action"):
        findings.append("next_action_missing")
    if not worker.get("machine_observable_release_conditions"):
        findings.append("release_conditions_missing")

    active = context.get("session_state") == "ACTIVE_UNIQUE_WORK_REMAINS"
    if active and context.get("archive_allowed") is not False:
        findings.append("active_session_archive_must_be_false")
    if active and worker.get("archive_status_when_active") != "DO_NOT_ARCHIVE":
        findings.append("active_archive_status_invalid")
    return findings


def build_receipt(context: dict[str, Any]) -> dict[str, Any]:
    findings = validate_context(context)
    active = context.get("session_state") == "ACTIVE_UNIQUE_WORK_REMAINS"
    body = {
        "schema": "stegverse.steggate_session_continuity_receipt.v1",
        "goal_id": context.get("goal_id"),
        "context_digest": digest(context),
        "state": "PASS" if not findings else "FAIL_CLOSED",
        "archive_allowed": False if active else bool(context.get("archive_allowed", False)),
        "historical_context_preserved": not findings,
        "architecture_reconciliation_state": (context.get("current_work") or {}).get("architecture_reconciliation_state"),
        "deployment_state": (context.get("current_work") or {}).get("deployment_state"),
        "next_action": (context.get("worker_policy") or {}).get("next_action"),
        "findings": sorted(findings),
    }
    return {**body, "receipt_digest": digest(body)}


def main() -> int:
    try:
        context = json.loads(CONTEXT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        receipt = {
            "schema": "stegverse.steggate_session_continuity_receipt.v1",
            "state": "FAIL_CLOSED",
            "archive_allowed": False,
            "historical_context_preserved": False,
            "findings": [f"context_unreadable:{type(exc).__name__}"],
            "next_action": "Restore the canonical StegGate session context before continuing or archiving.",
        }
        receipt["receipt_digest"] = digest(receipt)
        RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(receipt, sort_keys=True))
        return 1

    receipt = build_receipt(context)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt["state"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
