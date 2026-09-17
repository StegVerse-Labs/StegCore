from __future__ import annotations

"""Deterministic, non-authorizing authority-basis resolution for evaluator tests.

This module does not issue authority, interpret role labels as authority, verify
TVC credentials, or replace the control plane. It evaluates a frozen set of
already-supplied authority/delegation assertions against one exact candidate so
StegCore can derive the commit-time booleans consumed by StegGate without asking
the SDK to invent authority semantics.
"""

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Mapping

REQUEST_SCHEMA = "stegcore.authority-basis-request.v1"
RESULT_SCHEMA = "stegcore.authority-basis-resolution.v1"
REQUEST_AUTHORITY_EFFECT = "NONE_TEST_EVIDENCE_ONLY"
RESULT_AUTHORITY_EFFECT = "NONE_RESOLUTION_ONLY"
ACTIVE = "ACTIVE"
INACTIVE_STATES = {"SUSPENDED", "REVOKED", "EXPIRED"}


class AuthorityBasisError(ValueError):
    pass


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AuthorityBasisError(f"{field} is required")
    return value.strip()


def _text_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
        raise AuthorityBasisError(f"{field} must be a non-empty array of strings")
    return list(dict.fromkeys(item.strip() for item in value))


def _parse_time(value: Any, field: str) -> datetime:
    text = _text(value, field)
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise AuthorityBasisError(f"{field} must be RFC3339/ISO-8601") from exc
    if parsed.tzinfo is None:
        raise AuthorityBasisError(f"{field} must include timezone")
    return parsed.astimezone(timezone.utc)


def _candidate_matches(assertion: Mapping[str, Any], candidate: Mapping[str, str]) -> bool:
    def covers(field: str, expected: str) -> bool:
        values = assertion[field]
        return "*" in values or expected in values

    return (
        covers("actions", candidate["action"])
        and covers("targets", candidate["target"])
        and covers("scopes", candidate["scope"])
    )


def _temporally_current(assertion: Mapping[str, Any], observed_at: datetime) -> bool:
    start = _parse_time(assertion["valid_from"], "valid_from")
    end = _parse_time(assertion["valid_until"], "valid_until")
    return start <= observed_at <= end


def _normalize_assertion(value: Any, *, delegation: bool) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise AuthorityBasisError("authority/delegation assertions must be objects")
    item = deepcopy(dict(value))
    base = {
        "assertion_id",
        "actions",
        "targets",
        "scopes",
        "status",
        "valid_from",
        "valid_until",
        "source_ref",
        "evidence_refs",
    }
    allowed = set(base)
    if delegation:
        allowed |= {"delegator_identity", "delegate_identity", "authority_reference"}
    else:
        allowed |= {"subject_identity"}
    unknown = sorted(set(item) - allowed)
    if unknown:
        raise AuthorityBasisError("unknown assertion fields: " + ", ".join(unknown))

    item["assertion_id"] = _text(item.get("assertion_id"), "assertion_id")
    if delegation:
        item["delegator_identity"] = _text(item.get("delegator_identity"), "delegator_identity")
        item["delegate_identity"] = _text(item.get("delegate_identity"), "delegate_identity")
        item["authority_reference"] = _text(item.get("authority_reference"), "authority_reference")
    else:
        item["subject_identity"] = _text(item.get("subject_identity"), "subject_identity")
    item["actions"] = _text_list(item.get("actions"), "actions")
    item["targets"] = _text_list(item.get("targets"), "targets")
    item["scopes"] = _text_list(item.get("scopes"), "scopes")
    status = _text(item.get("status"), "status").upper()
    if status != ACTIVE and status not in INACTIVE_STATES:
        raise AuthorityBasisError("status must be ACTIVE, SUSPENDED, REVOKED, or EXPIRED")
    item["status"] = status
    _parse_time(item.get("valid_from"), "valid_from")
    _parse_time(item.get("valid_until"), "valid_until")
    if _parse_time(item["valid_until"], "valid_until") < _parse_time(item["valid_from"], "valid_from"):
        raise AuthorityBasisError("valid_until must not precede valid_from")
    item["source_ref"] = _text(item.get("source_ref"), "source_ref")
    refs = item.get("evidence_refs")
    if not isinstance(refs, list) or not all(isinstance(ref, str) and ref.strip() for ref in refs):
        raise AuthorityBasisError("evidence_refs must be an array of strings")
    item["evidence_refs"] = list(dict.fromkeys(ref.strip() for ref in refs))
    return item


def validate_authority_basis_request(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise AuthorityBasisError("authority basis request must be an object")
    request = deepcopy(dict(value))
    allowed = {
        "schema",
        "task_id",
        "actor_identity",
        "actor_role",
        "candidate",
        "authority_assertions",
        "delegation_assertions",
        "delegation_required",
        "authority_effect",
    }
    unknown = sorted(set(request) - allowed)
    if unknown:
        raise AuthorityBasisError("unknown authority basis request fields: " + ", ".join(unknown))
    if request.get("schema") != REQUEST_SCHEMA:
        raise AuthorityBasisError(f"schema must be {REQUEST_SCHEMA}")
    request["task_id"] = _text(request.get("task_id"), "task_id")
    request["actor_identity"] = _text(request.get("actor_identity"), "actor_identity")
    role = request.get("actor_role")
    if role is not None:
        request["actor_role"] = _text(role, "actor_role")
    candidate = request.get("candidate")
    if not isinstance(candidate, Mapping):
        raise AuthorityBasisError("candidate must be an object")
    candidate = {
        "action": _text(candidate.get("action"), "candidate.action"),
        "target": _text(candidate.get("target"), "candidate.target"),
        "scope": _text(candidate.get("scope"), "candidate.scope"),
    }
    request["candidate"] = candidate
    raw_authority = request.get("authority_assertions", [])
    raw_delegation = request.get("delegation_assertions", [])
    if not isinstance(raw_authority, list) or not isinstance(raw_delegation, list):
        raise AuthorityBasisError("authority_assertions and delegation_assertions must be arrays")
    request["authority_assertions"] = [_normalize_assertion(item, delegation=False) for item in raw_authority]
    request["delegation_assertions"] = [_normalize_assertion(item, delegation=True) for item in raw_delegation]
    if not isinstance(request.get("delegation_required"), bool):
        raise AuthorityBasisError("delegation_required must be boolean")
    if request.get("authority_effect") != REQUEST_AUTHORITY_EFFECT:
        raise AuthorityBasisError("authority basis request must be non-authorizing")
    return request


def resolve_authority_basis(value: Any, *, observed_at: str) -> dict[str, Any]:
    """Resolve current test-state facts without granting or minting authority."""

    request = validate_authority_basis_request(value)
    observed = _parse_time(observed_at, "observed_at")
    actor = request["actor_identity"]
    candidate = request["candidate"]

    actor_assertions = [
        item for item in request["authority_assertions"] if item["subject_identity"] == actor
    ]
    matching_authority = [
        item for item in actor_assertions
        if item["status"] == ACTIVE
        and _temporally_current(item, observed)
        and _candidate_matches(item, candidate)
    ]
    matching_authority.sort(key=lambda item: item["assertion_id"])

    selected_authority = matching_authority[0] if matching_authority else None
    if selected_authority is not None:
        actor_current: bool | None = True
        authority_reason = "matching_current_authority_assertion"
    elif actor_assertions:
        actor_current = False
        authority_reason = "actor_authority_assertions_do_not_cover_current_candidate"
    else:
        actor_current = None
        authority_reason = "actor_authority_unestablished"

    selected_delegation = None
    if request["delegation_required"]:
        if selected_authority is None:
            delegation_current: bool | None = None if actor_current is None else False
            delegation_reason = "delegation_cannot_be_established_without_current_authority_basis"
        else:
            related = [
                item for item in request["delegation_assertions"]
                if item["delegate_identity"] == actor
                and item["authority_reference"] == selected_authority["assertion_id"]
            ]
            matching = [
                item for item in related
                if item["status"] == ACTIVE
                and _temporally_current(item, observed)
                and _candidate_matches(item, candidate)
            ]
            matching.sort(key=lambda item: item["assertion_id"])
            selected_delegation = matching[0] if matching else None
            if selected_delegation is not None:
                delegation_current = True
                delegation_reason = "matching_current_delegation_assertion"
            elif related:
                delegation_current = False
                delegation_reason = "delegation_assertions_do_not_cover_current_candidate"
            else:
                delegation_current = None
                delegation_reason = "delegation_unestablished"
    else:
        delegation_current = True
        delegation_reason = "delegation_not_required_for_declared_basis"

    if actor_current is None or delegation_current is None:
        disposition = "FAIL_CLOSED"
    elif actor_current is False or delegation_current is False:
        disposition = "DENY"
    else:
        disposition = "ALLOW"

    refs: list[str] = []
    for item in (selected_authority, selected_delegation):
        if item:
            refs.extend(item["evidence_refs"])
            refs.append(item["source_ref"])

    return {
        "schema": RESULT_SCHEMA,
        "task_id": request["task_id"],
        "observed_at": observed.isoformat(),
        "actor_identity": actor,
        "actor_role": request.get("actor_role"),
        "candidate": dict(candidate),
        "disposition": disposition,
        "actor_authority_current": actor_current,
        "delegation_current": delegation_current,
        "authority_reason": authority_reason,
        "delegation_reason": delegation_reason,
        "selected_authority_assertion_id": selected_authority["assertion_id"] if selected_authority else None,
        "selected_delegation_assertion_id": selected_delegation["assertion_id"] if selected_delegation else None,
        "target_binding": candidate["target"] if actor_current is True else None,
        "evidence_refs": list(dict.fromkeys(refs)),
        "role_label_used_as_authority": False,
        "role_policy_interpreted": False,
        "authority_issued": False,
        "credential_verified": False,
        "resolution_authority": "STEGCORE_TEST_AUTHORITY_BASIS",
        "authority_effect": RESULT_AUTHORITY_EFFECT,
    }


__all__ = [
    "AuthorityBasisError",
    "REQUEST_AUTHORITY_EFFECT",
    "REQUEST_SCHEMA",
    "RESULT_SCHEMA",
    "resolve_authority_basis",
    "validate_authority_basis_request",
]
