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

from stegcore.three_layer import (
    ExecutionBoundary,
    JudgmentConditions,
    SignalAdmission,
    ThreeLayerRequest,
    ThreeLayerResult,
    evaluate_three_layer,
)


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
class VerifiedTransportBindings:
    """Transport-owned facts supplied by verified Interlock/InTr processing.

    These values are deliberately absent from the Governance request payload so
    the target system cannot self-assert transport completion or carrier state.
    """

    interlock_exchange_id: str
    intr_packet_id: str
    intr_profile_ref: str
    governed_transition_profile_ref: str
    carrier_profile_ref: str


def parse_governance_connector_request(
    profile: Mapping[str, Any],
    payload: Mapping[str, Any],
    transport: VerifiedTransportBindings,
) -> GovernanceConnectorRequest:
    """Parse the canonical serialized request into the existing runtime request.

    Structural or binding defects raise ValueError. Callers may convert those
    parser failures to a fail-closed boundary receipt; this function never
    grants authority or executes a consequence.
    """
    if payload.get("schema_version") != "stegverse.governance-connector.request/v1":
        raise ValueError("connector.request_schema_unsupported")

    allowed_fields = {
        "schema_version", "profile_id", "operation_id", "system_id", "boundary_id",
        "authority_ref", "intent_ref", "candidate_ref", "evidence_refs", "resolved_facts",
    }
    if set(payload) != allowed_fields:
        raise ValueError("connector.request_field_set_invalid")

    if not all((
        transport.interlock_exchange_id,
        transport.intr_packet_id,
        transport.intr_profile_ref,
        transport.governed_transition_profile_ref,
        transport.carrier_profile_ref,
    )):
        raise ValueError("connector.transport_binding_missing")

    if payload.get("profile_id") != profile.get("profile_id"):
        raise ValueError("connector.profile_id_mismatch")
    system = profile.get("system")
    interlock = profile.get("interlock")
    if not isinstance(system, Mapping) or not isinstance(interlock, Mapping):
        raise ValueError("connector.profile_structure_invalid")
    if payload.get("system_id") != system.get("system_id"):
        raise ValueError("connector.system_id_mismatch")
    if payload.get("boundary_id") != system.get("boundary_id"):
        raise ValueError("connector.boundary_id_mismatch")

    operation = _operation(profile, str(payload.get("operation_id") or ""))
    if operation is None:
        raise ValueError("connector.operation_unknown")
    if transport.intr_profile_ref != interlock.get("intr_profile_ref"):
        raise ValueError("connector.intr_profile_mismatch")
    if transport.governed_transition_profile_ref != interlock.get("governed_transition_profile_ref"):
        raise ValueError("connector.transition_profile_mismatch")
    if transport.carrier_profile_ref != interlock.get("carrier_profile_ref"):
        raise ValueError("connector.carrier_profile_mismatch")

    authority_ref = payload.get("authority_ref")
    intent_ref = payload.get("intent_ref")
    candidate_ref = payload.get("candidate_ref")
    evidence_refs = payload.get("evidence_refs")
    if not isinstance(authority_ref, str) or not authority_ref:
        raise ValueError("connector.authority_ref_missing")
    if not isinstance(intent_ref, str) or not intent_ref or not isinstance(candidate_ref, str) or not candidate_ref:
        raise ValueError("connector.intent_or_candidate_missing")
    if not isinstance(evidence_refs, list) or not evidence_refs or not all(isinstance(x, str) and x for x in evidence_refs):
        raise ValueError("connector.evidence_refs_missing")

    facts = payload.get("resolved_facts")
    if not isinstance(facts, Mapping) or set(facts) != {"judgment_conditions", "signal_admission", "execution_boundary"}:
        raise ValueError("connector.resolved_facts_invalid")
    judgment = facts.get("judgment_conditions")
    signal = facts.get("signal_admission")
    boundary = facts.get("execution_boundary")
    if not all(isinstance(x, Mapping) for x in (judgment, signal, boundary)):
        raise ValueError("connector.resolved_fact_layer_invalid")

    if boundary.get("policy_ref") != operation.get("policy_ref"):
        raise ValueError("connector.policy_ref_mismatch")

    tl = ThreeLayerRequest(
        judgment_conditions=JudgmentConditions(
            refusal_available=bool(judgment.get("refusal_available")),
            operator_recoverability=judgment.get("operator_recoverability", "unknown"),
            workload_state=judgment.get("workload_state", "unknown"),
            time_pressure=judgment.get("time_pressure", "unknown"),
            isolation_state=judgment.get("isolation_state", "unknown"),
            evidence_refs=tuple(judgment.get("evidence_refs") or ()),
        ),
        signal_admission=SignalAdmission(
            admitted_signal_refs=tuple(signal.get("admitted_signal_refs") or ()),
            excluded_signal_refs=tuple(signal.get("excluded_signal_refs") or ()),
            transformations=tuple(signal.get("transformations") or ()),
            missing_inputs=tuple(signal.get("missing_inputs") or ()),
            uncertainty_state=signal.get("uncertainty_state", "unknown"),
            reference_state_hash=str(signal.get("reference_state_hash") or ""),
            expected_reference_state_hash=str(signal.get("expected_reference_state_hash") or ""),
            reconstruction_available=bool(signal.get("reconstruction_available")),
            transformation_provenance_complete=bool(signal.get("transformation_provenance_complete")),
        ),
        execution_boundary=ExecutionBoundary(
            actor_authority_current=bool(boundary.get("actor_authority_current")),
            policy_current=bool(boundary.get("policy_current")),
            delegation_current=bool(boundary.get("delegation_current")),
            evidence_current=bool(boundary.get("evidence_current")),
            affected_entity_conditions_represented=bool(boundary.get("affected_entity_conditions_represented")),
            recoverability_profile=boundary.get("recoverability_profile", "unknown"),
            validity_window_open=bool(boundary.get("validity_window_open")),
            policy_ref=str(boundary.get("policy_ref") or ""),
            delegation_ref=str(boundary.get("delegation_ref") or ""),
            evidence_refs=tuple(boundary.get("evidence_refs") or ()),
        ),
        action=str(operation.get("action_class") or ""),
        target=str(system.get("system_id") or ""),
        scope=f"operation:{payload.get('operation_id')}",
    )

    return GovernanceConnectorRequest(
        profile_id=str(payload["profile_id"]),
        operation_id=str(payload["operation_id"]),
        system_id=str(payload["system_id"]),
        boundary_id=str(payload["boundary_id"]),
        interlock_exchange_id=transport.interlock_exchange_id,
        intr_packet_id=transport.intr_packet_id,
        intr_profile_ref=transport.intr_profile_ref,
        governed_transition_profile_ref=transport.governed_transition_profile_ref,
        carrier_profile_ref=transport.carrier_profile_ref,
        authority_ref=authority_ref,
        intent_ref=intent_ref,
        candidate_ref=candidate_ref,
        evidence_refs=tuple(evidence_refs),
        three_layer_request=tl,
    )


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



def resolve_governance_connector_profile(
    registry: Mapping[str, Any],
    profile_id: str,
) -> Mapping[str, Any]:
    """Resolve one non-authorizing Governance connector profile by id."""
    if registry.get("schema_version") != "stegverse.governance-connector-registry.v1":
        raise ValueError("connector.registry_schema_unsupported")
    if registry.get("credential_authority") != "TV/TVC":
        raise ValueError("connector.registry_credential_authority_mismatch")
    if registry.get("authority_effect") != "NONE":
        raise ValueError("connector.registry_authority_effect_invalid")
    profiles = registry.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        raise ValueError("connector.registry_profiles_missing")

    seen: set[str] = set()
    resolved: Mapping[str, Any] | None = None
    for profile in profiles:
        if not isinstance(profile, Mapping):
            raise ValueError("connector.registry_profile_invalid")
        pid = profile.get("profile_id")
        if not isinstance(pid, str) or not pid:
            raise ValueError("connector.registry_profile_identity_invalid")
        if pid in seen:
            raise ValueError("connector.registry_profile_duplicate")
        seen.add(pid)
        profile_error = _profile_error(profile)
        if profile_error:
            raise ValueError(profile_error)
        if pid == profile_id:
            resolved = profile

    if resolved is None:
        raise ValueError("connector.registry_profile_unknown")
    return resolved


def parse_registered_governance_connector_request(
    registry: Mapping[str, Any],
    payload: Mapping[str, Any],
    transport: VerifiedTransportBindings,
) -> tuple[Mapping[str, Any], GovernanceConnectorRequest]:
    """Resolve payload.profile_id from the canonical registry, then parse."""
    profile_id = payload.get("profile_id")
    if not isinstance(profile_id, str) or not profile_id:
        raise ValueError("connector.profile_id_missing")
    profile = resolve_governance_connector_profile(registry, profile_id)
    return profile, parse_governance_connector_request(profile, payload, transport)


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
