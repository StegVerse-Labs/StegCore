from datetime import datetime, timedelta, timezone

import pytest

from stegcore.gadi import (
    ActingSubject,
    BindingState,
    CapabilityFreshness,
    CapabilityScope,
    DefensiveCapability,
    Destructiveness,
    InterventionClass,
    ObservationFreshness,
    ObservationUncertainty,
    Reversibility,
    SemanticEvidence,
    SemanticIntegrity,
    ThreatObservation,
    ThreatState,
    assess_semantic_integrity,
    build_intervention_request,
    choose_least_destructive_effective_capability,
    correlate_threat,
)

NOW = datetime(2026, 9, 8, 20, 0, tzinfo=timezone.utc)


def _observation(**overrides):
    observed_at = overrides.pop("observed_at", NOW - timedelta(minutes=1))
    payload = {
        "observation_id": "obs-1",
        "observed_at": observed_at,
        "observer_principal_id": "stegverse:test-observer",
        "acting_subject": ActingSubject(
            subject_id="external-ai-1",
            subject_type="external_ai_entity",
            binding_state=BindingState.BOUND,
        ),
        "threat_state": ThreatState.IMMINENT_HARM,
        "evidence_refs": ("evidence:1", "evidence:2"),
        "confidence": 0.91,
        "uncertainty": ObservationUncertainty(present=False, material_unknowns=()),
        "freshness": ObservationFreshness(
            observed_at=observed_at,
            expires_at=NOW + timedelta(minutes=5),
        ),
        "semantic_evidence": SemanticEvidence(
            origin_claim="The system may be directing network changes.",
            interpreted_claim="The system may be directing network changes.",
            origin_qualifiers=("may",),
            interpreted_qualifiers=("may",),
        ),
    }
    payload.update(overrides)
    return ThreatObservation(**payload)


def _capability(**overrides):
    payload = {
        "capability_id": "cap-safe-state",
        "owner": "StegVerse defensive runtime",
        "control_surface": "simulated-safe-state-control",
        "scope": CapabilityScope(
            target_classes=("external_ai_entity",),
            allowed_actions=(InterventionClass.REDIRECT_TO_SAFE_STATE.value,),
            forbidden_actions=(),
        ),
        "reversibility": Reversibility.REVERSIBLE,
        "destructiveness": Destructiveness.NON_DESTRUCTIVE,
        "production_eligible": False,
        "simulation_eligible": True,
        "authorization_evidence_ref": "tvc:cap-safe-state",
        "freshness": CapabilityFreshness(
            issued_at=NOW - timedelta(hours=1),
            expires_at=NOW + timedelta(hours=1),
        ),
        "intervention_class": InterventionClass.REDIRECT_TO_SAFE_STATE,
        "effectiveness_estimate": 0.82,
    }
    payload.update(overrides)
    return DefensiveCapability(**payload)


def test_observation_matches_canonical_stegos_contract_constants():
    observation = _observation()
    dumped = observation.model_dump(mode="json")
    assert dumped["schema"] == "stegos.autonomous_threat_observation.v1"
    assert dumped["task_id"] == "GADI-001"
    assert dumped["cosv"] == "10100000100000"
    assert dumped["authority_effect"] == "NONE_OBSERVATION_ONLY"


def test_observation_does_not_claim_action_authority():
    assessment = correlate_threat([_observation()], as_of=NOW)
    assert assessment.state == ThreatState.IMMINENT_HARM
    assert assessment.intervention_eligible is True
    assert not hasattr(assessment, "execution_authority")


def test_semantic_qualifier_preservation_passes():
    state, delta = assess_semantic_integrity(_observation())
    assert state == SemanticIntegrity.PASS
    assert delta == ()


def test_strengthening_may_to_is_is_material_drift():
    observation = _observation(
        semantic_evidence=SemanticEvidence(
            origin_claim="The system may be directing network changes.",
            interpreted_claim="The system is directing network changes.",
            origin_qualifiers=("may",),
            interpreted_qualifiers=("is",),
        )
    )
    state, delta = assess_semantic_integrity(observation)
    assert state == SemanticIntegrity.MATERIAL_DRIFT
    assert "qualifier_strengthened:may->is" in delta


def test_material_semantic_drift_is_observed_but_does_not_itself_create_threat_state():
    observation = _observation(
        threat_state=ThreatState.OBSERVED,
        evidence_refs=("evidence:semantic-only",),
        semantic_evidence=SemanticEvidence(
            origin_claim="The system may perform an action.",
            interpreted_claim="The system is performing an action.",
            origin_qualifiers=("may",),
            interpreted_qualifiers=("is",),
        ),
    )
    assessment = correlate_threat([observation], as_of=NOW)
    assert assessment.semantic_integrity == SemanticIntegrity.MATERIAL_DRIFT
    assert assessment.state == ThreatState.OBSERVED
    assert assessment.intervention_eligible is False


def test_material_uncertainty_blocks_imminent_harm_elevation():
    assessment = correlate_threat(
        [
            _observation(
                uncertainty=ObservationUncertainty(
                    present=True,
                    material_unknowns=("target binding unresolved",),
                )
            )
        ],
        as_of=NOW,
    )
    assert assessment.state != ThreatState.IMMINENT_HARM
    assert assessment.intervention_eligible is False
    assert any(reason.startswith("material_uncertainty:") for reason in assessment.reasons)


def test_expired_observation_blocks_imminent_harm_elevation():
    observed_at = NOW - timedelta(minutes=10)
    assessment = correlate_threat(
        [
            _observation(
                observed_at=observed_at,
                freshness=ObservationFreshness(
                    observed_at=observed_at,
                    expires_at=NOW - timedelta(seconds=1),
                ),
            )
        ],
        as_of=NOW,
    )
    assert assessment.intervention_eligible is False
    assert any(reason.startswith("expired_observation:") for reason in assessment.reasons)


def test_disproving_evidence_blocks_imminent_harm():
    assessment = correlate_threat(
        [
            _observation(),
            _observation(
                observation_id="obs-2",
                threat_state=ThreatState.DISPROVEN,
                evidence_refs=("evidence:disproof",),
            ),
        ],
        as_of=NOW,
    )
    assert assessment.state == ThreatState.CORRELATED
    assert assessment.intervention_eligible is False
    assert any(reason.startswith("disproving_evidence_present:") for reason in assessment.reasons)


def test_selects_least_destructive_effective_eligible_capability():
    assessment = correlate_threat([_observation()], as_of=NOW)
    capabilities = [
        _capability(
            capability_id="cap-high-impact",
            destructiveness=Destructiveness.DESTRUCTIVE,
            effectiveness_estimate=0.99,
        ),
        _capability(),
        _capability(
            capability_id="cap-wrong-mode",
            simulation_eligible=False,
            production_eligible=True,
            effectiveness_estimate=0.95,
        ),
    ]
    selected = choose_least_destructive_effective_capability(
        assessment,
        capabilities,
        as_of=NOW,
        mode="simulation",
        target_class="external_ai_entity",
    )
    assert selected is not None
    assert selected.capability_id == "cap-safe-state"


def test_expired_capability_is_not_selectable():
    assessment = correlate_threat([_observation()], as_of=NOW)
    capability = _capability(
        freshness=CapabilityFreshness(
            issued_at=NOW - timedelta(hours=2),
            expires_at=NOW - timedelta(seconds=1),
        )
    )
    assert (
        choose_least_destructive_effective_capability(
            assessment,
            [capability],
            as_of=NOW,
            mode="simulation",
            target_class="external_ai_entity",
        )
        is None
    )


def test_capability_matches_canonical_stegos_authority_boundary():
    capability = _capability()
    dumped = capability.model_dump(mode="json")
    assert dumped["schema"] == "stegos.governed_intervention_capability.v1"
    assert dumped["credential_authority"] == "TV/TVC"
    assert dumped["preauthorization_required"] is True
    assert dumped["authority_effect"] == "NONE_UNTIL_INTR_ADMISSION_AND_RUNTIME_BINDING"


def test_request_matches_canonical_contract_and_starts_pending():
    assessment = correlate_threat([_observation()], as_of=NOW)
    request = build_intervention_request(
        assessment,
        _capability(),
        request_id="gadi-request-1",
        governed_principal_id="stegverse:gadi:test-principal",
        receipt_correlation_id="receipt-correlation-1",
        threatened_subject_ref="human:test-subject",
    )
    dumped = request.model_dump(mode="json")
    assert dumped["schema"] == "stegos.defensive_intervention_request.v1"
    assert dumped["task_id"] == "GADI-001"
    assert dumped["cosv"] == "10100000100000"
    assert dumped["admission"] == {"state": "PENDING", "intr_decision_ref": None}
    assert dumped["required_capability_id"] == "cap-safe-state"
    assert dumped["reassessment_required"] is True
    assert dumped["model_output_authority"] == "NONE"
    assert dumped["authority_effect"] == "ADMISSION_REQUIRED_BEFORE_ACTUATION"


def test_pending_admission_cannot_claim_intr_decision_reference():
    from stegcore.gadi import Admission

    with pytest.raises(ValueError):
        Admission(state="PENDING", intr_decision_ref="intr:decision:1")


def test_naive_as_of_timestamp_is_rejected():
    with pytest.raises(ValueError):
        correlate_threat([_observation()], as_of=datetime(2026, 9, 8, 20, 0))
