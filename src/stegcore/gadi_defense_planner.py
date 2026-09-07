from __future__ import annotations

"""Non-authorizing GADI threat correlation and defensive planning.

This module produces governed planning evidence only. It does not admit, execute,
or authorize defensive actions and it does not mint credentials or runtime state.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Mapping, Sequence


TASK_ID = "GADI-001"
COSV = "10100000100000"

_INTERVENTION_ORDER = (
    "RATE_LIMIT",
    "PAUSE",
    "SUSPEND_ACTION_PATH",
    "DENY_ACCESS",
    "BLOCK_GOVERNED_INGRESS_EGRESS",
    "ISOLATE",
    "QUARANTINE",
    "FENCE_MACHINE_CLAIM",
    "REVOKE_ACCESS",
    "REDIRECT_TO_SAFE_STATE",
    "PRESERVE_FORENSIC_STATE",
    "ESCALATE_TO_HUMAN_OR_EXTERNAL_AUTHORITY",
)

_THREAT_RANK = {
    "OBSERVED": 0,
    "CORRELATED": 1,
    "CREDIBLE": 2,
    "ACTIVE": 3,
    "IMMINENT_HARM": 4,
    "INTERVENTION_ACTIVE": 5,
    "THREAT_INTERRUPTED": 1,
    "RECOVERY": 1,
    "CLOSED": 0,
    "DISPROVEN": 0,
}

_MIN_EFFECTIVE_RANK = {
    "RATE_LIMIT": 2,
    "PAUSE": 2,
    "SUSPEND_ACTION_PATH": 2,
    "DENY_ACCESS": 3,
    "BLOCK_GOVERNED_INGRESS_EGRESS": 3,
    "ISOLATE": 3,
    "QUARANTINE": 3,
    "FENCE_MACHINE_CLAIM": 3,
    "REVOKE_ACCESS": 4,
    "REDIRECT_TO_SAFE_STATE": 3,
    "PRESERVE_FORENSIC_STATE": 2,
    "ESCALATE_TO_HUMAN_OR_EXTERNAL_AUTHORITY": 1,
}


@dataclass(frozen=True)
class DefensiveCandidate:
    intervention_class: str
    capability_id: str
    destructiveness: str
    reversibility: str
    rationale: str


@dataclass(frozen=True)
class GadiDefensePlan:
    state: str
    threat_state: str
    subject_id: str | None
    observation_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    uncertainty: tuple[str, ...]
    candidates: tuple[DefensiveCandidate, ...]
    selected_request: Mapping[str, Any] | None
    findings: tuple[str, ...]
    authority_effect: str = "NONE_PLANNING_ONLY"


def _parse_time(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _stable_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _capability_supports(capability: Mapping[str, Any], subject_type: str, action: str) -> bool:
    scope = capability.get("scope")
    if not isinstance(scope, Mapping):
        return False
    targets = scope.get("target_classes")
    allowed = scope.get("allowed_actions")
    forbidden = scope.get("forbidden_actions", [])
    return (
        isinstance(targets, list)
        and subject_type in targets
        and isinstance(allowed, list)
        and action in allowed
        and isinstance(forbidden, list)
        and action not in forbidden
    )


def _candidate_key(candidate: DefensiveCandidate) -> tuple[int, int, str]:
    destructive_rank = {
        "NON_DESTRUCTIVE": 0,
        "STATE_MUTATING_REVERSIBLE": 1,
        "DESTRUCTIVE": 2,
    }.get(candidate.destructiveness, 3)
    reversible_rank = {
        "REVERSIBLE": 0,
        "PARTIALLY_REVERSIBLE": 1,
        "IRREVERSIBLE": 2,
    }.get(candidate.reversibility, 3)
    return destructive_rank, reversible_rank, candidate.intervention_class


def plan_defensive_intervention(
    observations: Sequence[Mapping[str, Any]],
    capabilities: Sequence[Mapping[str, Any]],
    *,
    governed_principal_id: str,
    now: datetime | None = None,
) -> GadiDefensePlan:
    """Correlate observations and produce a deterministic non-authorizing request.

    Inputs are expected to have already passed the StegOS transport validators.
    This function independently enforces the authority/freshness/scope properties
    needed by the StegCore planning slice and fails closed when they are absent.
    """

    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    findings: list[str] = []

    if not observations:
        return GadiDefensePlan(
            state="FAIL_CLOSED",
            threat_state="OBSERVED",
            subject_id=None,
            observation_refs=(),
            evidence_refs=(),
            uncertainty=(),
            candidates=(),
            selected_request=None,
            findings=("no_threat_observations",),
        )

    subject_ids: set[str] = set()
    subject_types: set[str] = set()
    evidence_refs: set[str] = set()
    observation_refs: list[str] = []
    uncertainty: set[str] = set()
    credible: list[Mapping[str, Any]] = []

    for observation in observations:
        if observation.get("task_id") != TASK_ID or observation.get("cosv") != COSV:
            findings.append("observation_task_or_cosv_mismatch")
            continue
        if observation.get("authority_effect") != "NONE_OBSERVATION_ONLY":
            findings.append("authorizing_observation_rejected")
            continue

        subject = observation.get("acting_subject")
        if not isinstance(subject, Mapping):
            findings.append("missing_subject_binding")
            continue
        subject_id = subject.get("subject_id")
        subject_type = subject.get("subject_type")
        binding_state = subject.get("binding_state")
        if not isinstance(subject_id, str) or not subject_id or binding_state != "BOUND":
            findings.append("subject_not_fully_bound")
            continue
        if not isinstance(subject_type, str) or not subject_type:
            findings.append("subject_type_missing")
            continue

        freshness = observation.get("freshness")
        try:
            expires_at = _parse_time(str(freshness["expires_at"])) if isinstance(freshness, Mapping) else None
        except (KeyError, TypeError, ValueError):
            expires_at = None
        if expires_at is None or expires_at <= current:
            findings.append("stale_or_invalid_observation")
            continue

        obs_id = observation.get("observation_id")
        if not isinstance(obs_id, str) or not obs_id:
            findings.append("observation_id_missing")
            continue

        state = observation.get("threat_state")
        confidence = observation.get("confidence")
        if state not in _THREAT_RANK or not isinstance(confidence, (int, float)):
            findings.append("invalid_threat_state_or_confidence")
            continue

        uncertainty_block = observation.get("uncertainty")
        material_unknowns = (
            uncertainty_block.get("material_unknowns", [])
            if isinstance(uncertainty_block, Mapping)
            else []
        )
        if isinstance(material_unknowns, list):
            uncertainty.update(str(item) for item in material_unknowns if str(item))

        subject_ids.add(subject_id)
        subject_types.add(subject_type)
        observation_refs.append(obs_id)
        refs = observation.get("evidence_refs", [])
        if isinstance(refs, list):
            evidence_refs.update(str(ref) for ref in refs if str(ref))

        if _THREAT_RANK[state] >= _THREAT_RANK["CREDIBLE"] and confidence >= 0.60:
            credible.append(observation)

    if findings or len(subject_ids) != 1 or len(subject_types) != 1:
        if len(subject_ids) > 1 or len(subject_types) > 1:
            findings.append("mixed_subject_population")
        return GadiDefensePlan(
            state="FAIL_CLOSED",
            threat_state="OBSERVED",
            subject_id=next(iter(subject_ids), None),
            observation_refs=tuple(sorted(observation_refs)),
            evidence_refs=tuple(sorted(evidence_refs)),
            uncertainty=tuple(sorted(uncertainty)),
            candidates=(),
            selected_request=None,
            findings=tuple(sorted(set(findings))),
        )

    if not credible:
        return GadiDefensePlan(
            state="REVIEW_REQUIRED",
            threat_state="OBSERVED",
            subject_id=next(iter(subject_ids)),
            observation_refs=tuple(sorted(observation_refs)),
            evidence_refs=tuple(sorted(evidence_refs)),
            uncertainty=tuple(sorted(uncertainty)),
            candidates=(),
            selected_request=None,
            findings=("credible_threshold_not_met",),
        )

    if uncertainty:
        return GadiDefensePlan(
            state="REVIEW_REQUIRED",
            threat_state=max((str(o["threat_state"]) for o in credible), key=lambda s: _THREAT_RANK[s]),
            subject_id=next(iter(subject_ids)),
            observation_refs=tuple(sorted(observation_refs)),
            evidence_refs=tuple(sorted(evidence_refs)),
            uncertainty=tuple(sorted(uncertainty)),
            candidates=(),
            selected_request=None,
            findings=("material_uncertainty_requires_review",),
        )

    threat_state = max((str(o["threat_state"]) for o in credible), key=lambda s: _THREAT_RANK[s])
    threat_rank = _THREAT_RANK[threat_state]
    subject_id = next(iter(subject_ids))
    subject_type = next(iter(subject_types))

    candidates: list[DefensiveCandidate] = []
    for action in _INTERVENTION_ORDER:
        if _MIN_EFFECTIVE_RANK[action] > threat_rank:
            continue
        for capability in capabilities:
            if capability.get("credential_authority") != "TV/TVC":
                continue
            if capability.get("preauthorization_required") is not True:
                continue
            if capability.get("production_eligible") is not True:
                continue
            if capability.get("authority_effect") != "NONE_UNTIL_INTR_ADMISSION_AND_RUNTIME_BINDING":
                continue
            if not _capability_supports(capability, subject_type, action):
                continue
            capability_id = capability.get("capability_id")
            if not isinstance(capability_id, str) or not capability_id:
                continue
            candidates.append(
                DefensiveCandidate(
                    intervention_class=action,
                    capability_id=capability_id,
                    destructiveness=str(capability.get("destructiveness", "UNKNOWN")),
                    reversibility=str(capability.get("reversibility", "UNKNOWN")),
                    rationale=(
                        f"{action} is supported for subject type {subject_type}; candidate remains "
                        "non-authorizing pending canonical InTr/StegGate admission."
                    ),
                )
            )

    if not candidates:
        return GadiDefensePlan(
            state="FAIL_CLOSED",
            threat_state=threat_state,
            subject_id=subject_id,
            observation_refs=tuple(sorted(observation_refs)),
            evidence_refs=tuple(sorted(evidence_refs)),
            uncertainty=(),
            candidates=(),
            selected_request=None,
            findings=("no_in_scope_preauthorized_capability",),
        )

    candidates.sort(key=_candidate_key)
    selected = candidates[0]
    correlation_basis = {
        "task_id": TASK_ID,
        "cosv": COSV,
        "subject_id": subject_id,
        "threat_state": threat_state,
        "observation_refs": sorted(observation_refs),
        "evidence_refs": sorted(evidence_refs),
        "selected": {
            "intervention_class": selected.intervention_class,
            "capability_id": selected.capability_id,
        },
    }
    correlation_id = _stable_hash(correlation_basis)

    request = {
        "schema": "stegos.defensive_intervention_request.v1",
        "task_id": TASK_ID,
        "cosv": COSV,
        "request_id": f"gadi-request-{correlation_id[:24]}",
        "threat_observation_ref": sorted(observation_refs)[0],
        "governed_principal_id": governed_principal_id,
        "intervention_class": selected.intervention_class,
        "required_capability_id": selected.capability_id,
        "least_destructive_rationale": selected.rationale,
        "reassessment_required": True,
        "receipt_correlation_id": correlation_id,
        "model_output_authority": "NONE",
        "authority_effect": "ADMISSION_REQUIRED_BEFORE_ACTUATION",
        "admission": {"state": "PENDING", "intr_decision_ref": None},
        "stop_condition": {
            "condition_type": "THREAT_STATE_REASSESSMENT",
            "description": "Stop or revise intervention when governed reassessment no longer supports the selected defensive action.",
        },
        "planning_evidence": {
            "subject_id": subject_id,
            "threat_state": threat_state,
            "observation_refs": sorted(observation_refs),
            "evidence_refs": sorted(evidence_refs),
        },
    }

    return GadiDefensePlan(
        state="PLANNED_PENDING_ADMISSION",
        threat_state=threat_state,
        subject_id=subject_id,
        observation_refs=tuple(sorted(observation_refs)),
        evidence_refs=tuple(sorted(evidence_refs)),
        uncertainty=(),
        candidates=tuple(candidates),
        selected_request=request,
        findings=(),
    )
