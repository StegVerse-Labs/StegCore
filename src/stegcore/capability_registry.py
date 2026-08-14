from __future__ import annotations

"""Machine-readable registry for StegVerse capability existences.

The registry records lifecycle/evidence state; it does not evaluate policy, execute
capabilities, mint receipts, or infer activation from repository artifacts.
"""

import json
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field

from .admissible_existence import CapabilityExistenceDeclaration, ExistencePhase


class CapabilityPhaseEvidence(BaseModel):
    standing_evidence_refs: list[str] = Field(default_factory=list)
    admissibility_evidence_refs: list[str] = Field(default_factory=list)
    integration_evidence_refs: list[str] = Field(default_factory=list)
    activation_proof_ref: Optional[str] = None
    blockers: list[str] = Field(default_factory=list)
    continuation_owner: Optional[str] = None


class CapabilityRegistryEntry(BaseModel):
    declaration: CapabilityExistenceDeclaration
    existence_hash: str = Field(min_length=64, max_length=64)
    phase: ExistencePhase
    evidence: CapabilityPhaseEvidence = Field(default_factory=CapabilityPhaseEvidence)


class CapabilityExistenceRegistry(BaseModel):
    artifact_type: Literal["stegcore.capability_existence_registry"] = "stegcore.capability_existence_registry"
    schema_version: Literal["1.0"] = "1.0"
    entries: list[CapabilityRegistryEntry]


class RegistryFinding(BaseModel):
    capability_id: str
    code: str
    detail: str


class CapabilityRegistryValidation(BaseModel):
    artifact_type: Literal["stegcore.capability_existence_registry_validation"] = "stegcore.capability_existence_registry_validation"
    schema_version: Literal["1.0"] = "1.0"
    valid: bool
    entry_count: int
    findings: list[RegistryFinding]


_PHASES_REQUIRING_STANDING = {"STANDING", "ADMISSIBLE", "ACTIVATED", "SUSPENDED", "SUPERSEDED", "TERMINATED"}
_PHASES_REQUIRING_ADMISSIBILITY = {"ADMISSIBLE", "ACTIVATED", "SUSPENDED", "SUPERSEDED", "TERMINATED"}
_PHASES_REQUIRING_ACTIVATION = {"ACTIVATED", "SUSPENDED", "SUPERSEDED"}


def validate_capability_registry(registry: CapabilityExistenceRegistry) -> CapabilityRegistryValidation:
    findings: list[RegistryFinding] = []
    seen_ids: set[str] = set()
    seen_hashes: set[str] = set()

    for entry in registry.entries:
        capability_id = entry.declaration.capability_id
        expected_hash = entry.declaration.existence_hash

        if capability_id in seen_ids:
            findings.append(RegistryFinding(capability_id=capability_id, code="duplicate_capability_id", detail="capability_id must be unique"))
        seen_ids.add(capability_id)

        if entry.existence_hash in seen_hashes:
            findings.append(RegistryFinding(capability_id=capability_id, code="duplicate_existence_hash", detail="existence_hash must be unique"))
        seen_hashes.add(entry.existence_hash)

        if entry.existence_hash != expected_hash:
            findings.append(RegistryFinding(capability_id=capability_id, code="existence_hash_mismatch", detail=f"expected {expected_hash}"))

        evidence = entry.evidence
        if entry.phase in _PHASES_REQUIRING_STANDING and not evidence.standing_evidence_refs:
            findings.append(RegistryFinding(capability_id=capability_id, code="standing_evidence_missing", detail="phase requires standing evidence"))

        if entry.phase in _PHASES_REQUIRING_ADMISSIBILITY and not evidence.admissibility_evidence_refs:
            findings.append(RegistryFinding(capability_id=capability_id, code="admissibility_evidence_missing", detail="phase requires admissibility evidence"))

        if entry.phase in _PHASES_REQUIRING_ACTIVATION:
            if not evidence.integration_evidence_refs:
                findings.append(RegistryFinding(capability_id=capability_id, code="integration_evidence_missing", detail="activated lineage requires integration evidence"))
            if not evidence.activation_proof_ref:
                findings.append(RegistryFinding(capability_id=capability_id, code="activation_proof_missing", detail="activated lineage requires an activation proof"))

        if entry.phase == "ACTIVATED" and evidence.blockers:
            findings.append(RegistryFinding(capability_id=capability_id, code="activated_with_open_blockers", detail="ACTIVATED cannot retain unresolved activation blockers"))

        if entry.phase == "ADMISSIBLE" and evidence.blockers and not evidence.continuation_owner:
            findings.append(RegistryFinding(capability_id=capability_id, code="blocked_admissible_without_owner", detail="blocked ADMISSIBLE capability requires a continuation owner"))

    return CapabilityRegistryValidation(
        valid=not findings,
        entry_count=len(registry.entries),
        findings=findings,
    )


def load_capability_registry(path: str | Path) -> CapabilityExistenceRegistry:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return CapabilityExistenceRegistry.model_validate(data)
