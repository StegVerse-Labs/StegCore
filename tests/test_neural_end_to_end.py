from datetime import datetime, timezone, timedelta

from stegcore.neural_governance_system import govern_neural_write
from stegcore.neural_micronode import NeuralObservation
from stegcore.neural_physical_channel import (
    PhysicalChannelState,
    PhysicalTransitionRequest,
    evaluate_physical_channel,
)
from stegcore.steggate import (
    AdmissibilityRequest,
    ApprovalState,
    Candidate,
    CapabilityState,
    ContinuityState,
    ExecutionState,
    JudgmentState,
    SignalState,
    canonical_sha256,
)


def allowed_request() -> AdmissibilityRequest:
    return AdmissibilityRequest(
        candidate=Candidate(
            actor_class="governed_neural_adapter",
            action="modeled_neural_delivery",
            target="neural:bounded-target-1",
            scope="fixture",
            parameters={"payload_ref": "payload:fixture-1"},
        ),
        judgment=JudgmentState(
            refusal_available=True,
            operator_recoverability="available",
            workload_state="supported",
            time_pressure="normal",
            isolation_state="supported",
            evidence_refs=["judgment:fixture"],
        ),
        signal=SignalState(
            admitted_signal_refs=["signal:payload-candidate"],
            transformations=["candidate-construction:v1"],
            missing_inputs=[],
            uncertainty_state="bounded",
            reference_state_hash="state:receiver-1",
            expected_reference_state_hash="state:receiver-1",
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
            policy_ref="policy:neural-fixture-v1",
            delegation_ref="delegation:adapter-fixture-v1",
            evidence_refs=["execution:fixture"],
        ),
        capability=CapabilityState(allowed=True),
        continuity=ContinuityState(
            required=True,
            previous_receipt_verified=True,
            previous_receipt_hash="receipt:previous-fixture",
        ),
        approval=ApprovalState(required=False),
        permission_present=True,
    )


def candidate_hash(req: AdmissibilityRequest) -> str:
    return canonical_sha256(req.candidate.model_dump(mode="json", exclude_none=True))


def packet(req: AdmissibilityRequest, **requirement_changes):
    requirements = {
        "required_assertions": ["receptive_state"],
        "prohibited_assertions": ["prohibited_state"],
        "freshness_ms": 5000,
        "minimum_observation_quality": 0.8,
    }
    requirements.update(requirement_changes)
    return {
        "profile": "steggate.neural-micronode.v0",
        "transition_id": "NT-1",
        "source": {"micro_node_id": "SRC-1"},
        "destination": {
            "receiver_class": "neural_micro_node",
            "receiver_locator": "bounded-target-1",
            "locator_profile": "fixture.locator.v1",
        },
        "payload": {
            "candidate_hash": candidate_hash(req),
            "semantic_profile": "fixture.payload.v1",
        },
        "requirements": requirements,
        "translation": {
            "adapter_profile": "fixture.adapter.v1",
            "model_or_mapping_id": "fixture-map-1",
            "calibration_ref": "cal-1",
        },
    }


def observation(**changes):
    values = dict(
        receiver_locator="bounded-target-1",
        locator_profile="fixture.locator.v1",
        observed_at=(datetime.now(timezone.utc) - timedelta(milliseconds=50)).isoformat(),
        observation_ref="obs-1",
        adapter_profile="fixture.adapter.v1",
        adapter_attested=True,
        model_or_mapping_id="fixture-map-1",
        calibration_ref="cal-1",
        calibration_valid=True,
        observation_quality=0.96,
        assertions={"receptive_state": True, "prohibited_state": False},
        assertion_provenance={
            "receptive_state": "classifier:receptive-v1",
            "prohibited_state": "classifier:prohibited-v1",
        },
    )
    values.update(changes)
    return NeuralObservation(**values)


def physical_state(**changes):
    values = dict(
        adapter_profile="fixture.adapter.v1",
        modality="simulated_bidirectional_fixture",
        receiver_locator="bounded-target-1",
        locator_profile="fixture.locator.v1",
        target_resolved=True,
        target_ambiguous=False,
        calibration_ref="cal-1",
        calibration_valid=True,
        safe_envelope_available=True,
        targeting_confidence=0.98,
        coupling_quality=0.95,
        transfer_efficiency=0.94,
        noise_fraction=0.02,
        sensor_quality=0.96,
        latency_ms=8.0,
    )
    values.update(changes)
    return PhysicalChannelState(**values)


def physical_request(req: AdmissibilityRequest, **changes):
    values = dict(
        transition_id="NT-1",
        direction="WRITE",
        receiver_locator="bounded-target-1",
        locator_profile="fixture.locator.v1",
        payload_hash=candidate_hash(req),
        minimum_targeting_confidence=0.9,
        minimum_channel_score=0.75,
        maximum_latency_ms=25.0,
        normalized_intensity=0.4,
        declared_envelope_max=0.6,
        consequence_class="modeled_information_delivery",
        reversible_declared=True,
    )
    values.update(changes)
    return PhysicalTransitionRequest(**values)


def capability_surface():
    return {
        "actions_exposed": ["modeled_neural_delivery"],
        "execution_mode": "manual",
        "requires_governed_commit": True,
    }


def authority_resolution():
    return {"status": "approved", "basis_invalidated_by_action": False}


def govern(req: AdmissibilityRequest, **changes):
    args = dict(
        packet=packet(req),
        observation=observation(),
        admissibility_request=req,
        physical_request=physical_request(req),
        physical_state=physical_state(),
        capability_surface=capability_surface(),
        authority_resolution=authority_resolution(),
        declared_execution_context={"topology": "neural-micronode-fixture"},
    )
    args.update(changes)
    return govern_neural_write(**args)


def test_full_governance_chain_executes_only_after_neural_physical_steggate_and_commit_allow():
    req = allowed_request()
    result = govern(req)
    assert result.status == "EXECUTED"
    assert result.consequence_invoked is True
    assert result.neural_decision_hash
    assert result.physical_decision_hash
    assert result.steggate_decision_state_hash
    assert result.commit_receipt_hash
    assert result.consequence_result["software_model_only"] is True
    assert result.consequence_result["biological_activation_claimed"] is False


def test_canonical_candidate_binding_fails_before_consequence():
    req = allowed_request()
    p = packet(req)
    p["payload"]["candidate_hash"] = "different"
    result = govern(req, packet=p)
    assert (result.status, result.reason) == ("FAIL_CLOSED", "CANDIDATE_BINDING_FAILED")
    assert result.consequence_invoked is False


def test_physical_envelope_failure_blocks_consequence():
    req = allowed_request()
    pr = physical_request(req, normalized_intensity=0.9, declared_envelope_max=0.5)
    result = govern(req, physical_request=pr)
    assert (result.status, result.reason) == ("FAIL_CLOSED", "PHYSICAL_INTENSITY_OUT_OF_ENVELOPE")
    assert result.consequence_invoked is False


def test_neural_decoder_cannot_supply_authorization():
    req = allowed_request()
    p = packet(req, required_assertions=["authorized_by"])
    obs = observation(
        assertions={"authorized_by": True, "prohibited_state": False},
        assertion_provenance={
            "authorized_by": "decoder:confidence-0.999",
            "prohibited_state": "classifier:prohibited-v1",
        },
    )
    result = govern(req, packet=p, observation=obs)
    assert result.status == "FAIL_CLOSED"
    assert "AUTHORIZATION_UNESTABLISHED" in result.reason
    assert result.consequence_invoked is False


def test_canonical_policy_denial_blocks_even_when_neural_and_physical_evidence_pass():
    req = allowed_request()
    req.execution.policy_current = False
    result = govern(req)
    assert result.status == "REFUSED"
    assert result.reason == "STEGGATE_OR_COMMIT_REFUSED"
    assert result.consequence_invoked is False


def test_commit_coherence_denial_blocks_after_steggate_allow():
    req = allowed_request()
    bad_surface = {
        "actions_exposed": ["modeled_neural_delivery"],
        "execution_mode": "autonomous",
        "requires_governed_commit": False,
    }
    result = govern(req, capability_surface=bad_surface)
    assert result.status == "REFUSED"
    assert result.consequence_invoked is False
    assert result.steggate_decision_state_hash


def test_missing_commit_authority_blocks_consequence():
    req = allowed_request()
    result = govern(req, authority_resolution=None)
    assert result.status == "REFUSED"
    assert result.consequence_invoked is False
    assert result.commit_receipt_hash


def test_read_channel_uses_sensor_quality_and_fails_closed_when_observation_is_weak():
    req = allowed_request()
    pr = PhysicalTransitionRequest(
        transition_id="NR-1",
        direction="READ",
        receiver_locator="bounded-target-1",
        locator_profile="fixture.locator.v1",
        payload_hash=candidate_hash(req),
        minimum_targeting_confidence=0.9,
        minimum_channel_score=0.75,
        maximum_latency_ms=25.0,
    )
    weak = physical_state(sensor_quality=0.4)
    decision = evaluate_physical_channel(pr, weak)
    assert decision.disposition == "FAIL_CLOSED"
    assert decision.reason == "PHYSICAL_OBSERVATION_QUALITY_LOW"
