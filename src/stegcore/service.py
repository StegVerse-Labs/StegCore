from __future__ import annotations

"""HTTP service for the reconciled canonical StegGate evaluation chain."""

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .steggate import (
    AdmissibilityRequest,
    ApprovalState,
    Candidate,
    CapabilityState,
    ContinuityState,
    ExecutionState,
    JudgmentState,
    SignalState,
    evaluate_admissibility,
)
from .transaction_lifecycle import TransactionLedger, run_manifested_transaction
from .version import __version__

SERVICE_VERSION = __version__
RUNTIME_CONTRACT_VERSION = "stegverse.steggate.runtime-identity.v1"
RUNTIME_IDENTITY = "stegverse:steggate:canonical:three-layer:v1"
CANONICAL_OWNER = "StegVerse-Labs/StegCore"
CANONICAL_ADMISSIBILITY_RUNTIME = "stegcore.three_layer.evaluate_three_layer"
DISPOSITIONS = ["ALLOW", "DENY", "REVIEW", "FAIL_CLOSED"]


class ManifestedValidationRequest(BaseModel):
    """Bounded production-route validation request.

    This surface preserves a transaction identity established by the upstream
    manifest/ingestion carrier while still running the canonical governed
    StegGate path. The embedded consequence is always simulated and carries no
    external side effect or execution authority.
    """

    transaction_id: str = Field(min_length=1)
    request: AdmissibilityRequest
    # Manifest-selected semantics: the already-admitted manifest names the
    # processing capability and route; StegCore never substitutes its own.
    processing_capability: str = Field(min_length=1)
    route_id: str = Field(min_length=1)
    input_data: Any = Field(default_factory=dict)
    source: str = Field(default="stegverse-sdk:production-validation", min_length=1)
    subject: str = Field(default="external-validation", min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)
    external_side_effects_enabled: bool = False


app = FastAPI(
    title="StegGate",
    version=SERVICE_VERSION,
    description=(
        "StegCore StegGate evaluation service. The service composes the existing "
        "three-layer admissibility runtime with pre-commit capability, continuity, "
        "and human-approval bindings; it does not create a parallel policy authority."
    ),
)


def runtime_identity() -> dict[str, object]:
    return {
        "service": "StegGate",
        "service_version": SERVICE_VERSION,
        "contract_version": RUNTIME_CONTRACT_VERSION,
        "runtime_identity": RUNTIME_IDENTITY,
        "canonical_owner": CANONICAL_OWNER,
        "canonical_admissibility_runtime": CANONICAL_ADMISSIBILITY_RUNTIME,
        "evaluation_endpoint": "/v1/evaluate",
        "manifested_validation_endpoint": "/v1/manifested-validation",
        "capabilities_endpoint": "/v1/capabilities",
        "dispositions": DISPOSITIONS,
        "canonical_three_layer_bound": True,
        "complete_matrix_output": True,
        "candidate_hash_binding": True,
        "permission_distinct_from_admissibility": True,
        "application_specific_policy_authority": False,
        "transport_identity_authoritative": False,
        "execution_authority": False,
        "continuity_receipt_minting_authority": False,
        "binding_fields": [
            "contract_version",
            "runtime_identity",
            "canonical_owner",
            "canonical_admissibility_runtime",
        ],
    }


@app.get("/")
def root() -> dict[str, object]:
    return {
        "service": "StegGate",
        "version": SERVICE_VERSION,
        "state": "ACTIVE",
        "health": "/health",
        "runtime_identity": "/v1/runtime-identity",
        "capabilities": "/v1/capabilities",
        "evaluate": "/v1/evaluate",
        "manifested_validation": "/v1/manifested-validation",
        "self_test": "/v1/self-test",
        "docs": "/docs",
        "canonical_admissibility_runtime": CANONICAL_ADMISSIBILITY_RUNTIME,
        "execution_authority": False,
        "continuity_receipt_minting_authority": False,
    }


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "service": "StegGate",
        "state": "healthy",
        "version": SERVICE_VERSION,
        "runtime_identity": RUNTIME_IDENTITY,
        "canonical_three_layer_bound": True,
        "admissibility_matrix": "active",
        "manifested_validation": True,
        "fail_closed": True,
    }


@app.get("/v1/runtime-identity")
def runtime_identity_endpoint() -> dict[str, object]:
    return runtime_identity()


@app.get("/v1/capabilities")
def capabilities() -> dict[str, object]:
    return {
        "service": "StegGate",
        "contract_version": RUNTIME_CONTRACT_VERSION,
        "runtime_identity": RUNTIME_IDENTITY,
        "canonical_owner": CANONICAL_OWNER,
        "canonical_admissibility_runtime": CANONICAL_ADMISSIBILITY_RUNTIME,
        "dispositions": DISPOSITIONS,
        "canonical_three_layer_bound": True,
        "complete_matrix_output": True,
        "candidate_hash_binding": True,
        "approval_candidate_hash_binding": True,
        "continuity_input_supported": True,
        "manifested_validation_supported": True,
        "external_transaction_identity_supported": True,
        "permission_distinct_from_admissibility": True,
        "application_specific_policy_authority": False,
        "transport_identity_authoritative": False,
        "arbitrary_external_execution_exposed": False,
        "continuity_receipt_minting_authority": False,
    }


@app.post("/v1/evaluate")
def evaluate(request: AdmissibilityRequest) -> dict[str, object]:
    return evaluate_admissibility(request).model_dump(mode="json")


@app.post("/v1/manifested-validation")
def manifested_validation(payload: ManifestedValidationRequest) -> dict[str, Any]:
    if payload.external_side_effects_enabled:
        raise ValueError("manifested_validation_external_side_effects_prohibited")

    ledger = TransactionLedger()

    def simulated_executor() -> dict[str, Any]:
        return {
            "status": "SIMULATED_PRODUCTION_VALIDATION_CONSEQUENCE",
            "external_side_effect": False,
            "transaction_id": payload.transaction_id,
        }

    metadata = dict(payload.metadata)
    metadata.update(
        {
            "service_execution_surface": "StegVerse-Labs/StegCore:/v1/manifested-validation",
            "external_side_effects_enabled": False,
            "production_route_validation": True,
        }
    )

    result = run_manifested_transaction(
        payload.request,
        simulated_executor,
        input_data=payload.input_data,
        source=payload.source,
        subject=payload.subject,
        ledger=ledger,
        processing_capability=payload.processing_capability,
        route_id=payload.route_id,
        transaction_id=payload.transaction_id,
        metadata=metadata,
    )
    response = result.model_dump(mode="json")
    response["service_runtime_identity"] = RUNTIME_IDENTITY
    response["service_canonical_owner"] = CANONICAL_OWNER
    response["service_external_side_effect"] = False
    response["service_execution_authority"] = False
    return response


def _base_request() -> AdmissibilityRequest:
    return AdmissibilityRequest(
        candidate=Candidate(
            actor_class="system",
            action="self_test",
            target="steggate",
            scope="self_test",
            parameters={"fixture": "allow"},
        ),
        judgment=JudgmentState(
            refusal_available=True,
            operator_recoverability="available",
            workload_state="supported",
            time_pressure="normal",
            isolation_state="supported",
            evidence_refs=["evidence:self-test"],
        ),
        signal=SignalState(
            admitted_signal_refs=["signal:self-test"],
            transformations=["self-test:v1"],
            missing_inputs=[],
            uncertainty_state="bounded",
            reference_state_hash="state:self-test",
            expected_reference_state_hash="state:self-test",
            reconstruction_available=True,
            transformation_provenance_complete=True,
        ),
        execution=ExecutionState(
            actor_authority_current=True,
            policy_current=True,
            delegation_current=True,
            evidence_current=True,
            affected_entity_conditions_represented=True,
            recoverability_profile="recoverable",
            validity_window_open=True,
            policy_ref="policy:self-test",
            delegation_ref="delegation:self-test",
            evidence_refs=["execution:self-test"],
        ),
        capability=CapabilityState(allowed=True),
        continuity=ContinuityState(
            required=True,
            previous_receipt_verified=True,
            previous_receipt_hash="receipt:self-test",
        ),
        approval=ApprovalState(required=False),
        permission_present=False,
    )


@app.get("/v1/self-test")
def self_test() -> dict[str, object]:
    allow_request = _base_request()
    allow_result = evaluate_admissibility(allow_request)

    deny_request = allow_request.model_copy(deep=True)
    deny_request.execution.policy_current = False
    deny_result = evaluate_admissibility(deny_request)

    review_request = allow_request.model_copy(deep=True)
    review_request.approval.required = True
    review_request.approval.valid = None
    review_request.approval.candidate_hash = None
    review_result = evaluate_admissibility(review_request)

    fail_closed_request = allow_request.model_copy(deep=True)
    fail_closed_request.signal.reference_state_hash = None
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
        "runtime_identity": RUNTIME_IDENTITY,
        "canonical_three_layer_bound": all(
            result.canonical_three_layer_request_hash
            for result in (allow_result, deny_result, review_result, fail_closed_result)
        ),
        "expected": expected,
        "observed": observed,
        "matrix_rows": {
            "ALLOW": len(allow_result.matrix),
            "DENY": len(deny_result.matrix),
            "REVIEW": len(review_result.matrix),
            "FAIL_CLOSED": len(fail_closed_result.matrix),
        },
    }
