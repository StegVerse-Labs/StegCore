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
from .steggate import AdmissibilityRequest, AdmissibilityEvaluation, evaluate_admissibility
from .admissible_existence import (
    CapabilityAuthorityEnvelope,
    CapabilityExistenceDeclaration,
    CapabilityExistenceTransition,
    CapabilityExistenceEvaluation,
    evaluate_capability_existence,
)
from .capability_registry import (
    CapabilityPhaseEvidence,
    CapabilityRegistryEntry,
    CapabilityExistenceRegistry,
    CapabilityRegistryValidation,
    load_capability_registry,
    validate_capability_registry,
)
from .transaction_lifecycle import (
    TransactionManifest,
    TransitionReceipt,
    ReplayDescriptor,
    ManifestedTransactionResult,
    TransactionLedger,
    manifest_transaction,
    run_manifested_transaction,
)
from .transaction_discovery import (
    DiscoveryRecord,
    DiscoveryQuery,
    TransactionDiscoveryIndex,
)
from .transaction_discovery_store import DiscoveryRecordStore, SqliteDiscoveryStore
from .manifold_governance import (
    PopulationTransition,
    TransitionStanding,
    BundleStanding,
    ManifoldPlan,
    ManifoldGovernanceAction,
    plan_manifold,
    govern_manifold_action,
)
from .sdk_operation_events import (
    SDK_CHOICE_CODES,
    CORE_GOVERNED_CHOICES,
    CHOICE_LABELS,
    SDKOperationEvent,
    SDKChoiceUsage,
    SDKUsageSummary,
    SDKOperationEventLedger,
)

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
    "AdmissibilityEvaluation",
    "evaluate_admissibility",
    "CapabilityAuthorityEnvelope",
    "CapabilityExistenceDeclaration",
    "CapabilityExistenceTransition",
    "CapabilityExistenceEvaluation",
    "evaluate_capability_existence",
    "CapabilityPhaseEvidence",
    "CapabilityRegistryEntry",
    "CapabilityExistenceRegistry",
    "CapabilityRegistryValidation",
    "load_capability_registry",
    "validate_capability_registry",
    "TransactionManifest",
    "TransitionReceipt",
    "ReplayDescriptor",
    "ManifestedTransactionResult",
    "TransactionLedger",
    "manifest_transaction",
    "run_manifested_transaction",
    "DiscoveryRecord",
    "DiscoveryQuery",
    "TransactionDiscoveryIndex",
    "DiscoveryRecordStore",
    "SqliteDiscoveryStore",
    "PopulationTransition",
    "TransitionStanding",
    "BundleStanding",
    "ManifoldPlan",
    "ManifoldGovernanceAction",
    "plan_manifold",
    "govern_manifold_action",
    "SDK_CHOICE_CODES",
    "CORE_GOVERNED_CHOICES",
    "CHOICE_LABELS",
    "SDKOperationEvent",
    "SDKChoiceUsage",
    "SDKUsageSummary",
    "SDKOperationEventLedger",
]
