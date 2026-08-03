from __future__ import annotations

"""Bound proof-anchor evaluation for offline and downstream verification.

This module adds immutable policy/delegation/epoch binding around the existing
three-layer evaluator. It does not verify or mint Continuity receipts and it does
not fetch authority from external services.
"""

from dataclasses import asdict, dataclass
from typing import Any, Callable, Generic, Mapping, Optional, TypeVar

from .commit_governance import canonical_hash
from .three_layer import ThreeLayerRequest, ThreeLayerResult, evaluate_three_layer

T = TypeVar("T")


@dataclass(frozen=True)
class ProofAnchorBinding:
    policy_version: str
    policy_artifact_hash: str
    delegation_version: str
    delegation_artifact_hash: str
    decision_epoch: str
    evaluated_at: str

    def validate(self) -> None:
        required = {
            "policy_version": self.policy_version,
            "policy_artifact_hash": self.policy_artifact_hash,
            "delegation_version": self.delegation_version,
            "delegation_artifact_hash": self.delegation_artifact_hash,
            "decision_epoch": self.decision_epoch,
            "evaluated_at": self.evaluated_at,
        }
        missing = [name for name, value in required.items() if not str(value).strip()]
        if missing:
            raise ValueError(f"missing proof-anchor binding fields: {', '.join(sorted(missing))}")


@dataclass(frozen=True)
class BoundProofDecision:
    artifact_type: str
    binding: ProofAnchorBinding
    binding_hash: str
    request_hash: str
    decision: str
    reason_code: str
    findings: tuple[Mapping[str, Any], ...]
    continuity_receipt_minted: bool
    proof_hash: str
    runtime_result: ThreeLayerResult


@dataclass(frozen=True)
class BoundExecutionObservation(Generic[T]):
    artifact_type: str
    status: str
    proof: BoundProofDecision
    result: Optional[T] = None

    @property
    def executed(self) -> bool:
        return self.status == "executed"


def _stable_result_payload(result: ThreeLayerResult) -> dict[str, Any]:
    """Return the deterministic decision surface, excluding observation time."""

    return {
        "decision": result.decision,
        "reason_code": result.reason_code,
        "request_hash": result.request_hash,
        "findings": [asdict(finding) for finding in result.findings],
        "policy_ref": result.receipt.get("policy_ref"),
        "delegation_ref": result.receipt.get("delegation_ref"),
        "reference_state_hash": result.receipt.get("reference_state_hash"),
        "expected_reference_state_hash": result.receipt.get("expected_reference_state_hash"),
        "continuity_receipt_minted": result.receipt.get("continuity_receipt_minted"),
    }


def evaluate_bound_proof(
    request: ThreeLayerRequest,
    binding: ProofAnchorBinding,
) -> BoundProofDecision:
    """Evaluate a request and bind the decision to immutable governance artifacts."""

    binding.validate()
    result = evaluate_three_layer(request)
    binding_payload = asdict(binding)
    binding_hash = canonical_hash(binding_payload)
    stable_result = _stable_result_payload(result)
    proof_payload = {
        "artifact_type": "stegcore.bound_proof_decision.v1",
        "binding": binding_payload,
        "binding_hash": binding_hash,
        "request": asdict(request),
        "result": stable_result,
    }
    proof_hash = canonical_hash(proof_payload)
    return BoundProofDecision(
        artifact_type="stegcore.bound_proof_decision.v1",
        binding=binding,
        binding_hash=binding_hash,
        request_hash=result.request_hash,
        decision=result.decision,
        reason_code=result.reason_code,
        findings=tuple(asdict(finding) for finding in result.findings),
        continuity_receipt_minted=result.receipt.get("continuity_receipt_minted") is True,
        proof_hash=proof_hash,
        runtime_result=result,
    )


def verify_bound_proof(
    request: ThreeLayerRequest,
    binding: ProofAnchorBinding,
    expected: BoundProofDecision,
) -> bool:
    """Re-evaluate locally and verify the deterministic proof surface."""

    actual = evaluate_bound_proof(request, binding)
    return (
        actual.artifact_type == expected.artifact_type
        and actual.binding_hash == expected.binding_hash
        and actual.request_hash == expected.request_hash
        and actual.decision == expected.decision
        and actual.reason_code == expected.reason_code
        and actual.findings == expected.findings
        and actual.continuity_receipt_minted is False
        and actual.proof_hash == expected.proof_hash
    )


def execute_bound_proof(
    request: ThreeLayerRequest,
    binding: ProofAnchorBinding,
    executor: Callable[[], T],
) -> BoundExecutionObservation[T]:
    """Execute only after a bound three-layer ALLOW decision.

    A downstream callback cannot negotiate with, replace, or override the
    decision. For DENY or FAIL-CLOSED, the callback is not invoked.
    """

    proof = evaluate_bound_proof(request, binding)
    if proof.decision != "ALLOW":
        return BoundExecutionObservation(
            artifact_type="stegcore.bound_execution_observation.v1",
            status="refused",
            proof=proof,
        )

    result = executor()
    return BoundExecutionObservation(
        artifact_type="stegcore.bound_execution_observation.v1",
        status="executed",
        proof=proof,
        result=result,
    )
