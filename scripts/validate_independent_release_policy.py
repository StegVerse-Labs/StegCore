#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
from datetime import datetime, timezone
from typing import Any

SCHEMA_VERSION = "stegcore.independent-release-policy.v1"
REPOSITORY = "StegVerse-Labs/StegCore"


def load(path: pathlib.Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root must be an object")
    return value


def parse_time(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include timezone")
    return parsed.astimezone(timezone.utc)


def validate(decision: dict[str, Any], readiness: dict[str, Any], *, now: datetime | None = None) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    errors: list[str] = []

    required = (
        "schema_version", "decision_id", "policy_version", "authority_ref", "repository",
        "candidate_commit", "release_readiness_assessment_hash", "runtime_evidence_hash",
        "governance_freshness_evidence_hash", "verdict", "issued_at", "expires_at",
    )
    for key in required:
        if decision.get(key) in (None, ""):
            errors.append(f"missing:{key}")

    if decision.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version_mismatch")
    if decision.get("repository") != REPOSITORY:
        errors.append("repository_mismatch")
    if decision.get("verdict") not in {"PASS", "DENY"}:
        errors.append("invalid_verdict")

    bindings = {
        "candidate_commit": readiness.get("stegcore_commit"),
        "release_readiness_assessment_hash": readiness.get("assessment_hash"),
        "runtime_evidence_hash": readiness.get("runtime_evidence_hash"),
        "governance_freshness_evidence_hash": readiness.get("governance_freshness_evidence_hash"),
    }
    for key, expected in bindings.items():
        if decision.get(key) != expected:
            errors.append(f"binding_mismatch:{key}")

    try:
        issued = parse_time(str(decision.get("issued_at", "")))
        expires = parse_time(str(decision.get("expires_at", "")))
        if expires <= issued:
            errors.append("invalid_validity_window")
        if now < issued:
            errors.append("decision_not_yet_valid")
        if now >= expires:
            errors.append("decision_expired")
    except (TypeError, ValueError):
        errors.append("invalid_timestamp")

    pass_verdict = decision.get("verdict") == "PASS"
    status = "PASS" if not errors and pass_verdict else "BLOCKED"
    return {
        "schema_version": "stegcore.independent-release-policy-validation.v1",
        "status": status,
        "decision_id": decision.get("decision_id"),
        "policy_version": decision.get("policy_version"),
        "authority_ref": decision.get("authority_ref"),
        "verdict": decision.get("verdict"),
        "exact_candidate_binding": not any(e.startswith("binding_mismatch:") for e in errors),
        "errors": errors,
        "release_policy_gate": "pass" if status == "PASS" else "pending_or_denied",
        "release_authority_created": False,
        "tag_authority_created": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decision", type=pathlib.Path, required=True)
    parser.add_argument("--readiness", type=pathlib.Path, default=pathlib.Path("evidence/release-readiness.json"))
    parser.add_argument("--output", type=pathlib.Path)
    args = parser.parse_args()

    if not args.decision.exists():
        result = {
            "schema_version": "stegcore.independent-release-policy-validation.v1",
            "status": "BLOCKED",
            "errors": ["independent_policy_decision_missing"],
            "release_policy_gate": "pending_or_denied",
            "release_authority_created": False,
            "tag_authority_created": False,
        }
    else:
        result = validate(load(args.decision), load(args.readiness))

    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
