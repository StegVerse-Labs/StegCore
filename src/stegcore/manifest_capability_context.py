from __future__ import annotations

"""Canonical Admissible-Existence capability context for manifested transactions.

This module resolves requested capability identifiers against the canonical
StegCore capability-existence registry. Resolution is evidence/observation only:
it never grants policy, execution, credential, continuity, or activation
authority. Caller-supplied phase claims are not trusted.
"""

from typing import Literal, Mapping, Optional

from pydantic import BaseModel, Field

from .capability_registry import CapabilityExistenceRegistry, CapabilityRegistryEntry
from .steggate import canonical_sha256

RequiredCapabilityPhase = Literal["STANDING", "ADMISSIBLE", "ACTIVATED"]


class RequestedCapability(BaseModel):
    """A capability the manifested route intends to rely upon.

    ``required_phase`` is an execution precondition, not an assertion about the
    capability's actual lifecycle state. The actual state is resolved from the
    canonical registry.
    """

    capability_id: str = Field(min_length=1)
    required_phase: Optional[RequiredCapabilityPhase] = None


class ResolvedCapabilityEvidence(BaseModel):
    capability_id: str
    capability_version: str
    owner_repository: str
    existence_hash: str
    existence_phase: str
    required_phase: Optional[RequiredCapabilityPhase] = None
    required_phase_satisfied: bool
    standing_evidence_refs: list[str] = Field(default_factory=list)
    admissibility_evidence_refs: list[str] = Field(default_factory=list)
    integration_evidence_refs: list[str] = Field(default_factory=list)
    activation_proof_ref: Optional[str] = None
    blockers: list[str] = Field(default_factory=list)
    continuation_owner: Optional[str] = None
    credential_authority: Literal["TV/TVC"] = "TV/TVC"
    github_token_runtime_authority: Literal[False] = False
    resolution_grants_authority: Literal[False] = False


class ManifestCapabilityContext(BaseModel):
    artifact_type: Literal["stegcore.manifest_capability_context"] = "stegcore.manifest_capability_context"
    schema_version: Literal["1.0"] = "1.0"
    requested_capabilities: list[RequestedCapability]
    resolved_capabilities: list[ResolvedCapabilityEvidence]
    all_required_phases_satisfied: bool
    context_hash: str
    source: Literal["canonical_admissible_existence_registry"] = "canonical_admissible_existence_registry"
    caller_phase_claims_authoritative: Literal[False] = False
    grants_authority: Literal[False] = False


def _phase_satisfied(entry: CapabilityRegistryEntry, required: Optional[RequiredCapabilityPhase]) -> bool:
    if required is None:
        return True
    if required == "STANDING":
        return entry.phase in {"STANDING", "ADMISSIBLE", "ACTIVATED", "SUSPENDED", "SUPERSEDED", "TERMINATED"}
    if required == "ADMISSIBLE":
        return entry.phase in {"ADMISSIBLE", "ACTIVATED", "SUSPENDED", "SUPERSEDED", "TERMINATED"}
    # ACTIVATED is deliberately strict. A suspended, superseded, terminated, or
    # merely admissible capability is not currently activated for this boundary.
    return entry.phase == "ACTIVATED"


def resolve_manifest_capability_context(
    registry: CapabilityExistenceRegistry,
    requested_capabilities: list[RequestedCapability | Mapping[str, object]],
) -> ManifestCapabilityContext:
    """Resolve a manifested run's capability context from canonical AE state.

    Unknown/duplicate capability requests and unmet declared phase requirements
    fail closed before consequential execution. Registry resolution never grants
    authority; canonical StegGate remains the policy/consequence boundary.
    """

    requested = [
        item if isinstance(item, RequestedCapability) else RequestedCapability.model_validate(item)
        for item in requested_capabilities
    ]
    ids = [item.capability_id for item in requested]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate_requested_capability_id")

    by_id = {entry.declaration.capability_id: entry for entry in registry.entries}
    resolved: list[ResolvedCapabilityEvidence] = []
    for request in requested:
        entry = by_id.get(request.capability_id)
        if entry is None:
            raise ValueError(f"capability_not_found:{request.capability_id}")
        declaration = entry.declaration
        evidence = entry.evidence
        satisfied = _phase_satisfied(entry, request.required_phase)
        resolved.append(
            ResolvedCapabilityEvidence(
                capability_id=declaration.capability_id,
                capability_version=declaration.capability_version,
                owner_repository=declaration.owner_repository,
                existence_hash=entry.existence_hash,
                existence_phase=entry.phase,
                required_phase=request.required_phase,
                required_phase_satisfied=satisfied,
                standing_evidence_refs=list(evidence.standing_evidence_refs),
                admissibility_evidence_refs=list(evidence.admissibility_evidence_refs),
                integration_evidence_refs=list(evidence.integration_evidence_refs),
                activation_proof_ref=evidence.activation_proof_ref,
                blockers=list(evidence.blockers),
                continuation_owner=evidence.continuation_owner,
            )
        )

    unsatisfied = [
        item.capability_id for item in resolved if not item.required_phase_satisfied
    ]
    if unsatisfied:
        raise ValueError("capability_required_phase_not_satisfied:" + ",".join(unsatisfied))

    body = {
        "artifact_type": "stegcore.manifest_capability_context",
        "schema_version": "1.0",
        "requested_capabilities": [item.model_dump(mode="json") for item in requested],
        "resolved_capabilities": [item.model_dump(mode="json") for item in resolved],
        "all_required_phases_satisfied": True,
        "source": "canonical_admissible_existence_registry",
        "caller_phase_claims_authoritative": False,
        "grants_authority": False,
    }
    return ManifestCapabilityContext(**body, context_hash=canonical_sha256(body))
