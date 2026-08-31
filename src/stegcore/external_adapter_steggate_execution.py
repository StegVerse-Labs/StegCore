from __future__ import annotations

"""Bridge Universal Governance adapter admission into canonical StegGate commit execution."""

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Callable, Mapping

from stegcore.commit_governance import execute_if_coherent, verify_receipt_integrity
from stegcore.external_governance_adapter import (
    AdapterPreparedRequest,
    ConsequenceGateResult,
    gate_external_consequence,
    native_candidate_hash,
)
from stegcore.universal_governance_connector import GovernanceConnectorResult


PROFILE_ID = "SG-EXECUTION-DETERMINISTIC-v1"


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _sha256_uri(value: Any) -> str:
    raw = _canonical_json(value).encode("utf-8")
    return "sha256:" + sha256(raw).hexdigest()


def _is_sha256_uri(value: Any) -> bool:
    return (
        isinstance(value, str)
        and value.startswith("sha256:")
        and len(value) == 71
        and all(ch in "0123456789abcdef" for ch in value[7:])
    )


@dataclass(frozen=True)
class TargetCredentialBinding:
    credential_id: str
    credential_hash: str
    subject_binding: str


@dataclass(frozen=True)
class PreparedStegGateExecution:
    execution_request: Mapping[str, Any]
    governance_receipt_hash: str
    intr_packet_id: str
    adapter_id: str
    consequence_gate: ConsequenceGateResult


@dataclass(frozen=True)
class ExternalConsequenceExecutionEvidence:
    status: str
    executor_invoked: bool
    consequence_observed: bool
    profile_ref: str
    candidate_id: str
    candidate_hash: str
    credential_id: str
    credential_hash: str
    authority_ref: str
    governance_receipt_hash: str
    intr_packet_id: str
    coherence_receipt_hash: str | None
    result: Any
    credential_authority: str
    adapter_authority_effect: str
    target_authority_effect: str


def _native_operation_for_prepared(
    adapter: Mapping[str, Any],
    prepared: AdapterPreparedRequest,
) -> str:
    matches = [
        op for op in adapter.get("operations", [])
        if isinstance(op, Mapping)
        and op.get("governance_operation_id") == prepared.payload.get("operation_id")
    ]
    if len(matches) != 1:
        raise ValueError("execution.adapter_operation_binding_ambiguous")
    native = matches[0].get("native_operation")
    if not isinstance(native, str) or not native:
        raise ValueError("execution.native_operation_missing")
    return native


def build_steggate_execution_request(
    adapter: Mapping[str, Any],
    registry: Mapping[str, Any],
    prepared: AdapterPreparedRequest,
    governance_result: GovernanceConnectorResult,
    *,
    parameters: Mapping[str, Any],
    credential: TargetCredentialBinding,
    capability_surface: Mapping[str, Any] | None = None,
) -> PreparedStegGateExecution:
    gate = gate_external_consequence(adapter, registry, prepared, governance_result)
    if gate.state != "ELIGIBLE_FOR_SEPARATE_CONSEQUENCE_AUTHORITY":
        raise ValueError("execution.governance_or_adapter_gate_not_eligible")
    if not _is_sha256_uri(credential.credential_hash):
        raise ValueError("execution.credential_hash_invalid")
    if not credential.credential_id or not credential.subject_binding:
        raise ValueError("execution.credential_binding_missing")

    native_operation = _native_operation_for_prepared(adapter, prepared)
    action = {"name": native_operation, "parameters": dict(parameters)}
    candidate_id = str(prepared.payload.get("candidate_ref") or "")
    if not candidate_id:
        raise ValueError("execution.candidate_id_missing")
    candidate_hash = native_candidate_hash(
        candidate_ref=candidate_id,
        native_operation=native_operation,
        parameters=parameters,
    )
    if prepared.payload.get("candidate_hash") != candidate_hash:
        raise ValueError("execution.governance_candidate_hash_mismatch")
    if governance_result.candidate_hash != candidate_hash:
        raise ValueError("execution.governance_result_candidate_hash_mismatch")

    surface = dict(capability_surface or {
        "actions_exposed": [native_operation],
        "execution_mode": "governed",
        "requires_governed_commit": True,
    })
    if set(surface.get("actions_exposed") or []) != {native_operation}:
        raise ValueError("execution.capability_action_not_exposed_or_broadened")
    if surface.get("execution_mode") not in {"manual", "bounded", "governed"}:
        raise ValueError("execution.capability_mode_forbidden")
    if surface.get("requires_governed_commit") is not True:
        raise ValueError("execution.governed_commit_required")

    authority_ref = prepared.consequence_authority_ref
    if not authority_ref:
        raise ValueError("execution.authority_ref_missing")
    execution_basis = {
        "candidate_hash": candidate_hash,
        "credential_hash": credential.credential_hash,
        "authority_ref": authority_ref,
        "governance_receipt_hash": governance_result.receipt_hash,
        "intr_packet_id": governance_result.intr_packet_id,
    }
    execution_id = "SGEXEC-" + sha256(_canonical_json(execution_basis).encode("utf-8")).hexdigest()[:24]

    request = {
        "schema_version": "steggate.execution-request.v1",
        "execution_id": execution_id,
        "candidate_id": candidate_id,
        "candidate_hash": candidate_hash,
        "credential_binding": {
            "credential_id": credential.credential_id,
            "credential_hash": credential.credential_hash,
            "subject_binding": credential.subject_binding,
        },
        "action": action,
        "capability_surface": surface,
        "authority_ref": authority_ref,
        "profile_ref": PROFILE_ID,
    }
    validate_steggate_execution_request(request, prepared=prepared)
    return PreparedStegGateExecution(
        execution_request=request,
        governance_receipt_hash=governance_result.receipt_hash,
        intr_packet_id=governance_result.intr_packet_id,
        adapter_id=prepared.adapter_id,
        consequence_gate=gate,
    )


def validate_steggate_execution_request(
    request: Mapping[str, Any],
    *,
    prepared: AdapterPreparedRequest,
) -> None:
    required = {
        "schema_version", "execution_id", "candidate_id", "candidate_hash",
        "credential_binding", "action", "capability_surface", "authority_ref", "profile_ref",
    }
    if set(request) != required:
        raise ValueError("execution.request_field_set_invalid")
    if request.get("schema_version") != "steggate.execution-request.v1":
        raise ValueError("execution.request_schema_invalid")
    if request.get("profile_ref") != PROFILE_ID:
        raise ValueError("execution.profile_ref_invalid")
    if request.get("candidate_id") != prepared.payload.get("candidate_ref"):
        raise ValueError("execution.candidate_id_mismatch")
    action = request.get("action")
    if not isinstance(action, Mapping) or set(action) != {"name", "parameters"}:
        raise ValueError("execution.action_invalid")
    expected_hash = native_candidate_hash(
        candidate_ref=str(request["candidate_id"]),
        native_operation=str(action["name"]),
        parameters=action["parameters"],
    )
    if request.get("candidate_hash") != expected_hash:
        raise ValueError("execution.candidate_binding_mismatch")
    if prepared.payload.get("candidate_hash") != expected_hash:
        raise ValueError("execution.governance_candidate_hash_mismatch")
    credential = request.get("credential_binding")
    if not isinstance(credential, Mapping) or set(credential) != {"credential_id", "credential_hash", "subject_binding"}:
        raise ValueError("execution.credential_binding_invalid")
    if not credential.get("credential_id") or not credential.get("subject_binding") or not _is_sha256_uri(credential.get("credential_hash")):
        raise ValueError("execution.credential_binding_invalid")
    if request.get("authority_ref") != prepared.consequence_authority_ref:
        raise ValueError("execution.authority_ref_mismatch")
    surface = request.get("capability_surface")
    if not isinstance(surface, Mapping):
        raise ValueError("execution.capability_surface_invalid")
    if set(surface.get("actions_exposed") or []) != {action["name"]}:
        raise ValueError("execution.capability_action_not_exposed_or_broadened")
    if surface.get("execution_mode") not in {"manual", "bounded", "governed"}:
        raise ValueError("execution.capability_mode_forbidden")
    if surface.get("requires_governed_commit") is not True:
        raise ValueError("execution.governed_commit_required")


def execute_external_consequence_if_coherent(
    prepared_execution: PreparedStegGateExecution,
    *,
    prepared_adapter_request: AdapterPreparedRequest,
    task_runner: Callable[[str, Mapping[str, Any]], Any],
    authority_resolution: Mapping[str, Any],
    previous_receipt_hash: str | None = None,
) -> ExternalConsequenceExecutionEvidence:
    request = prepared_execution.execution_request
    validate_steggate_execution_request(request, prepared=prepared_adapter_request)

    credential = request["credential_binding"]
    if authority_resolution.get("authority_ref") != request["authority_ref"]:
        return _blocked_evidence(prepared_execution, request, "AUTHORITY_REF_MISMATCH")
    if authority_resolution.get("credential_id") != credential["credential_id"]:
        return _blocked_evidence(prepared_execution, request, "CREDENTIAL_ID_MISMATCH")
    if authority_resolution.get("credential_hash") != credential["credential_hash"]:
        return _blocked_evidence(prepared_execution, request, "CREDENTIAL_HASH_MISMATCH")
    if authority_resolution.get("subject_binding") != credential["subject_binding"]:
        return _blocked_evidence(prepared_execution, request, "SUBJECT_BINDING_MISMATCH")

    action = request["action"]
    result = execute_if_coherent(
        task_runner=task_runner,
        task=action["name"],
        payload=action["parameters"],
        capability_surface=request["capability_surface"],
        state_hash=prepared_execution.governance_receipt_hash,
        actor_binding=credential["subject_binding"],
        authority_resolution=authority_resolution,
        previous_receipt_hash=previous_receipt_hash,
    )
    receipt = result["receipt"]
    if not verify_receipt_integrity(receipt):
        raise ValueError("execution.coherence_receipt_integrity_failed")
    completed = result["status"] == "COMPLETED"
    return ExternalConsequenceExecutionEvidence(
        status=result["status"],
        executor_invoked=completed,
        consequence_observed=completed,
        profile_ref=PROFILE_ID,
        candidate_id=request["candidate_id"],
        candidate_hash=request["candidate_hash"],
        credential_id=credential["credential_id"],
        credential_hash=credential["credential_hash"],
        authority_ref=request["authority_ref"],
        governance_receipt_hash=prepared_execution.governance_receipt_hash,
        intr_packet_id=prepared_execution.intr_packet_id,
        coherence_receipt_hash=receipt["receipt_hash"],
        result=result.get("result"),
        credential_authority="TV/TVC",
        adapter_authority_effect="NONE",
        target_authority_effect="TARGET_CONSEQUENCE_ONLY" if completed else "NONE",
    )


def _blocked_evidence(
    prepared_execution: PreparedStegGateExecution,
    request: Mapping[str, Any],
    reason: str,
) -> ExternalConsequenceExecutionEvidence:
    credential = request["credential_binding"]
    return ExternalConsequenceExecutionEvidence(
        status="DENIED:" + reason,
        executor_invoked=False,
        consequence_observed=False,
        profile_ref=PROFILE_ID,
        candidate_id=request["candidate_id"],
        candidate_hash=request["candidate_hash"],
        credential_id=credential["credential_id"],
        credential_hash=credential["credential_hash"],
        authority_ref=request["authority_ref"],
        governance_receipt_hash=prepared_execution.governance_receipt_hash,
        intr_packet_id=prepared_execution.intr_packet_id,
        coherence_receipt_hash=None,
        result=None,
        credential_authority="TV/TVC",
        adapter_authority_effect="NONE",
        target_authority_effect="NONE",
    )
