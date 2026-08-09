#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTEXT = ROOT / "data" / "steggate-session-context.json"
ARCHITECTURE = ROOT / "data" / "steggate-architecture-reconciliation-state.json"
RECEIPT = ROOT / "data" / "steggate-session-continuity-receipt.json"

REQUIRED_DISPOSITIONS = {"ALLOW", "DENY", "REVIEW", "FAIL_CLOSED"}
REQUIRED_REALITY_PLANES = {"decision", "execution", "observed"}
REQUIRED_CLASSIFICATIONS = {
    "ADAPTER_TO_EXISTING_CANONICAL_ENGINE",
    "NORMALIZATION_OF_EXISTING_CANONICAL_RESULTS",
    "NEW_REQUIRED_SEMANTIC_NOT_PRESENT_ELSEWHERE",
    "DUPLICATE_REMOVE_OR_REFACTOR",
}


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
    if not architectural.get("existing_canonical_layers"):
        findings.append("canonical_layers_missing")
    if not architectural.get("reconciliation_record"):
        findings.append("reconciliation_record_missing")

    guard = context.get("archive_guard") or {}
    if guard.get("historical_context_loss_is_failure") is not True:
        findings.append("historical_context_loss_guard_missing")
    if len(guard.get("required_before_archive") or []) < 5:
        findings.append("archive_preconditions_incomplete")

    current = context.get("current_work") or {}
    worker = context.get("worker_policy") or {}
    if not current.get("implementation_owner"):
        findings.append("implementation_owner_missing")
    if not current.get("provisional_files"):
        findings.append("provisional_file_inventory_missing")
    if not worker.get("next_action"):
        findings.append("next_action_missing")
    if not worker.get("machine_observable_release_conditions"):
        findings.append("release_conditions_missing")

    goal_complete = context.get("goal_activation_complete") is True
    if not goal_complete:
        state = context.get("session_state")
        if state == "ACTIVE_UNIQUE_WORK_REMAINS":
            if context.get("archive_allowed") is not False:
                findings.append("active_incomplete_goal_archive_must_be_false")
            if context.get("conversation_archive_allowed") is not False:
                findings.append("active_incomplete_goal_conversation_archive_must_be_false")
            if worker.get("archive_status_when_active") != "DO_NOT_ARCHIVE_UNTIL_GOAL_ACTIVATED_OR_DURABLY_TRANSFERRED":
                findings.append("incomplete_goal_archive_status_invalid")
        elif state == "MERGED_INTO_CANONICAL_WORKSTREAM":
            consolidation = context.get("session_consolidation") or {}
            if consolidation.get("all_unique_context_transferred") is not True:
                findings.append("merged_session_unique_context_not_transferred")
            if consolidation.get("machine_owned_continuation") is not True:
                findings.append("merged_session_continuation_not_machine_owned")
            if not consolidation.get("canonical_locations"):
                findings.append("merged_session_canonical_locations_missing")
            if not consolidation.get("remaining_tasks"):
                findings.append("merged_session_remaining_tasks_missing")
            if context.get("archive_allowed") is not True:
                findings.append("merged_session_archive_must_be_true")
            if context.get("conversation_archive_allowed") is not True:
                findings.append("merged_session_conversation_archive_must_be_true")
        else:
            findings.append("incomplete_goal_session_state_invalid")
    return findings


def validate_architecture(architecture: dict[str, Any], context: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    state = architecture.get("state")
    if architecture.get("schema") != "stegverse.steggate_architecture_reconciliation.v1":
        findings.append("architecture_schema_invalid")
    if architecture.get("goal_id") != context.get("goal_id"):
        findings.append("architecture_goal_mismatch")
    if architecture.get("canonical_issue") != context.get("canonical_issue"):
        findings.append("architecture_owner_mismatch")
    if not architecture.get("canonical_layers"):
        findings.append("architecture_canonical_layers_missing")
    if not architecture.get("next_action"):
        findings.append("architecture_next_action_missing")

    if state == "COMPLETE":
        if not architecture.get("canonical_call_graph"):
            findings.append("architecture_complete_call_graph_missing")
        if not architecture.get("reconciled_live_service"):
            findings.append("architecture_complete_service_reconciliation_missing")
        if not architecture.get("removed_duplication"):
            findings.append("architecture_complete_duplication_record_missing")
    else:
        if not architecture.get("provisional_layers"):
            findings.append("architecture_provisional_layers_missing")
        if set(architecture.get("required_classifications") or []) != REQUIRED_CLASSIFICATIONS:
            findings.append("architecture_classification_set_incomplete")
        if not architecture.get("verified_findings"):
            findings.append("architecture_findings_missing")
        if architecture.get("archive_allowed") is not False:
            findings.append("architecture_incomplete_archive_must_be_false")
    return findings


def build_receipt(context: dict[str, Any], architecture: dict[str, Any] | None = None) -> dict[str, Any]:
    findings = validate_context(context)
    if architecture is None:
        findings.append("architecture_state_unavailable")
    else:
        findings.extend(validate_architecture(architecture, context))

    goal_complete = context.get("goal_activation_complete") is True
    architecture_state = None if architecture is None else architecture.get("state")
    archive_allowed = bool(context.get("archive_allowed", False)) and not findings
    body = {
        "schema": "stegverse.steggate_session_continuity_receipt.v1",
        "goal_id": context.get("goal_id"),
        "context_digest": digest(context),
        "architecture_digest": None if architecture is None else digest(architecture),
        "state": "PASS" if not findings else "FAIL_CLOSED",
        "archive_allowed": archive_allowed,
        "historical_context_preserved": not findings,
        "goal_activation_complete": goal_complete,
        "session_state": context.get("session_state"),
        "architecture_reconciliation_state": architecture_state,
        "deployment_state": (context.get("current_work") or {}).get("deployment_state"),
        "next_action": (context.get("worker_policy") or {}).get("next_action"),
        "findings": sorted(findings),
    }
    return {**body, "receipt_digest": digest(body)}


def main() -> int:
    try:
        context = json.loads(CONTEXT.read_text(encoding="utf-8"))
        architecture = json.loads(ARCHITECTURE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        receipt = {
            "schema": "stegverse.steggate_session_continuity_receipt.v1",
            "state": "FAIL_CLOSED",
            "archive_allowed": False,
            "historical_context_preserved": False,
            "findings": [f"continuity_input_unreadable:{type(exc).__name__}"],
            "next_action": "Restore the canonical StegGate session and architecture context before continuing or archiving.",
        }
        receipt["receipt_digest"] = digest(receipt)
        RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(receipt, sort_keys=True))
        return 1

    receipt = build_receipt(context, architecture)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt["state"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
