#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "ecosystem_management/personal_data_control_session_consolidation.v1.json"
HANDOFF = ROOT / "docs/PERSONAL_DATA_CONTROL_ECOSYSTEM_MIRROR_HANDOFF.md"
REGISTRY = ROOT / "ecosystem_management/task_registry.yml"
REPORT = ROOT / "brain_reports/personal_data_control_session_consolidation_report.json"
WORKFLOW = ROOT / ".github/workflows/personal-data-control-session-consolidation.yml"

ALLOWED_CLAIMS = {
    "UNCLAIMED",
    "CLAIMED_FOR_IMPLEMENTATION",
    "CLAIMED_FOR_VALIDATION",
    "CLAIMED_FOR_INTEGRATION",
    "MACHINE_OWNED",
    "BLOCKED",
    "COMPLETE",
    "SUPERSEDED",
    "MERGED_INTO_CANONICAL_WORKSTREAM",
}

REQUIRED_TASK_FIELDS = {
    "task_id",
    "goal",
    "repository",
    "branch",
    "location",
    "owner",
    "claim_state",
    "completion_state",
    "validation_state",
    "integration_state",
    "archival_dependency",
    "evidence",
    "next_action",
}


def main() -> int:
    failures: list[str] = []
    for path in (STATE, HANDOFF, REGISTRY, WORKFLOW):
        if not path.is_file():
            failures.append(f"missing:{path.relative_to(ROOT)}")

    if failures:
        return finish(failures, [])

    state = json.loads(STATE.read_text(encoding="utf-8"))
    inventory = state.get("inventory", [])
    task_ids: set[str] = set()

    if state.get("goal_id") != "SV-PDCL-ECOSYSTEM-001":
        failures.append("goal_id mismatch")
    if state.get("claim_policy", {}).get("external_tasks_allowed") is not False:
        failures.append("external tasks must be prohibited")
    if state.get("claim_policy", {}).get("chat_session_ownership_allowed") is not False:
        failures.append("chat-session ownership must be prohibited")
    if len(inventory) < 8:
        failures.append("inventory must preserve at least eight session goals")

    for item in inventory:
        missing = REQUIRED_TASK_FIELDS - set(item)
        if missing:
            failures.append(f"{item.get('task_id', '<unknown>')}:missing:{','.join(sorted(missing))}")
            continue
        task_id = item["task_id"]
        if task_id in task_ids:
            failures.append(f"duplicate task_id:{task_id}")
        task_ids.add(task_id)
        if item["claim_state"] not in ALLOWED_CLAIMS:
            failures.append(f"{task_id}:invalid claim_state")
        if not item["location"] or not item["owner"] or not item["next_action"]:
            failures.append(f"{task_id}:unaddressable task")
        if item["claim_state"] in {"CLAIMED_FOR_IMPLEMENTATION", "CLAIMED_FOR_VALIDATION", "CLAIMED_FOR_INTEGRATION", "BLOCKED", "MACHINE_OWNED"}:
            if not item.get("release_condition"):
                failures.append(f"{task_id}:active claim missing release_condition")

    consolidation = state.get("session_consolidation", {})
    if consolidation.get("unique_chat_only_requirements_remaining") != 0:
        failures.append("chat-only requirements remain")
    if consolidation.get("transferred_or_complete") != consolidation.get("total_goals"):
        failures.append("not every goal is transferred or complete")

    registry_text = REGISTRY.read_text(encoding="utf-8")
    for marker in (
        "personal-data-control-session-consolidation",
        "ecosystem_management/personal_data_control_session_consolidation.v1.json",
        "docs/PERSONAL_DATA_CONTROL_ECOSYSTEM_MIRROR_HANDOFF.md",
    ):
        if marker not in registry_text:
            failures.append(f"task registry missing marker:{marker}")

    handoff_text = HANDOFF.read_text(encoding="utf-8")
    for marker in (
        "SV-PDCL-ECOSYSTEM-001",
        "PDCL-STEGTALK-001",
        "MERGED INTO",
        "ARCHIVE CONDITION",
    ):
        if marker not in handoff_text:
            failures.append(f"handoff missing marker:{marker}")

    return finish(failures, inventory)


def finish(failures: list[str], inventory: list[dict]) -> int:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "schema_version": "1.0.0",
        "goal_id": "SV-PDCL-ECOSYSTEM-001",
        "result": "FAIL" if failures else "PASS",
        "failures": failures,
        "task_count": len(inventory),
        "external_tasks_allowed": False,
        "chat_session_ownership_allowed": False,
        "next_executable_task": "PDCL-STEGTALK-001 validation observation",
        "authority_effect": False,
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"PERSONAL_DATA_CONTROL_SESSION_CONSOLIDATION={report['result']}")
    print(f"TASK_COUNT={report['task_count']}")
    print("EXTERNAL_TASKS_ALLOWED=false")
    print("CHAT_SESSION_OWNERSHIP_ALLOWED=false")
    for failure in failures:
        print(f"FAILURE={failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
