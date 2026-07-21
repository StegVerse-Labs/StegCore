from __future__ import annotations

import hashlib
import json
from typing import Any

FORBIDDEN = (
    "source_material_retained",
    "bundle_retained",
    "secret_material_included",
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


def evaluate_github_complete_history(document: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    records = document.get("records")
    if not isinstance(records, list):
        records = []
        blockers.append("records_missing_or_invalid")

    for field in FORBIDDEN:
        if document.get(field) is not False:
            blockers.append(f"report_forbidden_field:{field}")

    passed = 0
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            blockers.append(f"record_{index}_invalid")
            continue
        name = str(record.get("full_name") or index)
        for field in FORBIDDEN:
            if record.get(field) is not False:
                blockers.append(f"{name}:forbidden_field:{field}")
        state = record.get("state")
        if state == "PASS_COMPLETE_HISTORY_EXPORT":
            passed += 1
            required = (
                "refs_hash",
                "bundle_refs_hash",
                "bundle_hash",
                "record_hash",
            )
            for field in required:
                if not record.get(field):
                    blockers.append(f"{name}:missing:{field}")
            if int(record.get("ref_count") or 0) <= 0:
                blockers.append(f"{name}:empty_ref_set")
            if int(record.get("bundle_ref_count") or 0) <= 0:
                blockers.append(f"{name}:empty_bundle_ref_set")
            if int(record.get("object_count") or 0) <= 0:
                blockers.append(f"{name}:empty_object_set")
            if int(record.get("commit_count") or 0) <= 0:
                blockers.append(f"{name}:empty_commit_set")
            adjacent = record.get("adjacent_state")
            if not isinstance(adjacent, dict):
                blockers.append(f"{name}:adjacent_state_missing")
            else:
                for field in ("releases_hash", "tags_hash", "issues_hash", "pull_requests_hash"):
                    if not adjacent.get(field):
                        blockers.append(f"{name}:missing:{field}")
        elif state != "BLOCKED_COMPLETE_HISTORY_EXPORT":
            blockers.append(f"{name}:invalid_state")

    decision = "ALLOW_COMPLETE_HISTORY_EVIDENCE_ONLY" if records and passed > 0 and not blockers else "DENY"
    result = {
        "schema_version": "1.0.0",
        "decision": decision,
        "provider_id": "github",
        "record_count": len(records),
        "passed_record_count": passed,
        "blockers": sorted(set(blockers)),
        "evidence_only": True,
        "manual_action_required": False,
        "production_mutation_allowed": False,
        "execution_authority": False,
        "traffic_cutover_authority": False,
        "cancellation_authority": False,
        "provider_retirement_authority": False,
        "continuity_receipt_minted": False,
    }
    result["evaluation_hash"] = _digest(result)
    return result
