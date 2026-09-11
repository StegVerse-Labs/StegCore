from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.materialize_gadi_local_admission import (
    GADILocalAdmissionError,
    GOVERNANCE_REGISTRY,
    INTR_REGISTRY,
    materialize_local_admission,
)
from stegcore.gadi import (
    Admission,
    DefensiveInterventionRequest,
    InterventionClass,
    SemanticIntegrity,
    StopCondition,
)
from stegcore.gadi_intr_admission import canonical_request_hash, expected_candidate_ref


def pending_request() -> DefensiveInterventionRequest:
    return DefensiveInterventionRequest(
        request_id="gadi-controlled-request-1",
        threat_observation_ref="observation:gadi:controlled:1",
        governed_principal_id="principal:stegverse:defender",
        threatened_subject_ref="human:controlled-test-subject",
        intervention_class=InterventionClass.REDIRECT_TO_SAFE_STATE,
        required_capability_id="gadi.sim.safe-state.redirect.v1",
        admission=Admission(state="PENDING", intr_decision_ref=None),
        least_destructive_rationale="Reversible safe-state redirect is the bounded controlled-simulation response.",
        reversibility="REVERSIBLE",
        stop_condition=StopCondition(
            condition_type="THREAT_INTERRUPTED",
            description="Stop when the bounded controlled threat is interrupted.",
        ),
        receipt_correlation_id="receipt:gadi:controlled:1",
        authority_refs=("tv://gadi/support/gadi.sim.safe-state.redirect.v1",),
        semantic_integrity=SemanticIntegrity.PASS,
    )


def governance_payload(request: DefensiveInterventionRequest, *, allow: bool = True) -> dict:
    return {
        "schema_version": "stegverse.governance-connector.request/v1",
        "profile_id": "gadi.defensive-intervention.v1",
        "operation_id": "admit-defensive-intervention",
        "system_id": "stegverse.gadi.defensive-intervention",
        "boundary_id": "interlock:gadi.defensive-intervention",
        "authority_ref": "tv://gadi/support/gadi.sim.safe-state.redirect.v1",
        "intent_ref": "intent:gadi:controlled:1",
        "candidate_ref": expected_candidate_ref(request),
        "candidate_hash": canonical_request_hash(request),
        "evidence_refs": ["evidence:gadi:controlled:1"],
        "resolved_facts": {
            "judgment_conditions": {
                "refusal_available": True,
                "operator_recoverability": "available",
                "workload_state": "supported",
                "time_pressure": "normal",
                "isolation_state": "supported",
                "evidence_refs": ["judgment:gadi:1"],
            },
            "signal_admission": {
                "admitted_signal_refs": ["signal:gadi:1"],
                "excluded_signal_refs": [],
                "transformations": ["canonicalize"],
                "missing_inputs": [] if allow else ["required-current-signal"],
                "uncertainty_state": "bounded",
                "reference_state_hash": "state:gadi:1",
                "expected_reference_state_hash": "state:gadi:1",
                "reconstruction_available": True,
                "transformation_provenance_complete": True,
            },
            "execution_boundary": {
                "actor_authority_current": True,
                "policy_current": True,
                "delegation_current": True,
                "evidence_current": True,
                "affected_entity_conditions_represented": True,
                "recoverability_profile": "recoverable",
                "validity_window_open": True,
                "policy_ref": "policy.gadi.defensive-intervention.v1",
                "delegation_ref": "delegation:gadi:controlled:1",
                "evidence_refs": ["execution:gadi:1"],
            },
        },
    }


def governance_registry() -> dict:
    return json.loads(Path(GOVERNANCE_REGISTRY).read_text(encoding="utf-8"))


def materialize(payload=None, *, allow=True):
    request = pending_request()
    return materialize_local_admission(
        pending_request_payload=request.model_dump(mode="json"),
        governance_payload=governance_payload(request, allow=allow) if payload is None else payload,
        governance_registry=governance_registry(),
        intr_registry_path=INTR_REGISTRY,
        recorded_at="2026-09-11T15:05:00Z",
    )


def test_local_intr_governance_allow_projects_admitted_without_execution_authority():
    result = materialize()
    assert result["state"] == "ADMITTED"
    assert result["projected_request"]["admission"]["state"] == "ADMITTED"
    assert result["projected_request"]["admission"]["intr_decision_ref"].startswith("intr://governance-decision/")
    assert result["governance_decision"]["decision"] == "ALLOW"
    assert result["governance_decision"]["execution_authority_granted"] is False
    assert result["projection_receipt"]["execution_authority_granted"] is False
    assert result["intr_transport"]["profile_id"] == "governance-external-action"
    assert result["intr_transport"]["registry_sha256"].startswith("sha256:")
    assert result["resolved_governance_facts_created"] is False
    assert result["threat_observation_created"] is False
    assert result["runtime_binding_created"] is False
    assert result["credential_minted"] is False
    assert result["claim_or_fence_minted"] is False
    assert result["execution_authority_granted"] is False
    assert result["network_fetch_performed"] is False
    assert result["credential_authority"] == "TV/TVC"
    assert result["authority_effect"] == "NONE_ADMISSION_MATERIALIZATION_ONLY"


def test_governance_deny_projects_denied_not_execution():
    result = materialize(allow=False)
    assert result["state"] == "DENIED"
    assert result["projected_request"]["admission"]["state"] == "DENIED"
    assert result["governance_decision"]["decision"] in {"DENY", "FAIL-CLOSED"}
    assert result["execution_authority_granted"] is False


def test_candidate_hash_must_bind_exact_pending_request():
    request = pending_request()
    payload = governance_payload(request)
    payload["candidate_hash"] = "sha256:" + "0" * 64
    with pytest.raises(GADILocalAdmissionError, match="candidate_hash mismatch"):
        materialize(payload)


def test_candidate_ref_must_bind_exact_pending_request():
    request = pending_request()
    payload = governance_payload(request)
    payload["candidate_ref"] = "gadi-request:other"
    with pytest.raises(GADILocalAdmissionError, match="candidate_ref mismatch"):
        materialize(payload)


def test_non_pending_request_is_rejected_before_transport():
    request = pending_request().model_copy(update={
        "admission": Admission(state="ADMITTED", intr_decision_ref="intr://existing"),
    })
    with pytest.raises(GADILocalAdmissionError, match="requires PENDING"):
        materialize_local_admission(
            pending_request_payload=request.model_dump(mode="json"),
            governance_payload=governance_payload(pending_request()),
            governance_registry=governance_registry(),
            intr_registry_path=INTR_REGISTRY,
            recorded_at="2026-09-11T15:05:00Z",
        )


def test_governance_payload_cannot_self_assert_transport_fields():
    request = pending_request()
    payload = governance_payload(request)
    payload["intr_packet_id"] = "forged"
    with pytest.raises(ValueError, match="request_field_set_invalid"):
        materialize_local_admission(
            pending_request_payload=request.model_dump(mode="json"),
            governance_payload=payload,
            governance_registry=governance_registry(),
            intr_registry_path=INTR_REGISTRY,
            recorded_at="2026-09-11T15:05:00Z",
        )


def test_profile_or_operation_drift_fails_closed():
    request = pending_request()
    payload = governance_payload(request)
    payload["operation_id"] = "execute"
    with pytest.raises(GADILocalAdmissionError, match="operation mismatch"):
        materialize(payload)
