#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "PERSONAL_DATA_CONTROL_DECISION_BOUNDARY.md"
SCHEMA = ROOT / "schemas" / "personal-data-control-decision.schema.json"
MANIFEST = ROOT / "runtime" / "personal-data-control-decision.v1.json"
WORKFLOW = ROOT / ".github" / "workflows" / "stegcore-tests.yml"

REQUIRED_STATES = {
    "NOT_REQUESTED",
    "RECEIVED",
    "IDENTITY_VERIFICATION_REQUIRED",
    "VERIFIED",
    "PROCESSING_RESTRICTED",
    "INVENTORY_COMPLETE",
    "DELETION_IN_PROGRESS",
    "PROCESSOR_PROPAGATION_PENDING",
    "COMPLETED",
    "PARTIALLY_DENIED",
    "DENIED",
    "APPEAL_OPEN",
    "CHANNEL_FAILED",
}


def main() -> int:
    failures: list[str] = []
    for path in (DOC, SCHEMA, MANIFEST, WORKFLOW):
        if not path.is_file():
            failures.append(f"missing {path.relative_to(ROOT)}")

    if failures:
        for failure in failures:
            print(f"- {failure}")
        return 1

    document = DOC.read_text(encoding="utf-8")
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    workflow = WORKFLOW.read_text(encoding="utf-8")

    for marker in (
        "StegCore ALLOW != external deletion performed",
        "PROCESSOR_PROPAGATION_PENDING",
        "Every implementation task for this layer must name",
    ):
        if marker not in document:
            failures.append(f"document missing marker: {marker}")

    states = set(schema["$defs"]["state"]["enum"])
    if states != REQUIRED_STATES:
        failures.append("schema state set does not match required governed states")

    if manifest.get("state") != "ACTIVATED_AND_CI_BOUND":
        failures.append("manifest state is not ACTIVATED_AND_CI_BOUND")
    if manifest.get("external_tasks_required") is not False:
        failures.append("external_tasks_required must be false")
    if manifest.get("manual_tasks_required") is not False:
        failures.append("manual_tasks_required must be false")
    if any(manifest.get("authority", {}).values()):
        failures.append("all authority flags must remain false")

    task = manifest.get("task", {})
    required_task_fields = {
        "task_id",
        "repository",
        "implementation_paths",
        "verification_paths",
        "validator_command",
        "success_marker",
        "completion_predicate",
        "status",
        "receipt_path",
    }
    missing_fields = sorted(required_task_fields - set(task))
    if missing_fields:
        failures.append(f"task missing fields: {', '.join(missing_fields)}")
    if task.get("repository") != "StegVerse-Labs/StegCore":
        failures.append("task repository mismatch")
    if task.get("status") != "COMPLETE":
        failures.append("task status must be COMPLETE")

    for relative in task.get("implementation_paths", []) + task.get("verification_paths", []):
        if not (ROOT / relative).exists():
            failures.append(f"task path missing: {relative}")

    if "check_personal_data_control_decision.py" not in workflow:
        failures.append("validator not bound into StegCore Tests workflow")

    if failures:
        print("STEGCORE_PERSONAL_DATA_CONTROL_DECISION=FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("STEGCORE_PERSONAL_DATA_CONTROL_DECISION=PASS")
    print("external_tasks_required=false")
    print("manual_tasks_required=false")
    print("authority_granted=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
