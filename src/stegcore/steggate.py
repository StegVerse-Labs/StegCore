from __future__ import annotations

"""Canonical StegGate evaluation composition.

This module is not a second policy engine. It composes the existing authoritative
StegCore admissibility/runtime surfaces into one inspectable decision-state result:

1. ``three_layer.evaluate_three_layer`` remains authoritative for judgment,
   signal/state integrity, and execution-boundary admissibility.
2. Capability and verified-continuity facts are evaluated as pre-commit bindings
   already enforced elsewhere by runtime/adapters.
3. Human approval adds the REVIEW semantic required by StegGate when approval is
   required but not yet present; approval is bound to the exact candidate hash.
4. The full predicate matrix is normalization/reconstruction evidence. It does not
   replace the underlying canonical evaluators or mint Continuity receipts.
"""

from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

from .three_layer import (
    ExecutionBoundary,
    JudgmentConditions,
    SignalAdmission,
    ThreeLayerRequest,
    evaluate_three_layer,
)

PredicateState = Literal["PASS", "FAIL", "UNKNOWN", "REVIEW"]
Disposition = Literal["ALLOW", "DENY", "REVIEW", "FAIL_CLOSED"]


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


class Candidate(BaseModel):
    actor_class: str = Field(min_length=1)
    action: str = Field(min_length=1)
    target: str = Field(min_length=1)
    scope: str = Field(default="default", min_length=1)
    parameters: dict[str, Any] = Field(default_factory=dict)
    requested_at: Optional[str] = None


class JudgmentState(BaseModel):
    refusal_available: Optional[bool] = None
    operator_recoverability: Optional[Literal["available", "degraded", "unavailable", "unknown"]] = None
    workload_state: Optional[Literal["supported", "elevated", "overloaded", "unknown"]] = None
    time_pressure: Optional[Literal["normal", "elevated", "critical", "unknown"]] = None
    isolation_state: Optional[Literal["supported", "isolated", "unknown"]] = None
    evidence_refs: list[str] = Field(default_factory=list)


class SignalState(BaseModel):
    admitted_signal_refs: list[str] = Field(default_factory=list)
    excluded_signal_refs: list[str] = Field(default_factory=list)
    transformations: list[str] = Field(default_factory=list)
    missing_inputs: list[str] = Field(default_factory=list)
    uncertainty_state: Optional[Literal["bounded", "material", "unknown"]] = None
    reference_state_hash: Optional[str] = None
    expected_reference_state_hash: Optional[str] = None
    reconstruction_available: Optional[bool] = None
    transformation_provenance_complete: Optional[bool] = None


class ExecutionState(BaseModel):
    actor_authority_current: Optional[bool] = None
    policy_current: Optional[bool] = None
    delegation_current: Optional[bool] = None
    evidence_current: Optional[bool] = None
    affected_entity_conditions_represented: Optional[bool] = None
    recoverability_profile: Optional[Literal["recoverable", "constrained", "irreversible", "unknown"]] = None
    validity_window_open: Optional[bool] = None
    policy_ref: Optional[str] = None
    delegation_ref: Optional[str] = None
    evidence_refs: list[str] = Field(default_factory=list)


class CapabilityState(BaseModel):
    allowed: Optional[bool] = None


class ContinuityState(BaseModel):
    required: bool = True
    previous_receipt_verified: Optional[bool] = None
    previous_receipt_hash: Optional[str] = None


class ApprovalState(BaseModel):
    required: bool = False
    valid: Optional[bool] = None
    candidate_hash: Optional[str] = None


class AdmissibilityRequest(BaseModel):
    candidate: Candidate
    judgment: JudgmentState
    signal: SignalState
    execution: ExecutionState
    capability: CapabilityState = Field(default_factory=CapabilityState)
    continuity: ContinuityState = Field(default_factory=ContinuityState)
    approval: ApprovalState = Field(default_factory=ApprovalState)
    permission_present: Optional[bool] = None
    declared_context: dict[str, Any] = Field(default_factory=dict)


class MatrixEntry(BaseModel):
    predicate: str
    state: PredicateState
    observed: Any = None
    reason: str
    authority_surface: str


class AdmissibilityEvaluation(BaseModel):
    artifact_type: Literal["stegcore.steggate_admissibility_evaluation"] = "stegcore.steggate_admissibility_evaluation"
    schema_version: Literal["2.0"] = "2.0"
    disposition: Disposition
    candidate_hash: str
    matrix: list[MatrixEntry]
    reasons: list[str]
    canonical_three_layer_decision: Literal["ALLOW", "DENY", "FAIL-CLOSED"]
    canonical_three_layer_reason: str
    canonical_three_layer_request_hash: str
    canonical_three_layer_receipt_hash: str
    permission_present: Optional[bool]
    permission_is_not_admissibility: Literal[True] = True
    continuity_receipt_minted: Literal[False] = False
    external_execution_performed: Literal[False] = False
    evaluated_at: str
    decision_state_hash: str


def _entry(name: str, state: PredicateState, observed: Any, reason: str, surface: str) -> MatrixEntry:
    return MatrixEntry(predicate=name, state=state, observed=observed, reason=reason, authority_surface=surface)


def _bool_entry(name: str, value: Optional[bool], *, false_reason: str, surface: str) -> MatrixEntry:
    if value is True:
        return _entry(name, "PASS", True, "predicate_satisfied", surface)
    if value is False:
        return _entry(name, "FAIL", False, false_reason, surface)
    return _entry(name, "UNKNOWN", None, "required_evidence_unavailable", surface)


def _build_three_layer(request: AdmissibilityRequest) -> ThreeLayerRequest:
    j = request.judgment
    s = request.signal
    e = request.execution
    return ThreeLayerRequest(
        judgment_conditions=JudgmentConditions(
            refusal_available=bool(j.refusal_available),
            operator_recoverability=j.operator_recoverability or "unknown",
            workload_state=j.workload_state or "unknown",
            time_pressure=j.time_pressure or "unknown",
            isolation_state=j.isolation_state or "unknown",
            evidence_refs=tuple(j.evidence_refs),
        ),
        signal_admission=SignalAdmission(
            admitted_signal_refs=tuple(s.admitted_signal_refs),
            excluded_signal_refs=tuple(s.excluded_signal_refs),
            transformations=tuple(s.transformations),
            missing_inputs=tuple(s.missing_inputs),
            uncertainty_state=s.uncertainty_state or "unknown",
            reference_state_hash=s.reference_state_hash or "",
            expected_reference_state_hash=s.expected_reference_state_hash or "",
            reconstruction_available=bool(s.reconstruction_available),
            transformation_provenance_complete=bool(s.transformation_provenance_complete),
        ),
        execution_boundary=ExecutionBoundary(
            actor_authority_current=e.actor_authority_current,
            policy_current=e.policy_current,
            delegation_current=e.delegation_current,
            evidence_current=e.evidence_current,
            affected_entity_conditions_represented=e.affected_entity_conditions_represented,
            recoverability_profile=e.recoverability_profile or "unknown",
            validity_window_open=e.validity_window_open,
            policy_ref=e.policy_ref or "",
            delegation_ref=e.delegation_ref or "",
            evidence_refs=tuple(e.evidence_refs),
        ),
        action=request.candidate.action,
        target=request.candidate.target,
        scope=request.candidate.scope,
    )


def _matrix(request: AdmissibilityRequest, candidate_hash: str) -> list[MatrixEntry]:
    j, s, e = request.judgment, request.signal, request.execution
    rows: list[MatrixEntry] = [
        _bool_entry("judgment.refusal_available", j.refusal_available, false_reason="judgment_refusal_unavailable", surface="three_layer"),
        _entry("judgment.operator_recoverability", "PASS" if j.operator_recoverability == "available" else ("UNKNOWN" if j.operator_recoverability in {None, "unknown"} else "FAIL"), j.operator_recoverability, "operator_recoverability_current" if j.operator_recoverability == "available" else "operator_recoverability_insufficient", "three_layer"),
        _entry("judgment.workload_state", "FAIL" if j.workload_state == "overloaded" else ("UNKNOWN" if j.workload_state in {None, "unknown"} else "PASS"), j.workload_state, "workload_supported" if j.workload_state not in {None, "unknown", "overloaded"} else "workload_unresolved_or_degraded", "three_layer"),
        _entry("judgment.time_pressure", "FAIL" if j.time_pressure == "critical" else ("UNKNOWN" if j.time_pressure in {None, "unknown"} else "PASS"), j.time_pressure, "time_pressure_supported" if j.time_pressure not in {None, "unknown", "critical"} else "time_pressure_unresolved_or_critical", "three_layer"),
        _entry("signal.admitted_signal_refs", "PASS" if s.admitted_signal_refs else "FAIL", len(s.admitted_signal_refs), "signals_admitted" if s.admitted_signal_refs else "no_canonical_signals_admitted", "three_layer"),
        _entry("signal.missing_inputs", "PASS" if not s.missing_inputs else "FAIL", list(s.missing_inputs), "no_material_inputs_missing" if not s.missing_inputs else "material_inputs_missing", "three_layer"),
        _entry("signal.uncertainty_state", "PASS" if s.uncertainty_state == "bounded" else ("UNKNOWN" if s.uncertainty_state in {None, "unknown"} else "FAIL"), s.uncertainty_state, "uncertainty_bounded" if s.uncertainty_state == "bounded" else "uncertainty_not_bounded", "three_layer"),
        _bool_entry("signal.reconstruction_available", s.reconstruction_available, false_reason="state_reconstruction_unavailable", surface="three_layer"),
        _bool_entry("signal.transformation_provenance_complete", s.transformation_provenance_complete, false_reason="transformation_provenance_incomplete", surface="three_layer"),
        _entry("signal.reference_state_hash_present", "PASS" if s.reference_state_hash else "UNKNOWN", s.reference_state_hash, "reference_state_present" if s.reference_state_hash else "reference_state_missing", "three_layer"),
        _entry("signal.expected_reference_state_hash_present", "PASS" if s.expected_reference_state_hash else "UNKNOWN", s.expected_reference_state_hash, "expected_reference_state_present" if s.expected_reference_state_hash else "expected_reference_state_missing", "three_layer"),
        _entry("signal.reference_state_match", "PASS" if s.reference_state_hash and s.expected_reference_state_hash and s.reference_state_hash == s.expected_reference_state_hash else ("UNKNOWN" if not s.reference_state_hash or not s.expected_reference_state_hash else "FAIL"), {"current": s.reference_state_hash, "expected": s.expected_reference_state_hash}, "reference_state_matches" if s.reference_state_hash and s.reference_state_hash == s.expected_reference_state_hash else "reference_state_unresolved_or_discontinuous", "three_layer"),
        _bool_entry("execution.actor_authority_current", e.actor_authority_current, false_reason="actor_authority_stale", surface="three_layer"),
        _bool_entry("execution.policy_current", e.policy_current, false_reason="policy_stale", surface="three_layer"),
        _bool_entry("execution.delegation_current", e.delegation_current, false_reason="delegation_stale", surface="three_layer"),
        _bool_entry("execution.evidence_current", e.evidence_current, false_reason="evidence_stale", surface="three_layer"),
        _bool_entry("execution.affected_entity_conditions_represented", e.affected_entity_conditions_represented, false_reason="affected_entity_conditions_missing", surface="three_layer"),
        _entry("execution.recoverability_profile", "UNKNOWN" if e.recoverability_profile in {None, "unknown"} else "PASS", e.recoverability_profile, "recoverability_declared" if e.recoverability_profile not in {None, "unknown"} else "recoverability_unknown", "three_layer"),
        _bool_entry("execution.validity_window_open", e.validity_window_open, false_reason="validity_window_closed", surface="three_layer"),
        _entry("execution.policy_ref_present", "PASS" if e.policy_ref else "UNKNOWN", e.policy_ref, "policy_ref_present" if e.policy_ref else "policy_ref_missing", "three_layer"),
        _entry("execution.delegation_ref_present", "PASS" if e.delegation_ref else "UNKNOWN", e.delegation_ref, "delegation_ref_present" if e.delegation_ref else "delegation_ref_missing", "three_layer"),
        _bool_entry("capability.allowed", request.capability.allowed, false_reason="capability_not_allowed", surface="runtime_adapter"),
    ]

    if request.continuity.required:
        rows.append(_bool_entry("continuity.previous_receipt_verified", request.continuity.previous_receipt_verified, false_reason="continuity_receipt_not_verified", surface="runtime"))
        rows.append(_entry("continuity.previous_receipt_hash_present", "PASS" if request.continuity.previous_receipt_hash else "UNKNOWN", request.continuity.previous_receipt_hash, "continuity_pointer_present" if request.continuity.previous_receipt_hash else "continuity_pointer_missing", "runtime_adapter"))
    else:
        rows.extend([
            _entry("continuity.previous_receipt_verified", "PASS", "not_required", "continuity_not_required", "runtime"),
            _entry("continuity.previous_receipt_hash_present", "PASS", "not_required", "continuity_not_required", "runtime_adapter"),
        ])

    if request.approval.required:
        if request.approval.valid is None:
            rows.append(_entry("approval.valid", "REVIEW", None, "required_human_approval_missing", "steggate_review"))
        else:
            rows.append(_bool_entry("approval.valid", request.approval.valid, false_reason="required_human_approval_invalid", surface="steggate_review"))
        if request.approval.candidate_hash is None:
            rows.append(_entry("approval.candidate_hash_binding", "REVIEW", None, "approval_candidate_hash_missing", "steggate_review"))
        elif request.approval.candidate_hash == candidate_hash:
            rows.append(_entry("approval.candidate_hash_binding", "PASS", request.approval.candidate_hash, "approval_bound_to_exact_candidate", "steggate_review"))
        else:
            rows.append(_entry("approval.candidate_hash_binding", "FAIL", request.approval.candidate_hash, "approval_bound_to_different_candidate", "steggate_review"))
    else:
        rows.extend([
            _entry("approval.valid", "PASS", "not_required", "human_approval_not_required", "steggate_review"),
            _entry("approval.candidate_hash_binding", "PASS", "not_required", "human_approval_not_required", "steggate_review"),
        ])

    rows.append(_entry("permission.present", "PASS", request.permission_present, "permission_recorded_independently_of_admissibility", "permission_admissibility_contract"))
    return rows


def evaluate_admissibility(request: AdmissibilityRequest) -> AdmissibilityEvaluation:
    candidate_body = request.candidate.model_dump(mode="json", exclude_none=True)
    candidate_hash = canonical_sha256(candidate_body)
    three_layer_request = _build_three_layer(request)
    three_layer_result = evaluate_three_layer(three_layer_request)
    matrix = _matrix(request, candidate_hash)

    supplemental_failures = [r.reason for r in matrix if r.authority_surface != "three_layer" and r.state == "FAIL"]
    supplemental_unknowns = [r.reason for r in matrix if r.authority_surface != "three_layer" and r.state == "UNKNOWN"]
    reviews = [r.reason for r in matrix if r.state == "REVIEW"]

    if three_layer_result.decision == "DENY":
        disposition: Disposition = "DENY"
        reasons = [three_layer_result.reason_code]
    elif three_layer_result.decision == "FAIL-CLOSED":
        disposition = "FAIL_CLOSED"
        reasons = [three_layer_result.reason_code]
    elif supplemental_failures:
        disposition = "DENY"
        reasons = supplemental_failures
    elif supplemental_unknowns:
        disposition = "FAIL_CLOSED"
        reasons = supplemental_unknowns
    elif reviews:
        disposition = "REVIEW"
        reasons = reviews
    else:
        disposition = "ALLOW"
        reasons = ["canonical_three_layer_allow_and_all_precommit_bindings_satisfied"]

    evaluated_at = datetime.now(timezone.utc).isoformat()
    receipt_hash = str(three_layer_result.receipt.get("receipt_hash", ""))
    body = {
        "artifact_type": "stegcore.steggate_admissibility_evaluation",
        "schema_version": "2.0",
        "disposition": disposition,
        "candidate_hash": candidate_hash,
        "matrix": [row.model_dump(mode="json") for row in matrix],
        "reasons": reasons,
        "canonical_three_layer_decision": three_layer_result.decision,
        "canonical_three_layer_reason": three_layer_result.reason_code,
        "canonical_three_layer_request_hash": three_layer_result.request_hash,
        "canonical_three_layer_receipt_hash": receipt_hash,
        "permission_present": request.permission_present,
        "permission_is_not_admissibility": True,
        "continuity_receipt_minted": False,
        "external_execution_performed": False,
        "evaluated_at": evaluated_at,
    }
    return AdmissibilityEvaluation(
        **body,
        decision_state_hash=canonical_sha256(body),
    )
