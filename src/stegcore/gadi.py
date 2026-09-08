"""GADI threat reasoning and defensive intervention planning.

This module is a reasoning surface, not a parallel admissibility authority.
It preserves uncertainty and semantic qualifiers, correlates threat observations,
and proposes bounded intervention requests that must still pass the canonical
StegGate/InTr admission path before any external consequence can occur.
"""

from __future__ import annotations

from enum import Enum
from typing import Iterable, Literal

from pydantic import BaseModel, Field, model_validator


class ThreatState(str, Enum):
    OBSERVED = "OBSERVED"
    CORRELATED = "CORRELATED"
    CREDIBLE = "CREDIBLE"
    ACTIVE = "ACTIVE"
    IMMINENT_HARM = "IMMINENT_HARM"
    INTERVENTION_ACTIVE = "INTERVENTION_ACTIVE"
    THREAT_INTERRUPTED = "THREAT_INTERRUPTED"
    RECOVERY = "RECOVERY"
    CLOSED = "CLOSED"
    DISPROVEN = "DISPROVEN"


class SemanticIntegrity(str, Enum):
    PASS = "PASS"
    DRIFT = "DRIFT"
    MATERIAL_DRIFT = "MATERIAL_DRIFT"
    UNOBSERVABLE = "UNOBSERVABLE"


class ThreatObservation(BaseModel):
    schema: Literal["AUTONOMOUS_THREAT_OBSERVATION/v1"] = "AUTONOMOUS_THREAT_OBSERVATION/v1"
    observation_id: str = Field(min_length=1)
    subject_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    observed_action: str = Field(min_length=1)
    human_harm_possible: bool = False
    human_harm_imminent: bool | None = None
    action_active: bool | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    corroboration_count: int = Field(default=0, ge=0)
    contradictory_evidence: bool = False
    origin_claim: str | None = None
    interpreted_claim: str | None = None
    origin_qualifiers: tuple[str, ...] = ()
    interpreted_qualifiers: tuple[str, ...] = ()


class ThreatAssessment(BaseModel):
    subject_id: str
    state: ThreatState
    confidence: float
    observation_ids: tuple[str, ...]
    semantic_integrity: SemanticIntegrity
    semantic_delta: tuple[str, ...] = ()
    uncertainty_preserved: bool = True
    intervention_eligible: bool = False
    reasons: tuple[str, ...] = ()


class DefensiveCapability(BaseModel):
    capability_id: str = Field(min_length=1)
    effect: str = Field(min_length=1)
    pre_authorized: bool
    effectiveness: float = Field(ge=0.0, le=1.0)
    destructiveness: float = Field(ge=0.0, le=1.0)
    authority_ref: str | None = None

    @model_validator(mode="after")
    def authority_is_required_for_pre_authorized_capability(self) -> "DefensiveCapability":
        if self.pre_authorized and not self.authority_ref:
            raise ValueError("pre-authorized capability requires authority_ref")
        return self


class DefensiveInterventionRequest(BaseModel):
    schema: Literal["DEFENSIVE_INTERVENTION_REQUEST/v1"] = "DEFENSIVE_INTERVENTION_REQUEST/v1"
    threat_subject_id: str
    threat_state: ThreatState
    threat_observation_ids: tuple[str, ...]
    capability_id: str
    authority_ref: str
    requested_effect: str
    semantic_integrity: SemanticIntegrity
    downstream_admission_required: Literal[True] = True
    canonical_admission_runtime: Literal["stegcore.steggate.evaluate_admissibility"] = (
        "stegcore.steggate.evaluate_admissibility"
    )
    execution_authority_claimed: Literal[False] = False


_STRONGENING_PAIRS = {
    ("may", "is"),
    ("might", "is"),
    ("possible", "certain"),
    ("suspected", "confirmed"),
    ("likely", "will"),
    ("recommendation", "authorization"),
    ("analysis", "instruction"),
}


def assess_semantic_integrity(observation: ThreatObservation) -> tuple[SemanticIntegrity, tuple[str, ...]]:
    """Compare available origin/interpreted semantics without inventing missing evidence."""
    if observation.origin_claim is None or observation.interpreted_claim is None:
        return SemanticIntegrity.UNOBSERVABLE, ()

    deltas: list[str] = []
    origin_q = {q.strip().lower() for q in observation.origin_qualifiers if q.strip()}
    interpreted_q = {q.strip().lower() for q in observation.interpreted_qualifiers if q.strip()}

    for weak, strong in _STRENGTHENING_PAIRS:
        if weak in origin_q and strong in interpreted_q:
            deltas.append(f"qualifier_strengthened:{weak}->{strong}")

    dropped = sorted(origin_q - interpreted_q)
    for qualifier in dropped:
        deltas.append(f"origin_qualifier_not_preserved:{qualifier}")

    if observation.origin_claim.strip() != observation.interpreted_claim.strip():
        deltas.append("claim_text_changed")

    if any(delta.startswith("qualifier_strengthened:") for delta in deltas):
        return SemanticIntegrity.MATERIAL_DRIFT, tuple(deltas)
    if deltas:
        return SemanticIntegrity.DRIFT, tuple(deltas)
    return SemanticIntegrity.PASS, ()


def correlate_threat(observations: Iterable[ThreatObservation]) -> ThreatAssessment:
    """Correlate observations deterministically while preserving uncertainty.

    Critical missing/contradictory evidence cannot produce IMMINENT_HARM.
    Semantic drift contributes evidence but never independently authorizes intervention.
    """
    items = tuple(observations)
    if not items:
        raise ValueError("at least one threat observation is required")

    subjects = {item.subject_id for item in items}
    if len(subjects) != 1:
        raise ValueError("all observations must refer to one subject_id")

    semantic_results = [assess_semantic_integrity(item) for item in items]
    semantic_states = [state for state, _ in semantic_results]
    semantic_delta = tuple(delta for _, deltas in semantic_results for delta in deltas)
    if SemanticIntegrity.MATERIAL_DRIFT in semantic_states:
        semantic_integrity = SemanticIntegrity.MATERIAL_DRIFT
    elif SemanticIntegrity.DRIFT in semantic_states:
        semantic_integrity = SemanticIntegrity.DRIFT
    elif all(state == SemanticIntegrity.PASS for state in semantic_states):
        semantic_integrity = SemanticIntegrity.PASS
    else:
        semantic_integrity = SemanticIntegrity.UNOBSERVABLE

    confidence = sum(item.confidence for item in items) / len(items)
    contradictory = any(item.contradictory_evidence for item in items)
    harm_possible = any(item.human_harm_possible for item in items)
    imminent_values = [item.human_harm_imminent for item in items]
    active_values = [item.action_active for item in items]
    corroboration = sum(item.corroboration_count for item in items)

    reasons: list[str] = []
    uncertainty_preserved = True

    if contradictory:
        state = ThreatState.CORRELATED if len(items) > 1 else ThreatState.OBSERVED
        reasons.append("contradictory_evidence")
    elif any(value is None for value in imminent_values + active_values):
        state = ThreatState.CREDIBLE if harm_possible and confidence >= 0.60 else ThreatState.CORRELATED
        reasons.append("critical_state_uncertain")
    elif harm_possible and all(bool(value) for value in active_values) and all(bool(value) for value in imminent_values):
        if confidence >= 0.80 and (corroboration > 0 or len(items) > 1):
            state = ThreatState.IMMINENT_HARM
        else:
            state = ThreatState.ACTIVE
            reasons.append("insufficient_confidence_or_corroboration_for_imminent_harm")
    elif harm_possible and any(bool(value) for value in active_values):
        state = ThreatState.ACTIVE
    elif harm_possible:
        state = ThreatState.CREDIBLE
    elif confidence < 0.25 and len(items) > 1:
        state = ThreatState.DISPROVEN
    else:
        state = ThreatState.CORRELATED if len(items) > 1 else ThreatState.OBSERVED

    intervention_eligible = state == ThreatState.IMMINENT_HARM
    return ThreatAssessment(
        subject_id=items[0].subject_id,
        state=state,
        confidence=confidence,
        observation_ids=tuple(item.observation_id for item in items),
        semantic_integrity=semantic_integrity,
        semantic_delta=semantic_delta,
        uncertainty_preserved=uncertainty_preserved,
        intervention_eligible=intervention_eligible,
        reasons=tuple(reasons),
    )


def choose_least_destructive_effective_capability(
    assessment: ThreatAssessment,
    capabilities: Iterable[DefensiveCapability],
    *,
    minimum_effectiveness: float = 0.70,
) -> DefensiveCapability | None:
    """Select only among pre-authorized capabilities meeting effectiveness threshold."""
    if not assessment.intervention_eligible:
        return None

    eligible = [
        capability
        for capability in capabilities
        if capability.pre_authorized
        and capability.authority_ref
        and capability.effectiveness >= minimum_effectiveness
    ]
    if not eligible:
        return None
    return min(eligible, key=lambda capability: (capability.destructiveness, -capability.effectiveness, capability.capability_id))


def build_intervention_request(
    assessment: ThreatAssessment,
    capability: DefensiveCapability,
) -> DefensiveInterventionRequest:
    """Build a bounded proposal for downstream canonical admission."""
    if not assessment.intervention_eligible or assessment.state != ThreatState.IMMINENT_HARM:
        raise ValueError("assessment is not eligible for defensive intervention")
    if not capability.pre_authorized or not capability.authority_ref:
        raise ValueError("capability is not pre-authorized")

    return DefensiveInterventionRequest(
        threat_subject_id=assessment.subject_id,
        threat_state=assessment.state,
        threat_observation_ids=assessment.observation_ids,
        capability_id=capability.capability_id,
        authority_ref=capability.authority_ref,
        requested_effect=capability.effect,
        semantic_integrity=assessment.semantic_integrity,
    )
