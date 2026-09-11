from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path

import pytest

from stegcore.gadi import (
    Admission,
    DefensiveInterventionRequest,
    InterventionClass,
    SemanticIntegrity,
    StopCondition,
)
from stegcore.gadi_intr_admission import (
    GADI_BOUNDARY_ID,
    GADI_OPERATION_ID,
    GADI_PROFILE_ID,
    GADI_SYSTEM_ID,
    GadiAdmissionProjectionError,
    canonical_request_hash,
    expected_candidate_ref,
    project_governance_decision_to_gadi_admission,
    projection_receipt,
)
from stegcore.universal_governance_connector import (
    GovernanceConnectorResult,
    resolve_governance_connector_profile,
)

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "contracts" / "universal_governance_connector_snapshot" / "universal-governance-connector-profiles.v1.json"


def request() -> DefensiveInterventionRequest:
    return DefensiveInterventionRequest(
        request_id="gadi-request-1",
        threat_observation_ref="observation:1",
        governed_principal_id="principal:stegverse:defender",
        threatened_subject_ref="human:test-subject",
        intervention_class=InterventionClass.REDIRECT_TO_SAFE_STATE,
        required_capability_id="capability:safe-state:1",
        admission=Admission(state="PENDING", intr_decision_ref=None),
        least_destructive_rationale="Reversible safe-state redirect interrupts the bounded test threat.",
        reversibility="REVERSIBLE",
        stop_condition=StopCondition(
            condition_type="THREAT_INTERRUPTED",
            description="Stop after the bounded threat is no longer active.",
        ),
        receipt_correlation_id="receipt:gadi:1",
        authority_refs=("authority:tvtvc:gadi:1",),
        semantic_integrity=SemanticIntegrity.PASS,
    )


def result(req: DefensiveInterventionRequest, *, decision: str = "ALLOW") -> GovernanceConnectorResult:
    return GovernanceConnectorResult(
        artifact_type="stegcore.universal_governance_connector_decision",
        decision=decision,
        reason_code="allow" if decision == "ALLOW" else "deny",
        profile_id=GADI_PROFILE_ID,
        profile_version="1.0.0",
        operation_id=GADI_OPERATION_ID,
        system_id=GADI_SYSTEM_ID,
        boundary_id=GADI_BOUNDARY_ID,
        interlock_exchange_id="interlock-exchange:gadi:1",
        intr_packet_id="intr-packet:gadi:1",
        intr_profile_ref="governance-external-action",
        governed_transition_profile_ref="gadi.defensive-transition.v1",
        carrier_profile_ref="heartbeat-derived-intr.v1",
        policy_ref="policy.gadi.defensive-intervention.v1",
        authority_ref="authority:tvtvc:gadi:1",
        intent_ref="intent:gadi:1",
        candidate_ref=expected_candidate_ref(req),
        candidate_hash=canonical_request_hash(req),
        evidence_refs=("evidence:gadi:1",),
        three_layer_receipt={"decision": decision},
        eligible_for_separate_consequence_authorization=decision == "ALLOW",
        execution_authority_granted=False,
        credential_authority="TV/TVC",
        continuity_receipt_minted=False,
        authority_effect="NONE",
        receipt_hash="a" * 64,
    )


def test_registry_resolves_narrow_gadi_profile_without_execution_authority():
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    profile = resolve_governance_connector_profile(registry, GADI_PROFILE_ID)
    assert profile["system"]["system_id"] == GADI_SYSTEM_ID
    assert profile["system"]["boundary_id"] == GADI_BOUNDARY_ID
    assert profile["interlock"]["intr_profile_ref"] == "governance-external-action"
    assert profile["interlock"]["governed_transition_profile_ref"] == "gadi.defensive-transition.v1"
    assert profile["runtime"]["execution_requires_separate_authority"] is True
    operation = profile["operations"][0]
    assert operation["operation_id"] == GADI_OPERATION_ID
    assert operation["protected_consequence"] is True
    assert operation["bypass_disposition"] == "FAIL_CLOSED"
    assert all(value is False for key, value in profile["authority_boundaries"].items() if key.endswith("grants_execution_authority"))
    assert profile["authority_boundaries"]["credential_authority"] == "TV/TVC"


def test_allow_projects_only_admission_not_execution_authority():
    pending = request()
    governance = result(pending, decision="ALLOW")
    projected = project_governance_decision_to_gadi_admission(pending, governance)
    assert projected.admission.state == "ADMITTED"
    assert projected.admission.intr_decision_ref == "intr://governance-decision/" + "a" * 64
    assert pending.admission.state == "PENDING"
    receipt = projection_receipt(pending, projected, governance)
    assert receipt["runtime_binding_minted"] is False
    assert receipt["execution_authority_granted"] is False
    assert receipt["credential_authority"] == "TV/TVC"
    assert receipt["authority_effect"] == "NONE_ADMISSION_PROJECTION_ONLY"


def test_deny_projects_denied_with_decision_reference():
    pending = request()
    governance = result(pending, decision="DENY")
    projected = project_governance_decision_to_gadi_admission(pending, governance)
    assert projected.admission.state == "DENIED"
    assert projected.admission.intr_decision_ref == "intr://governance-decision/" + "a" * 64


def test_candidate_hash_mismatch_fails_closed():
    pending = request()
    governance = replace(result(pending), candidate_hash="sha256:" + "0" * 64)
    with pytest.raises(GadiAdmissionProjectionError, match="candidate hash mismatch"):
        project_governance_decision_to_gadi_admission(pending, governance)


def test_execution_authority_drift_fails_closed():
    pending = request()
    governance = replace(result(pending), execution_authority_granted=True)
    with pytest.raises(GadiAdmissionProjectionError, match="execution authority"):
        project_governance_decision_to_gadi_admission(pending, governance)


def test_non_pending_request_cannot_be_reprojected():
    pending = request()
    already = pending.model_copy(update={"admission": Admission(state="ADMITTED", intr_decision_ref="intr://existing")})
    with pytest.raises(GadiAdmissionProjectionError, match="requires PENDING"):
        project_governance_decision_to_gadi_admission(already, result(pending))
