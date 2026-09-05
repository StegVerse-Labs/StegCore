import json
from pathlib import Path

import pytest

from stegcore.temporal_governed_analysis import evaluate_temporal_event


FIXTURE = Path("fixtures/temporal-governed-analysis/baseball-third-base-counterfactual.json")


def load_fixture():
    with FIXTURE.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_counterfactual_projection_preserves_unresolved_state():
    payload = load_fixture()
    result = evaluate_temporal_event(
        payload["event"],
        payload["governing_context"],
        evaluation_id="EVAL-001",
        evaluation_uncertainty=0.2,
    )

    assert result["temporal_application"] == "COUNTERFACTUAL"
    assert result["conclusion"] == "UNRESOLVED"
    assert result["authority_effect"] == "NONE_ANALYSIS_ONLY"
    assert result["adjudicative_authority"] == "NONE"
    assert result["representation_assertion"] == "INTERPRETIVE_ENCODING_NOT_GROUND_TRUTH"
    assert {item["state"] for item in result["results"]} == {"SATISFIED", "UNRESOLVED"}
    assert any("outside its historical applicability" in note for note in result["variance"]["notes"])


def test_uncertainty_dimensions_remain_separate():
    payload = load_fixture()
    result = evaluate_temporal_event(
        payload["event"],
        payload["governing_context"],
        evaluation_id="EVAL-002",
        evaluation_uncertainty=0.35,
    )

    variance = result["variance"]
    assert variance["source_uncertainty"] == 0.15
    assert variance["observation_uncertainty"] == 0.25
    assert variance["semantic_mapping_uncertainty"] == 0.05
    assert variance["rule_mapping_uncertainty"] == 0.0
    assert variance["interpretation_uncertainty"] == 0.0
    assert variance["evaluation_uncertainty"] == 0.35


def test_conflicting_encodings_yield_contradictory_not_forced_answer():
    payload = load_fixture()
    payload["event"]["observations"].append(
        {
            "observation_id": "OBS-3",
            "subject": "fielder.third",
            "predicate": "fielder_possesses_ball_before_tag",
            "object": False,
            "state": "OBSERVED",
            "evidence_refs": ["video:example-baseball-1978#2600800-2601100-alt"],
        }
    )

    result = evaluate_temporal_event(
        payload["event"],
        payload["governing_context"],
        evaluation_id="EVAL-003",
    )

    assert result["conclusion"] == "CONTRADICTORY"
    p1 = next(item for item in result["results"] if item["predicate_id"] == "P1")
    assert p1["state"] == "CONTRADICTORY"


def test_missing_observation_is_unresolved_not_denied():
    payload = load_fixture()
    payload["event"]["observations"] = [
        item
        for item in payload["event"]["observations"]
        if item["predicate"] != "tag_precedes_base_contact"
    ]

    result = evaluate_temporal_event(
        payload["event"],
        payload["governing_context"],
        evaluation_id="EVAL-004",
    )

    p2 = next(item for item in result["results"] if item["predicate_id"] == "P2")
    assert p2["state"] == "UNRESOLVED"
    assert result["conclusion"] == "UNRESOLVED"


def test_event_without_non_ground_truth_assertion_is_rejected():
    payload = load_fixture()
    payload["event"]["representation"]["assertion"] = "GROUND_TRUTH"

    with pytest.raises(ValueError, match="disclaim ground-truth equivalence"):
        evaluate_temporal_event(
            payload["event"],
            payload["governing_context"],
            evaluation_id="EVAL-005",
        )


def test_invalid_evaluation_uncertainty_is_rejected():
    payload = load_fixture()

    with pytest.raises(ValueError, match="evaluation_uncertainty"):
        evaluate_temporal_event(
            payload["event"],
            payload["governing_context"],
            evaluation_id="EVAL-006",
            evaluation_uncertainty=1.5,
        )
