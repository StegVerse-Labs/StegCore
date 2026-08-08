from __future__ import annotations

"""Bounded runtime producer for Action-First reconstruction records.

This module turns an existing StegCore ``AdapterObservation`` into the portable
Action-First reconstruction record defined by the pinned ara interop schema.
It observes and reconstructs; it never authorizes execution, promotes a latent
constraint into Governance truth, verifies signatures, or mints Continuity.
"""

from dataclasses import dataclass, field
from typing import Any, Literal, Mapping, Optional, Sequence

from .runtime_adapters import AdapterObservation

SCHEMA_VERSION = "stegverse.action-first-reconstruction.v1"
SCHEMA_SOURCE_REPOSITORY = "StegVerse-Labs/ara-admissibility-interop"
SCHEMA_SOURCE_COMMIT = "d48b2734c2fdb8018271e2413a0d786f6cc5e479"
SCHEMA_SOURCE_BLOB = "c49f70190ad313e2c849564c411080cd3c7a610f"

Observability = Literal[
    "UNOBSERVED",
    "OBSERVED",
    "RECORDED",
    "VERIFIED",
    "CORROBORATED",
    "FULLY_OBSERVED",
    "UNKNOWN",
]
DeltaStatus = Literal["ZERO", "NONZERO", "UNKNOWN", "NOT_COMPUTABLE"]
Identifiability = Literal[
    "IDENTIFIABLE", "PARTIALLY_IDENTIFIABLE", "NON_IDENTIFIABLE", "NOT_TESTED"
]
ConstraintPromotion = Literal["NONE", "CANDIDATE", "TESTABLE"]
ContinuityConsequence = Literal[
    "PASS",
    "PARTIAL",
    "BROKEN",
    "INTENTIONALLY_TERMINATED",
    "REVALIDATION_REQUIRED",
    "NOT_REQUIRED",
    "UNKNOWN",
    "FAIL_CLOSED",
]


@dataclass(frozen=True)
class RuntimeStateIdentity:
    state_ref: str
    state_hash: Optional[str]
    observability_identity: Observability

    def as_record(self) -> dict[str, Any]:
        return {
            "state_ref": self.state_ref,
            "state_hash": self.state_hash,
            "observability_identity": self.observability_identity,
        }


@dataclass(frozen=True)
class ResidualObservation:
    """Externally calculated distance result; StegCore does not invent the metric."""

    metric_ref: str
    value: Optional[float]
    status: DeltaStatus

    def as_record(self) -> dict[str, Any]:
        return {"status": self.status, "metric_ref": self.metric_ref, "value": self.value}


@dataclass(frozen=True)
class ReconstructionPosture:
    status: Literal["COMPLETE", "PARTIAL", "UNKNOWN", "FAIL_CLOSED"] = "UNKNOWN"
    causal_reconstructability: float = 0.0
    identifiability: Identifiability = "NOT_TESTED"
    prediction_fit: float = 0.0
    constraint_promotion: ConstraintPromotion = "NONE"


@dataclass(frozen=True)
class ActionFirstRuntimeInput:
    record_id: str
    transition_id: str
    prior_state_ref: str
    admissibility_matrix_ref: str
    action_candidate_ref: str
    calculated_state: RuntimeStateIdentity
    realized_state: RuntimeStateIdentity
    observed_state: RuntimeStateIdentity
    model_reality_delta: ResidualObservation
    reality_observation_delta: ResidualObservation
    observer_universe_ref: str
    observation_coverage: float
    observation_level: Observability
    known_constraint_refs: Sequence[str] = field(default_factory=tuple)
    unknown_candidate_refs: Sequence[str] = field(default_factory=tuple)
    latent_candidate_refs: Sequence[str] = field(default_factory=tuple)
    irreducible_uncertainty_ref: Optional[str] = None
    irreversibility_crossed: bool = False
    irreversibility_boundary_ref: Optional[str] = None
    rollback_requires_new_transition: bool = False
    reconstruction: ReconstructionPosture = field(default_factory=ReconstructionPosture)
    continuity_consequence: ContinuityConsequence = "UNKNOWN"
    terminal_declared: bool = False
    viability_horizon_ref: Optional[str] = None
    future_admissible_transition_capacity: Optional[float] = None


def _validate_hash(value: Optional[str], label: str) -> None:
    if value is None:
        return
    if not value.startswith("sha256:") or len(value) != 71:
        raise ValueError(f"{label} must be null or sha256:<64 lowercase hex>")
    suffix = value[7:]
    if any(ch not in "0123456789abcdef" for ch in suffix):
        raise ValueError(f"{label} must use lowercase hexadecimal")


def _validate_ratio(value: float, label: str) -> None:
    if value < 0.0 or value > 1.0:
        raise ValueError(f"{label} must be between 0 and 1")


def _validate_residual(residual: ResidualObservation, label: str) -> None:
    if not residual.metric_ref:
        raise ValueError(f"{label}.metric_ref is required")
    if residual.value is not None and residual.value < 0:
        raise ValueError(f"{label}.value must be nonnegative")
    if residual.status == "ZERO" and residual.value not in (0, 0.0):
        raise ValueError(f"{label}: ZERO requires value 0")
    if residual.status == "NONZERO" and (residual.value is None or residual.value <= 0):
        raise ValueError(f"{label}: NONZERO requires value > 0")
    if residual.status in {"UNKNOWN", "NOT_COMPUTABLE"} and residual.value is not None:
        raise ValueError(f"{label}: unresolved residual must not invent a value")


def _validate_runtime_input(value: ActionFirstRuntimeInput) -> None:
    required_strings = {
        "record_id": value.record_id,
        "transition_id": value.transition_id,
        "prior_state_ref": value.prior_state_ref,
        "admissibility_matrix_ref": value.admissibility_matrix_ref,
        "action_candidate_ref": value.action_candidate_ref,
        "observer_universe_ref": value.observer_universe_ref,
    }
    for label, item in required_strings.items():
        if not item:
            raise ValueError(f"{label} is required")

    for label, state in (
        ("calculated_state", value.calculated_state),
        ("realized_state", value.realized_state),
        ("observed_state", value.observed_state),
    ):
        if not state.state_ref:
            raise ValueError(f"{label}.state_ref is required")
        _validate_hash(state.state_hash, f"{label}.state_hash")

    _validate_ratio(value.observation_coverage, "observation_coverage")
    _validate_ratio(value.reconstruction.causal_reconstructability, "causal_reconstructability")
    _validate_ratio(value.reconstruction.prediction_fit, "prediction_fit")
    _validate_residual(value.model_reality_delta, "model_reality_delta")
    _validate_residual(value.reality_observation_delta, "reality_observation_delta")

    if value.future_admissible_transition_capacity is not None and value.future_admissible_transition_capacity < 0:
        raise ValueError("future_admissible_transition_capacity must be nonnegative")
    if value.irreversibility_crossed and not value.irreversibility_boundary_ref:
        raise ValueError("irreversibility_boundary_ref is required after boundary crossing")
    if value.rollback_requires_new_transition and not value.irreversibility_crossed:
        raise ValueError("rollback requiring a new transition implies irreversibility crossing")

    # Governance owns promotion. This runtime may record candidates/testability only.
    if value.reconstruction.constraint_promotion not in {"NONE", "CANDIDATE", "TESTABLE"}:
        raise ValueError("StegCore cannot promote reconstructed constraints into Governance truth")


def build_action_first_record(
    observation: AdapterObservation[Any],
    runtime_input: ActionFirstRuntimeInput,
) -> dict[str, Any]:
    """Build one schema-shaped reconstruction record from an observed runtime decision.

    The function deliberately does not infer causal truth from a decision or residual.
    Callers must supply the state identities, metric reference, and observation posture.
    """

    _validate_runtime_input(runtime_input)
    decision_state = observation.decision_state

    if runtime_input.action_candidate_ref not in {
        decision_state.candidate_id,
        decision_state.candidate_hash,
    }:
        raise ValueError("action_candidate_ref must bind to the runtime decision candidate")

    # If runtime never invoked the executor, it cannot claim a crossed consequence boundary.
    if not decision_state.executor_invoked and runtime_input.irreversibility_crossed:
        raise ValueError("non-executed runtime observation cannot claim irreversibility crossing")

    # A realized state can exist without being observed, but a runtime execution claimed as
    # committed must have a realized-state identity supplied rather than a placeholder.
    if decision_state.commit_state == "COMMITTED" and runtime_input.realized_state.observability_identity == "UNKNOWN":
        raise ValueError("committed execution requires a bounded realized-state identity")

    reconstruction = runtime_input.reconstruction
    return {
        "schema_version": SCHEMA_VERSION,
        "record_id": runtime_input.record_id,
        "transition_id": runtime_input.transition_id,
        "prior_state_ref": runtime_input.prior_state_ref,
        "admissibility_matrix_ref": runtime_input.admissibility_matrix_ref,
        "action_candidate_ref": runtime_input.action_candidate_ref,
        "irreversibility": {
            "crossed": runtime_input.irreversibility_crossed,
            "boundary_ref": runtime_input.irreversibility_boundary_ref,
            "rollback_requires_new_transition": runtime_input.rollback_requires_new_transition,
        },
        "calculated_state": runtime_input.calculated_state.as_record(),
        "realized_state": runtime_input.realized_state.as_record(),
        "observed_state": runtime_input.observed_state.as_record(),
        "model_reality_delta": runtime_input.model_reality_delta.as_record(),
        "reality_observation_delta": runtime_input.reality_observation_delta.as_record(),
        "observation_profile": {
            "observer_universe_ref": runtime_input.observer_universe_ref,
            "coverage": runtime_input.observation_coverage,
            "level": runtime_input.observation_level,
        },
        "constraint_partition": {
            "known_refs": list(runtime_input.known_constraint_refs),
            "unknown_candidate_refs": list(runtime_input.unknown_candidate_refs),
            "latent_candidate_refs": list(runtime_input.latent_candidate_refs),
            "irreducible_uncertainty_ref": runtime_input.irreducible_uncertainty_ref,
        },
        "reconstruction": {
            "status": reconstruction.status,
            "causal_reconstructability": reconstruction.causal_reconstructability,
            "identifiability": reconstruction.identifiability,
            "prediction_fit": reconstruction.prediction_fit,
            "constraint_promotion": reconstruction.constraint_promotion,
        },
        "continuity_consequence": runtime_input.continuity_consequence,
        "viability": {
            "terminal_declared": runtime_input.terminal_declared,
            "horizon_ref": runtime_input.viability_horizon_ref,
            "future_admissible_transition_capacity": runtime_input.future_admissible_transition_capacity,
        },
    }


def runtime_semantic_source() -> Mapping[str, str]:
    """Expose the exact interop schema source consumed by this runtime producer."""

    return {
        "repository": SCHEMA_SOURCE_REPOSITORY,
        "commit": SCHEMA_SOURCE_COMMIT,
        "blob": SCHEMA_SOURCE_BLOB,
        "schema_version": SCHEMA_VERSION,
    }
