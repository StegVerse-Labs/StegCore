from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Sequence


TERMINAL_STATES = {"SATISFIED", "DENIED", "UNRESOLVED", "NOT_APPLICABLE", "CONTRADICTORY"}


@dataclass(frozen=True)
class PredicateResult:
    provision_id: str
    predicate_id: str
    state: str
    evidence_refs: Sequence[str]
    reason: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            "provision_id": self.provision_id,
            "predicate_id": self.predicate_id,
            "state": self.state,
            "evidence_refs": list(self.evidence_refs),
            "reason": self.reason,
        }


def _matching_observations(event: Mapping[str, Any], predicate_name: str) -> List[Mapping[str, Any]]:
    return [
        observation
        for observation in event.get("observations", [])
        if observation.get("predicate") == predicate_name
    ]


def _evaluate_operator(observation: Mapping[str, Any], operator: str, expected: Any) -> str:
    observation_state = observation.get("state")
    if observation_state == "UNRESOLVED":
        return "UNRESOLVED"
    if observation_state == "CONTRADICTORY":
        return "CONTRADICTORY"

    actual = observation.get("object")
    if operator == "EXISTS":
        return "SATISFIED"
    if operator == "EQUALS":
        return "SATISFIED" if actual == expected else "DENIED"
    if operator == "NOT_EQUALS":
        return "SATISFIED" if actual != expected else "DENIED"
    if operator == "IN":
        if not isinstance(expected, list):
            return "UNRESOLVED"
        return "SATISFIED" if actual in expected else "DENIED"
    if operator == "NOT_IN":
        if not isinstance(expected, list):
            return "UNRESOLVED"
        return "SATISFIED" if actual not in expected else "DENIED"
    return "UNRESOLVED"


def _evaluate_predicate(
    event: Mapping[str, Any],
    provision_id: str,
    predicate: Mapping[str, Any],
) -> PredicateResult:
    predicate_name = predicate["observation_predicate"]
    matches = _matching_observations(event, predicate_name)
    if not matches:
        return PredicateResult(
            provision_id=provision_id,
            predicate_id=predicate["predicate_id"],
            state="UNRESOLVED",
            evidence_refs=(),
            reason=f"No observation encodes predicate {predicate_name!r}.",
        )

    states = [
        _evaluate_operator(match, predicate["operator"], predicate.get("expected"))
        for match in matches
    ]
    evidence_refs = sorted(
        {
            evidence_ref
            for match in matches
            for evidence_ref in match.get("evidence_refs", [])
        }
    )

    if "CONTRADICTORY" in states or ("SATISFIED" in states and "DENIED" in states):
        state = "CONTRADICTORY"
    elif "UNRESOLVED" in states:
        state = "UNRESOLVED"
    elif all(item == "SATISFIED" for item in states):
        state = "SATISFIED"
    elif all(item == "DENIED" for item in states):
        state = "DENIED"
    else:
        state = "UNRESOLVED"

    return PredicateResult(
        provision_id=provision_id,
        predicate_id=predicate["predicate_id"],
        state=state,
        evidence_refs=evidence_refs,
        reason=f"Evaluated {len(matches)} encoded observation(s) for {predicate_name!r}.",
    )


def _conclusion(states: Iterable[str]) -> str:
    materialized = list(states)
    if not materialized:
        return "NOT_APPLICABLE"
    if "CONTRADICTORY" in materialized:
        return "CONTRADICTORY"
    if "UNRESOLVED" in materialized:
        return "UNRESOLVED"
    if "DENIED" in materialized:
        return "DENIED"
    if all(state == "SATISFIED" for state in materialized):
        return "SATISFIED"
    return "UNRESOLVED"


def evaluate_temporal_event(
    event: Mapping[str, Any],
    governing_context: Mapping[str, Any],
    *,
    evaluation_id: str,
    adjudicative_authority: str = "NONE",
    evaluation_uncertainty: float = 0.0,
) -> Dict[str, Any]:
    """Evaluate encoded observations against a versioned governing context.

    The result is analytical only. This function never promotes an encoding into
    ground truth, never treats a counterfactual ruleset as historically applicable,
    and preserves unresolved/contradictory source states.
    """

    if adjudicative_authority not in {"NONE", "BOUND_EXTERNAL_AUTHORITY"}:
        raise ValueError("Unsupported adjudicative_authority")
    if not 0 <= evaluation_uncertainty <= 1:
        raise ValueError("evaluation_uncertainty must be in [0, 1]")

    representation = event.get("representation", {})
    if representation.get("assertion") != "INTERPRETIVE_ENCODING_NOT_GROUND_TRUTH":
        raise ValueError("Temporal event must explicitly disclaim ground-truth equivalence")

    results: List[PredicateResult] = []
    for provision in governing_context.get("ruleset", {}).get("provisions", []):
        for predicate in provision.get("predicates", []):
            results.append(_evaluate_predicate(event, provision["provision_id"], predicate))

    event_uncertainty = event.get("uncertainty", {})
    context_uncertainty = governing_context.get("uncertainty", {})
    temporal_application = governing_context.get("temporal_application", "CONTEMPORANEOUS")

    notes = []
    if temporal_application == "COUNTERFACTUAL":
        notes.append("Selected governing context is projected outside its historical applicability window.")
    if adjudicative_authority == "NONE":
        notes.append("Result has no adjudicative authority and must not be represented as an official ruling or legal conclusion.")

    return {
        "evaluation_id": evaluation_id,
        "event_id": event["event_id"],
        "context_id": governing_context["context_id"],
        "results": [result.as_dict() for result in results],
        "conclusion": _conclusion(result.state for result in results),
        "temporal_application": temporal_application,
        "variance": {
            "source_uncertainty": event_uncertainty["source_uncertainty"],
            "observation_uncertainty": event_uncertainty["observation_uncertainty"],
            "semantic_mapping_uncertainty": event_uncertainty["semantic_mapping_uncertainty"],
            "rule_mapping_uncertainty": context_uncertainty["rule_mapping_uncertainty"],
            "interpretation_uncertainty": context_uncertainty["interpretation_uncertainty"],
            "evaluation_uncertainty": evaluation_uncertainty,
            "notes": notes,
        },
        "adjudicative_authority": adjudicative_authority,
        "authority_effect": "NONE_ANALYSIS_ONLY",
        "representation_assertion": "INTERPRETIVE_ENCODING_NOT_GROUND_TRUTH",
        "provenance": list(event.get("provenance", []))
        + list(governing_context.get("authority", {}).get("source_refs", [])),
    }
