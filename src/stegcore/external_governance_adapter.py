from __future__ import annotations

"""Thin external-system adapter for the Universal Governance Connector.

This module translates native system facts into the canonical Governance
request contract and consumes the returned Governance decision. It does not
execute target consequences, grant credentials, or provide transport.
"""

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Mapping

from stegcore.universal_governance_connector import (
    GovernanceConnectorResult,
    VerifiedTransportBindings,
    evaluate_governance_connector,
    parse_registered_governance_connector_request,
    resolve_governance_connector_profile,
)


@dataclass(frozen=True)
class NativeGovernanceAction:
    native_operation: str
    native_action_ref: str
    native_intent_ref: str
    native_authority_ref: str
    native_parameters: Mapping[str, Any]
    native_evidence_refs: tuple[str, ...]
    resolved_governance_facts: Mapping[str, Any]
    consequence_authority_ref: str


@dataclass(frozen=True)
class AdapterPreparedRequest:
    adapter_id: str
    payload: Mapping[str, Any]
    consequence_authority_ref: str
    enforcement_claim: str
    protected_consequence: bool
    adapter_authority_effect: str = "NONE"


@dataclass(frozen=True)
class ConsequenceGateResult:
    state: str
    decision: str
    reason_code: str
    eligible_for_separate_consequence_authority: bool
    consequence_authority_ref_present: bool
    consequence_executed: bool
    adapter_grants_execution_authority: bool
    governance_grants_execution_authority: bool
    credential_authority: str
    authority_effect: str


_ENFORCEMENT_RANK = {"OBSERVABLE": 0, "GOVERNED": 1, "ENFORCED": 2}
_CANDIDATE_HASH_PROFILE = "stegverse.external-native-action-candidate.v1"


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def native_candidate_hash(*, candidate_ref: str, native_operation: str, parameters: Mapping[str, Any]) -> str:
    basis = {
        "candidate_ref": candidate_ref,
        "native_operation": native_operation,
        "parameters": dict(parameters),
    }
    return "sha256:" + sha256(_canonical_json(basis).encode("utf-8")).hexdigest()


def _adapter_operation(adapter: Mapping[str, Any], native_operation: str) -> Mapping[str, Any] | None:
    for op in adapter.get("operations", []):
        if isinstance(op, Mapping) and op.get("native_operation") == native_operation:
            return op
    return None


def validate_external_governance_adapter(
    adapter: Mapping[str, Any],
    registry: Mapping[str, Any],
) -> Mapping[str, Any]:
    if adapter.get("schema_version") != "stegverse.governance-external-adapter.v1":
        raise ValueError("adapter.schema_unsupported")
    profile_id = adapter.get("governance_profile_id")
    if not isinstance(profile_id, str) or not profile_id:
        raise ValueError("adapter.profile_id_missing")
    profile = resolve_governance_connector_profile(registry, profile_id)
    if adapter.get("candidate_hash_profile") != _CANDIDATE_HASH_PROFILE:
        raise ValueError("adapter.candidate_hash_profile_invalid")

    if adapter.get("system_id") != profile.get("system", {}).get("system_id"):
        raise ValueError("adapter.system_id_mismatch")
    if adapter.get("boundary_id") != profile.get("system", {}).get("boundary_id"):
        raise ValueError("adapter.boundary_id_mismatch")

    claim = adapter.get("enforcement_claim")
    profile_claim = profile.get("system", {}).get("enforcement_class")
    if claim not in _ENFORCEMENT_RANK or profile_claim not in _ENFORCEMENT_RANK:
        raise ValueError("adapter.enforcement_claim_invalid")
    if _ENFORCEMENT_RANK[claim] > _ENFORCEMENT_RANK[profile_claim]:
        raise ValueError("adapter.enforcement_claim_exceeds_profile")
    if claim == "ENFORCED":
        if adapter.get("bypass_path_declared") is not False:
            raise ValueError("adapter.enforced_bypass_declared")
        refs = adapter.get("bypass_evidence_refs")
        if not isinstance(refs, list) or not refs:
            raise ValueError("adapter.enforced_bypass_evidence_missing")

    authority = adapter.get("authority_boundaries")
    if not isinstance(authority, Mapping):
        raise ValueError("adapter.authority_boundaries_missing")
    for key in (
        "adapter_grants_execution_authority",
        "adapter_grants_credential_authority",
        "governance_allow_executes_consequence",
    ):
        if authority.get(key) is not False:
            raise ValueError("adapter.authority_escalation")
    if authority.get("credential_authority") != "TV/TVC":
        raise ValueError("adapter.credential_authority_mismatch")
    if authority.get("authority_effect") != "NONE":
        raise ValueError("adapter.authority_effect_invalid")

    profile_ops = {x["operation_id"] for x in profile.get("operations", []) if isinstance(x, Mapping)}
    seen: set[str] = set()
    ops = adapter.get("operations")
    if not isinstance(ops, list) or not ops:
        raise ValueError("adapter.operations_missing")
    for op in ops:
        if not isinstance(op, Mapping):
            raise ValueError("adapter.operation_invalid")
        native = op.get("native_operation")
        if not isinstance(native, str) or not native or native in seen:
            raise ValueError("adapter.native_operation_invalid")
        seen.add(native)
        if op.get("governance_operation_id") not in profile_ops:
            raise ValueError("adapter.governance_operation_unknown")
        if op.get("consequence_authority_ref_required") is not True:
            raise ValueError("adapter.separate_consequence_authority_required")
        for key in ("input_mapping", "evidence_mapping"):
            if not isinstance(op.get(key), Mapping) or not op[key]:
                raise ValueError(f"adapter.{key}_invalid")
        if op["input_mapping"].get("native_parameters") != "candidate_hash_basis.parameters":
            raise ValueError("adapter.native_parameters_candidate_hash_mapping_invalid")
    return profile


def prepare_external_governance_request(
    adapter: Mapping[str, Any],
    registry: Mapping[str, Any],
    native: NativeGovernanceAction,
) -> AdapterPreparedRequest:
    profile = validate_external_governance_adapter(adapter, registry)
    operation = _adapter_operation(adapter, native.native_operation)
    if operation is None:
        raise ValueError("adapter.native_operation_unknown")
    if not native.native_action_ref or not native.native_intent_ref or not native.native_authority_ref:
        raise ValueError("adapter.native_identity_or_authority_missing")
    if not isinstance(native.native_parameters, Mapping):
        raise ValueError("adapter.native_parameters_missing")
    if not native.native_evidence_refs:
        raise ValueError("adapter.native_evidence_missing")
    if not isinstance(native.resolved_governance_facts, Mapping):
        raise ValueError("adapter.resolved_governance_facts_missing")
    if operation.get("consequence_authority_ref_required") is True and not native.consequence_authority_ref:
        raise ValueError("adapter.consequence_authority_ref_missing")

    candidate_hash = native_candidate_hash(
        candidate_ref=native.native_action_ref,
        native_operation=native.native_operation,
        parameters=native.native_parameters,
    )
    payload = {
        "schema_version": "stegverse.governance-connector.request/v1",
        "profile_id": profile["profile_id"],
        "operation_id": operation["governance_operation_id"],
        "system_id": adapter["system_id"],
        "boundary_id": adapter["boundary_id"],
        "authority_ref": native.native_authority_ref,
        "intent_ref": native.native_intent_ref,
        "candidate_ref": native.native_action_ref,
        "candidate_hash": candidate_hash,
        "evidence_refs": list(native.native_evidence_refs),
        "resolved_facts": dict(native.resolved_governance_facts),
    }
    return AdapterPreparedRequest(
        adapter_id=str(adapter["adapter_id"]),
        payload=payload,
        consequence_authority_ref=native.consequence_authority_ref,
        enforcement_claim=str(adapter["enforcement_claim"]),
        protected_consequence=bool(operation.get("protected_consequence")),
    )


def evaluate_prepared_external_governance_request(
    registry: Mapping[str, Any],
    prepared: AdapterPreparedRequest,
    transport: VerifiedTransportBindings,
) -> GovernanceConnectorResult:
    profile, parsed = parse_registered_governance_connector_request(
        registry, prepared.payload, transport
    )
    return evaluate_governance_connector(profile, parsed)


def gate_external_consequence(
    adapter: Mapping[str, Any],
    registry: Mapping[str, Any],
    prepared: AdapterPreparedRequest,
    result: GovernanceConnectorResult,
) -> ConsequenceGateResult:
    validate_external_governance_adapter(adapter, registry)
    if result.execution_authority_granted is not False:
        raise ValueError("adapter.governance_execution_authority_violation")
    if result.credential_authority != "TV/TVC":
        raise ValueError("adapter.governance_credential_authority_violation")

    authority_present = bool(prepared.consequence_authority_ref)
    eligible = (
        result.decision == "ALLOW"
        and result.eligible_for_separate_consequence_authorization is True
        and authority_present
    )
    if result.decision == "ALLOW" and not authority_present:
        state = "FAIL-CLOSED"
        reason = "adapter.consequence_authority_ref_missing"
    elif eligible:
        state = "ELIGIBLE_FOR_SEPARATE_CONSEQUENCE_AUTHORITY"
        reason = "adapter.governance_allow_non_executing"
    else:
        state = "CONSEQUENCE_BLOCKED"
        reason = result.reason_code

    return ConsequenceGateResult(
        state=state,
        decision=result.decision,
        reason_code=reason,
        eligible_for_separate_consequence_authority=eligible,
        consequence_authority_ref_present=authority_present,
        consequence_executed=False,
        adapter_grants_execution_authority=False,
        governance_grants_execution_authority=False,
        credential_authority="TV/TVC",
        authority_effect="NONE",
    )
