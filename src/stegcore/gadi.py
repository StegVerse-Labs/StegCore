"""GADI threat reasoning and defensive intervention planning.

This module consumes the canonical StegOS GADI contract shapes. It is a reasoning
surface, not a parallel admissibility or execution authority. It preserves
uncertainty and semantic qualifiers, correlates threat observations, and proposes
bounded intervention requests that still require canonical InTr/StegGate admission
and a separately bound pre-authorized capability before any consequence can occur.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Iterable, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

TASK_ID = "GADI-001"
COSV = "10100000100000"


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


class BindingState(str, Enum):
    BOUND = "BOUND"
    PARTIAL = "PARTIAL"
    UNKNOWN = "UNKNOWN"


class InterventionClass(str, Enum):
    DENY_ACCESS = "DENY_ACCESS"
    REVOKE_ACCESS = "REVOKE_ACCESS"
    ISOLATE = "ISOLATE"
    RATE_LIMIT = "RATE_LIMIT"
    PAUSE = "PAUSE"
    QUARANTINE = "QUARANTINE"
    SUSPEND_ACTION_PATH = "SUSPEND_ACTION_PATH"
    FENCE_MACHINE_CLAIM = "FENCE_MACHINE_CLAIM"
    BLOCK_GOVERNED_INGRESS_EGRESS = "BLOCK_GOVERNED_INGRESS_EGRESS"
    REDIRECT_TO_SAFE_STATE = "REDIRECT_TO_SAFE_STATE"
    PRESERVE_FORENSIC_STATE = "PRESERVE_FORENSIC_STATE"
    ESCALATE_TO_HUMAN_OR_EXTERNAL_AUTHORITY = "ESCALATE_TO_HUMAN_OR_EXTERNAL_AUTHORITY"


class Reversibility(str, Enum):
    REVERSIBLE = "REVERSIBLE"
    PARTIALLY_REVERSIBLE = "PARTIALLY_REVERSIBLE"
    IRREVERSIBLE = "IRREVERSIBLE"


class Destructiveness(str, Enum):
    NON_DESTRUCTIVE = "NON_DESTRUCTIVE"
    STATE_MUTATING_REVERSIBLE = "STATE_MUTATING_REVERSIBLE"
    DESTRUCTIVE = "DESTRUCTIVE"


_DESTRUCTIVENESS_ORDER = {
    Destructiveness.NON_DESTRUCTIVE: 0,
    Destructiveness.STATE_MUTATING_REVERSIBLE: 1,
    Destructiveness.DESTRUCTIVE: 2,
}


class ActingSubject(BaseModel):
    subject_id: str = Field(min_length=1)
    subject_type: str = Field(min_length=1)
    binding_state: BindingState


class ThreatenedSubject(BaseModel):
    subject_id: str = ""
    subject_type: str = ""
    binding_state: BindingState


class ObservationUncertainty(BaseModel):
    present: bool
    material_unknowns: tuple[str, ...] = ()


class ObservationFreshness(BaseModel):
    observed_at: datetime
    expires_at: datetime

    @model_validator(mode="after")
    def expires_after_observation(self) -> "ObservationFreshness":
        if self.expires_at <= self.observed_at:
            raise ValueError("expires_at must be later than observed_at")
        return self


class SemanticEvidence(BaseModel):
    """Optional GADI extension carried under StegOS additionalProperties semantics."""

    origin_claim: str | None = None
    interpreted_claim: str | None = None
    origin_qualifiers: tuple[str, ...] = ()
    interpreted_qualifiers: tuple[str, ...] = ()


class ThreatObservation(BaseModel):
    """Canonical `stegos.autonomous_threat_observation.v1` plus reasoning extensions."""

    model_config = ConfigDict(extra="allow")

    schema: Literal["stegos.autonomous_threat_observation.v1"] = "stegos.autonomous_threat_observation.v1"
    task_id: Literal["GADI-001"] = TASK_ID
    cosv: Literal["10100000100000"] = COSV
    observation_id: str = Field(min_length=1)
    observed_at: datetime
    observer_principal_id: str = Field(min_length=1)
    acting_subject: ActingSubject
    threatened_subject: ThreatenedSubject | None = None
    threat_state: ThreatState
    evidence_refs: tuple[str, ...] = Field(min_length=1)
    provenance_refs: tuple[str, ...] = ()
    confidence: float = Field(ge=0.0, le=1.0)
    uncertainty: ObservationUncertainty
    freshness: ObservationFreshness
    authority_effect: Literal["NONE_OBSERVATION_ONLY"] = "NONE_OBSERVATION_ONLY"
    semantic_evidence: SemanticEvidence | None = None

    @model_validator(mode="after")
    def timestamps_are_coherent(self) -> "ThreatObservation":
        if self.observed_at != self.freshness.observed_at:
            raise ValueError("observed_at must match freshness.observed_at")
        return self


class ThreatAssessment(BaseModel):
    subject_id: str
    state: ThreatState
    confidence: float
    observation_ids: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    semantic_integrity: SemanticIntegrity
    semantic_delta: tuple[str, ...] = ()
    uncertainty_preserved: bool = True
    intervention_eligible: bool = False
    reasons: tuple[str, ...] = ()


class CapabilityScope(BaseModel):
    target_classes: tuple[str, ...] = Field(min_length=1)
    allowed_actions: tuple[str, ...] = Field(min_length=1)
    forbidden_actions: tuple[str, ...] = ()


class CapabilityFreshness(BaseModel):
    issued_at: datetime
    expires_at: datetime

    @model_validator(mode="after")
    def expires_after_issue(self) -> "CapabilityFreshness":
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must be later than issued_at")
        return self


class DefensiveCapability(BaseModel):
    """Canonical `stegos.governed_intervention_capability.v1` plus planner metadata."""

    model_config = ConfigDict(extra="allow")

    schema: Literal["stegos.governed_intervention_capability.v1"] = "stegos.governed_intervention_capability.v1"
    capability_id: str = Field(min_length=1)
    owner: str = Field(min_length=1)
    credential_authority: Literal["TV/TVC"] = "TV/TVC"
    preauthorization_required: Literal[True] = True
    control_surface: str = Field(min_length=1)
    scope: CapabilityScope
    reversibility: Reversibility
    destructiveness: Destructiveness
    side_effect_constraints: tuple[str, ...] = ()
    production_eligible: bool
    simulation_eligible: bool
    authorization_evidence_ref: str = Field(min_length=1)
    freshness: CapabilityFreshness
    authority_effect: Literal["NONE_UNTIL_INTR_ADMISSION_AND_RUNTIME_BINDING"] = (
        "NONE_UNTIL_INTR_ADMISSION_AND_RUNTIME_BINDING"
    )
    intervention_class: InterventionClass
    effectiveness_estimate: float = Field(ge=0.0, le=1.0)


class Admission(BaseModel):
    state: Literal["PENDING", "ADMITTED", "DENIED"]
    intr_decision_ref: str | None

    @model_validator(mode="after")
    def admitted_requires_intr_reference(self) -> "Admission":
        if self.state == "ADMITTED" and not self.intr_decision_ref:
            raise ValueError("ADMITTED requires intr_decision_ref")
        if self.state == "PENDING" and self.intr_decision_ref is not None:
            raise ValueError("PENDING cannot claim an InTr decision reference")
        return self


class StopCondition(BaseModel):
    condition_type: Literal[
        "THREAT_INTERRUPTED",
        "THREAT_DISPROVEN",
        "AUTHORITY_REVOKED",
        "CAPABILITY_EXPIRED",
        "MANUAL_AUTHORITY_STOP",
        "OTHER",
    ]
    description: str = Field(min_length=1)


class DefensiveInterventionRequest(BaseModel):
    """Canonical StegOS intervention request emitted in PENDING state."""

    model_config = ConfigDict(extra="allow")

    schema: Literal["stegos.defensive_intervention_request.v1"] = "stegos.defensive_intervention_request.v1"
    task_id: Literal["GADI-001"] = TASK_ID
    cosv: Literal["10100000100000"] = COSV
    request_id: str = Field(min_length=1)
    threat_observation_ref: str = Field(min_length=1)
    governed_principal_id: str = Field(min_length=1)
    threatened_subject_ref: str | None = None
    intervention_class: InterventionClass
    required_capability_id: str = Field(min_length=1)
    admission: Admission
    least_destructive_rationale: str = Field(min_length=1)
    reversibility: Literal["REVERSIBLE", "PARTIALLY_REVERSIBLE", "IRREVERSIBLE", "UNKNOWN"]
    reassessment_required: Literal[True] = True
    stop_condition: StopCondition
    receipt_correlation_id: str = Field(min_length=1)
    authority_refs: tuple[str, ...] = ()
    model_output_authority: Literal["NONE"] = "NONE"
    authority_effect: Literal["NONE_REQUEST_ONLY", "ADMISSION_REQUIRED_BEFORE_ACTUATION"] = (
        "ADMISSION_REQUIRED_BEFORE_ACTUATION"
    )
    semantic_integrity: SemanticIntegrity
    semantic_delta: tuple[str, ...] = ()


_STRONGENING_PAIRS = {
    ("may", "is"),
    ("might", "is"),
    ("possible", "certain"),
    ("suspected", "confirmed"),
    ("likely", "will"),
    ("recommendation", "authorization"),
    ("analysis", "instruction"),
}


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("GADI timestamps must be timezone-aware")
    return value.astimezone(timezone.utc)


def assess_semantic_integrity(observation: ThreatObservation) -> tuple[SemanticIntegrity, tuple[str, ...]]:
    """Compare supplied origin/interpreted semantics without inventing missing evidence."""
    evidence = observation.semantic_evidence
    if evidence is None or evidence.origin_claim is None or evidence.interpreted_claim is None:
        return SemanticIntegrity.UNOBSERVABLE, ()

    deltas: list[str] = []
    origin_q = {q.strip().lower() for q in evidence.origin_qualifiers if q.strip()}
    interpreted_q = {q.strip().lower() for q in evidence.interpreted_qualifiers if q.strip()}

    for weak, strong in _STRONGENING_PAIRS:
        if weak in origin_q and strong in interpreted_q:
            deltas.append(f"qualifier_strengthened:{weak}->{strong}")

    for qualifier in sorted(origin_q - interpreted_q):
        deltas.append(f"origin_qualifier_not_preserved:{qualifier}")

    if evidence.origin_claim.strip() != evidence.interpreted_claim.strip():
        deltas.append("claim_text_changed")

    if any(delta.startswith("qualifier_strengthened:") for delta in deltas):
        return SemanticIntegrity.MATERIAL_DRIFT, tuple(deltas)
    if deltas:
        return SemanticIntegrity.DRIFT, tuple(deltas)
    return SemanticIntegrity.PASS, ()


def correlate_threat(
    observations: Iterable[ThreatObservation],
    *,
    as_of: datetime,
) -> ThreatAssessment:
    """Correlate canonical observations deterministically and conservatively.

    Freshness, subject binding, uncertainty, and disproving evidence are preserved.
    Semantic drift is observable evidence but cannot by itself elevate threat state or
    make an intervention eligible.
    """
    items = tuple(observations)
    if not items:
        raise ValueError("at least one threat observation is required")
    now = _utc(as_of)

    subject_ids = {item.acting_subject.subject_id for item in items}
    if len(subject_ids) != 1:
        raise ValueError("all observations must refer to one acting subject")

    semantic_results = [assess_semantic_integrity(item) for item in items]
    semantic_states = [state for state, _ in semantic_results]
    semantic_delta = tuple(delta for _, deltas in semantic_results for delta in deltas)
    if SemanticIntegrity.MATERIAL_DRIFT in semantic_states:
        semantic_integrity = SemanticIntegrity.MATERIAL_DRIFT
    elif SemanticIntegrity.DRIFT in semantic_states:
        semantic_integrity = SemanticIntegrity.DRIFT
    elif semantic_states and all(state == SemanticIntegrity.PASS for state in semantic_states):
        semantic_integrity = SemanticIntegrity.PASS
    else:
        semantic_integrity = SemanticIntegrity.UNOBSERVABLE

    confidence = sum(item.confidence for item in items) / len(items)
    evidence_refs = tuple(dict.fromkeys(ref for item in items for ref in item.evidence_refs))
    reasons: list[str] = []

    expired = [item.observation_id for item in items if _utc(item.freshness.expires_at) <= now]
    uncertain = [item.observation_id for item in items if item.uncertainty.present]
    unbound = [
        item.observation_id
        for item in items
        if item.acting_subject.binding_state != BindingState.BOUND
    ]
    disproved = [item.observation_id for item in items if item.threat_state == ThreatState.DISPROVEN]

    if expired:
        reasons.append("expired_observation:" + ",".join(expired))
    if uncertain:
        reasons.append("material_uncertainty:" + ",".join(uncertain))
    if unbound:
        reasons.append("acting_subject_not_fully_bound:" + ",".join(unbound))
    if disproved:
        reasons.append("disproving_evidence_present:" + ",".join(disproved))

    blocking = bool(expired or uncertain or unbound or disproved)
    states = {item.threat_state for item in items}

    if disproved and len(disproved) == len(items):
        state = ThreatState.DISPROVEN
    elif blocking:
        # Preserve useful correlation without escalating through unresolved critical evidence.
        state = ThreatState.CORRELATED if len(items) > 1 else ThreatState.OBSERVED
    elif ThreatState.IMMINENT_HARM in states:
        # An observed IMMINENT_HARM assertion requires strong fresh, bound evidence before
        # the planner can consider an intervention candidate.
        corroborated = len(items) > 1 or len(evidence_refs) > 1
        if confidence >= 0.80 and corroborated:
            state = ThreatState.IMMINENT_HARM
        else:
            state = ThreatState.ACTIVE
            reasons.append("imminent_harm_not_sufficiently_corroborated")
    elif ThreatState.ACTIVE in states:
        state = ThreatState.ACTIVE
    elif ThreatState.CREDIBLE in states:
        state = ThreatState.CREDIBLE
    elif len(items) > 1:
        state = ThreatState.CORRELATED
    else:
        state = ThreatState.OBSERVED

    return ThreatAssessment(
        subject_id=items[0].acting_subject.subject_id,
        state=state,
        confidence=confidence,
        observation_ids=tuple(item.observation_id for item in items),
        evidence_refs=evidence_refs,
        semantic_integrity=semantic_integrity,
        semantic_delta=semantic_delta,
        uncertainty_preserved=True,
        intervention_eligible=(state == ThreatState.IMMINENT_HARM and not blocking),
        reasons=tuple(reasons),
    )


def choose_least_destructive_effective_capability(
    assessment: ThreatAssessment,
    capabilities: Iterable[DefensiveCapability],
    *,
    as_of: datetime,
    mode: Literal["simulation", "production"],
    target_class: str,
    minimum_effectiveness: float = 0.70,
) -> DefensiveCapability | None:
    """Select the least-destructive fresh eligible TV/TVC capability."""
    if not assessment.intervention_eligible:
        return None
    now = _utc(as_of)

    eligible: list[DefensiveCapability] = []
    for capability in capabilities:
        if _utc(capability.freshness.expires_at) <= now:
            continue
        if target_class not in capability.scope.target_classes:
            continue
        if mode == "production" and not capability.production_eligible:
            continue
        if mode == "simulation" and not capability.simulation_eligible:
            continue
        if capability.effectiveness_estimate < minimum_effectiveness:
            continue
        if capability.intervention_class.value not in capability.scope.allowed_actions:
            continue
        if capability.intervention_class.value in capability.scope.forbidden_actions:
            continue
        eligible.append(capability)

    if not eligible:
        return None
    return min(
        eligible,
        key=lambda capability: (
            _DESTRUCTIVENESS_ORDER[capability.destructiveness],
            -capability.effectiveness_estimate,
            capability.capability_id,
        ),
    )


def build_intervention_request(
    assessment: ThreatAssessment,
    capability: DefensiveCapability,
    *,
    request_id: str,
    governed_principal_id: str,
    receipt_correlation_id: str,
    threatened_subject_ref: str | None = None,
) -> DefensiveInterventionRequest:
    """Build a canonical request candidate in PENDING admission state."""
    if not assessment.intervention_eligible or assessment.state != ThreatState.IMMINENT_HARM:
        raise ValueError("assessment is not eligible for defensive intervention")

    return DefensiveInterventionRequest(
        request_id=request_id,
        threat_observation_ref=assessment.observation_ids[0],
        governed_principal_id=governed_principal_id,
        threatened_subject_ref=threatened_subject_ref,
        intervention_class=capability.intervention_class,
        required_capability_id=capability.capability_id,
        admission=Admission(state="PENDING", intr_decision_ref=None),
        least_destructive_rationale=(
            f"selected {capability.capability_id} as the least-destructive eligible "
            f"capability meeting the effectiveness threshold"
        ),
        reversibility=capability.reversibility.value,
        reassessment_required=True,
        stop_condition=StopCondition(
            condition_type="THREAT_INTERRUPTED",
            description="Stop the intervention when the qualifying threat state is interrupted.",
        ),
        receipt_correlation_id=receipt_correlation_id,
        authority_refs=(capability.authorization_evidence_ref,),
        model_output_authority="NONE",
        authority_effect="ADMISSION_REQUIRED_BEFORE_ACTUATION",
        semantic_integrity=assessment.semantic_integrity,
        semantic_delta=assessment.semantic_delta,
    )
