from __future__ import annotations

"""StegCore package: canonical governed admissibility runtime for StegVerse."""

from .version import __version__
from .models import NodeState, StateEvent
from .state_engine import StateEngine
from .registry import Registry
from .decision import (
    VerifiedReceiptEnvelope,
    ActionIntent,
    PolicyContext,
    DecisionRequest,
    DecisionResult,
    decide,
)
from .runtime import ExecutionObservation, GovernedRuntime, governed_execute
from .three_layer import (
    JudgmentConditions,
    SignalAdmission,
    ExecutionBoundary,
    ThreeLayerRequest,
    LayerFinding,
    ThreeLayerResult,
    evaluate_three_layer,
)
from .auri_gateway import AuriGatewayResult, canonical_sha256, evaluate_auri_candidate
from .steggate import AdmissibilityRequest, AdmissibilityResult, evaluate_admissibility

__all__ = [
    "__version__",
    "NodeState",
    "StateEvent",
    "StateEngine",
    "Registry",
    "VerifiedReceiptEnvelope",
    "ActionIntent",
    "PolicyContext",
    "DecisionRequest",
    "DecisionResult",
    "decide",
    "ExecutionObservation",
    "GovernedRuntime",
    "governed_execute",
    "JudgmentConditions",
    "SignalAdmission",
    "ExecutionBoundary",
    "ThreeLayerRequest",
    "LayerFinding",
    "ThreeLayerResult",
    "evaluate_three_layer",
    "AuriGatewayResult",
    "canonical_sha256",
    "evaluate_auri_candidate",
    "AdmissibilityRequest",
    "AdmissibilityResult",
    "evaluate_admissibility",
]
