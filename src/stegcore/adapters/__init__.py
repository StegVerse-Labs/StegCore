"""StegCore adapters for activation-specific governance surfaces."""

from .entity_001_002 import (
    AdmissibilityResult,
    evaluate_schema_record,
    evaluate_transition_admissibility,
    map_schema_record_to_transition,
)

__all__ = [
    "AdmissibilityResult",
    "evaluate_schema_record",
    "evaluate_transition_admissibility",
    "map_schema_record_to_transition",
]
