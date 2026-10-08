from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


TERMINAL = {"COMPLETE", "SUPERSEDED", "TERMINATED"}
CURRENT = {"ACTIVE_SESSION", "ACTIVE_WORKER", "MACHINE_OWNED", "HANDOFF_READY"}
FUTURE = {"PLANNED", "DECLARED", "HANDOFF_READY"}
PHASES = {"DECLARED", "STANDING", "ADMISSIBLE", "ACTIVATED", "SUSPENDED", "SUPERSEDED", "TERMINATED"}
FORBIDDEN_AUTHORITY = {
    "HEARTBEAT_WORKER_EXECUTOR_AUTHORITY",
    "HEARTBEAT_TRANSPORT_AUTHORITY",
    "HEARTBEAT_CUSTODY_AUTHORITY",
    "MASTER_RECORDS_EXECUTION_AUTHORITY",
    "GITHUB_TOKEN_RUNTIME_AUTHORITY",
    "NON_TV_TVC_CREDENTIAL_AUTHORITY",
}
RECONCILE = (
    "goal_id",
    "owner_repository",
    "ae_impact",
    "capability_id",
    "existence_phase",
    "blockers",
    "continuation_owner",
)


def _finding(code: str, task_id: str | None, detail: str) -> dict[str, str]:
    out = {"code": code, "detail": detail}
    if task_id:
        out["task_id"] = task_id
    return out


def _validate_policy_identity(record: dict[str, Any], findings: list[dict[str, str]]) -> None:
    authority = record.get("authority", {})
    if authority.get("credential_authority") != "TV/TVC":
        findings.append(_finding("credential_authority_invalid", None, "credential authority must be TV/TVC"))
    if authority.get("github_token_runtime_authority") is not False:
        findings.append(_finding("github_token_runtime_authority_forbidden", None, "GitHub token runtime authority must be false"))
    if authority.get("heartbeat_role") != "CARRIER_SYNCHRONIZATION_ONLY":
        findings.append(_finding("heartbeat_role_invalid", None, "heartbeat is carrier/synchronization continuity only"))
    if authority.get("worker_control_plane_separate") is not True:
        findings.append(_finding("worker_control_plane_not_separate", None, "worker control plane must be separate from heartbeat"))
    if authority.get("master_records_organization_record_separate") is not True:
        findings.append(_finding("master_records_organization_record_not_separate", None, "Master Records organization records must be separate from execution/transport"))


def _validate_task(task: dict[str, Any], findings: list[dict[str, str]], surface: str) -> None:
    task_id = task.get("task_id")
    if not task_id:
        findings.append(_finding("task_id_missing", None, f"{surface} task missing task_id"))
        return

    temporal = task.get("temporal_class")
    status = task.get("status")
    if temporal == "RECENTLY_COMPLETED" and status not in TERMINAL:
        findings.append(_finding("completed_status_invalid", task_id, f"{surface}: recently completed task must be terminal"))
    elif temporal == "CURRENT" and status not in CURRENT:
        findings.append(_finding("current_status_invalid", task_id, f"{surface}: current task has invalid status"))
    elif temporal == "FUTURE" and status not in FUTURE:
        findings.append(_finding("future_status_invalid", task_id, f"{surface}: future task has invalid status"))
    elif temporal not in {"RECENTLY_COMPLETED", "CURRENT", "FUTURE"}:
        findings.append(_finding("temporal_class_invalid", task_id, f"{surface}: unsupported temporal class"))

    if not task.get("owner_repository"):
        findings.append(_finding("owner_repository_missing", task_id, f"{surface}: owner repository required"))

    claims = set(task.get("authority_claims", []))
    forbidden = sorted(claims & FORBIDDEN_AUTHORITY)
    if forbidden:
        findings.append(_finding("forbidden_authority_claim", task_id, f"{surface}: forbidden authority claims: {', '.join(forbidden)}"))

    ae_impact = task.get("ae_impact")
    if ae_impact == "NONE":
        if not task.get("ae_rationale"):
            findings.append(_finding("ae_none_rationale_missing", task_id, f"{surface}: ae_impact NONE requires rationale"))
        if task.get("existence_phase") == "ACTIVATED":
            findings.append(_finding("ae_none_activation_invalid", task_id, f"{surface}: ae_impact NONE cannot claim ACTIVATED"))
    elif ae_impact == "CAPABILITY":
        if not task.get("capability_id"):
            findings.append(_finding("capability_id_missing", task_id, f"{surface}: capability-impacting task requires capability_id"))
        phase = task.get("existence_phase")
        if phase not in PHASES:
            findings.append(_finding("existence_phase_invalid", task_id, f"{surface}: invalid or missing existence phase"))
        if phase == "ACTIVATED":
            if not task.get("integration_evidence_refs"):
                findings.append(_finding("activation_integration_evidence_missing", task_id, f"{surface}: ACTIVATED requires integration evidence"))
            if not task.get("activation_proof_ref"):
                findings.append(_finding("activation_proof_missing", task_id, f"{surface}: ACTIVATED requires activation proof"))
        if temporal == "FUTURE" and phase == "ACTIVATED":
            findings.append(_finding("future_activation_forbidden", task_id, f"{surface}: future work cannot pre-claim ACTIVATED"))
    else:
        findings.append(_finding("ae_impact_invalid", task_id, f"{surface}: ae_impact must be CAPABILITY or NONE"))

    blockers = task.get("blockers", [])
    if temporal == "RECENTLY_COMPLETED" and blockers:
        findings.append(_finding("completed_with_blockers", task_id, f"{surface}: recently completed task cannot retain unresolved blockers"))
    if temporal == "CURRENT" and blockers and not task.get("continuation_owner"):
        findings.append(_finding("blocked_current_without_continuation_owner", task_id, f"{surface}: blocked current task requires continuation owner"))
    if temporal == "RECENTLY_COMPLETED" and not task.get("evidence_refs"):
        findings.append(_finding("completion_evidence_missing", task_id, f"{surface}: recently completed task requires durable evidence"))


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    if bundle.get("artifact_type") != "stegcore.ae_continuation_conformance_bundle":
        findings.append(_finding("artifact_type_invalid", None, "unexpected artifact_type"))
    if bundle.get("schema_version") != "1.0":
        findings.append(_finding("schema_version_invalid", None, "schema_version must be 1.0"))
    if bundle.get("policy_id") != "AE-CONTINUATION-CONFORMANCE-001":
        findings.append(_finding("policy_id_invalid", None, "policy_id must bind canonical conformance policy"))

    _validate_policy_identity(bundle, findings)

    handoff_tasks = bundle.get("handoff", {}).get("tasks", [])
    registry_tasks = bundle.get("worker_registry", {}).get("tasks", [])
    for task in handoff_tasks:
        _validate_task(task, findings, "handoff")
    for task in registry_tasks:
        _validate_task(task, findings, "worker_registry")

    handoff_by_id = {t.get("task_id"): t for t in handoff_tasks if t.get("task_id")}
    registry_by_id = {t.get("task_id"): t for t in registry_tasks if t.get("task_id")}

    for task_id, htask in handoff_by_id.items():
        if htask.get("registry_required") is True and task_id not in registry_by_id:
            findings.append(_finding("registry_task_missing", task_id, "HANDOFF requires matching Worker Task Registry record"))
            continue
        rtask = registry_by_id.get(task_id)
        if not rtask:
            continue
        for field in RECONCILE:
            if htask.get(field) != rtask.get(field):
                findings.append(_finding("cross_surface_mismatch", task_id, f"field {field} differs between HANDOFF and Worker Task Registry"))

    for task_id, rtask in registry_by_id.items():
        if rtask.get("handoff_required") is True and task_id not in handoff_by_id:
            findings.append(_finding("handoff_task_missing", task_id, "Worker Task Registry requires matching HANDOFF record"))

    return {
        "artifact_type": "stegcore.ae_continuation_conformance_validation",
        "schema_version": "1.0",
        "policy_id": "AE-CONTINUATION-CONFORMANCE-001",
        "valid": not findings,
        "handoff_task_count": len(handoff_tasks),
        "worker_registry_task_count": len(registry_tasks),
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate HANDOFF and Worker Task Registry state against StegCore Admissible-Existence invariants")
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = validate_bundle(json.loads(args.bundle.read_text(encoding="utf-8")))
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
