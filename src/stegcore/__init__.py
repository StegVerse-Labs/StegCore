from __future__ import annotations

"""
StegCore – constraint and governance layer for StegVerse.

This package currently includes:
- state/audit substrate (NodeState, StateEvent, StateEngine)
- minimal decision interface (docs-aligned)
- fail-closed runtime binding for injected execution callbacks

Continuity receipts and verification belong to StegID.
"""

from .models import NodeState, StateEvent
from .state_engine import StateEngine

# Optional: only if registry.py exists in your repo
from .registry import Registry

from .decision import (
    VerifiedReceiptEnvelope,
    ActionIntent,
    PolicyContext,
    DecisionRequest,
    DecisionResult,
    decide,
)
from .runtime import (
    ExecutionObservation,
    GovernedRuntime,
    canonical_hash,
    governed_execute,
)

__all__ = [
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
    "canonical_hash",
    "governed_execute",
]
