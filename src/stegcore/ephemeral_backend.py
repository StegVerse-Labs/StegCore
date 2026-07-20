from __future__ import annotations

import hashlib
import json
from typing import Any

FORBIDDEN_TRUE_FIELDS = (
    "manual_action_required",
    "network_access_used",
    "provider_credentials_used",
    "production_state_used",
    "production_mutation_allowed",
    "execution_authority",
    "traffic_cutover_authority",
    "cancellation_authority",
    "provider_retirement_authority",
    "continuity_receipt_minted",
)

REQUIRED_PASS_CHECKS = (
    "health_check_passed",
    "import_hash_equivalent",
    "export_hash_equivalent",
    "mutation_detected",
    "rollback_hash_equivalent",
)


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def evaluate_ephemeral_backend_report(report: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    results = report.get("results")
    if not isinstance(results, list):
        results = []
        blockers.append("results_missing_or_invalid")

    for field in FORBIDDEN_TRUE_FIELDS:
        if report.get(field) is not False:
            blockers.append(f"report_authority_boundary_violation:{field}")

    passed = 0
    for index, item in enumerate(results):
        if not isinstance(item, dict):
            blockers.append(f"result_invalid:{index}")
            continue
        pid = str(item.get("provider_id") or index)
        for field in FORBIDDEN_TRUE_FIELDS:
            if item.get(field) is not False:
                blockers.append(f"provider_authority_boundary_violation:{pid}:{field}")
        state = item.get("state")
        if state == "PASS_EPHEMERAL_BACKEND":
            checks = item.get("checks")
            if not isinstance(checks, dict):
                blockers.append(f"checks_missing:{pid}")
                continue
            for check in REQUIRED_PASS_CHECKS:
                if checks.get(check) is not True:
                    blockers.append(f"required_check_failed:{pid}:{check}")
            if checks.get("network_access_used") is not False:
                blockers.append(f"network_access_violation:{pid}")
            if checks.get("provider_credentials_used") is not False:
                blockers.append(f"credential_violation:{pid}")
            if checks.get("production_state_used") is not False:
                blockers.append(f"production_state_violation:{pid}")
            if not any(b.startswith((f"required_check_failed:{pid}:", f"network_access_violation:{pid}", f"credential_violation:{pid}", f"production_state_violation:{pid}")) for b in blockers):
                passed += 1
        elif state not in {"BLOCKED_PROMOTION_NOT_ELIGIBLE", "BLOCKED_EPHEMERAL_BACKEND_FAILURE"}:
            blockers.append(f"unknown_state:{pid}:{state}")

    outcome = "ALLOW_ISOLATED_EVIDENCE_ONLY" if not blockers else "DENY_EPHEMERAL_EVIDENCE"
    decision = {
        "schema_version": "1.0.0",
        "outcome": outcome,
        "source_report_hash": report.get("report_hash"),
        "provider_result_count": len(results),
        "passed_provider_count": passed,
        "blockers": sorted(set(blockers)),
        "isolated_evidence_only": True,
        "manual_action_required": False,
        "production_mutation_allowed": False,
        "execution_authority": False,
        "traffic_cutover_authority": False,
        "cancellation_authority": False,
        "provider_retirement_authority": False,
        "continuity_receipt_minted": False,
    }
    decision["decision_hash"] = _digest(decision)
    return decision
