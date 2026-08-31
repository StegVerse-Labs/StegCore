from __future__ import annotations

"""Profile-driven universal governance connector runtime.

This module composes a Governance-owned connector profile with the existing
StegCore three-layer evaluator. It does not provide transport, credentials,
continuity minting, custody, or target-system execution.
"""

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any, Mapping, Sequence

from stegcore.three_layer import ThreeLayerRequest, ThreeLayerResult, evaluate_three_layer


@dataclass(frozen=True)
class GovernanceConnectorRequest:
    profile_id: str
    operation_id: str
    system_id: str
    boundary_id: str
    interlock_exchange_id: str
    intr_packet_id: str
    intr_profile_ref: str
    governed_transition_profile_ref: str
    carrier_profile_ref: str
    authority_ref: str
    intent_ref: str
    candidate_ref: str
    evidence_refs: tuple[str, ...]
    three_layer_request: ThreeLayerRequest


@dataclass(frozen=True)
class GovernanceConnectorResult:
    artifact_type: str
    decision: str
    reason_code: str
    profile_id: str
    profile_version: str
    operation_id: str
    system_id: str
    boundary_id: str
    interlock_exchange_id: str
    intr_packet_id: str
    intr_profile_ref: str
    governed_transition_profile_ref: str
    carrier_profile_ref: str
    policy_ref: str
    authority_ref: str
    intent_ref: str
    candidate_ref: str
    evidence_refs: tuple[str, ...]
    three_layer_receipt: Mapping[str, Any] | None
    eligible_for_separate_consequence_authorization: bool
    execution_authority_granted: bool
    credential_authority: str
    continuity_receipt_minted: bool
    authority_effect: str
    receipt_hash: str


def _canonical_hash(value: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()


def _operation(profile: Mapping[str, Any], operation_id: str) -> Mapping[str, Any] | None:
    for op in profile.get("operations", []):
        if isinstance(op, Mapping) and op.get("operation_id") == operation_id:
            return op
    return None


def _profile_error(profile: Mapping[str, Any]) -> str | None:
    if profile.get("schema_version") != "stegverse.governance-connector-profile.v1":
        return "connector.profile_schema_unsupported"
    if not profile.get("profile_id") or not profile.get("profile_version"):
        return "connector.profile_identity_missing"
    system = profile.get("system")
    interlock = profile.get("interlock")
    runtime = profile.get("runtime")
    boundaries = profile.get("authority_boundaries")
    evidence = profile.get("evidence")
    if not all(isinstance(x, Mapping) for x in (system, interlock, runtime, boundaries, evidence)):
        return "connector.profile_structure_invalid"
    if system.get("enforcement_class") == "ENFORCED" and system.get("bypass_path_declared") is not False:
        return "connector.enforced_bypass_declared"
    if interlock.get("required") is not True or interlock.get("fail_closed_on_binding_error") is not True:
        return "connector.interlock_not_fail_closed"
    if runtime.get("evaluator_ref") != "stegcore.three_layer.evaluate_three_layer":
        return "connector.evaluator_unsupported"
    if runtime.get("execution_requires_separate_authority") is not True:
        return "connector.execution_authority_separation_missing"
    if set(runtime.get("decision_surface", [])) != {"ALLOW", "DENY", "FAIL-CLOSED"}:
        return "connector.decision_surface_invalid"
    required_false = (
        "profile_grants_execution_authority",
        "interlock_grants_execution_authority",
        "intr_grants_execution_authority",
        "carrier_grants_execution_authority",
        "governance_allow_grants_credential_authority",
    )
    if any(boundaries.get(key) is not False for key in required_false):
        return "connector.authority_escalation"
    if boundaries.get("credential_authority") != "TV/TVC":
        return "connector.credential_authority_mismatch"
    for key in (
        "ingress_receipt_required",
        "decision_receipt_required",
        "egress_receipt_required",
        "reconstruction_required",
    ):
        if evidence.get(key) is not True:
            return "connector.evidence_chain_incomplete"
    return None


def _result(
    profile: Mapping[str, Any],
    request: GovernanceConnectorRequest,
    *,
    decision: str,
    reason_code: str,
    three_layer_result: ThreeLayerResult | None = None,
) -> GovernanceConnectorResult:
    operation = _operation(profile, request.operation_id) or {}
    payload = {
        "artifact_type": "stegcore.universal_governance_connector_decision",
        "decision": decision,
        "reason_code": reason_code,
        "profile_id": str(profile.get("profile_id") or request.profile_id),
        "profile_version": str(profile.get("profile_version") or ""),
        "operation_id": request.operation_id,
        "system_id": request.system_id,
        "boundary_id": request.boundary_id,
        "interlock_exchange_id": request.interlock_exchange_id,
        "intr_packet_id": request.intr_packet_id,
        "intr_profile_ref": request.intr_profile_ref,
        "governed_transition_profile_ref": request.governed_transition_profile_ref,
        "carrier_profile_ref": request.carrier_profile_ref,
        "policy_ref": str(operation.get("policy_ref") or request.three_layer_request.execution_boundary.policy_ref),
        "authority_ref": request.authority_ref,
        "intent_ref": request.intent_ref,
        "candidate_ref": request.candidate_ref,
        "evidence_refs": list(request.evidence_refs),
        "three_layer_receipt": dict(three_layer_result.receipt) if three_layer_result is not None else None,
        "eligible_for_separate_consequence_authorization": decision == "ALLOW",
        "execution_authority_granted": False,
        "credential_authority": "TV/TVC",
        "continuity_receipt_minted": False,
        "authority_effect": "NONE",
    }
    receipt_hash = _canonical_hash(payload)
    return GovernanceConnectorResult(
        artifact_type=payload["artifact_type"],
        decision=decision,
        reason_code=reason_code,
        profile_id=payload["profile_id"],
        profile_version=payload["profile_version"],
        operation_id=request.operation_id,
        system_id=request.system_id,
        boundary_id=request.boundary_id,
        interlock_exchange_id=request.interlock_exchange_id,
        intr_packet_id=request.intr_packet_id,
        intr_profile_ref=request.intr_profile_ref,
        governed_transition_profile_ref=request.governed_transition_profile_ref,
        carrier_profile_ref=request.carrier_profile_ref,
        policy_ref=payload["policy_ref"],
        authority_ref=request.authority_ref,
        intent_ref=request.intent_ref,
        candidate_ref=request.candidate_ref,
        evidence_refs=tuple(request.evidence_refs),
        three_layer_receipt=payload["three_layer_receipt"],
        eligible_for_separate_consequence_authorization=payload["eligible_for_separate_consequence_authorization"],
        execution_authority_granted=False,
        credential_authority="TV/TVC",
        continuity_receipt_minted=False,
        authority_effect="NONE",
        receipt_hash=receipt_hash,
    )


def evaluate_governance_connector(
    profile: Mapping[str, Any],
    request: GovernanceConnectorRequest,
) -> GovernanceConnectorResult:
    """Validate connector bindings and evaluate through canonical three-layer governance.

    Connector/binding failures are represented as FAIL-CLOSED decisions.
    """
    profile_error = _profile_error(profile)
    if profile_error:
        return _result(profile, request, decision="FAIL-CLOSED", reason_code=profile_error)

    if request.profile_id != profile.get("profile_id"):
        return _result(profile, request, decision="FAIL-CLOSED", reason_code="connector.profile_id_mismatch")

    system = profile["system"]
    interlock = profile["interlock"]
    if request.system_id != system.get("system_id"):
        return _result(profile, request, decision="FAIL-CLOSED", reason_code="connector.system_id_mismatch")
    if request.boundary_id != system.get("boundary_id"):
        return _result(profile, request, decision="FAIL-CLOSED", reason_code="connector.boundary_id_mismatch")
    if not request.interlock_exchange_id or not request.intr_packet_id:
        return _result(profile, request, decision="FAIL-CLOSED", reason_code="connector.interlock_binding_missing")
    if request.intr_profile_ref != interlock.get("intr_profile_ref"):
        return _result(profile, request, decision="FAIL-CLOSED", reason_code="connector.intr_profile_mismatch")
    if request.governed_transition_profile_ref != interlock.get("governed_transition_profile_ref"):
        return _result(profile, request, decision="FAIL-CLOSED", reason_code="connector.transition_profile_mismatch")
    if request.carrier_profile_ref != interlock.get("carrier_profile_ref"):
        return _result(profile, request, decision="FAIL-CLOSED", reason_code="connector.carrier_profile_mismatch")

    operation = _operation(profile, request.operation_id)
    if operation is None:
        return _result(profile, request, decision="FAIL-CLOSED", reason_code="connector.operation_unknown")
    if operation.get("protected_consequence") is True and operation.get("bypass_disposition") != "FAIL_CLOSED":
        return _result(profile, request, decision="FAIL-CLOSED", reason_code="connector.protected_bypass_invalid")
    if operation.get("authority_ref_required") is True and not request.authority_ref:
        return _result(profile, request, decision="FAIL-CLOSED", reason_code="connector.authority_ref_missing")
    if operation.get("evidence_refs_required") is True and not request.evidence_refs:
        return _result(profile, request, decision="FAIL-CLOSED", reason_code="connector.evidence_refs_missing")
    if not request.intent_ref or not request.candidate_ref:
        return _result(profile, request, decision="FAIL-CLOSED", reason_code="connector.intent_or_candidate_missing")
    if request.three_layer_request.execution_boundary.policy_ref != operation.get("policy_ref"):
        return _result(profile, request, decision="FAIL-CLOSED", reason_code="connector.policy_ref_mismatch")
    if request.three_layer_request.target != request.system_id:
        return _result(profile, request, decision="FAIL-CLOSED", reason_code="connector.target_mismatch")
    if request.three_layer_request.action != operation.get("action_class"):
        return _result(profile, request, decision="FAIL-CLOSED", reason_code="connector.action_class_mismatch")

    evaluated = evaluate_three_layer(request.three_layer_request)
    return _result(
        profile,
        request,
        decision=evaluated.decision,
        reason_code=evaluated.reason_code,
        three_layer_result=evaluated,
    )
