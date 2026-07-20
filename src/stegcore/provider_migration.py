from __future__ import annotations

from typing import Any, Mapping

from .commit_governance import canonical_hash, finalize_receipt, verify_receipt_integrity
from .metered_platform import REQUIRED_RETIREMENT_GATES


def evaluate_provider_migration_plan(plan: Mapping[str, Any]) -> dict[str, Any]:
    gates = dict(plan.get("retirement_gates", {}))
    missing = [gate for gate in REQUIRED_RETIREMENT_GATES if gates.get(gate) is not True]
    state = str(plan.get("migration_state", "")).upper()

    if missing:
        result = "DENY"
        reason = "migration.evidence_incomplete"
    elif state not in {"MIGRATION_VERIFIED", "READY_FOR_RETIREMENT_REVIEW"}:
        result = "DENY"
        reason = "migration.state_not_reviewable"
    else:
        result = "ALLOW"
        reason = "migration.ready_for_separate_retirement_review"

    return finalize_receipt({
        "contract": "provider-migration-plan@1.0",
        "plan_hash": canonical_hash(plan),
        "provider_id": str(plan.get("provider_id", "")),
        "result": result,
        "reason_code": reason,
        "missing_retirement_gates": missing,
        "provider_retirement_authority": False,
        "cancellation_authority": False,
        "traffic_cutover_authority": False,
        "execution_authority": False,
        "continuity_receipt_minted": False,
    })


def verify_provider_migration_receipt(plan: Mapping[str, Any], receipt: Mapping[str, Any]) -> bool:
    return verify_receipt_integrity(receipt) and dict(receipt) == evaluate_provider_migration_plan(plan)
