from __future__ import annotations

"""Admissible-Existence structural lifecycle for StegVerse capabilities.

This module is deliberately not a policy evaluator. Every lifecycle transition is
first evaluated by the canonical StegGate composition. This layer only checks
structural lifecycle integrity and therefore cannot widen, reinterpret, or bypass
the canonical disposition.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field

from .steggate import AdmissibilityEvaluation, AdmissibilityRequest, canonical_sha256, evaluate_admissibility

ExistencePhase = Literal[
    "DECLARED",
    "STANDING",
    "ADMISSIBLE",
    "ACTIVATED",
    "SUSPENDED",
    "SUPERSEDED",
    "TERMINATED",
]
LifecycleOutcome = Literal["ADVANCED", "BLOCKED_CANONICAL", "BLOCKED_STRUCTURE"]


class CapabilityAuthorityEnvelope(BaseModel):
    """Authority metadata carried by the capability existence.

    Credential semantics are fixed to TV/TVC. This object never grants authority;
    it only records the envelope that downstream governed execution must respect.
    """

    credential_authority: Literal["TV/TVC"] = "TV/TVC"
    github_token_runtime_authority: Literal[False] = False
    may: list[str] = Field(default_factory=list)
    may_not: list[str] = Field(default_factory=list)


class CapabilityExistenceDeclaration(BaseModel):
    artifact_type: Literal["stegcore.capability_existence_declaration"] = "stegcore.capability_existence_declaration"
    schema_version: Literal["1.0"] = "1.0"
    capability_id: str = Field(min_length=1)
    capability_version: str = Field(min_length=1)
    owner_repository: str = Field(min_length=1)
    purpose: str = Field(min_length=1)
    dependencies: list[str] = Field(default_factory=list)
    predecessor_existence_hash: Optional[str] = None
    authority: CapabilityAuthorityEnvelope = Field(default_factory=CapabilityAuthorityEnvelope)
    evidence_refs: list[str] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)

    @property
    def existence_hash(self) -> str:
        return canonical_sha256(self.model_dump(mode="json", exclude_none=True))


class CapabilityExistenceTransition(BaseModel):
    declaration: CapabilityExistenceDeclaration
    from_phase: ExistencePhase
    target_phase: ExistencePhase
    admissibility: AdmissibilityRequest
    standing_verified: Optional[bool] = None
    integration_verified: Optional[bool] = None
    activation_proof_ref: Optional[str] = None
    successor_existence_hash: Optional[str] = None
    transition_evidence_refs: list[str] = Field(default_factory=list)


class CapabilityExistenceEvaluation(BaseModel):
    artifact_type: Literal["stegcore.capability_existence_evaluation"] = "stegcore.capability_existence_evaluation"
    schema_version: Literal["1.0"] = "1.0"
    existence_hash: str
    transition_hash: str
    from_phase: ExistencePhase
    target_phase: ExistencePhase
    resulting_phase: ExistencePhase
    lifecycle_outcome: LifecycleOutcome
    transition_admitted: bool
    structural_reasons: list[str]
    canonical_disposition: Literal["ALLOW", "DENY", "REVIEW", "FAIL_CLOSED"]
    canonical_candidate_hash: str
    canonical_reasons: list[str]
    canonical_evaluation: AdmissibilityEvaluation
    credential_authority: Literal["TV/TVC"] = "TV/TVC"
    github_token_runtime_authority: Literal[False] = False
    external_execution_performed: Literal[False] = False
    continuity_receipt_minted: Literal[False] = False


_ALLOWED_TRANSITIONS: dict[ExistencePhase, set[ExistencePhase]] = {
    "DECLARED": {"STANDING", "TERMINATED"},
    "STANDING": {"ADMISSIBLE", "TERMINATED"},
    "ADMISSIBLE": {"ACTIVATED", "TERMINATED"},
    "ACTIVATED": {"SUSPENDED", "SUPERSEDED", "TERMINATED"},
    "SUSPENDED": {"ACTIVATED", "SUPERSEDED", "TERMINATED"},
    "SUPERSEDED": {"TERMINATED"},
    "TERMINATED": set(),
}


def _structural_reasons(request: CapabilityExistenceTransition) -> list[str]:
    reasons: list[str] = []
    declaration = request.declaration

    if request.admissibility.candidate.target != declaration.capability_id:
        reasons.append("candidate_target_not_bound_to_capability_existence")

    if request.target_phase not in _ALLOWED_TRANSITIONS[request.from_phase]:
        reasons.append("invalid_existence_phase_transition")

    if request.target_phase == "STANDING" and request.standing_verified is not True:
        reasons.append("standing_not_verified")

    if request.target_phase == "ACTIVATED":
        if request.integration_verified is not True:
            reasons.append("integration_not_verified")
        if not request.activation_proof_ref:
            reasons.append("activation_proof_missing")

    if request.target_phase == "SUPERSEDED" and not request.successor_existence_hash:
        reasons.append("successor_existence_hash_missing")

    if request.declaration.predecessor_existence_hash == request.declaration.existence_hash:
        reasons.append("self_predecessor_forbidden")

    if request.successor_existence_hash == request.declaration.existence_hash:
        reasons.append("self_successor_forbidden")

    return reasons


def _stable_transition_hash(
    request: CapabilityExistenceTransition,
    canonical: AdmissibilityEvaluation,
    structural_reasons: list[str],
) -> str:
    """Replay-stable transition identity.

    Time-bound evaluation fields and canonical receipt hashes are intentionally not
    included in the identity. The original canonical evaluation is still retained
    in full on the result for provenance.
    """

    return canonical_sha256(
        {
            "existence_hash": request.declaration.existence_hash,
            "from_phase": request.from_phase,
            "target_phase": request.target_phase,
            "standing_verified": request.standing_verified,
            "integration_verified": request.integration_verified,
            "activation_proof_ref": request.activation_proof_ref,
            "successor_existence_hash": request.successor_existence_hash,
            "transition_evidence_refs": request.transition_evidence_refs,
            "canonical": {
                "disposition": canonical.disposition,
                "candidate_hash": canonical.candidate_hash,
                "reasons": canonical.reasons,
                "three_layer_decision": canonical.canonical_three_layer_decision,
                "three_layer_reason": canonical.canonical_three_layer_reason,
                "three_layer_request_hash": canonical.canonical_three_layer_request_hash,
                "permission_present": canonical.permission_present,
            },
            "structural_reasons": structural_reasons,
        }
    )


def evaluate_capability_existence(
    request: CapabilityExistenceTransition,
) -> CapabilityExistenceEvaluation:
    """Evaluate one structural capability transition through canonical StegGate.

    Canonical `ALLOW` is necessary but not sufficient for lifecycle advancement.
    Structural failures can block advancement, but can never turn a non-ALLOW
    canonical result into an allowed transition.
    """

    canonical = evaluate_admissibility(request.admissibility)
    structural_reasons = _structural_reasons(request)

    if canonical.disposition != "ALLOW":
        outcome: LifecycleOutcome = "BLOCKED_CANONICAL"
        admitted = False
        resulting_phase = request.from_phase
    elif structural_reasons:
        outcome = "BLOCKED_STRUCTURE"
        admitted = False
        resulting_phase = request.from_phase
    else:
        outcome = "ADVANCED"
        admitted = True
        resulting_phase = request.target_phase

    return CapabilityExistenceEvaluation(
        existence_hash=request.declaration.existence_hash,
        transition_hash=_stable_transition_hash(request, canonical, structural_reasons),
        from_phase=request.from_phase,
        target_phase=request.target_phase,
        resulting_phase=resulting_phase,
        lifecycle_outcome=outcome,
        transition_admitted=admitted,
        structural_reasons=structural_reasons,
        canonical_disposition=canonical.disposition,
        canonical_candidate_hash=canonical.candidate_hash,
        canonical_reasons=list(canonical.reasons),
        canonical_evaluation=canonical,
    )
