from __future__ import annotations

"""HTTP service for the canonical StegGate admissibility evaluator."""

from fastapi import FastAPI

from .steggate import (
    AdmissibilityRequest,
    ApprovalState,
    AuthorityState,
    Candidate,
    CapabilityState,
    ContinuityState,
    EvidenceState,
    PolicyState,
    evaluate_admissibility,
)


app = FastAPI(
    title="StegGate",
    version="0.1.0",
    description=(
        "Canonical StegCore admissibility gateway. Evaluates the complete material "
        "decision surface and preserves ALLOW, DENY, REVIEW, and FAIL_CLOSED."
    ),
)


@app.get("/")
def root() -> dict[str, object]:
    return {
        "service": "StegGate",
        "version": "0.1.0",
        "state": "ACTIVE",
        "health": "/health",
        "evaluate": "/v1/evaluate",
        "self_test": "/v1/self-test",
        "docs": "/docs",
        "execution_authority": False,
        "continuity_receipt_minting_authority": False,
    }


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "service": "StegGate",
        "state": "healthy",
        "version": "0.1.0",
        "admissibility_matrix": "active",
        "fail_closed": True,
    }


@app.get("/v1/capabilities")
def capabilities() -> dict[str, object]:
    return {
        "service": "StegGate",
        "dispositions": ["ALLOW", "DENY", "REVIEW", "FAIL_CLOSED"],
        "complete_matrix_output": True,
        "candidate_hash_binding": True,
        "approval_candidate_hash_binding": True,
        "continuity_input_supported": True,
        "arbitrary_external_execution_exposed": False,
        "continuity_receipt_minting_authority": False,
    }


@app.post("/v1/evaluate")
def evaluate(request: AdmissibilityRequest) -> dict[str, object]:
    return evaluate_admissibility(request).model_dump(mode="json")


def _base_request() -> AdmissibilityRequest:
    return AdmissibilityRequest(
        candidate=Candidate(
            actor_class="system",
            action="self_test",
            target="steggate",
            parameters={"fixture": "allow"},
        ),
        evidence=EvidenceState(verified=True, fresh=True),
        authority=AuthorityState(valid=True, action_allowed=True, target_allowed=True),
        policy=PolicyState(applicable=True, current=True, permits=True),
        capability=CapabilityState(allowed=True),
        continuity=ContinuityState(required=True, previous_receipt_verified=True),
        approval=ApprovalState(required=False),
    )


@app.get("/v1/self-test")
def self_test() -> dict[str, object]:
    allow_request = _base_request()
    allow_result = evaluate_admissibility(allow_request)

    deny_request = allow_request.model_copy(deep=True)
    deny_request.policy.permits = False
    deny_result = evaluate_admissibility(deny_request)

    review_request = allow_request.model_copy(deep=True)
    review_request.approval.required = True
    review_request.approval.valid = None
    review_request.approval.candidate_hash = None
    review_result = evaluate_admissibility(review_request)

    fail_closed_request = allow_request.model_copy(deep=True)
    fail_closed_request.evidence.verified = None
    fail_closed_result = evaluate_admissibility(fail_closed_request)

    observed = {
        "ALLOW": allow_result.disposition,
        "DENY": deny_result.disposition,
        "REVIEW": review_result.disposition,
        "FAIL_CLOSED": fail_closed_result.disposition,
    }
    expected = {
        "ALLOW": "ALLOW",
        "DENY": "DENY",
        "REVIEW": "REVIEW",
        "FAIL_CLOSED": "FAIL_CLOSED",
    }

    return {
        "service": "StegGate",
        "state": "PASS" if observed == expected else "FAIL",
        "expected": expected,
        "observed": observed,
        "matrix_rows": {
            "ALLOW": len(allow_result.matrix),
            "DENY": len(deny_result.matrix),
            "REVIEW": len(review_result.matrix),
            "FAIL_CLOSED": len(fail_closed_result.matrix),
        },
    }
