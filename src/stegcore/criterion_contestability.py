from __future__ import annotations

"""Deterministic pre-selection/criterion contestability boundary for StegCore.

This module keeps upstream orientation separate from execution authority.  A frame,
criterion, trajectory, model recommendation, or successful plan does not become
authoritative merely because it shaped a consequence-bearing candidate.
"""

from typing import Any, Mapping, Sequence


REQUIRED_CURRENT_PREDICATES = (
    "authority_current",
    "continuity_current",
    "governing_conditions_current",
    "consequence_attributable",
    "consequence_reconstructable",
)


class CriterionContestabilityInputError(ValueError):
    """Raised when the boundary receives structurally invalid input."""


def _bool_or_none(value: Any, field: str) -> bool | None:
    if value is None or isinstance(value, bool):
        return value
    raise CriterionContestabilityInputError(f"{field} must be boolean or null")


def _trajectory_ids(value: Any) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise CriterionContestabilityInputError("trajectory_ids must be a sequence")
    result = tuple(str(item).strip() for item in value)
    if not result or any(not item for item in result):
        raise CriterionContestabilityInputError(
            "trajectory_ids must contain at least one non-empty identifier"
        )
    if len(set(result)) != len(result):
        raise CriterionContestabilityInputError("trajectory_ids must be unique")
    return result


def evaluate_criterion_contestability(candidate: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate whether an upstream criterion may reach the consequence boundary.

    The function is intentionally independent from the general StegCore ``decide``
    interface.  It establishes an additional fail-closed predicate family that can
    be composed with permission/admissibility and commit-coherence evaluation.
    """

    consequence_bearing = _bool_or_none(
        candidate.get("consequence_bearing"), "consequence_bearing"
    )
    if consequence_bearing is None:
        raise CriterionContestabilityInputError("consequence_bearing is required")

    trajectories = _trajectory_ids(candidate.get("trajectory_ids", ()))
    criterion_id = str(candidate.get("selected_criterion_id", "")).strip()
    if not criterion_id:
        raise CriterionContestabilityInputError("selected_criterion_id is required")

    result: dict[str, Any] = {
        "selected_criterion_id": criterion_id,
        "trajectory_ids": list(trajectories),
        "trajectory_parallelity_preserved": len(trajectories) > 1,
        "synthetic_consensus_used": False,
        "orientation_used_as_authority": False,
        "contestability_used_as_admissibility": False,
        "execution_authority_conferred": False,
        "admissible": False,
        "decision": "DENY",
        "reasons": [],
    }

    if not consequence_bearing:
        result.update(
            decision="ALLOW",
            admissible=True,
            reasons=["orientation_or_coordination_only"],
        )
        return result

    checks = {
        "criterion_provenance_bound": _bool_or_none(
            candidate.get("criterion_provenance_bound"), "criterion_provenance_bound"
        ),
        "criterion_contestable_at_commit": _bool_or_none(
            candidate.get("criterion_contestable_at_commit"),
            "criterion_contestable_at_commit",
        ),
        "criterion_authority_current": _bool_or_none(
            candidate.get("criterion_authority_current"), "criterion_authority_current"
        ),
        "relation_governed": _bool_or_none(
            candidate.get("relation_governed"), "relation_governed"
        ),
    }

    current = {
        field: _bool_or_none(candidate.get(field), field)
        for field in REQUIRED_CURRENT_PREDICATES
    }

    consent_required = _bool_or_none(
        candidate.get("consent_or_standing_required", False),
        "consent_or_standing_required",
    )
    consent_current = _bool_or_none(
        candidate.get("consent_or_standing_current"),
        "consent_or_standing_current",
    )

    negative_reasons: list[str] = []
    if checks["criterion_provenance_bound"] is False:
        negative_reasons.append("criterion_provenance_unbound")
    if checks["criterion_contestable_at_commit"] is False:
        negative_reasons.append("criterion_not_contestable_at_commit")
    if checks["criterion_authority_current"] is False:
        negative_reasons.append("criterion_authority_not_current")
    if checks["relation_governed"] is False:
        negative_reasons.append("trajectory_relation_ungoverned")
    if consent_required and consent_current is False:
        negative_reasons.append("consent_or_standing_not_current")
    negative_reasons.extend(
        f"{field}_false" for field, value in current.items() if value is False
    )

    if negative_reasons:
        result["reasons"] = negative_reasons
        return result

    unresolved = [name for name, value in checks.items() if value is None]
    unresolved.extend(name for name, value in current.items() if value is None)
    if consent_required and consent_current is None:
        unresolved.append("consent_or_standing_current")

    if unresolved:
        result.update(
            decision="DEFER",
            reasons=[f"unresolved:{name}" for name in unresolved],
        )
        return result

    result.update(
        decision="ALLOW",
        admissible=True,
        reasons=["criterion_contestable_and_current_at_consequence_boundary"],
    )
    return result
