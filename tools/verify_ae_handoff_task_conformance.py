#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "ecosystem_management/ae_task_conformance.v1.json"
CAPABILITY_REGISTRY_PATH = ROOT / "management/admissible-existence-capability-registry.json"
TASK_REGISTRY_PATH = ROOT / "ecosystem_management/task_registry.yml"
HANDOFF_PATH = ROOT / "docs/STEGVERSE_ECOSYSTEM_MANAGEMENT_MIRROR_HANDOFF.md"
REPORT_PATH = ROOT / "brain_reports/ae_handoff_task_conformance_report.json"

PHASES = {"DECLARED", "STANDING", "ADMISSIBLE", "ACTIVATED", "SUSPENDED", "SUPERSEDED", "TERMINATED"}
TEMPORAL_CLASSES = {"recently_completed", "current", "future"}
RELATIONSHIPS = {"develops_capability", "integrates_capability", "validates_capability", "propagates_capability"}
REQUIRED_REGISTRY_MARKERS = (
    "admissible_existence_conformance:",
    "ecosystem_management/ae_task_conformance.v1.json",
    "tools/verify_ae_handoff_task_conformance.py",
)
REQUIRED_HANDOFF_MARKERS = (
    "## Admissible-Existence conformance gate",
    "ecosystem_management/ae_task_conformance.v1.json",
    "tools/verify_ae_handoff_task_conformance.py",
    "recently completed",
    "current",
    "future",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def finding(code: str, detail: str, *, task_id: str | None = None) -> dict[str, Any]:
    row: dict[str, Any] = {"code": code, "detail": detail}
    if task_id:
        row["task_id"] = task_id
    return row


def declaration_hash(entry: dict[str, Any]) -> str:
    return sha256_json(entry["declaration"])


def verify() -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    required_paths = [MANIFEST_PATH, CAPABILITY_REGISTRY_PATH, TASK_REGISTRY_PATH, HANDOFF_PATH]
    for path in required_paths:
        if not path.exists():
            findings.append(finding("required_surface_missing", str(path.relative_to(ROOT))))

    if findings:
        return {"valid": False, "findings": findings, "task_results": []}

    manifest = load_json(MANIFEST_PATH)
    capability_registry = load_json(CAPABILITY_REGISTRY_PATH)
    task_registry_text = TASK_REGISTRY_PATH.read_text(encoding="utf-8")
    handoff_text = HANDOFF_PATH.read_text(encoding="utf-8")

    for marker in REQUIRED_REGISTRY_MARKERS:
        if marker not in task_registry_text:
            findings.append(finding("worker_registry_ae_projection_missing", marker))
    for marker in REQUIRED_HANDOFF_MARKERS:
        if marker not in handoff_text:
            findings.append(finding("handoff_ae_projection_missing", marker))

    if manifest.get("canonical_admissibility_runtime") != "stegcore.steggate.evaluate_admissibility":
        findings.append(finding("canonical_admissibility_runtime_mismatch", str(manifest.get("canonical_admissibility_runtime"))))
    if manifest.get("credential_authority") != "TV/TVC":
        findings.append(finding("credential_authority_mismatch", str(manifest.get("credential_authority"))))
    if manifest.get("github_token_runtime_authority") != "NONE":
        findings.append(finding("github_token_runtime_authority_present", str(manifest.get("github_token_runtime_authority"))))

    rules = manifest.get("rules") or {}
    required_true_rules = {
        "completed_task_requires_evidence_for_claimed_phase",
        "current_task_requires_owner_and_continuation",
        "future_task_requires_capability_binding_before_activation",
        "activated_requires_integration_and_activation_proof",
        "blocked_admissible_requires_continuation_owner",
        "handoff_registry_projection_must_match",
    }
    for key in required_true_rules:
        if rules.get(key) is not True:
            findings.append(finding("required_rule_disabled", key))
    if rules.get("structural_verification_may_widen_authority") is not False:
        findings.append(finding("structural_authority_widening_not_forbidden", "must be false"))
    if rules.get("legacy_unclassified_tasks_are_conformant") is not False:
        findings.append(finding("legacy_silent_conformance_not_forbidden", "must be false"))

    capability_by_id: dict[str, dict[str, Any]] = {}
    for entry in capability_registry.get("entries", []):
        declaration = entry.get("declaration") or {}
        capability_id = declaration.get("capability_id")
        if not capability_id:
            findings.append(finding("capability_id_missing", "registry entry lacks capability_id"))
            continue
        if capability_id in capability_by_id:
            findings.append(finding("duplicate_capability_id", capability_id))
            continue
        capability_by_id[capability_id] = entry
        expected_hash = declaration_hash(entry)
        if entry.get("existence_hash") != expected_hash:
            findings.append(finding("existence_hash_mismatch", capability_id))
        authority = declaration.get("authority") or {}
        if authority.get("credential_authority") != "TV/TVC":
            findings.append(finding("capability_credential_authority_mismatch", capability_id))
        if authority.get("github_token_runtime_authority") is not False:
            findings.append(finding("capability_github_token_runtime_authority", capability_id))
        phase = entry.get("phase")
        evidence = entry.get("evidence") or {}
        if phase == "ACTIVATED":
            if not evidence.get("integration_evidence_refs"):
                findings.append(finding("activated_integration_evidence_missing", capability_id))
            if not evidence.get("activation_proof_ref"):
                findings.append(finding("activated_activation_proof_missing", capability_id))
            if evidence.get("blockers"):
                findings.append(finding("activated_with_open_blockers", capability_id))
        if phase == "ADMISSIBLE" and evidence.get("blockers") and not evidence.get("continuation_owner"):
            findings.append(finding("blocked_admissible_without_owner", capability_id))

    task_results: list[dict[str, Any]] = []
    seen_task_ids: set[str] = set()
    temporal_counts = {key: 0 for key in TEMPORAL_CLASSES}
    for task in manifest.get("tasks", []):
        task_id = str(task.get("task_id") or "")
        task_findings: list[dict[str, Any]] = []
        if not task_id:
            task_findings.append(finding("task_id_missing", "task_id is required"))
        elif task_id in seen_task_ids:
            task_findings.append(finding("duplicate_task_id", task_id, task_id=task_id))
        seen_task_ids.add(task_id)

        temporal_class = task.get("temporal_class")
        if temporal_class not in TEMPORAL_CLASSES:
            task_findings.append(finding("temporal_class_invalid", str(temporal_class), task_id=task_id))
        else:
            temporal_counts[temporal_class] += 1

        relationship = task.get("relationship")
        if relationship not in RELATIONSHIPS:
            task_findings.append(finding("relationship_invalid", str(relationship), task_id=task_id))

        capability_id = task.get("capability_id")
        capability = capability_by_id.get(capability_id)
        if capability is None:
            task_findings.append(finding("capability_binding_missing", str(capability_id), task_id=task_id))
        else:
            claimed_phase = task.get("claimed_phase")
            if claimed_phase not in PHASES:
                task_findings.append(finding("claimed_phase_invalid", str(claimed_phase), task_id=task_id))
            elif claimed_phase != capability.get("phase"):
                task_findings.append(finding("claimed_phase_registry_mismatch", f"task={claimed_phase} registry={capability.get('phase')}", task_id=task_id))
            target_phase = task.get("target_phase")
            if target_phase not in PHASES:
                task_findings.append(finding("target_phase_invalid", str(target_phase), task_id=task_id))

        owner = str(task.get("owner") or "").strip()
        continuation_owner = str(task.get("continuation_owner") or "").strip()
        evidence_refs = task.get("evidence_refs") or []
        blockers = task.get("blockers") or []
        handoff_ref = str(task.get("handoff_ref") or "").strip()
        if not owner:
            task_findings.append(finding("task_owner_missing", "owner required", task_id=task_id))
        if not continuation_owner:
            task_findings.append(finding("continuation_owner_missing", "continuation owner required", task_id=task_id))
        if not handoff_ref or not (ROOT / handoff_ref).exists():
            task_findings.append(finding("task_handoff_missing", handoff_ref, task_id=task_id))

        if temporal_class == "recently_completed" and not evidence_refs:
            task_findings.append(finding("completed_task_evidence_missing", "recently completed tasks require retained evidence", task_id=task_id))
        if temporal_class == "current" and not blockers and task.get("activation_claimed") is not True:
            task_findings.append(finding("current_task_state_ambiguous", "current task needs blockers or a justified activation claim", task_id=task_id))
        if temporal_class == "future" and task.get("activation_claimed") is True:
            task_findings.append(finding("future_task_premature_activation", "future task cannot claim activation", task_id=task_id))
        if task.get("target_phase") == "ACTIVATED" and task.get("activation_claimed") is True:
            evidence = (capability or {}).get("evidence") or {}
            if not evidence.get("integration_evidence_refs") or not evidence.get("activation_proof_ref"):
                task_findings.append(finding("activation_claim_without_required_proof", "integration and activation proof required", task_id=task_id))
        if task.get("claimed_phase") == "ADMISSIBLE" and blockers and not continuation_owner:
            task_findings.append(finding("blocked_admissible_task_without_owner", "continuation owner required", task_id=task_id))

        task_results.append({
            "task_id": task_id,
            "temporal_class": temporal_class,
            "relationship": relationship,
            "capability_id": capability_id,
            "conformant": not task_findings,
            "findings": task_findings,
        })
        findings.extend(task_findings)

    for temporal_class, count in temporal_counts.items():
        if count == 0:
            findings.append(finding("temporal_class_uncovered", temporal_class))

    legacy_policy = manifest.get("legacy_policy") or {}
    if legacy_policy.get("records_without_ae_binding") != "MIGRATION_REQUIRED":
        findings.append(finding("legacy_policy_invalid", "unbound legacy records must be MIGRATION_REQUIRED"))
    if legacy_policy.get("records_may_continue_existing_authority_while_migrating") is not False:
        findings.append(finding("legacy_authority_carry_forward_forbidden", "must be false"))
    if legacy_policy.get("future_activation_from_legacy_record") is not False:
        findings.append(finding("legacy_future_activation_forbidden", "must be false"))

    report = {
        "artifact_type": "stegcore.ae_handoff_task_conformance_report",
        "schema_version": "1.0",
        "valid": not findings,
        "canonical_issue": manifest.get("canonical_issue"),
        "canonical_admissibility_runtime": manifest.get("canonical_admissibility_runtime"),
        "credential_authority": "TV/TVC",
        "github_token_runtime_authority": "NONE",
        "external_execution_performed": False,
        "continuity_receipt_minted": False,
        "temporal_counts": temporal_counts,
        "capability_count": len(capability_by_id),
        "task_results": task_results,
        "findings": findings,
    }
    report["report_sha256"] = sha256_json(report)
    return report


def main() -> int:
    report = verify()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("AE_HANDOFF_TASK_CONFORMANCE_PASS" if report["valid"] else "AE_HANDOFF_TASK_CONFORMANCE_FAIL")
    print(f"report={REPORT_PATH.relative_to(ROOT)}")
    print(f"report_sha256={report['report_sha256']}")
    if report["findings"]:
        for item in report["findings"]:
            print(f"{item['code']}: {item['detail']}")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
