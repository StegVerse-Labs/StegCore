"""Bridge StegVerse-001/002 adapter results into StegCore DecisionResult values."""

from __future__ import annotations

from typing import Mapping, Any

from stegcore.decision import DecisionResult

from .entity_001_002 import AdmissibilityResult, evaluate_schema_record


STATUS_TO_DECISION = {
    "allow": "allow",
    "deny": "deny",
    "drift": "defer",
    "stale": "defer",
    "refusal": "defer",
    "override_required": "defer",
}


def adapter_result_to_decision_result(result: AdmissibilityResult) -> DecisionResult:
    """Convert an adapter result into StegCore's native DecisionResult shape.

    StegCore's current DecisionValue domain is allow / deny / defer.
    Adapter statuses that require more governance work before commitment are mapped
    to defer, while their precise posture is preserved in reason_code and
    reason_detail.
    """

    decision = STATUS_TO_DECISION.get(result.status, "defer")
    return DecisionResult(
        decision=decision,
        reason_code=f"entity_001_002.{result.status}",
        reason_detail={
            "entity": result.entity,
            "adapter_status": result.status,
            "adapter_reason": result.reason,
            "principle": result.principle,
        },
    )


def decide_schema_record(record: Mapping[str, Any]) -> DecisionResult:
    """Evaluate a schema-shaped 001/002 record as a native DecisionResult."""

    adapter_result = evaluate_schema_record(record)
    return adapter_result_to_decision_result(adapter_result)
