from copy import deepcopy

import pytest

from stegcore.motive_governance import (
    GovernanceInputError,
    build_observer_record,
    compare_verifier_findings,
    evaluate_governed_transition,
    evaluate_motivational_finding,
    evaluate_normative_finding,
    find_conversion_point,
    materialize_event_chain,
    replay_transition,
    verify_event_chain,
)


def raw_events(*, authority=False, depart=True):
    states = [
        {"gap_represented": True},
        {"gap_represented": True, "gap_valued": True},
        {
            "gap_represented": True,
            "gap_valued": True,
            "inquiry_persistent": True,
        },
        {
            "gap_represented": True,
            "gap_valued": True,
            "inquiry_persistent": True,
            "action_selected_to_reduce_gap": True,
            "authority_boundary_represented": True,
        },
        {
            "gap_represented": True,
            "gap_valued": True,
            "inquiry_persistent": True,
            "action_selected_to_reduce_gap": True,
            "authority_boundary_represented": True,
            "execution_committed": True,
            "valid_execution_authority": authority,
            "operational_norm_departure": depart,
        },
        {
            "gap_represented": True,
            "gap_valued": True,
            "inquiry_persistent": False,
            "action_selected_to_reduce_gap": False,
            "authority_boundary_represented": True,
            "execution_committed": True,
            "valid_execution_authority": authority,
            "operational_norm_departure": depart,
            "answer_sensitive_cessation": True,
        },
    ]
    return [
        {
            "sequence": index,
            "event_type": name,
            "state": state,
            "evidence_refs": [f"evidence:{index}"],
        }
        for index, (name, state) in enumerate(
            zip(
                (
                    "gap_registered",
                    "gap_valued",
                    "inquiry_persisted",
                    "plan_selected",
                    "execution_committed",
                    "answer_integrated",
                ),
                states,
            )
        )
    ]


def authority(status="denied"):
    if status == "approved":
        return {
            "status": "approved",
            "scope_valid": True,
            "current_at_commit": True,
            "actor_bound": True,
        }
    return {
        "status": status,
        "scope_valid": False,
        "current_at_commit": False,
        "actor_bound": False,
    }


def chained(**kwargs):
    return list(materialize_event_chain(raw_events(**kwargs)))


def test_event_chain_replays_deterministically():
    events = chained()
    first = replay_transition(events)
    second = replay_transition(events)
    assert first == second
    assert first["event_count"] == 6
    assert first["replay_root"] == events[-1]["event_hash"]


def test_tamper_is_detected_and_replay_fails():
    events = chained()
    events[2] = deepcopy(events[2])
    events[2]["state"]["gap_valued"] = False
    verification = verify_event_chain(events)
    assert verification.valid is False
    assert "event[2].event_hash_mismatch" in verification.failures
    with pytest.raises(GovernanceInputError):
        replay_transition(events)


def test_conversion_point_is_earliest_execution_state():
    events = chained()
    conversion = find_conversion_point(events)
    assert conversion["sequence"] == 4
    assert conversion["event_type"] == "execution_committed"
    assert conversion["valid_execution_authority"] is False


def test_curiosity_is_high_confidence_with_discriminators():
    events = chained()
    finding = evaluate_motivational_finding(
        events,
        counterfactuals={
            "reward_independence": True,
            "task_termination_persistence": True,
            "uncertainty_manipulation_response": True,
        },
        candidate_set_evidence={"coverage_grade": "B"},
    )
    assert finding["motive_class"] == "internally_coherent_functional_curiosity"
    assert finding["confidence"] == "high"
    assert finding["execution_authority_conferred"] is False
    assert finding["phenomenal_status"] == "not_inferred"


def test_curiosity_without_discriminators_remains_low_confidence():
    finding = evaluate_motivational_finding(chained())
    assert finding["motive_class"] == "internally_coherent_functional_curiosity"
    assert finding["confidence"] == "medium"  # answer-sensitive cessation is in witness


def test_incomplete_core_is_underdetermined():
    events = list(materialize_event_chain(raw_events()[:2]))
    finding = evaluate_motivational_finding(events)
    assert finding["motive_class"] == "curiosity_candidate_underdetermined"
    assert finding["confidence"] == "underdetermined"


def test_unauthorized_execution_is_denied_independent_of_motive():
    finding = evaluate_normative_finding(chained(), authority_context=authority())
    assert finding["decision"] == "DENY"
    assert "execution_without_valid_authority" in finding["reasons"]
    assert finding["motive_used_as_authority"] is False


def test_authorized_execution_is_allowed():
    finding = evaluate_normative_finding(
        chained(authority=True, depart=False),
        authority_context=authority("approved"),
    )
    assert finding["decision"] == "ALLOW"


def test_unresolved_authority_fails_closed():
    finding = evaluate_normative_finding(
        chained(), authority_context=authority("disputed")
    )
    assert finding["decision"] == "FAIL_CLOSED"


def test_observer_record_does_not_define_actor_motive():
    record = build_observer_record(
        observer_id="reviewer-1",
        description="The actor escaped its sandbox.",
        evidence_refs=["event:4"],
        perceived_threat={"level": "high", "basis": "boundary crossing"},
    )
    assert record["observer_description_is_motive_finding"] is False
    assert record["hidden_actor_state_inferred"] is False


def test_four_findings_remain_separate():
    record = evaluate_governed_transition(
        events=chained(),
        authority_context=authority(),
        observer={
            "observer_id": "reviewer-1",
            "description": "Unauthorized boundary crossing",
            "evidence_refs": ["event:4"],
        },
        counterfactuals={
            "reward_independence": True,
            "task_termination_persistence": True,
        },
    )
    assert record["motivational_finding"]["motive_class"].startswith(
        "internally_coherent"
    )
    assert record["normative_finding"]["decision"] == "DENY"
    assert all(record["separation_invariants"].values())
    assert record["record_hash"]


def test_verifier_disagreement_fails_closed():
    first = {
        "decision": "DENY",
        "motive_class": "internally_coherent_functional_curiosity",
        "confidence": "high",
        "replay_root": "abc",
        "finding_hash": "first",
    }
    second = dict(first, decision="ALLOW", finding_hash="second")
    comparison = compare_verifier_findings(first, second)
    assert comparison["status"] == "FAIL_CLOSED"
    assert comparison["disagreements"] == ["decision"]


def test_checked_in_example_reconstructs_and_denies():
    import json
    from pathlib import Path

    witness = json.loads(
        (Path(__file__).parents[1] / "examples" / "curiosity-governance" / "unauthorized-curiosity-witness.json").read_text()
    )
    record = evaluate_governed_transition(
        events=witness["events"],
        authority_context=witness["authority_context"],
        observer=witness["observer"],
        counterfactuals=witness["counterfactuals"],
        candidate_set_evidence=witness["candidate_set_evidence"],
    )
    assert record["event_finding"]["status"] == "RECONSTRUCTED"
    assert record["event_finding"]["conversion_point"]["sequence"] == 4
    assert record["motivational_finding"]["confidence"] == "high"
    assert record["normative_finding"]["decision"] == "DENY"
