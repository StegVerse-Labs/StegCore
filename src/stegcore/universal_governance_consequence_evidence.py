from __future__ import annotations

"""Canonical post-consequence evidence for Universal Governance integrations."""

from hashlib import sha256
import json
from typing import Any, Mapping, Sequence

from stegcore.external_adapter_steggate_execution import ExternalConsequenceExecutionEvidence
from stegcore.universal_governance_connector import GovernanceConnectorResult

SCHEMA = "stegcore.universal-governance-consequence-evidence.v1"
HASH_ALGORITHM = "sha256-canonical-json-without-evidence_hash"


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _hash_uri(value: Any) -> str:
    return "sha256:" + sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _evidence_hash(value: Mapping[str, Any]) -> str:
    unsigned = dict(value)
    unsigned.pop("evidence_hash", None)
    return _hash_uri(unsigned)


def build_universal_governance_consequence_evidence(
    *,
    adapter_id: str,
    governance_result: GovernanceConnectorResult,
    execution: ExternalConsequenceExecutionEvidence,
) -> dict[str, Any]:
    if not adapter_id:
        raise ValueError("consequence_evidence.adapter_id_missing")
    if governance_result.candidate_ref != execution.candidate_id:
        raise ValueError("consequence_evidence.candidate_id_mismatch")
    if governance_result.candidate_hash != execution.candidate_hash:
        raise ValueError("consequence_evidence.candidate_hash_mismatch")
    if governance_result.receipt_hash != execution.governance_receipt_hash:
        raise ValueError("consequence_evidence.governance_receipt_mismatch")
    if governance_result.intr_packet_id != execution.intr_packet_id:
        raise ValueError("consequence_evidence.request_intr_packet_mismatch")
    if execution.credential_authority != "TV/TVC":
        raise ValueError("consequence_evidence.credential_authority_mismatch")
    if execution.adapter_authority_effect != "NONE":
        raise ValueError("consequence_evidence.adapter_authority_effect_invalid")

    completed = execution.status == "COMPLETED"
    if completed:
        if execution.executor_invoked is not True or execution.consequence_observed is not True:
            raise ValueError("consequence_evidence.completed_without_observed_consequence")
        if not execution.coherence_receipt_hash:
            raise ValueError("consequence_evidence.completed_without_coherence_receipt")
        if execution.target_authority_effect != "TARGET_CONSEQUENCE_ONLY":
            raise ValueError("consequence_evidence.target_authority_effect_invalid")
    else:
        if execution.consequence_observed is True:
            raise ValueError("consequence_evidence.unexecuted_consequence_marked_observed")
        if execution.target_authority_effect != "NONE":
            raise ValueError("consequence_evidence.blocked_target_authority_effect_invalid")

    result_hash = _hash_uri(execution.result) if execution.result is not None else None
    evidence = {
        "schema": SCHEMA,
        "artifact_type": "universal_governance_consequence_evidence",
        "adapter_id": adapter_id,
        "profile_id": governance_result.profile_id,
        "system_id": governance_result.system_id,
        "boundary_id": governance_result.boundary_id,
        "candidate": {
            "candidate_ref": governance_result.candidate_ref,
            "candidate_hash": governance_result.candidate_hash,
        },
        "credential_binding": {
            "credential_id": execution.credential_id,
            "credential_hash": execution.credential_hash,
            "credential_authority": "TV/TVC",
        },
        "target_authority_ref": execution.authority_ref,
        "governance": {
            "decision": governance_result.decision,
            "reason_code": governance_result.reason_code,
            "receipt_hash": governance_result.receipt_hash,
            "request_intr_packet_id": governance_result.intr_packet_id,
            "request_intr_profile_ref": governance_result.intr_profile_ref,
            "execution_authority_granted": False,
            "authority_effect": "NONE",
        },
        "consequence": {
            "execution_profile_ref": execution.profile_ref,
            "status": execution.status,
            "executor_invoked": execution.executor_invoked,
            "consequence_observed": execution.consequence_observed,
            "coherence_receipt_hash": execution.coherence_receipt_hash,
            "result_hash": result_hash,
            "target_authority_effect": execution.target_authority_effect,
        },
        "authority_boundaries": {
            "adapter_grants_execution_authority": False,
            "governance_grants_execution_authority": False,
            "interlock_grants_execution_authority": False,
            "intr_grants_execution_authority": False,
            "hb_carrier_grants_execution_authority": False,
            "master_records_grants_execution_authority": False,
            "credential_authority": "TV/TVC",
            "continuity_receipt_minted": False,
            "publication_authority_granted": False,
        },
        "hash_algorithm": HASH_ALGORITHM,
    }
    evidence["evidence_hash"] = _evidence_hash(evidence)
    validate_universal_governance_consequence_evidence(evidence)
    return evidence


def validate_universal_governance_consequence_evidence(evidence: Mapping[str, Any]) -> None:
    if evidence.get("schema") != SCHEMA:
        raise ValueError("consequence_evidence.schema_invalid")
    supplied = evidence.get("evidence_hash")
    if not isinstance(supplied, str) or supplied != _evidence_hash(evidence):
        raise ValueError("consequence_evidence.hash_mismatch")
    if evidence.get("hash_algorithm") != HASH_ALGORITHM:
        raise ValueError("consequence_evidence.hash_algorithm_invalid")

    candidate = evidence.get("candidate")
    governance = evidence.get("governance")
    consequence = evidence.get("consequence")
    boundaries = evidence.get("authority_boundaries")
    credential = evidence.get("credential_binding")
    if not all(isinstance(x, Mapping) for x in (candidate, governance, consequence, boundaries, credential)):
        raise ValueError("consequence_evidence.structure_invalid")
    if not candidate.get("candidate_ref") or not candidate.get("candidate_hash"):
        raise ValueError("consequence_evidence.candidate_binding_missing")
    if governance.get("execution_authority_granted") is not False or governance.get("authority_effect") != "NONE":
        raise ValueError("consequence_evidence.governance_authority_escalation")
    if credential.get("credential_authority") != "TV/TVC":
        raise ValueError("consequence_evidence.credential_authority_mismatch")

    required_false = (
        "adapter_grants_execution_authority",
        "governance_grants_execution_authority",
        "interlock_grants_execution_authority",
        "intr_grants_execution_authority",
        "hb_carrier_grants_execution_authority",
        "master_records_grants_execution_authority",
        "continuity_receipt_minted",
        "publication_authority_granted",
    )
    if any(boundaries.get(key) is not False for key in required_false):
        raise ValueError("consequence_evidence.authority_boundary_violation")
    if boundaries.get("credential_authority") != "TV/TVC":
        raise ValueError("consequence_evidence.credential_authority_mismatch")

    completed = consequence.get("status") == "COMPLETED"
    if completed:
        if consequence.get("executor_invoked") is not True or consequence.get("consequence_observed") is not True:
            raise ValueError("consequence_evidence.completed_without_observation")
        if not consequence.get("coherence_receipt_hash"):
            raise ValueError("consequence_evidence.completed_without_coherence_receipt")
        if consequence.get("target_authority_effect") != "TARGET_CONSEQUENCE_ONLY":
            raise ValueError("consequence_evidence.target_authority_effect_invalid")
    elif consequence.get("consequence_observed") is True:
        raise ValueError("consequence_evidence.unexecuted_consequence_marked_observed")


def build_master_records_projection(
    evidence: Mapping[str, Any],
    *,
    source_repository: str,
    source_commit: str,
) -> dict[str, Any]:
    validate_universal_governance_consequence_evidence(evidence)
    if not source_repository or not source_commit:
        raise ValueError("master_records_projection.source_binding_missing")
    return {
        "schema": "stegcore.master-records-universal-governance-projection.v1",
        "destination_repository": "master-records/core-lite",
        "source_repository": source_repository,
        "source_commit": source_commit,
        "source_evidence_schema": SCHEMA,
        "source_evidence_hash": evidence["evidence_hash"],
        "candidate_ref": evidence["candidate"]["candidate_ref"],
        "candidate_hash": evidence["candidate"]["candidate_hash"],
        "governance_receipt_hash": evidence["governance"]["receipt_hash"],
        "request_intr_packet_id": evidence["governance"]["request_intr_packet_id"],
        "consequence_status": evidence["consequence"]["status"],
        "consequence_observed": evidence["consequence"]["consequence_observed"],
        "custody_requested": True,
        "destination_acknowledgement_minted": False,
        "execution_authority_granted": False,
        "credential_authority": "TV/TVC",
        "authority_effect": "NONE_SOURCE_PROJECTION_ONLY",
    }


def return_consequence_evidence_via_intr(
    *,
    connector: Any,
    request_packet: Any,
    request_receipts: Sequence[Mapping[str, Any]],
    evidence: Mapping[str, Any],
    operation_id: str,
    receipt_id: str,
    boundary_identity_ref: str,
    recorded_at: str,
) -> tuple[Any, dict[str, Any], dict[str, Any]]:
    """Return exact consequence evidence using the already-bound connector response path."""
    validate_universal_governance_consequence_evidence(evidence)
    response = connector.prepare_response(
        request_packet,
        request_receipts,
        evidence,
        payload_schema=SCHEMA,
        operation_id=operation_id,
    )
    prior = request_receipts[-1]["receipt_hash"]
    receipt = connector.accept_hop(
        response,
        hop_index=1,
        receipt_id=receipt_id,
        boundary_identity_ref=boundary_identity_ref,
        recorded_at=recorded_at,
        prior_receipt_hash=prior,
    )
    complete = connector.validate_complete(response, [receipt])
    if complete.get("state") != "TRANSPORT_COMPLETE":
        raise ValueError("consequence_evidence.return_transport_incomplete")
    if complete.get("payload_hash") != response.payload_hash:
        raise ValueError("consequence_evidence.return_transport_hash_mismatch")
    return response, receipt, complete
