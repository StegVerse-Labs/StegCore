from __future__ import annotations

"""Deterministic population-level planning over canonical StegGate evaluations.

This module is intentionally *not* an admissibility evaluator and it performs no
commit. Each candidate transition is evaluated by the canonical
``stegcore.steggate.evaluate_admissibility`` function. The resulting standing is
then arranged into a deterministic dependency/conflict/bundle plan.

Derived population observations (for example coherence or gradient metadata) are
carried only as evidence. They never alter authority, canonical disposition, or
commit eligibility.
"""

from dataclasses import dataclass, field
from typing import Any, Iterable, Literal, Mapping

from .steggate import AdmissibilityEvaluation, AdmissibilityRequest, canonical_sha256, evaluate_admissibility

CanonicalDisposition = Literal["ALLOW", "DENY", "REVIEW", "FAIL_CLOSED"]
PlanState = Literal["READY", "REVIEW_REQUIRED", "FAIL_CLOSED"]
BundleState = Literal["ALLOW", "DENY", "REVIEW", "FAIL_CLOSED"]
ManifoldActionState = Literal["CONTINUE", "REVIEWABLE", "FAIL_CLOSED"]


@dataclass(frozen=True)
class PopulationTransition:
    """One declared transition in a frozen manifold population."""

    transition_id: str
    base_manifold_hash: str
    request: AdmissibilityRequest
    depends_on: tuple[str, ...] = ()
    conflicts_with: tuple[str, ...] = ()
    bundle_id: str | None = None
    observations: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TransitionStanding:
    transition_id: str
    disposition: CanonicalDisposition
    candidate_hash: str
    evaluation_hash: str
    reasons: tuple[str, ...]
    depends_on: tuple[str, ...]
    conflicts_with: tuple[str, ...]
    bundle_id: str
    observations_hash: str
    derived_observations_authoritative: bool = False


@dataclass(frozen=True)
class BundleStanding:
    bundle_id: str
    transition_ids: tuple[str, ...]
    disposition: BundleState
    eligible_for_commit: bool
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class ManifoldPlan:
    schema: str
    base_manifold_hash: str
    state: PlanState
    ordered_transition_ids: tuple[str, ...]
    eligible_transition_ids: tuple[str, ...]
    conflict_pairs: tuple[tuple[str, str], ...]
    standings: tuple[TransitionStanding, ...]
    bundles: tuple[BundleStanding, ...]
    reasons: tuple[str, ...]
    plan_hash: str
    canonical_evaluator: str = "stegcore.steggate.evaluate_admissibility"
    canonical_evaluator_unchanged: bool = True
    commit_performed: bool = False
    continuity_receipt_minted: bool = False
    derived_observations_authoritative: bool = False
    authority_effect: str = "NONE_PLANNING_ONLY"


@dataclass(frozen=True)
class ManifoldGovernanceAction:
    """Production governance resolution for concurrent manifold transitions.

    This object does not itself perform external execution. It determines which
    canonically evaluated transitions may continue to the separately governed
    commit boundary, which transitions must remain reviewable, and which are
    denied or failed closed.
    """

    schema: str
    base_manifold_hash: str
    plan_hash: str
    state: ManifoldActionState
    continue_transition_ids: tuple[str, ...]
    review_transition_ids: tuple[str, ...]
    held_transition_ids: tuple[str, ...]
    denied_transition_ids: tuple[str, ...]
    fail_closed_transition_ids: tuple[str, ...]
    authority_boundary_refs: tuple[str, ...]
    reviewable_projection: Mapping[str, Any]
    action_hash: str
    canonical_evaluator: str = "stegcore.steggate.evaluate_admissibility"
    canonical_evaluator_unchanged: bool = True
    human_review_timing_is_authority: bool = False
    wall_clock_is_governance_authority: bool = False
    heartbeat_is_governance_authority: bool = False
    machine_speed_internal_transitions_may_continue: bool = True
    protected_boundary_crossing_requires_external_authority: bool = True
    external_execution_performed: bool = False
    continuity_receipt_minted: bool = False
    authority_effect: str = "NONE_UNTIL_SEPARATE_GOVERNED_COMMIT"


_DISPOSITION_SEVERITY: dict[str, int] = {
    "ALLOW": 0,
    "REVIEW": 1,
    "DENY": 2,
    "FAIL_CLOSED": 3,
}


def _normalize_text(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("identifier/hash values must be non-empty strings")
    return value.strip()


def _stable_evaluation_projection(evaluation: AdmissibilityEvaluation) -> dict[str, Any]:
    """Return the replay-stable semantic portion of one canonical evaluation.

    Canonical StegGate deliberately emits time-bound provenance fields such as
    ``evaluated_at``, ``decision_state_hash`` and the three-layer receipt hash.
    Those values remain canonical evaluation evidence, but incorporating them in
    a population *plan identity* would make an otherwise identical population
    hash differently merely because candidates were evaluated a few microseconds
    apart or in a different input permutation.

    The planner therefore binds the stable semantic standing while excluding only
    those time/provenance-bound values. It never recomputes, replaces or changes
    the canonical disposition or predicate matrix.
    """

    return {
        "artifact_type": evaluation.artifact_type,
        "schema_version": evaluation.schema_version,
        "disposition": evaluation.disposition,
        "candidate_hash": evaluation.candidate_hash,
        "matrix": [row.model_dump(mode="json") for row in evaluation.matrix],
        "reasons": list(evaluation.reasons),
        "canonical_three_layer_decision": evaluation.canonical_three_layer_decision,
        "canonical_three_layer_reason": evaluation.canonical_three_layer_reason,
        "canonical_three_layer_request_hash": evaluation.canonical_three_layer_request_hash,
        "permission_present": evaluation.permission_present,
        "permission_is_not_admissibility": evaluation.permission_is_not_admissibility,
        "continuity_receipt_minted": evaluation.continuity_receipt_minted,
        "external_execution_performed": evaluation.external_execution_performed,
    }


def _fail_closed(reason: str, *, base_manifold_hash: str = "UNRESOLVED") -> ManifoldPlan:
    body = {
        "schema": "stegcore.manifold-governance-plan.v1",
        "base_manifold_hash": base_manifold_hash,
        "state": "FAIL_CLOSED",
        "ordered_transition_ids": [],
        "eligible_transition_ids": [],
        "conflict_pairs": [],
        "standings": [],
        "bundles": [],
        "reasons": [reason],
        "canonical_evaluator": "stegcore.steggate.evaluate_admissibility",
        "canonical_evaluator_unchanged": True,
        "commit_performed": False,
        "continuity_receipt_minted": False,
        "derived_observations_authoritative": False,
        "authority_effect": "NONE_PLANNING_ONLY",
    }
    return ManifoldPlan(
        schema=body["schema"],
        base_manifold_hash=base_manifold_hash,
        state="FAIL_CLOSED",
        ordered_transition_ids=(),
        eligible_transition_ids=(),
        conflict_pairs=(),
        standings=(),
        bundles=(),
        reasons=(reason,),
        plan_hash=canonical_sha256(body),
    )


def _topological_order(by_id: dict[str, PopulationTransition]) -> tuple[str, ...] | None:
    incoming: dict[str, set[str]] = {
        transition_id: set(item.depends_on) for transition_id, item in by_id.items()
    }
    children: dict[str, set[str]] = {transition_id: set() for transition_id in by_id}
    for transition_id, dependencies in incoming.items():
        for dependency in dependencies:
            children[dependency].add(transition_id)

    ready = sorted(transition_id for transition_id, dependencies in incoming.items() if not dependencies)
    ordered: list[str] = []
    while ready:
        current = ready.pop(0)
        ordered.append(current)
        for child in sorted(children[current]):
            incoming[child].discard(current)
            if not incoming[child] and child not in ordered and child not in ready:
                ready.append(child)
        ready.sort()

    if len(ordered) != len(by_id):
        return None
    return tuple(ordered)


def _plan_payload(
    *,
    base_manifold_hash: str,
    state: PlanState,
    ordered_transition_ids: tuple[str, ...],
    eligible_transition_ids: tuple[str, ...],
    conflict_pairs: tuple[tuple[str, str], ...],
    standings: tuple[TransitionStanding, ...],
    bundles: tuple[BundleStanding, ...],
    reasons: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "schema": "stegcore.manifold-governance-plan.v1",
        "base_manifold_hash": base_manifold_hash,
        "state": state,
        "ordered_transition_ids": list(ordered_transition_ids),
        "eligible_transition_ids": list(eligible_transition_ids),
        "conflict_pairs": [list(pair) for pair in conflict_pairs],
        "standings": [
            {
                "transition_id": row.transition_id,
                "disposition": row.disposition,
                "candidate_hash": row.candidate_hash,
                "evaluation_hash": row.evaluation_hash,
                "reasons": list(row.reasons),
                "depends_on": list(row.depends_on),
                "conflicts_with": list(row.conflicts_with),
                "bundle_id": row.bundle_id,
                "observations_hash": row.observations_hash,
                "derived_observations_authoritative": False,
            }
            for row in standings
        ],
        "bundles": [
            {
                "bundle_id": row.bundle_id,
                "transition_ids": list(row.transition_ids),
                "disposition": row.disposition,
                "eligible_for_commit": row.eligible_for_commit,
                "reasons": list(row.reasons),
            }
            for row in bundles
        ],
        "reasons": list(reasons),
        "canonical_evaluator": "stegcore.steggate.evaluate_admissibility",
        "canonical_evaluator_unchanged": True,
        "commit_performed": False,
        "continuity_receipt_minted": False,
        "derived_observations_authoritative": False,
        "authority_effect": "NONE_PLANNING_ONLY",
    }


def plan_manifold(transitions: Iterable[PopulationTransition]) -> ManifoldPlan:
    """Evaluate and deterministically plan a frozen population of transitions.

    The function never performs a commit. It is safe to replay with the same
    declared population: equivalent permutations yield the same ``plan_hash``.
    """

    population = tuple(transitions)
    if not population:
        return _fail_closed("EMPTY_TRANSITION_POPULATION")

    try:
        normalized_ids = tuple(_normalize_text(item.transition_id) for item in population)
        base_values = tuple(_normalize_text(item.base_manifold_hash) for item in population)
    except ValueError as exc:
        return _fail_closed(f"INVALID_POPULATION_IDENTITY:{exc}")

    if len(set(normalized_ids)) != len(normalized_ids):
        return _fail_closed("DUPLICATE_TRANSITION_ID")
    if len(set(base_values)) != 1:
        return _fail_closed("MIXED_OR_STALE_BASE_MANIFOLD")

    base_manifold_hash = base_values[0]
    by_id = {item.transition_id.strip(): item for item in population}
    known_ids = set(by_id)

    normalized_dependencies: dict[str, tuple[str, ...]] = {}
    normalized_conflicts: dict[str, tuple[str, ...]] = {}
    for transition_id, item in by_id.items():
        dependencies = tuple(sorted(set(item.depends_on)))
        conflicts = tuple(sorted(set(item.conflicts_with)))
        if transition_id in dependencies or transition_id in conflicts:
            return _fail_closed("SELF_REFERENCE_IN_POPULATION", base_manifold_hash=base_manifold_hash)
        unknown_dependencies = sorted(set(dependencies) - known_ids)
        unknown_conflicts = sorted(set(conflicts) - known_ids)
        if unknown_dependencies:
            return _fail_closed(
                f"UNKNOWN_DEPENDENCY_REFERENCE:{transition_id}:{','.join(unknown_dependencies)}",
                base_manifold_hash=base_manifold_hash,
            )
        if unknown_conflicts:
            return _fail_closed(
                f"UNKNOWN_CONFLICT_REFERENCE:{transition_id}:{','.join(unknown_conflicts)}",
                base_manifold_hash=base_manifold_hash,
            )
        normalized_dependencies[transition_id] = dependencies
        normalized_conflicts[transition_id] = conflicts

    normalized_by_id = {
        transition_id: PopulationTransition(
            transition_id=transition_id,
            base_manifold_hash=base_manifold_hash,
            request=item.request,
            depends_on=normalized_dependencies[transition_id],
            conflicts_with=normalized_conflicts[transition_id],
            bundle_id=(item.bundle_id.strip() if isinstance(item.bundle_id, str) and item.bundle_id.strip() else None),
            observations=item.observations,
        )
        for transition_id, item in by_id.items()
    }

    ordered = _topological_order(normalized_by_id)
    if ordered is None:
        return _fail_closed("DEPENDENCY_CYCLE", base_manifold_hash=base_manifold_hash)

    standing_by_id: dict[str, TransitionStanding] = {}
    for transition_id in sorted(normalized_by_id):
        item = normalized_by_id[transition_id]
        evaluation = evaluate_admissibility(item.request)
        stable_evaluation = _stable_evaluation_projection(evaluation)
        standing_by_id[transition_id] = TransitionStanding(
            transition_id=transition_id,
            disposition=evaluation.disposition,
            candidate_hash=evaluation.candidate_hash,
            evaluation_hash=canonical_sha256(stable_evaluation),
            reasons=tuple(evaluation.reasons),
            depends_on=item.depends_on,
            conflicts_with=item.conflicts_with,
            bundle_id=item.bundle_id or transition_id,
            observations_hash=canonical_sha256(dict(item.observations)),
        )

    conflict_pairs_set: set[tuple[str, str]] = set()
    for transition_id, conflicts in normalized_conflicts.items():
        for other in conflicts:
            conflict_pairs_set.add(tuple(sorted((transition_id, other))))
    conflict_pairs = tuple(sorted(conflict_pairs_set))

    global_reasons: set[str] = set()
    state: PlanState = "READY"
    if any(row.disposition == "FAIL_CLOSED" for row in standing_by_id.values()):
        state = "FAIL_CLOSED"
        global_reasons.add("CANONICAL_TRANSITION_FAIL_CLOSED")
    elif any(row.disposition == "REVIEW" for row in standing_by_id.values()):
        state = "REVIEW_REQUIRED"
        global_reasons.add("CANONICAL_TRANSITION_REVIEW_REQUIRED")

    for left, right in conflict_pairs:
        if standing_by_id[left].disposition == "ALLOW" and standing_by_id[right].disposition == "ALLOW":
            if state != "FAIL_CLOSED":
                state = "REVIEW_REQUIRED"
            global_reasons.add(f"ALLOW_CONFLICT_REQUIRES_RESOLUTION:{left}:{right}")

    for transition_id in ordered:
        row = standing_by_id[transition_id]
        dependency_dispositions = [standing_by_id[dependency].disposition for dependency in row.depends_on]
        if "FAIL_CLOSED" in dependency_dispositions:
            state = "FAIL_CLOSED"
            global_reasons.add(f"DEPENDENCY_FAIL_CLOSED:{transition_id}")
        elif "REVIEW" in dependency_dispositions and state != "FAIL_CLOSED":
            state = "REVIEW_REQUIRED"
            global_reasons.add(f"DEPENDENCY_REVIEW_REQUIRED:{transition_id}")

    groups: dict[str, list[str]] = {}
    for transition_id, row in standing_by_id.items():
        groups.setdefault(row.bundle_id, []).append(transition_id)

    bundle_rows: list[BundleStanding] = []
    bundle_commit_eligible: dict[str, bool] = {}
    for bundle_id in sorted(groups):
        members = tuple(sorted(groups[bundle_id]))
        worst = max(
            (standing_by_id[member].disposition for member in members),
            key=lambda disposition: _DISPOSITION_SEVERITY[disposition],
        )
        reasons: set[str] = set()
        if worst != "ALLOW":
            reasons.add(f"BUNDLE_CANONICAL_{worst}")

        dependencies_ok = True
        for member in members:
            for dependency in standing_by_id[member].depends_on:
                if standing_by_id[dependency].disposition != "ALLOW":
                    dependencies_ok = False
                    reasons.add(f"DEPENDENCY_NOT_ALLOW:{member}:{dependency}")

        conflicts_ok = True
        member_set = set(members)
        for left, right in conflict_pairs:
            if left in member_set or right in member_set:
                if standing_by_id[left].disposition == "ALLOW" and standing_by_id[right].disposition == "ALLOW":
                    conflicts_ok = False
                    reasons.add(f"UNRESOLVED_ALLOW_CONFLICT:{left}:{right}")

        eligible = worst == "ALLOW" and dependencies_ok and conflicts_ok and state != "FAIL_CLOSED"
        bundle_commit_eligible[bundle_id] = eligible
        bundle_rows.append(
            BundleStanding(
                bundle_id=bundle_id,
                transition_ids=members,
                disposition=worst,
                eligible_for_commit=eligible,
                reasons=tuple(sorted(reasons)),
            )
        )

    eligible_ids = tuple(
        transition_id
        for transition_id in ordered
        if standing_by_id[transition_id].disposition == "ALLOW"
        and bundle_commit_eligible[standing_by_id[transition_id].bundle_id]
    )
    standings = tuple(standing_by_id[transition_id] for transition_id in sorted(standing_by_id))
    bundles = tuple(bundle_rows)
    reasons = tuple(sorted(global_reasons))

    payload = _plan_payload(
        base_manifold_hash=base_manifold_hash,
        state=state,
        ordered_transition_ids=ordered,
        eligible_transition_ids=eligible_ids,
        conflict_pairs=conflict_pairs,
        standings=standings,
        bundles=bundles,
        reasons=reasons,
    )
    return ManifoldPlan(
        schema=payload["schema"],
        base_manifold_hash=base_manifold_hash,
        state=state,
        ordered_transition_ids=ordered,
        eligible_transition_ids=eligible_ids,
        conflict_pairs=conflict_pairs,
        standings=standings,
        bundles=bundles,
        reasons=reasons,
        plan_hash=canonical_sha256(payload),
    )

def govern_manifold_action(
    transitions: Iterable[PopulationTransition],
    *,
    authority_boundary_refs: Iterable[str] = (),
) -> ManifoldGovernanceAction:
    """Resolve concurrent manifold progression through canonical StegVerse governance.

    The production invariant is state-boundary governance, not a temporal human
    race. Canonical ALLOW transitions whose dependency/bundle/conflict conditions
    are satisfied may continue to the separately governed commit boundary even
    while an unrelated branch is waiting for human review. REVIEW transitions and
    unresolved ALLOW conflicts remain reviewable; their dependent transitions are
    held. DENY and FAIL_CLOSED are never promoted.

    HB/time may observe the resulting projection but neither heartbeat cadence nor
    wall-clock timing grants transition authority.
    """

    population = tuple(transitions)
    plan = plan_manifold(population)
    standings = {row.transition_id: row for row in plan.standings}
    ordered = tuple(plan.ordered_transition_ids)

    denied = tuple(
        transition_id
        for transition_id in ordered
        if standings.get(transition_id) is not None
        and standings[transition_id].disposition == "DENY"
    )
    failed = tuple(
        transition_id
        for transition_id in ordered
        if standings.get(transition_id) is not None
        and standings[transition_id].disposition == "FAIL_CLOSED"
    )

    review_set = {
        transition_id
        for transition_id in ordered
        if standings.get(transition_id) is not None
        and standings[transition_id].disposition == "REVIEW"
    }
    for left, right in plan.conflict_pairs:
        left_row = standings.get(left)
        right_row = standings.get(right)
        if (
            left_row is not None
            and right_row is not None
            and left_row.disposition == "ALLOW"
            and right_row.disposition == "ALLOW"
        ):
            review_set.update((left, right))

    continued = tuple(plan.eligible_transition_ids) if plan.state != "FAIL_CLOSED" else ()
    review = tuple(transition_id for transition_id in ordered if transition_id in review_set)
    classified = set(continued) | set(review) | set(denied) | set(failed)
    held = tuple(transition_id for transition_id in ordered if transition_id not in classified)

    if plan.state == "FAIL_CLOSED":
        state: ManifoldActionState = "FAIL_CLOSED"
    elif review or held:
        state = "REVIEWABLE"
    else:
        state = "CONTINUE"

    boundary_refs = tuple(sorted({_normalize_text(ref) for ref in authority_boundary_refs}))
    projection = {
        "schema": "stegcore.governed-manifold-projection.v1",
        "base_manifold_hash": plan.base_manifold_hash,
        "plan_hash": plan.plan_hash,
        "state": state,
        "ordered_transition_ids": list(ordered),
        "continue_transition_ids": list(continued),
        "review_transition_ids": list(review),
        "held_transition_ids": list(held),
        "denied_transition_ids": list(denied),
        "fail_closed_transition_ids": list(failed),
        "authority_boundary_refs": list(boundary_refs),
        "transition_standings": [
            {
                "transition_id": row.transition_id,
                "disposition": row.disposition,
                "depends_on": list(row.depends_on),
                "conflicts_with": list(row.conflicts_with),
                "bundle_id": row.bundle_id,
                "candidate_hash": row.candidate_hash,
                "evaluation_hash": row.evaluation_hash,
            }
            for row in plan.standings
        ],
        "governance_invariants": {
            "human_in_the_loop_timing_is_governance_authority": False,
            "wall_clock_is_governance_authority": False,
            "heartbeat_is_governance_authority": False,
            "observation_is_authorization": False,
            "machine_speed_internal_transitions_may_continue_inside_existing_authority": True,
            "protected_boundary_crossing_requires_external_authority": True,
            "linear_transition_path_required": False,
            "manifold_reviewable_as_projection": True,
        },
        "external_execution_performed": False,
        "continuity_receipt_minted": False,
        "authority_effect": "NONE_UNTIL_SEPARATE_GOVERNED_COMMIT",
    }
    payload = {
        "schema": "stegcore.manifold-governance-action.v1",
        "projection": projection,
        "canonical_evaluator": "stegcore.steggate.evaluate_admissibility",
        "canonical_evaluator_unchanged": True,
    }
    return ManifoldGovernanceAction(
        schema=payload["schema"],
        base_manifold_hash=plan.base_manifold_hash,
        plan_hash=plan.plan_hash,
        state=state,
        continue_transition_ids=continued,
        review_transition_ids=review,
        held_transition_ids=held,
        denied_transition_ids=denied,
        fail_closed_transition_ids=failed,
        authority_boundary_refs=boundary_refs,
        reviewable_projection=projection,
        action_hash=canonical_sha256(payload),
    )


__all__ = [
    "PopulationTransition",
    "TransitionStanding",
    "BundleStanding",
    "ManifoldPlan",
    "ManifoldGovernanceAction",
    "plan_manifold",
    "govern_manifold_action",
]
