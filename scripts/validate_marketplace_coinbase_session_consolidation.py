from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONSOLIDATION = ROOT / "data/marketplace-coinbase-session-consolidation.json"
CLAIMS = ROOT / "data/marketplace-coinbase-work-claims.json"
TASKS = ROOT / "data/execution-orchestrator-tasks.json"
STATE = ROOT / "data/execution-orchestrator-state.json"
OUTPUT = ROOT / "data/marketplace-coinbase-session-consolidation-receipt.json"

REQUIRED_TASKS = {
    "MC-01-CRYPTO-ACCESSIBILITY",
    "MC-02-MARKETPLACE-COLLECTION",
    "MC-03-PUBLISHER-VERIFY",
    "MC-04-SITE-PROJECTION",
    "MC-05-TAG-AUTHORITY",
    "MC-06-FINALIZE-PAPER-RELEASE",
}
ALLOWED_CLAIM_STATES = {
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


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical(value)).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def validate() -> dict[str, Any]:
    findings: list[str] = []
    consolidation = load(CONSOLIDATION)
    claims = load(CLAIMS)
    tasks = load(TASKS)
    state = load(STATE)

    if consolidation.get("session_role") != "MERGED_INTO_CANONICAL_WORKSTREAM":
        findings.append("session_role_not_merged")
    if consolidation.get("archival_state") != "READY_AFTER_VALIDATION":
        findings.append("archival_state_not_ready_after_validation")

    archive_test = consolidation.get("archive_test") or {}
    for field in (
        "unique_information_remaining_in_chat",
        "unassigned_work_remaining",
        "canonical_owner_recorded",
        "machine_observers_installed",
        "authority_boundary_recorded",
        "deleting_session_impairs_execution",
    ):
        if field not in archive_test:
            findings.append(f"archive_test_missing_{field}")
    if archive_test.get("unique_information_remaining_in_chat") is not False:
        findings.append("unique_information_not_transferred")
    if archive_test.get("unassigned_work_remaining") is not False:
        findings.append("unassigned_work_remains")
    if archive_test.get("canonical_owner_recorded") is not True:
        findings.append("canonical_owner_missing")
    if archive_test.get("machine_observers_installed") is not True:
        findings.append("machine_observer_missing")
    if archive_test.get("authority_boundary_recorded") is not True:
        findings.append("authority_boundary_missing")
    if archive_test.get("deleting_session_impairs_execution") is not False:
        findings.append("session_still_required")

    requirements = consolidation.get("session_specific_requirements") or []
    if len(requirements) != 8:
        findings.append("session_requirement_count_mismatch")
    for requirement in requirements:
        if requirement.get("state") not in {"COMPLETE", "MERGED", "SUPERSEDED"}:
            findings.append(f"requirement_not_transferred:{requirement.get('id')}")
        if not requirement.get("destination"):
            findings.append(f"requirement_destination_missing:{requirement.get('id')}")

    claim_items = claims.get("claims") or []
    claim_ids = {item.get("task_id") for item in claim_items}
    if claim_ids != REQUIRED_TASKS:
        findings.append("claim_task_set_mismatch")
    for item in claim_items:
        if item.get("role") not in ALLOWED_CLAIM_STATES:
            findings.append(f"invalid_claim_state:{item.get('task_id')}")
        if not item.get("claim_timestamp"):
            findings.append(f"claim_timestamp_missing:{item.get('task_id')}")
        if not item.get("release_condition"):
            findings.append(f"claim_release_condition_missing:{item.get('task_id')}")
        if not item.get("collision_boundary"):
            findings.append(f"claim_collision_boundary_missing:{item.get('task_id')}")

    session_claim = claims.get("session_claim") or {}
    if session_claim.get("role") != "MERGED_INTO_CANONICAL_WORKSTREAM":
        findings.append("session_claim_not_merged")
    if session_claim.get("unique_execution_responsibility_remaining") is not False:
        findings.append("session_unique_execution_responsibility_remains")

    task_ids = {item.get("task_id") for item in tasks.get("tasks") or []}
    state_ids = {item.get("task_id") for item in state.get("tasks") or []}
    if task_ids != REQUIRED_TASKS:
        findings.append("canonical_task_registry_mismatch")
    if state_ids != REQUIRED_TASKS:
        findings.append("canonical_state_task_set_mismatch")

    state_by_id = {item.get("task_id"): item for item in state.get("tasks") or []}
    for completed in (
        "MC-01-CRYPTO-ACCESSIBILITY",
        "MC-02-MARKETPLACE-COLLECTION",
        "MC-03-PUBLISHER-VERIFY",
        "MC-04-SITE-PROJECTION",
    ):
        if state_by_id.get(completed, {}).get("state") != "COMPLETE":
            findings.append(f"completed_task_not_complete:{completed}")
    if state_by_id.get("MC-05-TAG-AUTHORITY", {}).get("state") != "WAITING_FOR_AUTHORITY":
        findings.append("tag_authority_state_mismatch")
    if state_by_id.get("MC-06-FINALIZE-PAPER-RELEASE", {}).get("state") != "WAITING_FOR_EVIDENCE":
        findings.append("finalization_state_mismatch")
    if state.get("development_halt") is not False:
        findings.append("development_halt_must_be_false")

    body = {
        "schema": "stegverse.session_consolidation_receipt.v1",
        "consolidation_id": consolidation.get("consolidation_id"),
        "goal_id": consolidation.get("goal_id"),
        "state": "COMPLETE" if not findings else "FAILED",
        "session_role": consolidation.get("session_role"),
        "canonical_location": claims.get("session_claim", {}).get("canonical_location"),
        "requirements_transferred": len(requirements),
        "requirements_required": 8,
        "claims_recorded": len(claim_items),
        "claims_required": 6,
        "canonical_tasks_recorded": len(task_ids),
        "canonical_tasks_required": 6,
        "unique_execution_responsibility_remaining": session_claim.get(
            "unique_execution_responsibility_remaining"
        ),
        "deleting_session_impairs_execution": archive_test.get("deleting_session_impairs_execution"),
        "findings": sorted(findings),
        "next_task": (
            "archive the originating ChatGPT session; continuation is repository-owned"
            if not findings
            else "correct the exact consolidation finding and rerun validation"
        ),
        "publication_authority": "NOT_GRANTED",
        "release_authority": "NOT_GRANTED",
        "execution_authority": "NOT_GRANTED",
        "live_authority": "NOT_GRANTED",
    }
    return {**body, "receipt_digest": digest(body)}


def main() -> int:
    receipt = validate()
    OUTPUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUTPUT)
    return 0 if receipt["state"] == "COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
