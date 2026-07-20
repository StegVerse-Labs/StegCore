from __future__ import annotations

import hashlib
import json
from typing import Any

FORBIDDEN_TRUE_FIELDS = (
    "manual_action_required",
    "production_mutation_allowed",
    "execution_authority",
    "traffic_cutover_authority",
    "cancellation_authority",
    "provider_retirement_authority",
    "continuity_receipt_minted",
)


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def evaluate_github_reconstruction(report: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    records = report.get("records")
    if not isinstance(records, list):
        records = []
        blockers.append("records_missing_or_invalid")

    if report.get("scope") != "default_branch_snapshot_only":
        blockers.append("scope_not_default_branch_snapshot_only")
    if report.get("history_complete") is not False:
        blockers.append("history_completeness_overclaimed")
    if report.get("temporary_source_destroyed") is not True:
        blockers.append("temporary_source_cleanup_not_proven")
    if report.get("source_content_retained") is not False:
        blockers.append("source_content_retention_not_false")
    if report.get("source_content_uploaded") is not False:
        blockers.append("source_content_upload_not_false")

    for field in FORBIDDEN_TRUE_FIELDS:
        if report.get(field) is not False:
            blockers.append(f"report_authority_field_not_false:{field}")

    passed = 0
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            blockers.append(f"record_invalid:{index}")
            continue
        repository = str(record.get("repository") or index)
        for field in FORBIDDEN_TRUE_FIELDS:
            if record.get(field) is not False:
                blockers.append(f"record_authority_field_not_false:{repository}:{field}")
        if record.get("temporary_source_destroyed") is not True:
            blockers.append(f"record_cleanup_not_proven:{repository}")
        if record.get("source_content_retained") is not False:
            blockers.append(f"record_source_retained:{repository}")
        if record.get("source_content_uploaded") is not False:
            blockers.append(f"record_source_uploaded:{repository}")

        state = record.get("state")
        if state == "PASS_DEFAULT_BRANCH_RECONSTRUCTION":
            required = (
                "source_commit",
                "source_tree",
                "source_tree_listing_hash",
                "archive_sha256",
                "reconstructed_manifest_hash",
                "record_hash",
            )
            for field in required:
                value = record.get(field)
                if not isinstance(value, str) or not value:
                    blockers.append(f"passed_record_missing:{repository}:{field}")
            if int(record.get("reconstructed_file_count") or 0) <= 0:
                blockers.append(f"passed_record_empty:{repository}")
            else:
                passed += 1

    decision = "ALLOW_RECONSTRUCTION_EVIDENCE_ONLY" if not blockers and passed > 0 else "DENY_RECONSTRUCTION_EVIDENCE"
    result = {
        "decision": decision,
        "passed_repository_count": passed,
        "record_count": len(records),
        "blockers": sorted(set(blockers)),
        "manual_action_required": False,
        "production_mutation_allowed": False,
        "execution_authority": False,
        "traffic_cutover_authority": False,
        "cancellation_authority": False,
        "provider_retirement_authority": False,
        "continuity_receipt_minted": False,
    }
    result["decision_hash"] = _digest(result)
    return result
