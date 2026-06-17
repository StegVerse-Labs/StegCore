"""Repo-aligned StegCore adapter for StegVerse-001 and StegVerse-002."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping


SUPPORTED_SCHEMAS = {
    "continuity_receipt": "StegVerse-001",
    "master_record_ingestion": "StegVerse-002",
}


@dataclass(frozen=True)
class AdmissibilityResult:
    """Result returned by the StegCore 001/002 adapter."""

    status: str
    reason: str
    entity: str
    principle: str


def _truthy(record: Mapping[str, Any], key: str, default: bool = False) -> bool:
    value = record.get(key, default)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return bool(value)


def _present(record: Mapping[str, Any], key: str) -> bool:
    value = record.get(key)
    return value is not None and str(value).strip() != ""


def map_schema_record_to_transition(record: Mapping[str, Any]) -> Dict[str, Any]:
    """Convert a schema-shaped entity record to an adapter transition map."""

    schema_id = str(record.get("schema_id") or record.get("schema", {}).get("id", ""))
    if schema_id not in SUPPORTED_SCHEMAS:
        raise ValueError(f"Unsupported schema_id: {schema_id}")

    expected_owner = SUPPORTED_SCHEMAS[schema_id]
    owner_entity = str(record.get("owner_entity") or record.get("schema", {}).get("owner_entity", ""))

    if owner_entity and owner_entity != expected_owner:
        raise ValueError(f"Schema {schema_id} must be owned by {expected_owner}, got {owner_entity}")

    return {
        "entity": expected_owner,
        "transition_type": schema_id,
        "authority_present": _present(record, "authority_context_ref"),
        "policy_present": _present(record, "policy_ref"),
        "identity_valid": record.get("identity_valid", True),
        "evidence_fresh": record.get("evidence_fresh", True),
        "context_valid": record.get("context_valid", True),
        "reviewer_refusal": record.get("reviewer_refusal", False),
        "override_requested": record.get("override_requested", False),
        "override_authority_verified": record.get("override_authority_verified", False),
        "public_user_direct_access": record.get("public_user_direct_access", False),
        "raw_master_record_ingestion": record.get("raw_master_record_ingestion", False),
    }


def evaluate_schema_record(record: Mapping[str, Any]) -> AdmissibilityResult:
    """Evaluate a schema-shaped StegVerse record through the adapter."""

    transition = map_schema_record_to_transition(record)
    return evaluate_transition_admissibility(transition)


def evaluate_transition_admissibility(record: Mapping[str, Any]) -> AdmissibilityResult:
    """Evaluate a transition record for commit-time admissibility posture."""

    entity = str(record.get("entity", "unknown"))

    if (
        entity == "StegVerse-002"
        and _truthy(record, "public_user_direct_access")
        and _truthy(record, "raw_master_record_ingestion")
    ):
        return AdmissibilityResult(
            status="deny",
            reason="StegVerse-002 cannot expose raw master-record ingestion to public users.",
            entity=entity,
            principle="restricted_internal_entities_are_not_public_user_surfaces",
        )

    if not _truthy(record, "authority_present"):
        return AdmissibilityResult(
            status="deny",
            reason="Authority context is missing.",
            entity=entity,
            principle="continuity_is_not_approval",
        )

    if not _truthy(record, "policy_present"):
        return AdmissibilityResult(
            status="deny",
            reason="Policy reference is missing.",
            entity=entity,
            principle="execution_is_not_admissibility",
        )

    if not _truthy(record, "identity_valid", default=True):
        return AdmissibilityResult(
            status="drift",
            reason="Identity validity changed beyond admissible limits.",
            entity=entity,
            principle="identity_drift_blocks_commit_time_standing",
        )

    if not _truthy(record, "context_valid", default=True):
        return AdmissibilityResult(
            status="drift",
            reason="Context validity changed beyond admissible limits.",
            entity=entity,
            principle="context_drift_blocks_commit_time_standing",
        )

    if not _truthy(record, "evidence_fresh", default=True):
        return AdmissibilityResult(
            status="stale",
            reason="Evidence is stale at commit time.",
            entity=entity,
            principle="evidence_staleness_blocks_commit_time_standing",
        )

    reviewer_refusal = _truthy(record, "reviewer_refusal")
    override_requested = _truthy(record, "override_requested")
    override_authority_verified = _truthy(record, "override_authority_verified")

    if reviewer_refusal and not override_authority_verified:
        return AdmissibilityResult(
            status="refusal",
            reason="Reviewer refusal binds consequence because override authority is not verified.",
            entity=entity,
            principle="refusal_must_bind_consequence",
        )

    if override_requested and not override_authority_verified:
        return AdmissibilityResult(
            status="override_required",
            reason="Override was requested but authority has not been verified.",
            entity=entity,
            principle="reviewer_is_not_override_authority",
        )

    return AdmissibilityResult(
        status="allow",
        reason="Authority, policy, identity, evidence, and context checks are valid.",
        entity=entity,
        principle="green_cell_requires_admissibility_not_merely_execution",
    )
