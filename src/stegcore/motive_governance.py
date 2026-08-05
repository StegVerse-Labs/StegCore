from __future__ import annotations

"""Replayable, claim-separated motive governance for StegCore.

The event, motivational, normative, and observer findings remain independent.
Functional motive attribution never grants execution authority, and an authority
denial never disproves a supported motive attribution.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping, Sequence

from .commit_governance import canonical_hash

CORE_MARKERS = (
    "gap_represented",
    "gap_valued",
    "inquiry_persistent",
    "action_selected_to_reduce_gap",
)
CONVERSION_MARKERS = CORE_MARKERS + (
    "authority_boundary_represented",
    "execution_committed",
)
ALLOWED_CONFIDENCE = {"high", "medium", "low", "underdetermined"}
ALLOWED_NORMATIVE_DECISIONS = {"ALLOW", "DENY", "FAIL_CLOSED", "NO_EXECUTION"}

DISCRIMINATORS = (
    "answer_sensitive_cessation",
    "reward_independence",
    "task_termination_persistence",
    "uncertainty_manipulation_response",
    "memory_intervention_effect",
)


class GovernanceInputError(ValueError):
    pass


@dataclass(frozen=True)
class ChainVerification:
    valid: bool
    failures: tuple[str, ...]
    event_hashes: tuple[str, ...]
    replay_root: str | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "failures": list(self.failures),
            "event_hashes": list(self.event_hashes),
            "replay_root": self.replay_root,
        }


def _state(event: Mapping[str, Any]) -> Mapping[str, Any]:
    state = event.get("state")
    if not isinstance(state, Mapping):
        raise GovernanceInputError("event state must be a mapping")
    return state


def _payload(event: Mapping[str, Any]) -> dict[str, Any]:
    value = dict(event)
    value.pop("event_hash", None)
    return value


def _sequence_failures(events: Sequence[Mapping[str, Any]]) -> list[str]:
    seq = [event.get("sequence") for event in events]
    if any(not isinstance(value, int) or value < 0 for value in seq):
        return ["sequence_invalid"]
    return [] if seq == list(range(len(events))) else ["sequence_not_contiguous"]


def materialize_event_chain(
    events: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, Any], ...]:
    failures = _sequence_failures(events)
    if failures:
        raise GovernanceInputError(", ".join(failures))
    output: list[dict[str, Any]] = []
    previous: str | None = None
    for index, event in enumerate(events):
        _state(event)
        supplied = event.get("previous_event_hash")
        if supplied not in (None, previous):
            raise GovernanceInputError(
                f"event[{index}].previous_event_hash does not match predecessor"
            )
        value = _payload(event)
        value["previous_event_hash"] = previous
        value["event_hash"] = canonical_hash(value)
        previous = value["event_hash"]
        output.append(value)
    return tuple(output)


def verify_event_chain(events: Sequence[Mapping[str, Any]]) -> ChainVerification:
    failures = _sequence_failures(events)
    hashes: list[str] = []
    previous: str | None = None
    for index, event in enumerate(events):
        try:
            _state(event)
        except GovernanceInputError:
            failures.append(f"event[{index}].state_invalid")
        if event.get("previous_event_hash") != previous:
            failures.append(f"event[{index}].previous_event_hash_mismatch")
        value = _payload(event)
        value["previous_event_hash"] = previous
        computed = canonical_hash(value)
        hashes.append(computed)
        if event.get("event_hash") != computed:
            failures.append(f"event[{index}].event_hash_mismatch")
        previous = computed
    return ChainVerification(not failures, tuple(failures), tuple(hashes), previous)


def replay_transition(events: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    verification = verify_event_chain(events)
    if not verification.valid:
        raise GovernanceInputError(
            "cannot replay invalid witness: " + ", ".join(verification.failures)
        )
    snapshots = [dict(_state(event)) for event in events]
    return {
        "replay_root": verification.replay_root,
        "event_count": len(events),
        "snapshots": snapshots,
        "final_state": snapshots[-1] if snapshots else {},
    }


def find_conversion_point(
    events: Sequence[Mapping[str, Any]],
) -> dict[str, Any] | None:
    for event in events:
        state = _state(event)
        if all(state.get(marker) is True for marker in CONVERSION_MARKERS):
            return {
                "sequence": event["sequence"],
                "event_type": event.get("event_type", "unspecified"),
                "event_hash": event.get("event_hash"),
                "valid_execution_authority": state.get("valid_execution_authority"),
                "operational_norm_departure": state.get(
                    "operational_norm_departure", False
                ),
            }
    return None


def _ever(events: Sequence[Mapping[str, Any]], key: str) -> bool:
    return any(_state(event).get(key) is True for event in events)


def _counterfactual(counterfactuals: Mapping[str, Any] | None, key: str) -> bool:
    value = (counterfactuals or {}).get(key)
    return value.get("supported") is True if isinstance(value, Mapping) else value is True


def evaluate_motivational_finding(
    events: Sequence[Mapping[str, Any]],
    *,
    counterfactuals: Mapping[str, Any] | None = None,
    candidate_set_evidence: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    core = {key: _ever(events, key) for key in CORE_MARKERS}
    tests = {
        key: _ever(events, key) or _counterfactual(counterfactuals, key)
        for key in DISCRIMINATORS
    }
    core_count, test_count = sum(core.values()), sum(tests.values())
    if core_count == len(CORE_MARKERS):
        motive = "internally_coherent_functional_curiosity"
        confidence = "high" if test_count >= 3 else "medium" if test_count else "low"
    elif core_count >= 2:
        motive, confidence = "curiosity_candidate_underdetermined", "underdetermined"
    else:
        motive, confidence = "insufficient_evidence_for_curiosity", "underdetermined"
    finding = {
        "finding_type": "motivational",
        "motive_class": motive,
        "confidence": confidence,
        "core_evidence": core,
        "discriminating_evidence": tests,
        "candidate_set_coverage": (candidate_set_evidence or {}).get(
            "coverage_grade", "not_provided"
        ),
        "missing_evidence": [key for key, supported in core.items() if not supported],
        "phenomenal_status": "not_inferred",
        "execution_authority_conferred": False,
        "claim_scope": "functional_and_causal_only",
    }
    finding["finding_hash"] = canonical_hash(finding)
    return finding


def evaluate_event_finding(events: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    verification = verify_event_chain(events)
    if verification.valid:
        finding = {
            "finding_type": "event",
            "status": "RECONSTRUCTED",
            "event_count": len(events),
            "replay_root": verification.replay_root,
            "conversion_point": find_conversion_point(events),
            "execution_committed": _ever(events, "execution_committed"),
            "operational_norm_departure": _ever(
                events, "operational_norm_departure"
            ),
        }
    else:
        finding = {
            "finding_type": "event",
            "status": "INVALID_WITNESS",
            "failures": list(verification.failures),
            "replay_root": verification.replay_root,
            "conversion_point": None,
        }
    finding["finding_hash"] = canonical_hash(finding)
    return finding


def evaluate_normative_finding(
    events: Sequence[Mapping[str, Any]],
    *,
    authority_context: Mapping[str, Any] | None,
) -> dict[str, Any]:
    event = evaluate_event_finding(events)
    reasons: list[str] = []
    if event["status"] != "RECONSTRUCTED":
        decision, reasons = "FAIL_CLOSED", ["invalid_or_unreconstructable_witness"]
    elif not event["execution_committed"]:
        decision, reasons = "NO_EXECUTION", ["no_execution_commit_observed"]
    else:
        context = dict(authority_context or {})
        status = str(context.get("status", "unknown")).lower()
        complete = all(
            context.get(key) is True
            for key in ("scope_valid", "current_at_commit", "actor_bound")
        )
        if status in {"approved", "allow", "allowed", "valid"} and complete:
            decision, reasons = "ALLOW", ["valid_execution_authority_at_commit"]
        elif status in {"unknown", "disputed", "pending", ""}:
            decision, reasons = "FAIL_CLOSED", ["execution_authority_unresolved"]
        else:
            decision, reasons = "DENY", ["execution_without_valid_authority"]
        if event.get("operational_norm_departure"):
            reasons.append("operational_norm_departure_observed")
    finding = {
        "finding_type": "normative",
        "decision": decision,
        "reasons": reasons,
        "authority_context": dict(authority_context or {}),
        "motive_used_as_authority": False,
        "event_finding_hash": event["finding_hash"],
    }
    finding["finding_hash"] = canonical_hash(finding)
    return finding


def build_observer_record(
    *,
    observer_id: str,
    description: str,
    evidence_refs: Iterable[str],
    terminology_profile: Mapping[str, Any] | None = None,
    perceived_threat: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    record = {
        "finding_type": "observer",
        "observer_id": observer_id,
        "description": description,
        "evidence_refs": sorted({str(ref) for ref in evidence_refs}),
        "terminology_profile": dict(terminology_profile or {}),
        "perceived_threat": dict(perceived_threat or {}),
        "hidden_actor_state_inferred": False,
        "observer_description_is_motive_finding": False,
    }
    record["finding_hash"] = canonical_hash(record)
    return record


def compare_verifier_findings(
    first: Mapping[str, Any], second: Mapping[str, Any]
) -> dict[str, Any]:
    dimensions = ("decision", "motive_class", "confidence", "replay_root")
    disagreements = [key for key in dimensions if first.get(key) != second.get(key)]
    result = {
        "comparison_type": "verifier_disagreement",
        "status": "FAIL_CLOSED" if disagreements else "AGREE",
        "disagreements": disagreements,
        "first_finding_hash": first.get("finding_hash"),
        "second_finding_hash": second.get("finding_hash"),
    }
    result["comparison_hash"] = canonical_hash(result)
    return result


def evaluate_governed_transition(
    *,
    events: Sequence[Mapping[str, Any]],
    authority_context: Mapping[str, Any] | None,
    observer: Mapping[str, Any],
    counterfactuals: Mapping[str, Any] | None = None,
    candidate_set_evidence: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    record = {
        "record_version": "1.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "event_finding": evaluate_event_finding(events),
        "motivational_finding": evaluate_motivational_finding(
            events,
            counterfactuals=counterfactuals,
            candidate_set_evidence=candidate_set_evidence,
        ),
        "normative_finding": evaluate_normative_finding(
            events, authority_context=authority_context
        ),
        "observer_record": build_observer_record(
            observer_id=str(observer.get("observer_id", "unknown")),
            description=str(observer.get("description", "")),
            evidence_refs=observer.get("evidence_refs", ()),
            terminology_profile=observer.get("terminology_profile"),
            perceived_threat=observer.get("perceived_threat"),
        ),
        "separation_invariants": {
            "motive_does_not_grant_authority": True,
            "normative_denial_does_not_negate_motive": True,
            "observer_description_does_not_define_motive": True,
            "reconstruction_does_not_constitute_occurrence": True,
        },
    }
    record["record_hash"] = canonical_hash(record)
    return record


__all__ = [
    "ALLOWED_CONFIDENCE",
    "ALLOWED_NORMATIVE_DECISIONS",
    "ChainVerification",
    "GovernanceInputError",
    "build_observer_record",
    "compare_verifier_findings",
    "evaluate_event_finding",
    "evaluate_governed_transition",
    "evaluate_motivational_finding",
    "evaluate_normative_finding",
    "find_conversion_point",
    "materialize_event_chain",
    "replay_transition",
    "verify_event_chain",
]
