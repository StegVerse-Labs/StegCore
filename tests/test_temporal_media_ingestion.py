import json
from pathlib import Path

import pytest

from stegcore.temporal_media_ingestion import ingest_temporal_media_event

FIXTURE = Path("fixtures/temporal-governed-analysis/media-reference-baseball.json")


def load_fixture():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_referenced_media_normalizes_to_tga_event_without_custody_claim():
    payload = load_fixture()
    event = ingest_temporal_media_event(
        payload["media_reference"],
        payload["observations"],
        event_id="MEDIA-EVENT-001",
        source_uncertainty=0.2,
        observation_uncertainty=0.35,
        semantic_mapping_uncertainty=0.1,
    )
    assert event["source"]["custody"] == "REFERENCED"
    assert event["source"]["integrity"]["sha256"] is None
    assert event["window"] == {
        "start_ms": 2600000,
        "end_ms": 2615000,
        "frame_anchors": [
            {"label": "contact", "offset_ms": 2603500},
            {"label": "tag-window", "offset_ms": 2610200},
        ],
    }
    assert event["representation"]["assertion"] == "INTERPRETIVE_ENCODING_NOT_GROUND_TRUTH"
    assert any("does not assert custody" in note for note in event["uncertainty"]["notes"])
    assert any("hash not supplied" in note for note in event["uncertainty"]["notes"])


def test_observation_uncertainty_and_states_are_preserved():
    payload = load_fixture()
    event = ingest_temporal_media_event(
        payload["media_reference"],
        payload["observations"],
        event_id="MEDIA-EVENT-002",
        observation_uncertainty=0.42,
    )
    assert event["uncertainty"]["observation_uncertainty"] == 0.42
    assert [item["state"] for item in event["observations"]] == ["INFERRED", "UNRESOLVED"]
    assert all(item["evidence_refs"] for item in event["observations"])


def test_invalid_or_zero_length_window_fails_closed():
    payload = load_fixture()
    payload["media_reference"]["window"]["end_ms"] = payload["media_reference"]["window"]["start_ms"]
    with pytest.raises(ValueError, match="greater than start_ms"):
        ingest_temporal_media_event(
            payload["media_reference"], payload["observations"], event_id="MEDIA-EVENT-003"
        )


def test_frame_anchor_outside_window_fails_closed():
    payload = load_fixture()
    payload["media_reference"]["window"]["frame_anchors"][0]["offset_ms"] = 9999999
    with pytest.raises(ValueError, match="inside the temporal window"):
        ingest_temporal_media_event(
            payload["media_reference"], payload["observations"], event_id="MEDIA-EVENT-004"
        )


def test_referenced_source_requires_addressable_uri():
    payload = load_fixture()
    payload["media_reference"]["uri"] = None
    with pytest.raises(ValueError, match="addressable uri"):
        ingest_temporal_media_event(
            payload["media_reference"], payload["observations"], event_id="MEDIA-EVENT-005"
        )


def test_missing_provenance_fails_closed():
    payload = load_fixture()
    payload["media_reference"]["provenance"] = []
    with pytest.raises(ValueError, match="provenance"):
        ingest_temporal_media_event(
            payload["media_reference"], payload["observations"], event_id="MEDIA-EVENT-006"
        )


def test_invalid_uncertainty_fails_closed():
    payload = load_fixture()
    with pytest.raises(ValueError, match="source_uncertainty"):
        ingest_temporal_media_event(
            payload["media_reference"],
            payload["observations"],
            event_id="MEDIA-EVENT-007",
            source_uncertainty=1.1,
        )
