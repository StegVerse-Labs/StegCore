"""StegCore adapters for activation-specific governance surfaces."""

from .decision_bridge import (
    adapter_result_to_decision_result,
    decide_schema_record,
)
from .entity_001_002 import (
    AdmissibilityResult,
    evaluate_schema_record,
    evaluate_transition_admissibility,
    map_schema_record_to_transition,
)

__all__ = [
    "AdmissibilityResult",
    "adapter_result_to_decision_result",
    "decide_schema_record",
    "evaluate_schema_record",
    "evaluate_transition_admissibility",
    "map_schema_record_to_transition",
]
