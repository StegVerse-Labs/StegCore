from __future__ import annotations

from copy import deepcopy
from typing import Any

REPRESENTATION_ASSERTION = "INTERPRETIVE_ENCODING_NOT_GROUND_TRUTH"
ALLOWED_CUSTODY = {"REFERENCED", "LOCAL", "LICENSED", "USER_SUPPLIED", "UNKNOWN"}
ALLOWED_SOURCE_KINDS = {"VIDEO", "AUDIO", "IMAGE_SEQUENCE", "MIXED"}
ALLOWED_INTEGRITY = {"VERIFIED", "UNVERIFIED", "PARTIAL", "UNKNOWN"}
ALLOWED_OBSERVATION_STATES = {"OBSERVED", "INFERRED", "UNRESOLVED", "CONTRADICTORY"}


def _unit_interval(name: str, value: Any) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{name} must be numeric")
    value = float(value)
    if value < 0 or value > 1:
        raise ValueError(f"{name} must be between 0 and 1")
    return value


def _normalize_window(window: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(window, dict):
        raise ValueError("window must be an object")
    start = window.get("start_ms")
    end = window.get("end_ms")
    if not isinstance(start, int) or isinstance(start, bool) or start < 0:
        raise ValueError("start_ms must be a non-negative integer")
    if not isinstance(end, int) or isinstance(end, bool) or end <= start:
        raise ValueError("end_ms must be an integer greater than start_ms")

    anchors = []
    for anchor in window.get("frame_anchors", []):
        if not isinstance(anchor, dict):
            raise ValueError("frame anchor must be an object")
        label = anchor.get("label")
        offset = anchor.get("offset_ms")
        if not isinstance(label, str) or not label:
            raise ValueError("frame anchor label is required")
        if not isinstance(offset, int) or isinstance(offset, bool) or not (start <= offset <= end):
            raise ValueError("frame anchor offset must fall inside the temporal window")
        anchors.append({"label": label, "offset_ms": offset})

    return {"start_ms": start, "end_ms": end, "frame_anchors": anchors}


def _normalize_source(source: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(source, dict):
        raise ValueError("source must be an object")
    source_id = source.get("source_id")
    source_kind = source.get("source_kind")
    custody = source.get("custody", "UNKNOWN")
    integrity = source.get("integrity") or {}

    if not isinstance(source_id, str) or not source_id:
        raise ValueError("source_id is required")
    if source_kind not in ALLOWED_SOURCE_KINDS:
        raise ValueError("unsupported source_kind")
    if custody not in ALLOWED_CUSTODY:
        raise ValueError("unsupported custody posture")
    if custody == "REFERENCED" and source.get("uri") is None:
        raise ValueError("REFERENCED custody requires an addressable uri")

    verification_state = integrity.get("verification_state", "UNKNOWN")
    if verification_state not in ALLOWED_INTEGRITY:
        raise ValueError("unsupported integrity verification_state")
    sha256 = integrity.get("sha256")
    if sha256 is not None:
        if not isinstance(sha256, str) or len(sha256) != 64 or any(c not in "0123456789abcdefABCDEF" for c in sha256):
            raise ValueError("sha256 must be a 64-character hexadecimal digest")

    return {
        "source_id": source_id,
        "source_kind": source_kind,
        "uri": source.get("uri"),
        "custody": custody,
        "integrity": {"sha256": sha256, "verification_state": verification_state},
    }


def _normalize_observations(observations: list[dict[str, Any]], source_id: str, window: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(observations, list):
        raise ValueError("observations must be a list")
    output = []
    default_ref = f"media:{source_id}#{window['start_ms']}-{window['end_ms']}"
    for index, observation in enumerate(observations):
        if not isinstance(observation, dict):
            raise ValueError("observation must be an object")
        observation_id = observation.get("observation_id") or f"OBS-{index + 1}"
        subject = observation.get("subject")
        predicate = observation.get("predicate")
        state = observation.get("state", "UNRESOLVED")
        if not isinstance(observation_id, str) or not observation_id:
            raise ValueError("observation_id must be non-empty")
        if not isinstance(subject, str) or not subject:
            raise ValueError("observation subject is required")
        if not isinstance(predicate, str) or not predicate:
            raise ValueError("observation predicate is required")
        if state not in ALLOWED_OBSERVATION_STATES:
            raise ValueError("unsupported observation state")
        refs = observation.get("evidence_refs")
        if refs is None:
            refs = [default_ref]
        if not isinstance(refs, list) or not refs or not all(isinstance(ref, str) and ref for ref in refs):
            raise ValueError("observation evidence_refs must contain at least one non-empty reference")
        output.append({
            "observation_id": observation_id,
            "subject": subject,
            "predicate": predicate,
            "object": deepcopy(observation.get("object")),
            "state": state,
            "evidence_refs": list(refs),
        })
    return output


def ingest_temporal_media_event(
    media_reference: dict[str, Any],
    observations: list[dict[str, Any]],
    *,
    event_id: str,
    event_time: str | None = None,
    encoding_version: str = "tga-media-ingestion.v1",
    source_uncertainty: float = 0.0,
    observation_uncertainty: float = 0.0,
    semantic_mapping_uncertainty: float = 0.0,
    uncertainty_notes: list[str] | None = None,
) -> dict[str, Any]:
    """Normalize a bounded media reference into a canonical TGA temporal-event record.

    This function performs no network fetch, download, media acquisition, custody change,
    rule evaluation, or adjudication. It only normalizes caller-supplied references and
    observation assertions into the canonical TGA event shape.
    """
    if not isinstance(event_id, str) or not event_id:
        raise ValueError("event_id is required")
    if not isinstance(media_reference, dict):
        raise ValueError("media_reference must be an object")

    source = _normalize_source(media_reference)
    window = _normalize_window(media_reference.get("window"))
    provenance = media_reference.get("provenance")
    if not isinstance(provenance, list) or not provenance or not all(isinstance(item, str) and item for item in provenance):
        raise ValueError("at least one provenance reference is required")

    normalized_observations = _normalize_observations(observations, source["source_id"], window)
    notes = list(uncertainty_notes or [])
    if source["integrity"]["sha256"] is None:
        notes.append("source content hash not supplied; source identity remains reference-bound only")
    if source["custody"] == "REFERENCED":
        notes.append("media is externally referenced; ingestion does not assert custody")

    return {
        "event_id": event_id,
        "event_time": event_time,
        "source": source,
        "window": window,
        "observations": normalized_observations,
        "representation": {
            "assertion": REPRESENTATION_ASSERTION,
            "encoding_version": encoding_version,
            "alternative_representation_ids": [],
        },
        "uncertainty": {
            "source_uncertainty": _unit_interval("source_uncertainty", source_uncertainty),
            "observation_uncertainty": _unit_interval("observation_uncertainty", observation_uncertainty),
            "semantic_mapping_uncertainty": _unit_interval("semantic_mapping_uncertainty", semantic_mapping_uncertainty),
            "notes": notes,
        },
        "provenance": list(provenance),
    }
