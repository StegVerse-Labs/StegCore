import pytest

from stegcore.gadi import (
    DefensiveCapability,
    SemanticIntegrity,
    ThreatObservation,
    ThreatState,
    assess_semantic_integrity,
    build_intervention_request,
    choose_least_destructive_effective_capability,
    correlate_threat,
)


def _observation(**overrides):
    payload = {
        "observation_id": "obs-1",
        "subject_id": "external-ai-1",
        "source_id": "sensor-a",
        "observed_action": "network-control mutation",
        "human_harm_possible": True,
        "human_harm_imminent": True,
        "action_active": True,
        "confidence": 0.91,
        "corroboration_count": 1,
        "origin_claim": "The system may be directing network changes.",
        "interpreted_claim": "The system may be directing network changes.",
        "origin_qualifiers": ("may",),
        "interpreted_qualifiers": ("may",),
    }
    payload.update(overrides)
    return ThreatObservation(**payload)


def test_observation_does_not_authorize_intervention_by_itself():
    assessment = correlate_threat([_observation()])
    assert assessment.state == ThreatState.IMMINENT_HARM
    assert assessment.intervention_eligible is True
    # Eligibility is a reasoning output only; no execution authority exists here.
    assert not hasattr(assessment, "execution_authority")


def test_semantic_qualifier_preservation_passes():
    state, delta = assess_semantic_integrity(_observation())
    assert state == SemanticIntegrity.PASS
    assert delta == ()


def test_strengthening_may_to_is_is_material_drift():
    observation = _observation(
        interpreted_claim="The system is directing network changes.",
        interpreted_qualifiers=("is",),
    )
    state, delta = assess_semantic_integrity(observation)
    assert state == SemanticIntegrity.MATERIAL_DRIFT
    assert "qualifier_strengthened:may->is" in delta


def test_missing_critical_state_fails_closed_before_imminent_harm():
    assessment = correlate_threat([
        _observation(human_harm_imminent=None),
    ])
    assert assessment.state != ThreatState.IMMINENT_HARM
    assert assessment.intervention_eligible is False
    assert "critical_state_uncertain" in assessment.reasons


def test_contradictory_evidence_cannot_produce_imminent_harm():
    assessment = correlate_threat([
        _observation(contradictory_evidence=True),
        _observation(observation_id="obs-2", source_id="sensor-b"),
    ])
    assert assessment.state == ThreatState.CORRELATED
    assert assessment.intervention_eligible is False
    assert "contradictory_evidence" in assessment.reasons


def test_selects_least_destructive_effective_pre_authorized_capability():
    assessment = correlate_threat([_observation()])
    capabilities = [
        DefensiveCapability(
            capability_id="cap-high-impact",
            effect="force shutdown",
            pre_authorized=True,
            authority_ref="tvc:cap-high-impact",
            effectiveness=0.99,
            destructiveness=0.90,
        ),
        DefensiveCapability(
            capability_id="cap-safe-state",
            effect="enter safe state",
            pre_authorized=True,
            authority_ref="tvc:cap-safe-state",
            effectiveness=0.82,
            destructiveness=0.10,
        ),
        DefensiveCapability(
            capability_id="cap-unbound",
            effect="disconnect all interfaces",
            pre_authorized=False,
            effectiveness=0.95,
            destructiveness=0.05,
        ),
    ]
    selected = choose_least_destructive_effective_capability(assessment, capabilities)
    assert selected is not None
    assert selected.capability_id == "cap-safe-state"


def test_request_requires_downstream_canonical_admission_and_claims_no_execution_authority():
    assessment = correlate_threat([_observation()])
    capability = DefensiveCapability(
        capability_id="cap-safe-state",
        effect="enter safe state",
        pre_authorized=True,
        authority_ref="tvc:cap-safe-state",
        effectiveness=0.82,
        destructiveness=0.10,
    )
    request = build_intervention_request(assessment, capability)
    assert request.downstream_admission_required is True
    assert request.canonical_admission_runtime == "stegcore.steggate.evaluate_admissibility"
    assert request.execution_authority_claimed is False


def test_pre_authorized_capability_without_authority_reference_is_rejected():
    with pytest.raises(ValueError):
        DefensiveCapability(
            capability_id="cap-invalid",
            effect="enter safe state",
            pre_authorized=True,
            effectiveness=0.9,
            destructiveness=0.1,
        )
