"""Admissibility evaluation for provider successor harness evidence."""
from __future__ import annotations

import hashlib
import json
from typing import Any

FORBIDDEN_TRUE = (
    "production_mutation_allowed",
    "traffic_cutover_authority",
    "cancellation_authority",
    "provider_retirement_authority",
    "execution_authority",
)


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def evaluate_successor_harness(report: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    results = report.get("results")
    if not isinstance(results, list):
        reasons.append("HARNESS_RESULTS_MISSING")
        results = []

    for field in FORBIDDEN_TRUE:
        if report.get(field) is True:
            reasons.append(f"REPORT_FORBIDDEN_AUTHORITY:{field}")

    blocked: list[str] = []
    for item in results:
        if not isinstance(item, dict):
            reasons.append("INVALID_PROVIDER_RESULT")
            continue
        provider = str(item.get("provider_id") or "unknown")
        for field in FORBIDDEN_TRUE:
            if item.get(field) is True:
                reasons.append(f"PROVIDER_FORBIDDEN_AUTHORITY:{provider}:{field}")
        if item.get("manual_action_required") is not False:
            reasons.append(f"MANUAL_ACTION_NOT_FALSE:{provider}")
        if item.get("state") != "PASS_NON_PRODUCTION_HARNESS":
            blocked.append(provider)

    decision = "DENY" if reasons or blocked else "ALLOW_NON_PRODUCTION_EVIDENCE_ONLY"
    reason_codes = sorted(set(reasons + (["PROVIDERS_BLOCKED"] if blocked else [])))
    receipt = {
        "decision": decision,
        "reason_codes": reason_codes,
        "blocked_providers": sorted(blocked),
        "provider_count": len(results),
        "source_report_hash": report.get("report_hash"),
        "production_authority": False,
        "traffic_cutover_authority": False,
        "cancellation_authority": False,
        "provider_retirement_authority": False,
        "receipt_minting_authority": False,
    }
    receipt["receipt_digest"] = hashlib.sha256(canonical(receipt).encode("utf-8")).hexdigest()
    return receipt
