from __future__ import annotations

from typing import Any, Mapping

from .commit_governance import canonical_hash, finalize_receipt, verify_receipt_integrity

REQUIRED_RETIREMENT_GATES = (
    "asset_inventory_complete",
    "export_verified",
    "successor_health_verified",
    "parallel_operation_passed",
    "rollback_verified",
    "secrets_rotated",
    "traffic_cutover_verified",
    "master_records_custody_recorded",
)


def evaluate_metered_platform(candidate: Mapping[str, Any]) -> dict[str, Any]:
    scope = str(candidate.get("scope", "")).upper()
    evidence = dict(candidate.get("evidence", {}))
    missing = [gate for gate in REQUIRED_RETIREMENT_GATES if evidence.get(gate) is not True]

    if scope == "REPLACEMENT_DESIGN_ONLY":
        result, reason = "ALLOW", "replacement.selection_allowed"
    elif scope == "PROVIDER_RETIREMENT" and missing:
        result, reason = "DENY", "retirement.evidence_incomplete"
    elif scope == "PROVIDER_RETIREMENT":
        result, reason = "ALLOW", "retirement.evidence_complete"
    else:
        result, reason = "DENY", "replacement.scope_invalid"

    receipt = finalize_receipt({
        "contract": "metered-platform-replacement@1.0",
        "candidate_hash": canonical_hash(candidate),
        "scope": scope,
        "result": result,
        "reason_code": reason,
        "missing_retirement_gates": missing,
        "provider_retirement_authority": False,
        "cancellation_authority": False,
        "continuity_receipt_minted": False,
    })
    return receipt


def verify_metered_platform_receipt(candidate: Mapping[str, Any], receipt: Mapping[str, Any]) -> bool:
    return verify_receipt_integrity(receipt) and dict(receipt) == evaluate_metered_platform(candidate)
