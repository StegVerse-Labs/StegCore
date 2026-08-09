from datetime import datetime, timezone, timedelta

from stegcore.neural_micronode import NeuralObservation, evaluate_neural_transition

NOW = datetime(2026, 8, 9, 2, 15, tzinfo=timezone.utc)


def packet(**requirements):
    req = {
        "required_assertions": ["receptive_state"],
        "prohibited_assertions": ["prohibited_state"],
        "freshness_ms": 5000,
        "minimum_observation_quality": 0.8,
    }
    req.update(requirements)
    return {
        "profile": "steggate.neural-micronode.v0",
        "transition_id": "T-1",
        "source": {"micro_node_id": "SRC-1"},
        "destination": {"receiver_class": "neural_micro_node", "receiver_locator": "bounded-target-1", "locator_profile": "fixture.v1"},
        "payload": {"candidate_hash": "abc123", "semantic_profile": "fixture.payload.v1"},
        "requirements": req,
        "translation": {"adapter_profile": "fixture.adapter.v1", "model_or_mapping_id": "fixture-map-1", "calibration_ref": "cal-1"},
    }


def observation(**changes):
    values = dict(
        receiver_locator="bounded-target-1",
        locator_profile="fixture.v1",
        observed_at=(NOW - timedelta(milliseconds=100)).isoformat(),
        observation_ref="obs-1",
        adapter_profile="fixture.adapter.v1",
        adapter_attested=True,
        model_or_mapping_id="fixture-map-1",
        calibration_ref="cal-1",
        calibration_valid=True,
        observation_quality=0.95,
        assertions={"receptive_state": True, "prohibited_state": False},
        assertion_provenance={"receptive_state": "classifier:receptive-v1", "prohibited_state": "classifier:prohibited-v1"},
    )
    values.update(changes)
    return NeuralObservation(**values)


def test_valid_bounded_receiver_evidence_allows_boundary_only():
    result = evaluate_neural_transition(packet(), observation(), now=NOW)
    assert result.disposition == "ALLOW"
    assert result.reason == "RECEIVER_EVIDENCE_SATISFIES_TRANSITION"
    assert len(result.decision_hash) == 64


def test_stale_receiver_evidence_fails_closed():
    obs = observation(observed_at=(NOW - timedelta(seconds=10)).isoformat())
    result = evaluate_neural_transition(packet(), obs, now=NOW)
    assert (result.disposition, result.reason) == ("FAIL_CLOSED", "RECEIVER_EVIDENCE_STALE")


def test_ambiguous_destination_fails_closed():
    result = evaluate_neural_transition(packet(), observation(destination_ambiguous=True), now=NOW)
    assert (result.disposition, result.reason) == ("FAIL_CLOSED", "DESTINATION_AMBIGUOUS")


def test_decoder_mapping_mismatch_cannot_silently_supply_provenance():
    result = evaluate_neural_transition(packet(), observation(model_or_mapping_id="different-model"), now=NOW)
    assert (result.disposition, result.reason) == ("FAIL_CLOSED", "TRANSLATION_PROVENANCE_INCOMPLETE")


def test_neural_assertion_cannot_be_upgraded_to_authorization():
    p = packet(required_assertions=["authorized_by"])
    obs = observation(
        assertions={"authorized_by": True, "prohibited_state": False},
        assertion_provenance={"authorized_by": "decoder-confidence:0.999", "prohibited_state": "classifier:prohibited-v1"},
    )
    result = evaluate_neural_transition(p, obs, now=NOW)
    assert (result.disposition, result.reason) == ("FAIL_CLOSED", "AUTHORIZATION_UNESTABLISHED")


def test_required_receiver_assertion_false_denies():
    obs = observation(assertions={"receptive_state": False, "prohibited_state": False})
    result = evaluate_neural_transition(packet(), obs, now=NOW)
    assert (result.disposition, result.reason) == ("DENY", "REQUIRED_ASSERTION_FALSE")


def test_prohibited_state_fails_closed():
    obs = observation(assertions={"receptive_state": True, "prohibited_state": True})
    result = evaluate_neural_transition(packet(), obs, now=NOW)
    assert (result.disposition, result.reason) == ("FAIL_CLOSED", "PROHIBITED_STATE_PRESENT")
