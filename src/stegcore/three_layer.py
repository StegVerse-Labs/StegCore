from __future__ import annotations

"""Deterministic three-layer admissibility evaluation.

This module evaluates conditions described by the Governance repository without
verifying or minting Continuity receipts. Callers must provide already-resolved
policy, authority, evidence, and state-integrity facts.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Any, Literal, Mapping, Sequence

ExecutionDecision = Literal["ALLOW", "DENY", "FAIL-CLOSED"]


@dataclass(frozen=True)
class JudgmentConditions:
    refusal_available: bool
    operator_recoverability: Literal["available", "degraded", "unavailable", "unknown"]
    workload_state: Literal["supported", "elevated", "overloaded", "unknown"] = "unknown"
    time_pressure: Literal["normal", "elevated", "critical", "unknown"] = "unknown"
    isolation_state: Literal["supported", "isolated", "unknown"] = "unknown"
    evidence_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class SignalAdmission:
    admitted_signal_refs: tuple[str, ...]
    excluded_signal_refs: tuple[str, ...] = ()
    transformations: tuple[str, ...] = ()
    missing_inputs: tuple[str, ...] = ()
    uncertainty_state: Literal["bounded", "material", "unknown"] = "unknown"
    reference_state_hash: str = ""
    expected_reference_state_hash: str = ""
    reconstruction_available: bool = False
    transformation_provenance_complete: bool = False


@dataclass(frozen=True)
class ExecutionBoundary:
    actor_authority_current: bool
    policy_current: bool
    delegation_current: bool
    evidence_current: bool
    affected_entity_conditions_represented: bool
    recoverability_profile: Literal["recoverable", "constrained", "irreversible", "unknown"]
    validity_window_open: bool
    policy_ref: str
    delegation_ref: str
    evidence_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class ThreeLayerRequest:
    judgment_conditions: JudgmentConditions
    signal_admission: SignalAdmission
    execution_boundary: ExecutionBoundary
    action: str
    target: str
    scope: str


@dataclass(frozen=True)
class LayerFinding:
    layer: Literal["judgment_conditions", "signal_admission", "execution_boundary"]
    code: str
    detail: str


@dataclass(frozen=True)
class ThreeLayerResult:
    artifact_type: Literal["stegcore.three_layer_admissibility"]
    decision: ExecutionDecision
    reason_code: str
    findings: tuple[LayerFinding, ...]
    request_hash: str
    issued_at: str
    receipt: Mapping[str, Any] = field(default_factory=dict)


def _canonical_hash(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return sha256(encoded).hexdigest()


def _result(
    request: ThreeLayerRequest,
    decision: ExecutionDecision,
    reason_code: str,
    findings: Sequence[LayerFinding],
) -> ThreeLayerResult:
    request_data = asdict(request)
    request_hash = _canonical_hash(request_data)
    issued_at = datetime.now(timezone.utc).isoformat()
    receipt_payload = {
        "artifact_type": "stegcore.three_layer_admissibility_receipt",
        "decision": decision,
        "reason_code": reason_code,
        "request_hash": request_hash,
        "policy_ref": request.execution_boundary.policy_ref,
        "delegation_ref": request.execution_boundary.delegation_ref,
        "judgment_evidence_refs": list(request.judgment_conditions.evidence_refs),
        "admitted_signal_refs": list(request.signal_admission.admitted_signal_refs),
        "execution_evidence_refs": list(request.execution_boundary.evidence_refs),
        "reference_state_hash": request.signal_admission.reference_state_hash,
        "expected_reference_state_hash": request.signal_admission.expected_reference_state_hash,
        "findings": [asdict(finding) for finding in findings],
        "issued_at": issued_at,
        "continuity_receipt_minted": False,
    }
    receipt_payload["receipt_hash"] = _canonical_hash(receipt_payload)
    return ThreeLayerResult(
        artifact_type="stegcore.three_layer_admissibility",
        decision=decision,
        reason_code=reason_code,
        findings=tuple(findings),
        request_hash=request_hash,
        issued_at=issued_at,
        receipt=receipt_payload,
    )


def evaluate_three_layer(request: ThreeLayerRequest) -> ThreeLayerResult:
    """Evaluate judgment, state formation, and execution in restrictive order."""

    judgment = request.judgment_conditions
    if not judgment.refusal_available:
        finding = LayerFinding(
            "judgment_conditions",
            "judgment.refusal_unavailable",
            "Meaningful refusal was not practically available.",
        )
        return _result(request, "DENY", finding.code, [finding])
    if judgment.operator_recoverability in {"degraded", "unavailable", "unknown"}:
        finding = LayerFinding(
            "judgment_conditions",
            "judgment.operator_recoverability_insufficient",
            "Operator authority could not be reliably recovered under the declared conditions.",
        )
        return _result(request, "DENY", finding.code, [finding])
    if judgment.workload_state == "overloaded" or judgment.time_pressure == "critical":
        finding = LayerFinding(
            "judgment_conditions",
            "judgment.conditions_degraded",
            "Declared workload or time pressure materially degrades judgment capacity.",
        )
        return _result(request, "DENY", finding.code, [finding])

    signal = request.signal_admission
    if not signal.admitted_signal_refs:
        finding = LayerFinding(
            "signal_admission",
            "signal.none_admitted",
            "No canonical signals were admitted for state construction.",
        )
        return _result(request, "DENY", finding.code, [finding])
    if signal.missing_inputs or signal.uncertainty_state in {"material", "unknown"}:
        finding = LayerFinding(
            "signal_admission",
            "signal.inputs_incomplete",
            "Material, unknown, or explicitly missing inputs prevent reliable state formation.",
        )
        return _result(request, "DENY", finding.code, [finding])
    if not signal.reconstruction_available or not signal.transformation_provenance_complete:
        finding = LayerFinding(
            "signal_admission",
            "signal.state_unreconstructable",
            "The admitted signal set or its transformations cannot be independently reconstructed.",
        )
        return _result(request, "DENY", finding.code, [finding])
    if not signal.reference_state_hash or not signal.expected_reference_state_hash:
        finding = LayerFinding(
            "signal_admission",
            "signal.reference_state_missing",
            "Current and expected reference-state hashes are required.",
        )
        return _result(request, "FAIL-CLOSED", finding.code, [finding])
    if signal.reference_state_hash != signal.expected_reference_state_hash:
        finding = LayerFinding(
            "signal_admission",
            "signal.reference_state_discontinuous",
            "The constructed reference state differs from the authorized reference state.",
        )
        return _result(request, "FAIL-CLOSED", finding.code, [finding])

    boundary = request.execution_boundary
    if not boundary.actor_authority_current:
        finding = LayerFinding("execution_boundary", "execution.authority_stale", "Actor authority is not current.")
        return _result(request, "DENY", finding.code, [finding])
    if not boundary.policy_current or not boundary.delegation_current:
        finding = LayerFinding(
            "execution_boundary",
            "execution.policy_or_delegation_stale",
            "Policy or delegation is not current at commit time.",
        )
        return _result(request, "DENY", finding.code, [finding])
    if not boundary.evidence_current or not boundary.validity_window_open:
        finding = LayerFinding(
            "execution_boundary",
            "execution.evidence_or_window_invalid",
            "Evidence freshness or the validity window failed at commit time.",
        )
        return _result(request, "DENY", finding.code, [finding])
    if not boundary.affected_entity_conditions_represented:
        finding = LayerFinding(
            "execution_boundary",
            "execution.affected_entities_missing",
            "Affected-entity conditions are not represented in the execution basis.",
        )
        return _result(request, "DENY", finding.code, [finding])
    if boundary.recoverability_profile == "unknown":
        finding = LayerFinding(
            "execution_boundary",
            "execution.recoverability_unknown",
            "Execution recoverability is unknown.",
        )
        return _result(request, "FAIL-CLOSED", finding.code, [finding])

    return _result(request, "ALLOW", "ok", [])
