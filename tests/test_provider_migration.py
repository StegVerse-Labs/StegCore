from stegcore.metered_platform import REQUIRED_RETIREMENT_GATES
from stegcore.provider_migration import (
    evaluate_provider_migration_plan,
    verify_provider_migration_receipt,
)


def complete_plan(state="READY_FOR_RETIREMENT_REVIEW"):
    return {
        "provider_id": "github",
        "migration_state": state,
        "retirement_gates": {gate: True for gate in REQUIRED_RETIREMENT_GATES},
    }


def test_incomplete_plan_denies():
    plan = complete_plan()
    plan["retirement_gates"]["rollback_verified"] = False
    receipt = evaluate_provider_migration_plan(plan)
    assert receipt["result"] == "DENY"
    assert receipt["reason_code"] == "migration.evidence_incomplete"
    assert receipt["missing_retirement_gates"] == ["rollback_verified"]


def test_complete_but_unreviewable_state_denies():
    receipt = evaluate_provider_migration_plan(complete_plan("PARALLEL_OPERATION"))
    assert receipt["result"] == "DENY"
    assert receipt["reason_code"] == "migration.state_not_reviewable"


def test_complete_plan_only_allows_separate_review():
    plan = complete_plan()
    receipt = evaluate_provider_migration_plan(plan)
    assert receipt["result"] == "ALLOW"
    assert receipt["reason_code"] == "migration.ready_for_separate_retirement_review"
    assert receipt["provider_retirement_authority"] is False
    assert receipt["cancellation_authority"] is False
    assert receipt["traffic_cutover_authority"] is False
    assert receipt["execution_authority"] is False
    assert receipt["continuity_receipt_minted"] is False
    assert verify_provider_migration_receipt(plan, receipt)


def test_mutated_receipt_fails_verification():
    plan = complete_plan()
    receipt = evaluate_provider_migration_plan(plan)
    receipt["execution_authority"] = True
    assert verify_provider_migration_receipt(plan, receipt) is False
