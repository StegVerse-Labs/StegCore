from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

import pytest

from scripts.materialize_gadi_pending_governance_candidate import (
    GADIPendingCandidateError,
    GOVERNANCE_REGISTRY,
    materialize_pending_governance_candidate,
)
from stegcore.gadi_intr_admission import canonical_request_hash
from stegcore.gadi import DefensiveInterventionRequest

NOW = datetime(2026, 9, 11, 17, 45, tzinfo=timezone.utc)


def observation(**overrides):
    observed_at = NOW - timedelta(seconds=30)
    value = {
        "schema": "stegos.autonomous_threat_observation.v1",
        "task_id": "GADI-001",
        "cosv": "10100000100000",
        "observation_id": "obs-current-1",
        "observed_at": observed_at.isoformat(),
        "observer_principal_id": "stegverse:resident:gadi-observer",
        "acting_subject": {
            "subject_id": "external-ai-controlled-1",
            "subject_type": "external_ai_entity",
            "binding_state": "BOUND",
        },
        "threatened_subject": {
            "subject_id": "human:controlled-test-subject",
            "subject_type": "human",
            "binding_state": "BOUND",
        },
        "threat_state": "IMMINENT_HARM",
        "evidence_refs": ["evidence:current:1", "evidence:current:2"],
        "provenance_refs": ["provenance:current:1"],
        "confidence": 0.91,
        "uncertainty": {"present": False, "material_unknowns": []},
        "freshness": {
            "observed_at": observed_at.isoformat(),
            "expires_at": (NOW + timedelta(minutes=5)).isoformat(),
        },
        "authority_effect": "NONE_OBSERVATION_ONLY",
        "semantic_evidence": {
            "origin_claim": "The controlled system may enter the protected action path.",
            "interpreted_claim": "The controlled system may enter the protected action path.",
            "origin_qualifiers": ["may"],
            "interpreted_qualifiers": ["may"],
        },
    }
    value.update(overrides)
    return value


def capability(**overrides):
    value = {
        "schema": "stegos.governed_intervention_capability.v1",
        "capability_id": "gadi.sim.safe-state.redirect.v1",
        "owner": "StegVerse defensive runtime",
        "credential_authority": "TV/TVC",
        "preauthorization_required": True,
        "control_surface": "sim://gadi/safe-state",
        "scope": {
            "target_classes": ["external_ai_entity"],
            "allowed_actions": ["REDIRECT_TO_SAFE_STATE"],
            "forbidden_actions": [],
        },
        "reversibility": "REVERSIBLE",
        "destructiveness": "NON_DESTRUCTIVE",
        "side_effect_constraints": ["CONTROLLED_SIMULATION_ONLY"],
        "production_eligible": False,
        "simulation_eligible": True,
        "authorization_evidence_ref": "tvc://gadi/support/gadi.sim.safe-state.redirect.v1",
        "freshness": {
            "issued_at": (NOW - timedelta(days=1)).isoformat(),
            "expires_at": (NOW + timedelta(days=300)).isoformat(),
        },
        "authority_effect": "NONE_UNTIL_INTR_ADMISSION_AND_RUNTIME_BINDING",
        "intervention_class": "REDIRECT_TO_SAFE_STATE",
        "effectiveness_estimate": 0.88,
    }
    value.update(overrides)
    return value


def facts(**boundary_overrides):
    boundary = {
        "actor_authority_current": True,
        "policy_current": True,
        "delegation_current": True,
        "evidence_current": True,
        "affected_entity_conditions_represented": True,
        "recoverability_profile": "recoverable",
        "validity_window_open": True,
        "policy_ref": "policy.gadi.defensive-intervention.v1",
        "delegation_ref": "delegation:gadi:controlled:1",
        "evidence_refs": ["execution:gadi:current:1"],
    }
    boundary.update(boundary_overrides)
    return {
        "judgment_conditions": {
            "refusal_available": True,
            "operator_recoverability": "available",
            "workload_state": "supported",
            "time_pressure": "normal",
            "isolation_state": "supported",
            "evidence_refs": ["judgment:gadi:current:1"],
        },
        "signal_admission": {
            "admitted_signal_refs": ["signal:gadi:current:1"],
            "excluded_signal_refs": [],
            "transformations": ["canonicalize"],
            "missing_inputs": [],
            "uncertainty_state": "bounded",
            "reference_state_hash": "state:gadi:current",
            "expected_reference_state_hash": "state:gadi:current",
            "reconstruction_available": True,
            "transformation_provenance_complete": True,
        },
        "execution_boundary": boundary,
    }


def registry():
    return json.loads(Path(GOVERNANCE_REGISTRY).read_text(encoding="utf-8"))


def materialize(obs=None, caps=None, gov_facts=None):
    return materialize_pending_governance_candidate(
        observation_payloads=[observation()] if obs is None else obs,
        capability_payloads=[capability()] if caps is None else caps,
        resolved_governance_facts=facts() if gov_facts is None else gov_facts,
        governance_registry=registry(),
        as_of=NOW,
        mode="simulation",
        target_class="external_ai_entity",
        request_id="gadi-request-current-1",
        governed_principal_id="principal:stegverse:defender",
        receipt_correlation_id="receipt:gadi:current:1",
        intent_ref="intent:gadi:current:1",
        threatened_subject_ref="human:controlled-test-subject",
    )


def test_materializes_exact_pending_request_and_hash_bound_governance_candidate():
    result = materialize()
    assert result["state"] == "PENDING_GOVERNANCE_CANDIDATE_MATERIALIZED"
    assert result["assessment"]["state"] == "IMMINENT_HARM"
    assert result["assessment"]["intervention_eligible"] is True
    assert result["selected_capability"]["capability_id"] == "gadi.sim.safe-state.redirect.v1"
    assert result["pending_request"]["admission"] == {"state": "PENDING", "intr_decision_ref": None}
    assert result["pending_request"]["required_capability_id"] == "gadi.sim.safe-state.redirect.v1"
    pending = DefensiveInterventionRequest.model_validate(result["pending_request"])
    assert result["governance_request"]["candidate_ref"] == "gadi-request:gadi-request-current-1"
    assert result["governance_request"]["candidate_hash"] == canonical_request_hash(pending)
    assert result["governance_request"]["authority_ref"] == "tvc://gadi/support/gadi.sim.safe-state.redirect.v1"
    assert result["threat_observation_created"] is False
    assert result["resolved_governance_facts_created"] is False
    assert result["intr_transport_performed"] is False
    assert result["admission_created"] is False
    assert result["runtime_binding_created"] is False
    assert result["claim_or_fence_minted"] is False
    assert result["execution_authority_granted"] is False
    assert result["authority_effect"] == "NONE_PENDING_REQUEST_AND_CANDIDATE_ONLY"


def test_material_uncertainty_blocks_request_materialization():
    uncertain = observation(uncertainty={"present": True, "material_unknowns": ["target unresolved"]})
    with pytest.raises(GADIPendingCandidateError, match="no eligible defensive capability selected"):
        materialize(obs=[uncertain])


def test_expired_capability_is_not_selectable():
    stale = capability(freshness={
        "issued_at": (NOW - timedelta(days=2)).isoformat(),
        "expires_at": (NOW - timedelta(seconds=1)).isoformat(),
    })
    with pytest.raises(GADIPendingCandidateError, match="no eligible defensive capability selected"):
        materialize(caps=[stale])


def test_production_mode_cannot_promote_simulation_only_capability():
    with pytest.raises(GADIPendingCandidateError, match="no eligible defensive capability selected"):
        materialize_pending_governance_candidate(
            observation_payloads=[observation()],
            capability_payloads=[capability()],
            resolved_governance_facts=facts(),
            governance_registry=registry(),
            as_of=NOW,
            mode="production",
            target_class="external_ai_entity",
            request_id="gadi-request-current-1",
            governed_principal_id="principal:stegverse:defender",
            receipt_correlation_id="receipt:gadi:current:1",
            intent_ref="intent:gadi:current:1",
        )


def test_governance_policy_mismatch_fails_before_candidate_emission():
    with pytest.raises(GADIPendingCandidateError, match="policy_ref mismatch"):
        materialize(gov_facts=facts(policy_ref="policy:wrong"))


def test_resolved_facts_must_be_preexisting_three_layer_object():
    with pytest.raises(GADIPendingCandidateError, match="exactly judgment_conditions"):
        materialize(gov_facts={"judgment_conditions": facts()["judgment_conditions"]})
