from __future__ import annotations

"""Canonical StegGate admissibility-matrix evaluator.

This module evaluates the complete material decision surface for a proposed governed
transition.  It deliberately preserves ALLOW, DENY, REVIEW, and FAIL_CLOSED as
distinct outcomes and returns every predicate result that contributed to the
terminal disposition.

The evaluator does not mint Continuity receipts and does not execute an external
side effect.  Execution remains a separate authority-bearing consequence.
"""

from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


PredicateState = Literal["PASS", "FAIL", "UNKNOWN", "REVIEW"]
Disposition = Literal["ALLOW", "DENY", "REVIEW", "FAIL_CLOSED"]


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


class Candidate(BaseModel):
    actor_class: str = Field(min_length=1)
    action: str = Field(min_length=1)
    target: str = Field(min_length=1)
    parameters: dict[str, Any] = Field(default_factory=dict)
    requested_at: Optional[str] = None


class EvidenceState(BaseModel):
    verified: Optional[bool] = None
    fresh: Optional[bool] = None


class AuthorityState(BaseModel):
    valid: Optional[bool] = None
    action_allowed: Optional[bool] = None
    target_allowed: Optional[bool] = None


class PolicyState(BaseModel):
    applicable: Optional[bool] = None
    current: Optional[bool] = None
    permits: Optional[bool] = None


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
    evidence: EvidenceState
    authority: AuthorityState
    policy: PolicyState
    capability: CapabilityState
    continuity: ContinuityState = Field(default_factory=ContinuityState)
    approval: ApprovalState = Field(default_factory=ApprovalState)
    declared_context: dict[str, Any] = Field(default_factory=dict)


class MatrixEntry(BaseModel):
    predicate: str
    state: PredicateState
    observed: Any = None
    reason: str


class AdmissibilityEvaluation(BaseModel):
    artifact_type: Literal["stegcore.steggate_admissibility_evaluation"] = (
        "stegcore.steggate_admissibility_evaluation"
    )
    schema_version: Literal["1.0"] = "1.0"
    disposition: Disposition
    candidate_hash: str
    matrix: list[MatrixEntry]
    reasons: list[str]
    evaluated_at: str
    decision_state_hash: str


def _bool_entry(name: str, value: Optional[bool], *, false_reason: str) -> MatrixEntry:
    if value is True:
        return MatrixEntry(
            predicate=name,
            state="PASS",
            observed=True,
            reason="predicate_satisfied",
        )
    if value is False:
        return MatrixEntry(
            predicate=name,
            state="FAIL",
            observed=False,
            reason=false_reason,
        )
    return MatrixEntry(
        predicate=name,
        state="UNKNOWN",
        observed=None,
        reason="required_evidence_unavailable",
    )


def evaluate_admissibility(request: AdmissibilityRequest) -> AdmissibilityEvaluation:
    candidate_body = request.candidate.model_dump(mode="json", exclude_none=True)
    candidate_hash = canonical_sha256(candidate_body)

    matrix = [
        _bool_entry(
            "evidence.verified",
            request.evidence.verified,
            false_reason="evidence_not_verified",
        ),
        _bool_entry(
            "evidence.fresh",
            request.evidence.fresh,
            false_reason="evidence_not_fresh",
        ),
        _bool_entry(
            "authority.valid",
            request.authority.valid,
            false_reason="authority_not_valid",
        ),
        _bool_entry(
            "authority.action_allowed",
            request.authority.action_allowed,
            false_reason="authority_does_not_cover_action",
        ),
        _bool_entry(
            "authority.target_allowed",
            request.authority.target_allowed,
            false_reason="authority_does_not_cover_target",
        ),
        _bool_entry(
            "policy.applicable",
            request.policy.applicable,
            false_reason="policy_not_applicable",
        ),
        _bool_entry(
            "policy.current",
            request.policy.current,
            false_reason="policy_not_current",
        ),
        _bool_entry(
            "policy.permits",
            request.policy.permits,
            false_reason="policy_prohibits_candidate",
        ),
        _bool_entry(
            "capability.allowed",
            request.capability.allowed,
            false_reason="capability_not_allowed",
        ),
    ]

    if request.continuity.required:
        matrix.append(
            _bool_entry(
                "continuity.previous_receipt_verified",
                request.continuity.previous_receipt_verified,
                false_reason="continuity_receipt_not_verified",
            )
        )
    else:
        matrix.append(
            MatrixEntry(
                predicate="continuity.previous_receipt_verified",
                state="PASS",
                observed="not_required",
                reason="continuity_not_required_for_candidate",
            )
        )

    if request.approval.required:
        if request.approval.valid is False:
            matrix.append(
                MatrixEntry(
                    predicate="approval.valid",
                    state="FAIL",
                    observed=False,
                    reason="required_human_approval_invalid",
                )
            )
        elif request.approval.valid is None:
            matrix.append(
                MatrixEntry(
                    predicate="approval.valid",
                    state="REVIEW",
                    observed=None,
                    reason="required_human_approval_missing",
                )
            )
        else:
            matrix.append(
                MatrixEntry(
                    predicate="approval.valid",
                    state="PASS",
                    observed=True,
                    reason="required_human_approval_valid",
                )
            )

        if request.approval.candidate_hash is None:
            matrix.append(
                MatrixEntry(
                    predicate="approval.candidate_hash_binding",
                    state="REVIEW",
                    observed=None,
                    reason="approval_candidate_hash_missing",
                )
            )
        elif request.approval.candidate_hash != candidate_hash:
            matrix.append(
                MatrixEntry(
                    predicate="approval.candidate_hash_binding",
                    state="FAIL",
                    observed=request.approval.candidate_hash,
                    reason="approval_bound_to_different_candidate",
                )
            )
        else:
            matrix.append(
                MatrixEntry(
                    predicate="approval.candidate_hash_binding",
                    state="PASS",
                    observed=request.approval.candidate_hash,
                    reason="approval_bound_to_exact_candidate",
                )
            )
    else:
        matrix.extend(
            [
                MatrixEntry(
                    predicate="approval.valid",
                    state="PASS",
                    observed="not_required",
                    reason="human_approval_not_required",
                ),
                MatrixEntry(
                    predicate="approval.candidate_hash_binding",
                    state="PASS",
                    observed="not_required",
                    reason="human_approval_not_required",
                ),
            ]
        )

    fail_reasons = [entry.reason for entry in matrix if entry.state == "FAIL"]
    unknown_reasons = [entry.reason for entry in matrix if entry.state == "UNKNOWN"]
    review_reasons = [entry.reason for entry in matrix if entry.state == "REVIEW"]

    # Known prohibition/invalidity outranks review. Missing critical evidence is
    # epistemically distinct from a known denial and therefore fails closed.
    if fail_reasons:
        disposition: Disposition = "DENY"
        reasons = fail_reasons
    elif unknown_reasons:
        disposition = "FAIL_CLOSED"
        reasons = unknown_reasons
    elif review_reasons:
        disposition = "REVIEW"
        reasons = review_reasons
    else:
        disposition = "ALLOW"
        reasons = ["all_material_admissibility_predicates_satisfied"]

    evaluated_at = datetime.now(timezone.utc).isoformat()
    body = {
        "artifact_type": "stegcore.steggate_admissibility_evaluation",
        "schema_version": "1.0",
        "disposition": disposition,
        "candidate_hash": candidate_hash,
        "matrix": [entry.model_dump(mode="json") for entry in matrix],
        "reasons": reasons,
        "evaluated_at": evaluated_at,
    }
    decision_state_hash = canonical_sha256(body)

    return AdmissibilityEvaluation(
        disposition=disposition,
        candidate_hash=candidate_hash,
        matrix=matrix,
        reasons=reasons,
        evaluated_at=evaluated_at,
        decision_state_hash=decision_state_hash,
    )
